from pathlib import Path

import numpy as np
import pdal
import rasterio

from skimage.morphology import remove_small_objects

from dataset import Dataset


class OpenSpace:

    def __init__(
        self,
        dataset: Dataset,
        resolution: float = 0.5,
        max_height: float = 2.0,
    ):
        self.dataset = dataset
        self.resolution = resolution
        self.max_height = max_height

    def build(self) -> Path:

        output = (
            self.dataset.path.parent
            / "open_space.tif"
        )

        pipeline = f"""
        [
            "{self.dataset.path}",

            {{
                "type":"filters.expression",
                "expression":"HeightAboveGround <= {self.max_height}"
            }},

            {{
                "type":"writers.gdal",
                "filename":"{output}",

                "origin_x":{self.dataset.grid.xmin},
                "origin_y":{self.dataset.grid.ymin},

                "width":{self.dataset.grid.width},
                "height":{self.dataset.grid.height},

                "resolution":{self.dataset.grid.resolution},

                "output_type":"count",
                "dimension":"Z",
                "data_type":"uint16"
            }}
        ]
        """

        pdal.Pipeline(pipeline).execute()

        self._invert(output)

        return output

    def _invert(
        self,
        raster: Path,
    ):

        with rasterio.open(raster) as src:

            image = src.read(1)

            profile = src.profile

        # Após o PDAL:
        # image > 0  = tem ponto HAG <= 2m = espaço aberto/circulável
        # image == 0 = sem ponto baixo = cheio/obstáculo
        open_space = image > 0


        from skimage.measure import label

        labels = label(image)

        open_space = remove_small_objects(
            open_space,
            max_size=19,
            connectivity=2,
        )

        # Convenção esperada pelo medial_axis.py:
        # 0 = open space
        # 1 = obstáculo
        output = (~open_space).astype("uint8")

        profile.update(
            dtype="uint8",
            nodata=255,
        )

        with rasterio.open(raster, "w", **profile) as dst:

            dst.write(
                output,
                1,
            )
