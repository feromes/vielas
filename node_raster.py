from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import label

from dataset import Dataset


JUNCTION = 3


class NodeRaster:

    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    def build(self):

        topology_path = (
            self.dataset.path.parent
            / "skeleton_topology.tif"
        )

        output = (
            self.dataset.path.parent
            / "node_raster.tif"
        )

        with rasterio.open(topology_path) as src:

            topology = src.read(1)

            profile = src.profile

        junctions = topology == JUNCTION

        labels, n_nodes = label(
            junctions,
            structure=np.ones((3, 3), dtype=np.uint8),
        )

        node_raster = np.zeros(
            topology.shape,
            dtype=np.uint16,
        )

        for node_id in range(1, n_nodes + 1):

            node_raster[
                labels == node_id
            ] = node_id

        profile.update(
            dtype="uint16",
            compress="deflate",
            nodata=0,
        )

        with rasterio.open(
            output,
            "w",
            **profile,
        ) as dst:

            dst.write(
                node_raster,
                1,
            )

        return output