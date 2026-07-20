from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
from scipy import ndimage


ROOT = Path("output/datasets")

SUMMARY = Path("output/summary")

FAVELA_FILE = Path(
    "download/habita2geosampa_habi_favela2geosampa.gpkg"
)


def describe(values, prefix):

    values = np.asarray(values)
    values = values[np.isfinite(values)]

    if values.size == 0:

        return {}

    return {

        f"{prefix}_mean": values.mean(),
        f"{prefix}_median": np.median(values),
        f"{prefix}_std": values.std(),

        f"{prefix}_min": values.min(),
        f"{prefix}_max": values.max(),

        f"{prefix}_p05": np.percentile(values, 5),
        f"{prefix}_p25": np.percentile(values, 25),
        f"{prefix}_p75": np.percentile(values, 75),
        f"{prefix}_p95": np.percentile(values, 95),

    }

def load_favelas():

    gdf = gpd.read_file(FAVELA_FILE)

    gdf["nome_upper"] = (
        gdf["nome"]
        .str.upper()
    )

    return gdf


def folder_to_name(folder):

    name = folder

    if "_" in name:

        name = name.split("_", 1)[1]

    return (
        name
        .replace("_", " ")
        .upper()
    )

def summarize_general(
    dataset_path: Path,
    favelas: gpd.GeoDataFrame,
) -> dict:

    result = {}

    favela = folder_to_name(
        dataset_path.parent.name
    )

    subset = (
        favelas[
            favelas.nome_upper == favela
        ]
    )

    if subset.empty:

        result["area_m2"] = np.nan
        result["perimeter_m"] = np.nan

        return result

    geometry = subset.geometry.iloc[0]

    result["area_m2"] = float(
        geometry.area
    )

    result["perimeter_m"] = float(
        geometry.length
    )

    return result

def summarize_acquisition(
    dataset_path: Path,
) -> dict:

    filename = (
        dataset_path
        / "acquisition_metrics.json"
    )

    if not filename.exists():
        return {}

    with open(filename) as f:
        return json.load(f)

def summarize_built(
    dataset_path: Path,
) -> dict:

    filename = (
        dataset_path
        / "occupied_hag.tif"
    )

    if not filename.exists():
        return {}

    with rasterio.open(filename) as src:

        hag = src.read(1)

        nodata = src.nodata

        pixel_area = abs(
            src.res[0] * src.res[1]
        )

    mask = np.isfinite(hag)

    if nodata is not None:
        mask &= hag != nodata

    mask &= hag > 0

    if mask.sum() == 0:
        return {}

    values = hag[mask]

    result = {}

    result["built_area_m2"] = (
        mask.sum()
        * pixel_area
    )

    result["built_volume_m3"] = (
        values.sum()
        * pixel_area
    )

    result.update(
        describe(
            values,
            "height",
        )
    )

    return result

def summarize_distance(
    dataset_path: Path,
) -> dict:

    filename = (
        dataset_path
        / "distance_to_building.tif"
    )

    if not filename.exists():
        return {}

    with rasterio.open(filename) as src:

        raster = src.read(1)

        nodata = src.nodata

        pixel_area = abs(
            src.res[0] * src.res[1]
        )

    mask = np.isfinite(raster)

    if nodata is not None:
        mask &= raster != nodata

    values = raster[mask]

    if values.size == 0:
        return {}

    result = {}

    result["valid_area_m2"] = (
        values.size
        * pixel_area
    )

    result.update(
        describe(
            values,
            "distance",
        )
    )

    return result

def summarize_width(
    dataset_path: Path,
) -> dict:

    filename = (
        dataset_path
        / "width.tif"
    )

    if not filename.exists():
        return {}

    with rasterio.open(filename) as src:

        raster = src.read(1)

        nodata = src.nodata

        pixel_area = abs(
            src.res[0] * src.res[1]
        )

    mask = np.isfinite(raster)

    if nodata is not None:
        mask &= raster != nodata

    values = raster[mask]

    if values.size == 0:
        return {}

    result = {}

    result["valid_area_m2"] = (
        values.size
        * pixel_area
    )

    result.update(
        describe(
            values,
            "width",
        )
    )

    return result

