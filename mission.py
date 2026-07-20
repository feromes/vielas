from dataclasses import dataclass
from pathlib import Path


OGDC_ROOT = Path("/Users/fernandogomes/dev/ogdc")


@dataclass(slots=True)
class Mission:
    year: int
    lidar_root: Path
    articulation: Path
    tile_field: str

    @classmethod
    def from_year(cls, year: int) -> "Mission":

        if year == 2017:
            return cls(
                year=2017,
                lidar_root=OGDC_ROOT / "LiDAR-Sampa-2017",
                articulation=OGDC_ROOT / "articulacao_2017.zip",
                tile_field="cd_quadric",
            )

        if year == 2020:
            return cls(
                year=2020,
                lidar_root=OGDC_ROOT / "LiDAR-Sampa-2020",
                articulation=OGDC_ROOT / "articulacao_2020.zip",
                tile_field="cd_quadric",
            )

        if year == 2024:
            return cls(
                year=2024,
                lidar_root=OGDC_ROOT / "LiDAR-Sampa-2024",
                articulation=OGDC_ROOT / "articulacao_2024.gpkg",
                tile_field="nome_arquivo",
            )

        raise ValueError(f"Unsupported mission: {year}")

    def laz_filename(self, tile: str) -> str:

        if self.year == 2017:
            return f"MDS_color_{tile}.laz"

        if self.year == 2020:
            return f"MDS_{tile}_1000.laz"

        return f"{tile}.laz"