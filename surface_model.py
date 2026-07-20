from __future__ import annotations

import json
from pathlib import Path

import pdal

from dataset import Dataset


class SurfaceModel:

    def __init__(
        self,
        dataset: Dataset,
        resolution: float = 0.5,
    ):
        self.dataset = dataset
        self.resolution = resolution

    def build(self):

        print("  Building DSM...")
        self._build_raster(
            dimension="Z",
            output=self.dataset.dsm,
        )

        print("  Building HAG...")
        self._build_raster(
            dimension="HeightAboveGround",
            output=self.dataset.hag,
        )

    def _build_raster(
        self,
        dimension: str,
        output: Path,
    ):

        pipeline = [
            {
                "type": "readers.las",
                "filename": str(self.dataset.path),
            },
            {
                "type": "writers.gdal",
                "filename": str(output),

                "origin_x": self.dataset.grid.xmin,
                "origin_y": self.dataset.grid.ymin,

                "width": self.dataset.grid.width,
                "height": self.dataset.grid.height,

                "resolution": self.dataset.grid.resolution,

                "dimension": dimension,
                "output_type": "max",

                "nodata": -9999,
                "data_type": "float32",
            },
        ]

        pdal.Pipeline(
            json.dumps(pipeline)
        ).execute()