def summarize_open_space(
    dataset_path: Path,
) -> dict:

    filename = (
        dataset_path
        / "open_space.tif"
    )

    if not filename.exists():
        return {}

    with rasterio.open(filename) as src:

        raster = src.read(1)

        nodata = src.nodata

        pixel_area = abs(
            src.res[0] * src.res[1]
        )

    mask = np.isfinite(raster)

    if nodata is not None:
        mask &= raster != nodata

    open_space = (
        raster > 0
    ) & mask

    if open_space.sum() == 0:
        return {}

    labels, components = ndimage.label(
        open_space
    )

    component_sizes = np.bincount(
        labels.ravel()
    )[1:]

    result = {}

    result["open_space_area_m2"] = (
        open_space.sum()
        * pixel_area
    )

    result["components"] = components

    result["largest_component_m2"] = (
        component_sizes.max()
        * pixel_area
    )

    result["component_area_mean_m2"] = (
        component_sizes.mean()
        * pixel_area
    )

    return result

def summarize_delta_raster(
    filename: Path,
    prefix: str,
) -> dict:

    if not filename.exists():
        return {}

    with rasterio.open(filename) as src:

        raster = src.read(1)

        nodata = src.nodata

        pixel_area = abs(
            src.res[0] * src.res[1]
        )

    mask = np.isfinite(raster)

    if nodata is not None:
        mask &= raster != nodata

    values = raster[mask]

    if values.size == 0:
        return {}

    result = {}

    result.update(
        describe(
            values,
            prefix,
        )
    )

    result[f"{prefix}_gain_area_m2"] = (
        (values > 0).sum()
        * pixel_area
    )

    result[f"{prefix}_loss_area_m2"] = (
        (values < 0).sum()
        * pixel_area
    )

    result[f"{prefix}_net_change"] = (
        values.sum()
        * pixel_area
    )

    return result

def summarize_temporal(
    dataset_path: Path,
) -> dict:

    temporal = (
        dataset_path.parent
        / "temporal"
    )

    if not temporal.exists():
        return {}

    result = {}

    result.update(
        summarize_delta_raster(
            temporal / "delta_hag.tif",
            "hag",
        )
    )

    result.update(
        summarize_delta_raster(
            temporal / "delta_dsm.tif",
            "dsm",
        )
    )

    result.update(
        summarize_delta_raster(
            temporal / "open_space_change.tif",
            "open_space",
        )
    )

    return result

def summarize_validation(
    dataset_path: Path,
) -> dict:

    filename = (
        dataset_path
        / "validation_summary.csv"
    )

    if not filename.exists():
        return {}

    df = pd.read_csv(filename)

    if df.empty:
        return {}

    row = {}

    for column in df.columns:

        row[column] = df.iloc[0][column]

    return row

def summarize_osm(
    dataset_path: Path,
) -> dict:

    filename = (
        dataset_path.parent
        / "osm_validation.csv"
    )

    if not filename.exists():
        return {}

    df = pd.read_csv(filename)

    if df.empty:
        return {}

    row = {}

    for column in df.columns:

        if column == "favela":
            continue

        row[column] = df.iloc[0][column]

    return row

