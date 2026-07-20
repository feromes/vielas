from pathlib import Path

import geopandas as gpd
from centerline.geometry import Centerline

import numpy as np
import rasterio
from shapely.geometry import LineString

from collections import Counter
from shapely.geometry import Point

INPUT = Path("output/datasets/são_remo/2020/pedestrian_network.gpkg")
OUTPUT = Path("centerline_test.gpkg")
DISTANCE = Path(
    "output/datasets/são_remo/2020/distance_to_building.tif"
)
MAX_TAIL_LENGTH = 1.00

gdf = gpd.read_file(INPUT)

gdf["geometry"] = gdf.apply(
    lambda row: row.geometry.buffer(
        row.width_median / 2,
        cap_style="round",
        join_style="round",
    ),
    axis=1,
)

polygon = gdf.union_all()

center = Centerline(
    polygon,
    interpolation_distance=0.5,
)

from shapely.ops import linemerge

merged = linemerge(center.geometry)

center_gdf = gpd.GeoDataFrame(
    geometry=list(center.geometry.geoms),
    crs=gdf.crs,
)

rows = []

with rasterio.open(DISTANCE) as src:

    def sample_line(line: LineString):

        length = line.length

        if length < 0.5:
            pts = [line.interpolate(0)]
        else:
            pts = [
                line.interpolate(d)
                for d in np.arange(0, length, 0.5)
            ]
            pts.append(line.interpolate(length))

        coords = [(p.x, p.y) for p in pts]

        values = np.array(
            list(src.sample(coords))
        )[:, 0]

        values = values[np.isfinite(values)]

        if len(values) == 0:
            return (
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            )

        length = line.length

        distance_ratio = (
            abs(values[-1] - values[0])
            / max(length, 0.001)
        )

        return (
            values.mean(),
            values.min(),
            values.max(),
            values.max() - values.min(),
            values.std(),
            distance_ratio,
        )

    rows = []

    if hasattr(merged, "geoms"):
        lines = [
            g
            for g in merged.geoms
            if g.geom_type == "LineString"
        ]
    else:
        lines = [merged]

    print(f"Centerline original: {len(center.geometry.geoms)} linhas")

    if hasattr(merged, "geoms"):
        print(f"Após linemerge: {len(merged.geoms)} linhas")
    else:
        print("Após linemerge: 1 linha")

    for geom in lines:

        mean, minimum, maximum, range_, std, distance_ratio = sample_line(geom)

        rows.append(
            {
                "geometry": geom,
                "length": geom.length,
                "distance_mean": mean,
                "distance_min": minimum,
                "distance_max": maximum,
                "distance_range": range_,
                "distance_std": std,
                "distance_ratio": distance_ratio,
                "tail_candidate": (
                    (distance_stats["ratio"] >= self.TAIL_RATIO)
                    and
                    (geom.length <= self.MAX_TAIL_LENGTH)
                ),
            }
        )

center_gdf = gpd.GeoDataFrame(
    rows,
    crs=gdf.crs,
)

print(center_gdf.length.describe())
print(center_gdf.nsmallest(30, "length")[["length"]])

# ---------------------------------------------------------
# Remove segmentos muito pequenos
# ---------------------------------------------------------

MIN_SEGMENT_LENGTH = 0.50  # metros

before = len(center_gdf)

center_gdf = center_gdf[
    center_gdf.length > MIN_SEGMENT_LENGTH
].copy()

after = len(center_gdf)

print(
    f"Removed {before - after} short segments "
    f"(< {MIN_SEGMENT_LENGTH:.2f} m)"
)

# ---------------------------------------------------------
# Build network nodes
# ---------------------------------------------------------

PRECISION = 2

counter = Counter()

for geom in center_gdf.geometry:

    coords = list(geom.coords)

    start = (
        round(coords[0][0], PRECISION),
        round(coords[0][1], PRECISION),
    )

    end = (
        round(coords[-1][0], PRECISION),
        round(coords[-1][1], PRECISION),
    )

    counter[start] += 1
    counter[end] += 1


nodes = []

for (x, y), degree in counter.items():

    nodes.append(
        {
            "geometry": Point(x, y),
            "degree": degree,
        }
    )


nodes_gdf = gpd.GeoDataFrame(
    nodes,
    crs=center_gdf.crs,
)

nodes_gdf.to_file(
    "nodes_test.gpkg",
    driver="GPKG",
)

center_gdf.to_file(
    OUTPUT,
    driver="GPKG",
)