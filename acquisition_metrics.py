from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from raster_grid import RasterGrid


@dataclass
class AcquisitionMetrics:

    array: np.ndarray

    grid: RasterGrid

    def to_dict(
        self,
    ) -> dict:

        area = (
            self.grid.width
            * self.grid.height
            * self.grid.resolution
            * self.grid.resolution
        )

        total_points = len(
            self.array
        )

        classification = self.array[
            "Classification"
        ]

        ground_mask = (
            classification == 2
        )

        ground_points = np.count_nonzero(
            ground_mask
        )

        return_number = self.array[
            "ReturnNumber"
        ]

        number_of_returns = self.array[
            "NumberOfReturns"
        ]

        first_return_mask = (
            return_number == 1
        )

        first_return_points = (
            np.count_nonzero(
                first_return_mask
            )
        )

        result = {

            "total_points":
                int(total_points),

            "points_per_m2":
                (
                    total_points
                    / area
                ),

            "ground_points":
                int(ground_points),

            "ground_points_per_m2":
                (
                    ground_points
                    / area
                ),

            "ground_percentage":
                (
                    100
                    * ground_points
                    / total_points
                ),

            "returns_mean":
                float(
                    np.mean(
                        number_of_returns
                    )
                ),

            "returns_median":
                float(
                    np.median(
                        number_of_returns
                    )
                ),

            "first_return_points":
                int(
                    first_return_points
                ),

            "first_return_density":
                (
                    first_return_points
                    / area
                ),

            "first_return_percentage":
                (
                    100
                    * first_return_points
                    / total_points
                ),

        }

        names = self.array.dtype.names

        if "ScanAngle" in names:

            scan = self.array[
                "ScanAngle"
            ].astype(float)

        elif "ScanAngleRank" in names:

            scan = self.array[
                "ScanAngleRank"
            ].astype(float)

        else:

            scan = None

        if scan is not None:

            abs_scan = np.abs(
                scan
            )

            result.update({

                "scan_min":
                    float(
                        scan.min()
                    ),

                "scan_max":
                    float(
                        scan.max()
                    ),

                "scan_range":
                    float(
                        scan.max()
                        -
                        scan.min()
                    ),

                "scan_abs_mean":
                    float(
                        abs_scan.mean()
                    ),

                "scan_abs_std":
                    float(
                        abs_scan.std()
                    ),

                "scan_abs_max":
                    float(
                        abs_scan.max()
                    ),

            })

        return result