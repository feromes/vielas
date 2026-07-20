from pathlib import Path

import pdal

from dataset import Dataset


class SecondReturnDensity:

    def __init__(
        self,
        dataset: Dataset,
        resolution: float = 0.5,
    ):
        self.dataset = dataset
        self.resolution = resolution

    def build(self) -> Path:

        output = (
            self.dataset.path.parent
            / "second_return_density.tif"
        )

        pipeline = f"""
        [
            "{self.dataset.path}",

            {{
                "type":"filters.expression",
                "expression":"ReturnNumber > 1"
            }},

            {{
                "type":"writers.gdal",
                "filename":"{output}",
                "resolution":{self.resolution},
                "output_type":"count",
                "dimension":"Z",
                "data_type":"uint16"
            }}
        ]
        """

        pdal.Pipeline(pipeline).execute()

        return output