def summarize_centerline(
    dataset_path: Path,
) -> dict:

    filename = dataset_path / "centerline_network.gpkg"

    if not filename.exists():
        return {}

    gdf = gpd.read_file(filename)

    result = {}

    result["segments_total"] = len(gdf)

    if "tail_candidate" in gdf.columns:

        result["segments_tail"] = int(
            gdf["tail_candidate"].sum()
        )

        gdf = gdf[
            ~gdf["tail_candidate"]
        ].copy()

    else:

        result["segments_tail"] = np.nan

    if "short_tail" in gdf.columns:

        result["segments_short_tail"] = int(
            gdf["short_tail"].sum()
        )

    else:

        result["segments_short_tail"] = np.nan

    result["segments_kept"] = len(gdf)

    if result["segments_total"] > 0:

        result["tail_ratio"] = (
            result["segments_tail"]
            / result["segments_total"]
        )

    else:

        result["tail_ratio"] = np.nan

    result["network_length"] = gdf.length.sum()

    alley = gdf[
        gdf["width_median"] < 5
    ]

    street = gdf[
        gdf["width_median"] >= 5
    ]

    result["alley_length"] = alley.length.sum()

    result["street_length"] = street.length.sum()

    result["alley_ratio"] = (
        result["alley_length"]
        / result["network_length"]
        if result["network_length"] > 0
        else np.nan
    )

    result.update(
        describe(
            gdf.length.to_numpy(),
            "segment_length",
        )
    )

    if "width_median" in gdf.columns:

        result.update(
            describe(
                gdf["width_median"]
                .dropna()
                .to_numpy(),
                "width",
            )
        )

    if "distance_median" in gdf.columns:

        result.update(
            describe(
                gdf["distance_median"]
                .dropna()
                .to_numpy(),
                "distance",
            )
        )

    if "context_height_median" in gdf.columns:

        result.update(
            describe(
                gdf["context_height_median"]
                .dropna()
                .to_numpy(),
                "context_height",
            )
        )

    return result

def build_summary(
    favelas,
    summary_function,
):

    rows = []

    datasets = [
        year
        for favela in ROOT.iterdir()
        if favela.is_dir()
        for year in favela.iterdir()
        if year.is_dir() and year.name.isdigit()
    ]

    total = len(datasets)

    for i, dataset_path in enumerate(datasets, start=1):

        if (
            summary_function is summarize_temporal
            and dataset_path.name != "2017"
        ):
            continue

        print(
            f"[{i:4d}/{total}] "
            f"{summary_function.__name__:<24}"
            f"{dataset_path.parent.name} "
            f"{dataset_path.name}"
        )

        row = {

            "favela": dataset_path.parent.name,

            "year": int(dataset_path.name),

        }

        if summary_function is summarize_general:

            row.update(
                summary_function(
                    dataset_path,
                    favelas,
                )
            )

        else:

            row.update(
                summary_function(
                    dataset_path,
                )
            )

        rows.append(row)

    return (
        pd.DataFrame(rows)
        .sort_values(
            ["favela", "year"]
        )
    )

def main():

    SUMMARY.mkdir(
        parents=True,
        exist_ok=True,
    )

    favelas = load_favelas()

    summaries = {

        "general_summary.csv":
            build_summary(
                favelas,
                summarize_general,
            ),

        "centerline_summary.csv":
            build_summary(
                favelas,
                summarize_centerline,
            ),

        "acquisition_summary.csv":
            build_summary(
                favelas,
                summarize_acquisition,
            ),

        "built_summary.csv":
            build_summary(
                favelas,
                summarize_built,
            ),

        "distance_summary.csv":
            build_summary(
                favelas,
                summarize_distance,
            ),

        "width_summary.csv":
            build_summary(
                favelas,
                summarize_width,
            ),

        "open_space_summary.csv":
            build_summary(
                favelas,
                summarize_open_space,
            ),

        "temporal_summary.csv":
            build_summary(
                favelas,
                summarize_temporal,
            ),

        "validation_summary.csv":
            build_summary(
                favelas,
                summarize_validation,
            ),

        "osm_summary.csv":
            build_summary(
                favelas,
                summarize_osm,
            ),

    }

    for filename, df in summaries.items():

        output = SUMMARY / filename

        df.to_csv(
            output,
            index=False,
        )

        print(
            f"{filename}: {len(df)} registros"
        )

if __name__ == "__main__":
    main()