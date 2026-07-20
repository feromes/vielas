from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask

from dataset import Dataset


class WidthHistogram:

    def __init__(
        self,
        dataset: Dataset,
        buffer: float = 12,
        bins: int = 60,
        max_width: float | None = None,
    ):
        self.dataset = dataset
        self.buffer = buffer
        self.bins = bins
        self.max_width = max_width

    def build(self):

        width_raster = (
            self.dataset.path.parent
            / "width.tif"
        )

        output_csv = (
            self.dataset.path.parent
            / "width_histogram.csv"
        )

        output_png = (
            self.dataset.path.parent
            / "width_histogram.png"
        )

        with rasterio.open(width_raster) as src:

            geom = gpd.GeoSeries(
                [self.dataset.favela.geometry],
                crs=src.crs,
            ).buffer(self.buffer)

            clipped, _ = mask(
                src,
                geom.geometry,
                crop=True,
                filled=True,
                nodata=np.nan,
            )

        values = clipped[0]

        values = values[
            np.isfinite(values)
            & (values > 0)
        ]

        if self.max_width is not None:
            values = values[values <= self.max_width]

        unique_widths, counts = np.unique(
            np.round(values, 6),
            return_counts=True,
        )

        hist = pd.DataFrame(
            {
                "width_m": unique_widths,
                "count": counts,
            }
        )

        hist["frequency"] = (
            hist["count"]
            / hist["count"].sum()
        )

        hist = hist.sort_values("width_m")

        hist.to_csv(
            output_csv,
            index=False,
        )

        stats = {
            "n": int(values.size),
            "min": float(np.min(values)),
            "p05": float(np.percentile(values, 5)),
            "p10": float(np.percentile(values, 10)),
            "p25": float(np.percentile(values, 25)),
            "median": float(np.percentile(values, 50)),
            "mean": float(np.mean(values)),
            "p75": float(np.percentile(values, 75)),
            "p90": float(np.percentile(values, 90)),
            "p95": float(np.percentile(values, 95)),
            "max": float(np.max(values)),
            "std": float(np.std(values)),
        }

        plt.figure(figsize=(14,5))

        plt.bar(
            hist["width_m"],
            hist["count"],
            width=0.15,
        )

        plt.xlabel("Local width (m)")
        plt.ylabel("Pixel count")
        plt.title(
            f"Discrete local widths — {self.dataset.favela.name}"
        )

        plt.tight_layout()
        plt.xlabel("Local width on medial axis (m)")
        plt.ylabel("Pixel count")
        plt.title(f"Width histogram — {self.dataset.favela.name}")
        plt.tight_layout()
        plt.savefig(output_png, dpi=300)
        plt.close()

        return output_csv, output_png, stats