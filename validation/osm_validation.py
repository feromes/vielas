from __future__ import annotations

from pathlib import Path

import geopandas as gpd

from dataset import Dataset

import subprocess


class OSMValidation:

    def __init__(
        self,
        dataset: Dataset,
        buffer: float = 30.0,
    ):

        self.dataset = dataset
        self.buffer = buffer

    @property
    def output(self) -> Path:

        return (
            self.dataset.path.parent.parent
            / "osm_network.gpkg"
        )
    
    @property
    def osm_pbf(self):

        return Path(
            "download/sudeste-260711.osm.pbf"
        )


    @property
    def osm_database(self):

        return Path(
            "download/osm_reference.gpkg"
        )

    def run(self):

        if self.output.exists():

            print("    Using cached OSM...")

            return gpd.read_file(
                self.output
            )

        self.ensure_database()

        print(
            "    Clipping OSM..."
        )

        osm = self.clip_database()

        print(
            f"    {len(osm)} segmentos baixados"
        )

        osm = self.clip(osm)

        print(
            f"    {len(osm)} segmentos na favela"
        )

        summary = self.summarize(osm)

        # print(summary)

        osm.to_file(
            self.output,
            driver="GPKG",
        )

        return summary

    def clip_database(
        self,
    ):

        osm = gpd.read_file(
            self.osm_database,
        )

        osm = osm.to_crs(
            self.dataset.crs
        )

        aoi = gpd.GeoDataFrame(

            geometry=[
                self.dataset.favela.geometry
            ],

            crs=self.dataset.crs,

        )

        aoi = aoi.buffer(
            self.buffer
        )

        osm = gpd.clip(
            osm,
            aoi,
        )


        return osm

    def clip(
        self,
        osm: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:

        aoi = gpd.GeoDataFrame(
            geometry=[
                self.dataset.favela.geometry
            ],
            crs=self.dataset.crs,
        )

        return gpd.clip(
            osm,
            aoi,
        )

    def total_length(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> float:

        return float(
            gdf.length.sum()
        )

    def summarize(
        self,
        osm: gpd.GeoDataFrame,
    ) -> dict:

        return {

            "segments":
                len(osm),

            "length_m":
                self.total_length(osm),

            "footway":
                int(
                    (osm.highway == "footway").sum()
                ),

            "path":
                int(
                    (osm.highway == "path").sum()
                ),

            "steps":
                int(
                    (osm.highway == "steps").sum()
                ),

            "pedestrian":
                int(
                    (osm.highway == "pedestrian").sum()
                ),

            "living_street":
                int(
                    (osm.highway == "living_street").sum()
                ),

        }

    def ensure_database(self):

        if self.osm_database.exists():

            return

        print(
            "    Building OSM database..."
        )

        subprocess.run(

            [

                "ogr2ogr",

                "-overwrite",

                "-f",

                "GPKG",

                str(self.osm_database),

                str(self.osm_pbf),

                "lines",

                "-where",

                "highway IS NOT NULL",

            ],

            check=True,

        )