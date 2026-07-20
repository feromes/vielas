from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import Affine

from dataset import Dataset

import numpy as np
import pandas as pd


class Validation:

    def __init__(
        self,
        dataset: Dataset,
        reference: Path,
    ):

        self.dataset = dataset
        self.reference = reference

        self.algorithm = None
        self.reference_mask = None

        self.profile = None
        self.transform = None

    def build_algorithm_mask(
        self,
        width_threshold: float,
    ):

        network = gpd.read_file(
            self.dataset.centerline_network
        )

        network = network[
            (~network.tail_candidate)
            &
            (network.width_median <= width_threshold)
        ].copy()

        network.geometry = network.buffer(
            network.width_median / 2,
            cap_style="flat",
            join_style="mitre",
        )

        # print(self.transform)
        # print(self.reference_mask is None)

        self.algorithm = rasterize(

            (
                (geom, 1)
                for geom in network.geometry
            ),

            out_shape=self.shape,

            transform=self.transform,

            fill=0,

            dtype="uint8",

            all_touched=True,

        ).astype(bool)

    def rasterize_reference(
        self,
        buffer: float = 0.0,
    ):

        gdf = gpd.read_file(self.reference)

        if buffer != 0:
            gdf.geometry = gdf.buffer(buffer)

        self.reference_mask = rasterize(

            [(geom, 1) for geom in gdf.geometry],

            out_shape=self.shape,

            transform=self.transform,

            fill=0,

            dtype=np.uint8,

            all_touched=False,

        ).astype(bool)

    def compute_confusion(self):

        a = self.algorithm
        r = self.reference_mask

        tp = a & r
        fp = a & ~r
        fn = ~a & r
        tn = ~a & ~r

        return tp, fp, fn, tn

    def compute_metrics(self):

        tp, fp, fn, tn = self.compute_confusion()

        TP = tp.sum()
        FP = fp.sum()
        FN = fn.sum()
        TN = tn.sum()

        precision = TP / (TP + FP) if TP + FP else 0
        recall = TP / (TP + FN) if TP + FN else 0

        f1 = (
            2 * precision * recall /
            (precision + recall)
            if precision + recall else 0
        )

        iou = TP / (TP + FP + FN) if TP + FP + FN else 0

        dice = (
            2 * TP /
            (2 * TP + FP + FN)
            if 2 * TP + FP + FN else 0
        )

        return {
            "tp": int(TP),
            "fp": int(FP),
            "fn": int(FN),
            "tn": int(TN),
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "iou": iou,
            "dice": dice,
        }

    def export_validation_map(self):

        tp, fp, fn, tn = self.compute_confusion()

        classes = np.zeros_like(
            self.algorithm,
            dtype=np.uint8,
        )

        classes[tp] = 1
        classes[fp] = 2
        classes[fn] = 3

        with rasterio.open(self.dataset.distance_to_building) as src:

            distance = src.read(1)

        # classes[distance > 5] = 0

        profile = self.profile.copy()

        profile.update(dtype="uint8", count=1)

        output = self.dataset.validation_classes

        with rasterio.open(output, "w", **profile) as dst:

            dst.write(classes, 1)

    def load_grid(self):

        with rasterio.open(self.dataset.open_space) as src:

            self.profile = src.profile.copy()
            self.transform = src.transform
            self.shape = src.shape

    def run(
        self,
        width_threshold: float,
        export_map: bool = False,
    ):

        self.load_grid()

        self.rasterize_reference()

        self.build_algorithm_mask(
            width_threshold,
        )

        if export_map:
            self.export_validation_map()

        return self.compute_metrics()

    def sensitivity(
        self,
        start=2,
        stop=8,
        step=0.5,
    ):

        results = []

        for threshold in np.arange(
            start,
            stop + step,
            step,
        ):

            metrics = self.run(
                width_threshold=threshold,
                export_map=False,
            )

            metrics["threshold"] = threshold

            results.append(metrics)

        df = pd.DataFrame(results)

        df.to_csv(
            self.dataset.validation_summary.with_suffix(".csv"),
            index=False,
        )

        return df

