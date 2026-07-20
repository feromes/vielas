from pathlib import Path
import json

import geopandas as gpd
import pdal

from mission import Mission
from favela import Favela
from dataset import Dataset
from raster_grid import RasterGrid


class DatasetBuilder:

    def create_aoi(
        self,
        favela,
        buffer: float = 30,
    ):

        aoi = (
            favela.geometry
            .envelope
            .buffer(buffer)
            .envelope
        )

        return aoi

    def find_tiles(
        self,
        mission: Mission,
        aoi,
    ):

        tiles = gpd.read_file(
            mission.articulation
        )

        selected = tiles[
            tiles.intersects(aoi)
        ]

        return selected[mission.tile_field].tolist()

    def find_laz_files(
        self,
        mission: Mission,
        tiles: list[str],
    ):
        return [
            mission.lidar_root / mission.laz_filename(tile)
            for tile in tiles
    ]

    def merge_laz(
        self,
        input_files: list[Path],
        output_file: Path,
        aoi,
    ):
        output_file.parent.mkdir(parents=True, exist_ok=True)

        srs = "EPSG:31983"
        polygon = aoi.wkt

        pipeline_definition = [
            {
                "type": "readers.las",
                "filename": str(path),
                "default_srs": srs,   # só usa se o arquivo não tiver SRS embutido
            }
            for path in input_files
        ]

        pipeline_definition.append(
            {
                "type": "filters.crop",
                "polygon": polygon,
                "a_srs": srs,
            }
        )

        pipeline_definition.append(
            {
                "type": "writers.las",
                "filename": str(output_file),
                "compression": "laszip",
                "a_srs": srs,
            }
        )

        pipeline = pdal.Pipeline(json.dumps(pipeline_definition))
        pipeline.execute()

    def build(
        self,
        mission,
        favela,
    ):

        favela = Favela(
            gid=int(favela.gid),
            name=favela.nome,
            geometry=favela.geometry,
        )

        aoi = self.create_aoi(
            favela
        )

        grid = RasterGrid.from_bounds(
            aoi.bounds,
            resolution=0.5,
        )

        tiles = self.find_tiles(
            mission,
            aoi,
        )

        print(f"[{mission.year}] {favela.name} - {len(tiles)} tiles encontrados.")

        laz_files = self.find_laz_files(
            mission,
            tiles,
        )

        output = (
            Path("output")
            / "datasets"
            / favela.slug
            / str(mission.year)
            / f"{favela.slug}_{mission.year}.laz"
        )

        self.merge_laz(
            laz_files,
            output,
            aoi,
        )

        return Dataset(
            mission=mission,
            favela=Favela(
                gid=int(favela.gid),
                name=favela.name,
                geometry=favela.geometry,
            ),
            path=output,
            grid=grid,
        )

    def list_favelas(self):

        return gpd.read_file(
            "download/habita2geosampa_habi_favela2geosampa.gpkg"
        )
    
