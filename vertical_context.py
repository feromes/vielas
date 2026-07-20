from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask

from dataset import Dataset


class VerticalContext:

    def __init__(
        self,
        dataset: Dataset,
        context_distance: float = 5.0,
        min_height: float = 2.0,
        min_width: float = 1.0,
    ):

        self.dataset = dataset
        self.context_distance = context_distance
        self.min_height = min_height
        self.min_width = min_width

    def run(
        self,
        network: Path,
        height_raster: Path,
    ) -> gpd.GeoDataFrame:

        gdf = gpd.read_file(network)

        if "width_median" not in gdf.columns:
            raise ValueError(
                "'width_median' não encontrado na rede. "
                "Execute primeiro o cálculo das larguras."
            )

        with rasterio.open(height_raster) as src:

            nodata = src.nodata

            means = []
            medians = []
            stds = []
            p95s = []
            maxs = []

            for _, row in gdf.iterrows():

                geom = row.geometry

                width = row.get("width_median", np.nan)

                try:
                    width = float(width)
                except (TypeError, ValueError):
                    width = self.min_width

                if not np.isfinite(width):
                    width = self.min_width

                width = max(width, self.min_width)

                # metade da largura da viela
                inner_radius = width / 2.0

                # acrescenta o contexto desejado
                outer_radius = inner_radius + self.context_distance

                inner = geom.buffer(inner_radius)
                outer = geom.buffer(outer_radius)

                area = outer.difference(inner)

                try:

                    image, _ = mask(
                        src,
                        [area],
                        crop=True,
                        filled=False,
                    )

                    values = image[0].compressed()

                    if nodata is not None:
                        values = values[values != nodata]

                    values = values[np.isfinite(values)]

                    # mantém apenas elementos verticais relevantes
                    values = values[values >= self.min_height]

                    if values.size == 0:

                        means.append(np.nan)
                        medians.append(np.nan)
                        stds.append(np.nan)
                        p95s.append(np.nan)
                        maxs.append(np.nan)

                        continue

                    means.append(np.mean(values))
                    medians.append(np.median(values))
                    stds.append(np.std(values))
                    p95s.append(np.percentile(values, 95))
                    maxs.append(np.max(values))

                except Exception:

                    means.append(np.nan)
                    medians.append(np.nan)
                    stds.append(np.nan)
                    p95s.append(np.nan)
                    maxs.append(np.nan)

        gdf["context_height_mean"] = means
        gdf["context_height_median"] = medians
        gdf["context_height_std"] = stds
        gdf["context_height_p95"] = p95s
        gdf["context_height_max"] = maxs

        return gdf