from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio

from rasterio.features import geometry_mask

from dataset import Dataset


class OccupiedModel:

    def __init__(
        self,
        dataset: Dataset,
    ):
        self.dataset = dataset

    def build(self):

        print("  Building occupied DSM...")
        self._build(
            self.dataset.dsm,
            self.dataset.occupied_dsm,
        )

        print("  Building occupied HAG...")
        self._build(
            self.dataset.hag,
            self.dataset.occupied_hag,
        )

    def _build(
        self,
        source: Path,
        destination: Path,
    ):

        with rasterio.open(source) as src:

            image = src.read(1)

            profile = src.profile

            transform = src.transform

        with rasterio.open(
            self.dataset.path.parent / "open_space.tif"
        ) as src:

            occupied = src.read(1).astype(bool)

        inside = geometry_mask(
            [self.dataset.favela.geometry],
            out_shape=image.shape,
            transform=transform,
            invert=True,
        )

        mask = occupied & inside

        nodata = profile["nodata"]

        image = np.where(
            mask,
            image,
            nodata,
        )

        profile.update(
            compress="lzw",
            nodata=-9999,
        )

        with rasterio.open(
            destination,
            "w",
            **profile,
        ) as dst:

            dst.write(
                image.astype("float32"),
                1,
            )