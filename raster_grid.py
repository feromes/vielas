from __future__ import annotations

from dataclasses import dataclass
from math import floor, ceil

from affine import Affine


@dataclass(slots=True)
class RasterGrid:

    xmin: float
    ymin: float
    xmax: float
    ymax: float
    resolution: float = 0.5

    @classmethod
    def from_bounds(
        cls,
        bounds,
        resolution: float = 0.5,
    ):

        xmin, ymin, xmax, ymax = bounds

        xmin = floor(xmin / resolution) * resolution
        ymin = floor(ymin / resolution) * resolution

        xmax = ceil(xmax / resolution) * resolution
        ymax = ceil(ymax / resolution) * resolution

        return cls(
            xmin,
            ymin,
            xmax,
            ymax,
            resolution,
        )

    @property
    def width(self):

        return int(
            round(
                (self.xmax - self.xmin)
                / self.resolution
            )
        )

    @property
    def height(self):

        return int(
            round(
                (self.ymax - self.ymin)
                / self.resolution
            )
        )

    @property
    def transform(self):

        return Affine(
            self.resolution,
            0,
            self.xmin,
            0,
            -self.resolution,
            self.ymax,
        )

    @property
    def bounds(self):

        return (
            self.xmin,
            self.ymin,
            self.xmax,
            self.ymax,
        )   