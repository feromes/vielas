from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize

from dataset import Dataset
from edt import EuclideanDistance


class PedestrianNetworkDistance:

    def __init__(
        self,
        dataset: Dataset,
    ):
        self.dataset = dataset

    @property
    def output(self) -> Path:

        return (
            self.dataset.path.parent
            / "pedestrian_network_distance.tif"
        )

    def build(self) -> Path:

        print(
            "  Building pedestrian network distance..."
        )

        network = gpd.read_file(
            self.dataset.pedestrian_network
        )

        mask = rasterize(
            (
                (geom, 0)
                for geom in network.geometry
            ),
            out_shape=(
                self.dataset.grid.height,
                self.dataset.grid.width,
            ),
            transform=self.dataset.grid.transform,
            fill=1,
            dtype=np.uint8,
            all_touched=True,
        )

        edt = EuclideanDistance.compute(mask)

        profile = {
            "driver": "GTiff",
            "height": self.dataset.grid.height,
            "width": self.dataset.grid.width,
            "count": 1,
            "dtype": "float32",
            "crs": self.dataset.crs,
            "transform": self.dataset.grid.transform,
            "compress": "deflate",
            "nodata": -9999,
        }

        with rasterio.open(
            self.output,
            "w",
            **profile,
        ) as dst:

            dst.write(
                edt,
                1,
            )

        return self.output