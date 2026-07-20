from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

from dataset import Dataset


class EuclideanDistance:

    def __init__(
        self,
        dataset: Dataset,
    ):
        self.dataset = dataset

    @staticmethod
    def compute(
        mask: np.ndarray,
    ) -> np.ndarray:

        return distance_transform_edt(mask).astype(
            np.float32
        )

    def build(self) -> Path:

        open_space = (
            self.dataset.path.parent
            / "open_space.tif"
        )

        output = (
            self.dataset.path.parent
            / "distance_to_building.tif"
        )

        with rasterio.open(open_space) as src:

            # open_space.tif:
            # 0 = espaço aberto
            # 1 = área ocupada
            #
            # A EDT calcula a distância dos pixels True
            # até o pixel False mais próximo.
            # Portanto, invertemos para que:
            # True  = espaço aberto
            # False = edificação
            mask = ~src.read(1).astype(bool)

            profile = src.profile

            pixel_size = src.res[0]

        edt = (
            self.compute(mask)
            * pixel_size
        )

        edt[~mask] = 0.0

        profile.update(
            dtype="float32",
            count=1,
            compress="deflate"
        )

        with rasterio.open(output, "w", **profile) as dst:
            dst.write(
                edt.astype(np.float32),
                1,
            )

        return output