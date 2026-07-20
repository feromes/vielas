from dataclasses import dataclass
from pathlib import Path

from mission import Mission
from favela import Favela
from raster_grid import RasterGrid


@dataclass(slots=True)
class Dataset:
    mission: Mission
    favela: Favela
    path: Path
    grid: RasterGrid

    @property
    def has_hag(self) -> bool:
        return self.path.stem.endswith("_hag")

    @property
    def occupied_mask(self):
        return self.path.parent / "occupied_mask.tif"


    @property
    def occupied_dsm(self):
        return self.path.parent / "occupied_dsm.tif"


    @property
    def occupied_hag(self):
        return self.path.parent / "occupied_hag.tif"

    @property
    def occupied_summary(self):
        return self.path.parent / "occupied_summary.csv"

    @property
    def hag(self):
        return self.path.parent / "hag.tif"

    @property
    def dsm(self):
        return self.path.parent / "dsm.tif"

    @property
    def open_space(self):
        return self.path.parent / "open_space.tif"

    @property
    def validation_classes(self):
        return self.path.parent / "validation_classes.tif"


    @property
    def validation_summary(self):
        return self.path.parent / "validation_summary.json"

    @property
    def pedestrian_network(self):
        return self.path.parent / "pedestrian_network.gpkg"

    @property
    def crs(self):
        return "EPSG:31983"

    @property
    def pedestrian_network_context(self) -> Path:
        return self.path.parent / "pedestrian_network_context.gpkg"

    @property
    def distance_to_building(self):
        return (
            self.path.parent
            / "distance_to_building.tif"
        )

    @property
    def centerline_network(self):
        return (
            self.path.parent
            / "centerline_network.gpkg"
        )

    