from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import xy
from shapely.geometry import Point

from dataset import Dataset

import pandas as pd


class NetworkValidation:

    def __init__(
        self,
        dataset: Dataset,
        reference: Path,
    ):

        self.dataset = dataset
        self.reference = reference

    @property
    def distance(self):

        return (
            self.dataset.path.parent
            / "pedestrian_network_distance.tif"
        )

    @property
    def sample_output(self):

        return (
            self.reference.parent
            / "osm_samples.gpkg"
        )

    @property
    def validation_output(self):

        return (
            self.reference.parent
            / "osm_validation.gpkg"
        )


    @property
    def summary_output(self):

        return (
            self.reference.parent
            / "osm_validation.csv"
        )

    def build(self):

        print(
            "  Sampling reference network..."
        )

        reference = gpd.read_file(
            self.reference
        )

        with rasterio.open(
            self.distance
        ) as src:

            edt = src.read(1)

            transform = src.transform

            profile = src.profile

        rows = []

        for segment_id, row in reference.iterrows():

            mask = rasterize(
                [(row.geometry, 1)],
                out_shape=edt.shape,
                transform=transform,
                fill=0,
                dtype=np.uint8,
                all_touched=True,
            )

            pixels = np.argwhere(
                mask == 1
            )

            for r, c in pixels:

                x, y = xy(
                    transform,
                    r,
                    c,
                    offset="center",
                )

                rows.append(
                    {
                        "segment": segment_id,
                        "highway": row.get(
                            "highway",
                            None,
                        ),
                        "distance": float(
                            edt[r, c]
                        ),
                        "geometry": Point(
                            x,
                            y,
                        ),
                    }
                )

        if len(rows) == 0:

            print(
                f"    {self.dataset.favela.name} "
                f"({self.dataset.mission.year}) "
                "→ nenhum ponto amostrado."
            )

            summary = {
                "favela": self.dataset.favela.name,
                "year": self.dataset.mission.year,
                "samples": 0,
                "mean": np.nan,
                "median": np.nan,
                "p90": np.nan,
                "maximum": np.nan,
                "within_0_5": np.nan,
                "within_1": np.nan,
                "within_2": np.nan,
                "within_3": np.nan,
                "within_5": np.nan,
                "std": np.nan,
                "osm_segments": len(reference),
                "osm_length_m": self.osm_length(reference),
                "lidar_length_m": self.lidar_length(),
                "lidar_vs_osm": np.nan,
            }

            pd.DataFrame([summary]).to_csv(
                self.summary_output,
                index=False,
            )

            return summary

        points = gpd.GeoDataFrame(
            rows,
            crs=profile["crs"],
        )

        points.to_file(
            self.sample_output,
            driver="GPKG",
        )

        summary = self.summarize(
            reference,
            points,
        )

        self.export_segments(
            reference,
            points,
        )

        pd.DataFrame(
            [summary]
        ).to_csv(
            self.summary_output,
            index=False,
        )

        print(
            f"    {len(points)} sampled points"
        )

        return summary

    def summarize(
        self,
        reference,
        points,
    ):

        d = points["distance"].to_numpy()

        summary = {

            "favela":
                self.dataset.favela.name,

            "year":
                self.dataset.mission.year,

            "samples":
                len(d),

            "mean":
                float(np.mean(d)),

            "median":
                float(np.median(d)),

            "p90":
                float(np.quantile(d, 0.90)),

            "maximum":
                float(np.max(d)),

            "within_0_5":
                float((d <= 0.5).mean()),

            "within_1":
                float((d <= 1).mean()),

            "within_2":
                float((d <= 2).mean()),

            "within_3":
                float((d <= 3).mean()),

            "within_5":
                float((d <= 5).mean()),

            "std":
                float(np.std(d)),

            "osm_segments":
                len(reference),

            "osm_length_m":
                self.osm_length(reference),

            "lidar_length_m":
                self.lidar_length(),

            "lidar_vs_osm":
                self.lidar_length()
                /
                self.osm_length(reference),

        }

        return summary

    def osm_length(
        self,
        reference: gpd.GeoDataFrame,
    ) -> float:

        return float(
            reference.length.sum()
        )


    def lidar_length(
        self,
    ) -> float:

        network = gpd.read_file(
            self.dataset.pedestrian_network
        )

        return float(
            network.length.sum()
        )

    def export_segments(
        self,
        reference: gpd.GeoDataFrame,
        points: gpd.GeoDataFrame,
    ):

        summary = (
            points
            .groupby("segment")
            .agg(
                mean_distance=("distance", "mean"),
                median_distance=("distance", "median"),
                p90=("distance",
                    lambda x: x.quantile(.9)),
                maximum=("distance", "max"),
                samples=("distance", "count"),
            )
        )

        reference = reference.join(summary)

        reference.to_file(
            self.validation_output,
            driver="GPKG",
        )