from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

from dataset import Dataset


class MedialDistance:

    def __init__(
        self,
        dataset: Dataset,
    ):
        self.dataset = dataset

    def build(self) -> Path:

        medial_axis = (
            self.dataset.path.parent
            / "medial_axis.tif"
        )

        output = (
            self.dataset.path.parent
            / "distance_to_medial_axis.tif"
        )

        with rasterio.open(medial_axis) as src:

            skeleton = src.read(1).astype(bool)

            profile = src.profile

            pixel_size = src.res[0]

        #
        # distance_transform_edt calcula a distância
        # de cada pixel True até o False mais próximo.
        #
        # Como queremos distância ATÉ o eixo medial,
        # o eixo deve ser False.
        #
        distance = distance_transform_edt(
            ~skeleton
        )

        distance *= pixel_size

        profile.update(
            dtype="float32",
            count=1,
            compress="deflate",
        )

        with rasterio.open(output, "w", **profile) as dst:

            dst.write(
                distance.astype(np.float32),
                1,
            )

        return output