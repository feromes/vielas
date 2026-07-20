from pathlib import Path
import json

import pdal

from dataset import Dataset
from raster_grid import RasterGrid
from acquisition_metrics import AcquisitionMetrics


class DatasetEnricher:

    def add_hag(
        self,
        dataset: Dataset,
        dem: Path,
    ) -> Dataset:

        output = dataset.path.with_stem(
            dataset.path.stem + "_hag"
        )

        pipeline_definition = [
            {
                "type": "readers.las",
                "filename": str(dataset.path),
            },
            {
                "type": "filters.hag_dem",
                "raster": str(dem),
            },
            {
                "type": "writers.las",
                "filename": str(output),
                "compression": "laszip",
                "extra_dims": "all",
            },
        ]

        pipeline = pdal.Pipeline(
            json.dumps(pipeline_definition)
        )

        pipeline.execute()

        array = pipeline.arrays[0]

        metrics = AcquisitionMetrics(
            array,
            dataset.grid,
        ).to_dict()

        with open(
            output.parent / "acquisition_metrics.json",
            "w",
        ) as f:

            json.dump(
                metrics,
                f,
                indent=4,
            )

        return Dataset(
            mission=dataset.mission,
            favela=dataset.favela,
            path=output,
            grid=dataset.grid,
        )