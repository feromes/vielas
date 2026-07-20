from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio

from temporal_dataset import TemporalDataset


class TemporalChange:

    def __init__(
        self,
        dataset: TemporalDataset,
    ):
        self.dataset = dataset

    def build(self):

        print("  Building delta DSM...")
        self._difference(
            before=self.dataset.before.occupied_dsm,
            after=self.dataset.after.occupied_dsm,
            output=self.dataset.delta_dsm,
        )

        print("  Building delta HAG...")
        self._difference(
            before=self.dataset.before.occupied_hag,
            after=self.dataset.after.occupied_hag,
            output=self.dataset.delta_hag,
        )

        print("  Building open-space change...")
        self._open_space_change(
            before=self.dataset.before.open_space,
            after=self.dataset.after.open_space,
            output=self.dataset.open_space_change,
        )

        return {
            "delta_dsm": self.dataset.delta_dsm,
            "delta_hag": self.dataset.delta_hag,
            "open_space_change": self.dataset.open_space_change,
        }

    def _difference(
        self,
        before: Path,
        after: Path,
        output: Path,
    ) -> Path:

        with rasterio.open(before) as src_before:

            before_image = src_before.read(1)

            profile = src_before.profile.copy()

            before_nodata = src_before.nodata

        with rasterio.open(after) as src_after:

            after_image = src_after.read(1)

            after_nodata = src_after.nodata

            self._validate_alignment(
                before_shape=before_image.shape,
                after_shape=after_image.shape,
                before_transform=profile["transform"],
                after_transform=src_after.transform,
                before_crs=profile["crs"],
                after_crs=src_after.crs,
            )

        valid = np.isfinite(before_image) & np.isfinite(after_image)

        if before_nodata is not None:
            valid &= before_image != before_nodata

        if after_nodata is not None:
            valid &= after_image != after_nodata

        nodata = -9999.0

        delta = np.full(
            before_image.shape,
            nodata,
            dtype=np.float32,
        )

        delta[valid] = (
            after_image[valid]
            - before_image[valid]
        )

        profile.update(
            dtype="float32",
            nodata=nodata,
            compress="lzw",
        )

        with rasterio.open(
            output,
            "w",
            **profile,
        ) as dst:

            dst.write(
                delta,
                1,
            )

        return output

    def _open_space_change(
        self,
        before: Path,
        after: Path,
        output: Path,
    ) -> Path:

        with rasterio.open(before) as src_before:

            before_image = src_before.read(1)

            profile = src_before.profile.copy()

        with rasterio.open(after) as src_after:

            after_image = src_after.read(1)

            self._validate_alignment(
                before_shape=before_image.shape,
                after_shape=after_image.shape,
                before_transform=profile["transform"],
                after_transform=src_after.transform,
                before_crs=profile["crs"],
                after_crs=src_after.crs,
            )

        # Convenção atual de open_space.tif:
        #
        # 0 = espaço aberto
        # 1 = obstáculo/ocupado
        #
        # Saída:
        #
        # -1 = abriu:
        #      ocupado em 2017 e aberto em 2020
        #
        #  0 = permaneceu igual
        #
        #  1 = fechou:
        #      aberto em 2017 e ocupado em 2020
        #
        # 99 = NoData

        nodata = 99

        change = np.full(
            before_image.shape,
            nodata,
            dtype=np.int8,
        )

        valid = (
            np.isin(before_image, [0, 1])
            &
            np.isin(after_image, [0, 1])
        )

        change[valid] = 0

        opened = (
            valid
            &
            (before_image == 1)
            &
            (after_image == 0)
        )

        closed = (
            valid
            &
            (before_image == 0)
            &
            (after_image == 1)
        )

        change[opened] = -1
        change[closed] = 1

        profile.update(
            dtype="int8",
            nodata=nodata,
            compress="lzw",
        )

        with rasterio.open(
            output,
            "w",
            **profile,
        ) as dst:

            dst.write(
                change,
                1,
            )

        return output

    def _validate_alignment(
        self,
        before_shape,
        after_shape,
        before_transform,
        after_transform,
        before_crs,
        after_crs,
    ):

        if before_shape != after_shape:
            raise ValueError(
                "Os rasters de 2017 e 2020 possuem dimensões diferentes."
            )

        if before_transform != after_transform:
            raise ValueError(
                "Os rasters de 2017 e 2020 não estão alinhados "
                "na mesma grade espacial."
            )

        if before_crs != after_crs:
            raise ValueError(
                "Os rasters de 2017 e 2020 possuem CRS diferentes."
            )