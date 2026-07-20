from pathlib import Path

import numpy as np
import rasterio
from skimage.morphology import medial_axis
from skimage.morphology import remove_small_objects

from dataset import Dataset


class MedialAxis:

    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    def build(self):

        open_space = (
            self.dataset.path.parent
            / "open_space.tif"
        )

        skeleton_output = (
            self.dataset.path.parent
            / "medial_axis.tif"
        )

        width_output = (
            self.dataset.path.parent
            / "width.tif"
        )

        with rasterio.open(open_space) as src:

            mask = ~src.read(1).astype(bool)

            profile = src.profile

            pixel_size = src.res[0]

        skeleton, distance = medial_axis(
            mask,
            return_distance=True,
        )

        skeleton = remove_small_objects(
            skeleton,
            max_size=19,
            connectivity=2,
        )

        width = (
            distance.astype(np.float32)
            * pixel_size
            * 2
        )

        width[~skeleton] = np.nan

        profile_bool = profile.copy()
        profile_bool.update(
            dtype="uint8",
            compress="deflate",
        )

        with rasterio.open(
            skeleton_output,
            "w",
            **profile_bool,
        ) as dst:

            dst.write(
                skeleton.astype(np.uint8),
                1,
            )

        profile_float = profile.copy()
        profile_float.update(
            dtype="float32",
            compress="deflate",
        )

        with rasterio.open(
            width_output,
            "w",
            **profile_float,
        ) as dst:

            dst.write(
                width,
                1,
            )

        return skeleton_output, width_output