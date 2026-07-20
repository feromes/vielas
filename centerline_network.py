from __future__ import annotations

from pathlib import Path

import numpy as np
import geopandas as gpd
import rasterio

from shapely.ops import linemerge
from centerline.geometry import Centerline

from dataset import Dataset


class CenterlineNetwork:

    INTERPOLATION_DISTANCE = 0.50
    TAIL_RATIO = 0.50
    SAMPLE_DISTANCE = 0.50
    MIN_SEGMENT_LENGTH = 0.20      # 20 cm

    def __init__(
        self,
        dataset: Dataset,
    ):

        self.dataset = dataset

    def _sample_raster(
        self,
        line,
        src,
        compute_ratio=False,
    ):

        length = line.length

        if length < self.SAMPLE_DISTANCE:

            pts = [
                line.interpolate(0)
            ]

        else:

            pts = [

                line.interpolate(d)

                for d in np.arange(
                    0,
                    length,
                    self.SAMPLE_DISTANCE,
                )

            ]

            pts.append(
                line.interpolate(length)
            )

        coords = [
            (p.x, p.y)
            for p in pts
        ]

        values = np.array(
            list(src.sample(coords))
        )[:, 0]

        values = values[
            np.isfinite(values)
        ]

        if len(values) == 0:

            return {
                "mean": np.nan,
                "min": np.nan,
                "max": np.nan,
                "median": np.nan,
                "std": np.nan,
                "ratio": np.nan,
            }

        stats = {

            "mean": values.mean(),

            "min": values.min(),

            "max": values.max(),

            "median": np.median(values),

            "std": values.std(),

            "ratio": np.nan,

        }

        if compute_ratio:

            stats["ratio"] = (
                abs(
                    values[-1]
                    -
                    values[0]
                )
                /
                max(length, 0.001)
            )

        return stats

    def build(self):

        network = gpd.read_file(
            self.dataset.pedestrian_network
        )

        network = network.copy()

        network["geometry"] = network.apply(

            lambda row: row.geometry.buffer(

                max(
                    row.width_median / 2,
                    self.SAMPLE_DISTANCE,
                ),

                cap_style="round",

                join_style="round",

            ),

            axis=1,

        )

        polygon = network.union_all()

        center = Centerline(

            polygon,

            interpolation_distance=
                self.INTERPOLATION_DISTANCE,

        )

        merged = linemerge(
            center.geometry
        )

        if hasattr(
            merged,
            "geoms",
        ):

            lines = [
                g
                for g in merged.geoms
                if g.geom_type == "LineString"
            ]

        else:

            lines = [merged]

        lines = [
            g
            for g in lines
            if g.length >= self.MIN_SEGMENT_LENGTH
        ]

        distance = (
            self.dataset.path.parent
            /
            "distance_to_building.tif"
        )

        width = (
            self.dataset.path.parent
            /
            "width.tif"
        )

        output = (
            self.dataset
            .centerline_network
        )

        rows = []

        with rasterio.open(distance) as distance_src, \
             rasterio.open(width) as width_src:

            for geom in lines:

                distance_stats = self._sample_raster(
                    geom,
                    distance_src,
                    compute_ratio=True,
                )

                width_stats = self._sample_raster(
                    geom,
                    width_src,
                )

                rows.append(

                    {

                        "geometry": geom,

                        "length": geom.length,

                        "distance_mean":
                            distance_stats["mean"],

                        "distance_min":
                            distance_stats["min"],

                        "distance_max":
                            distance_stats["max"],

                        "distance_median":
                            distance_stats["median"],

                        "distance_std":
                            distance_stats["std"],

                        "distance_ratio":
                            distance_stats["ratio"],

                        "width_mean":
                            width_stats["mean"],

                        "width_min":
                            width_stats["min"],

                        "width_max":
                            width_stats["max"],

                        "width_median":
                            width_stats["median"],

                        "width_std":
                            width_stats["std"],

                        "tail_candidate": (

                            distance_stats["ratio"]
                            >=
                            self.TAIL_RATIO

                        ),

                        "distance_range": distance_stats["max"] - distance_stats["min"],

                    }

                )

        context = gpd.GeoDataFrame(
            rows,
            crs=network.crs,
        )

        from collections import Counter

        NODE_PRECISION = 2
        MAX_SHORT_TAIL_LENGTH = 1.00

        def node_key(coord):
            return (
                round(coord[0], NODE_PRECISION),
                round(coord[1], NODE_PRECISION),
            )


        degree = Counter()

        for geom in context.geometry:

            start = node_key(geom.coords[0])
            end = node_key(geom.coords[-1])

            degree[start] += 1
            degree[end] += 1

        short_tail = []

        for geom in context.geometry:

            start = node_key(geom.coords[0])
            end = node_key(geom.coords[-1])

            is_terminal = (
                degree[start] == 1
                or degree[end] == 1
            )

            short_tail.append(
                is_terminal
                and geom.length <= MAX_SHORT_TAIL_LENGTH
            )

        context["short_tail"] = short_tail

        context["tail_candidate"] = (
            context["tail_candidate"]
            | context["short_tail"]
        )

        context.to_file(

            output,

            driver="GPKG",

        )

        return output