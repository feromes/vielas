from __future__ import annotations

import json
from pathlib import Path

import pdal

from dataset import Dataset


class GroundModel:

    def __init__(
        self,
        dataset: Dataset,
        resolution: float = 0.5,
        nodata: float = -9999.0,
    ):
        self.dataset = dataset
        self.resolution = resolution
        self.nodata = nodata

    def build(self) -> Path:
        """
        Gera um Modelo Digital do Terreno por interpolação linear
        sobre uma triangulação de Delaunay dos pontos classificados
        como terreno (Classification == 2).
        """

        output = (
            self.dataset.path.parent
            / f"{self.dataset.path.stem}_mdt.tif"
        )

        pipeline_definition = [
            {
                "type": "readers.las",
                "filename": str(self.dataset.path),
            },
            {
                "type": "filters.expression",
                "expression": "Classification == 2",
            },
            {
                "type": "filters.delaunay",
            },
            {
                "type": "filters.faceraster",
                "resolution": self.dataset.grid.resolution,
                "origin_x": self.dataset.grid.xmin,
                "origin_y": self.dataset.grid.ymin,
                "width": self.dataset.grid.width,
                "height": self.dataset.grid.height,
            },
            {
                "type": "writers.raster",
                "filename": str(output),
                "gdaldriver": "GTiff",
                "data_type": "float32",
                "nodata": self.nodata,
                "gdalopts": "COMPRESS=LZW,TILED=YES",
            },
        ]

        pipeline = pdal.Pipeline(
            json.dumps(pipeline_definition)
        )

        point_count = pipeline.execute()

        if point_count == 0:
            raise RuntimeError(
                "Nenhum ponto classificado como terreno "
                f"foi encontrado em {self.dataset.path}."
            )

        if not output.exists():
            raise RuntimeError(
                f"O MDT não foi criado: {output}"
            )

        return output