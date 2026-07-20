from pathlib import Path

import numpy as np
import rasterio

from dataset import Dataset


BACKGROUND = 0
ENDPOINT = 1
SEGMENT = 2
JUNCTION = 3
ISOLATED = 4


class SkeletonTopology:

    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    def build(self):

        skeleton_path = (
            self.dataset.path.parent
            / "medial_axis.tif"
        )

        output = (
            self.dataset.path.parent
            / "skeleton_topology.tif"
        )

        with rasterio.open(skeleton_path) as src:

            skeleton = src.read(1).astype(bool)

            profile = src.profile

        topology = np.zeros(
            skeleton.shape,
            dtype=np.uint8,
        )

        rows, cols = np.where(skeleton)

        for row, col in zip(rows, cols):

            r0 = max(0, row - 1)
            r1 = min(skeleton.shape[0], row + 2)

            c0 = max(0, col - 1)
            c1 = min(skeleton.shape[1], col + 2)

            window = skeleton[r0:r1, c0:c1]

            neighbours = (
                np.count_nonzero(window)
                - 1
            )

            if neighbours == 0:

                topology[row, col] = ISOLATED

            elif neighbours == 1:

                topology[row, col] = ENDPOINT

            elif neighbours == 2:

                topology[row, col] = SEGMENT

            else:

                topology[row, col] = JUNCTION

        profile.update(
            dtype="uint8",
            count=1,
            compress="deflate",
        )

        with rasterio.open(
            output,
            "w",
            **profile,
        ) as dst:

            dst.write(
                topology,
                1,
            )

        return output