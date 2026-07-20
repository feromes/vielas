from __future__ import annotations

import geopandas as gpd
import networkx as nx
import numpy as np
import rasterio

from rasterio.transform import xy
from shapely.geometry import LineString

from dataset import Dataset
from typing import Optional


OFFSETS = (
    (-1, -1),
    (-1,  0),
    (-1,  1),
    ( 0, -1),
    ( 0,  1),
    ( 1, -1),
    ( 1,  0),
    ( 1,  1),
)


class PedestrianNetwork:

    def __init__(
        self,
        dataset: Dataset,
    ):

        self.dataset = dataset

        self.width = None
        self.mask = None

        self.transform = None
        self.crs = None

        self.graph = None

    # ---------------------------------------------------------------------

    def build(self):

        self._read()

        self._build_graph()

        segments = self._trace_segments()

        gdf = self._build_geodataframe(
            segments,
        )

        gdf = self._clip(
            gdf,
        )

        self._save(
            gdf,
        )

        return gdf

    # ---------------------------------------------------------------------

    def _read(self):

        path = (
            self.dataset.path.parent
            / "width.tif"
        )

        with rasterio.open(path) as src:

            self.width = src.read(1)

            self.transform = src.transform

            self.crs = src.crs

        self.mask = (
            np.isfinite(self.width)
            & (self.width > 0)
        )

    # ---------------------------------------------------------------------

    def _build_graph(self):

        rows, cols = np.where(self.mask)

        pixels = set(
            zip(
                rows.tolist(),
                cols.tolist(),
            )
        )

        graph = nx.Graph()

        for row, col in pixels:

            graph.add_node(
                (row, col)
            )

            for dr, dc in OFFSETS:

                nb = (
                    row + dr,
                    col + dc,
                )

                if nb in pixels:

                    graph.add_edge(
                        (row, col),
                        nb,
                    )

        self.graph = graph

    # ---------------------------------------------------------------------

    @staticmethod
    def _edge_key(a, b):

        return (a, b) if a < b else (b, a)

    # ---------------------------------------------------------------------

    def _trace_segments(self):

        degree = dict(
            self.graph.degree()
        )

        branch_nodes = {
            node
            for node, d in degree.items()
            if d != 2
        }

        visited_edges = set()

        segments = []

        #
        # segmentos entre branch nodes
        #

        for start in branch_nodes:

            for nb in self.graph.neighbors(start):

                edge = self._edge_key(
                    start,
                    nb,
                )

                if edge in visited_edges:
                    continue

                chain = [
                    start,
                    nb,
                ]

                visited_edges.add(edge)

                previous = start
                current = nb

                while (
                    degree[current] == 2
                    and current not in branch_nodes
                ):

                    nxt = [
                        node
                        for node in self.graph.neighbors(current)
                        if node != previous
                    ]

                    if len(nxt) == 0:
                        break

                    nxt = nxt[0]

                    edge = self._edge_key(
                        current,
                        nxt,
                    )

                    if edge in visited_edges:
                        break

                    visited_edges.add(edge)

                    chain.append(
                        nxt,
                    )

                    previous = current
                    current = nxt

                segments.append(
                    {
                        "pixels": chain,
                    }
                )

        #
        # loops fechados
        #

        remaining = (
            {
                self._edge_key(a, b)
                for a, b in self.graph.edges()
            }
            - visited_edges
        )

        if remaining:

            loop_graph = nx.Graph()

            loop_graph.add_edges_from(
                remaining
            )

            for component in nx.connected_components(loop_graph):

                sub = loop_graph.subgraph(
                    component
                )

                start = next(
                    iter(component)
                )

                chain = [start]

                previous = None
                current = start

                while True:

                    nxt = [
                        node
                        for node in sub.neighbors(current)
                        if node != previous
                    ]

                    if not nxt:
                        break

                    nxt = nxt[0]

                    if (
                        nxt == chain[0]
                        and len(chain) > 2
                    ):
                        chain.append(nxt)
                        break

                    chain.append(nxt)

                    previous = current
                    current = nxt

                    if (
                        len(chain)
                        > sub.number_of_nodes() + 2
                    ):
                        break

                segments.append(
                    {
                        "pixels": chain,
                    }
                )

        return segments
    # ---------------------------------------------------------------------

    def _build_feature(
        self,
        segment: dict,
    ) -> Optional[dict]:

        pixels = segment["pixels"]

        if len(pixels) < 2:
            return None

        coords = []

        widths = []

        for row, col in pixels:

            x, y = xy(
                self.transform,
                row,
                col,
                offset="center",
            )

            coords.append((x, y))

            widths.append(
                float(
                    self.width[row, col]
                )
            )

        line = LineString(coords)

        line = line.simplify(
            tolerance=0.25,
            preserve_topology=True,
        )

        widths = np.asarray(
            widths,
            dtype=float,
        )

        mean = float(np.nanmean(widths))

        std = float(np.nanstd(widths))

        return {

            "geometry": line,

            "n_px": len(pixels),

            "length_m": float(
                line.length
            ),

            "width_mean": mean,

            "width_median": float(
                np.median(widths)
            ),

            "width_min": float(
                widths.min()
            ),

            "width_max": float(
                widths.max()
            ),

            "width_std": std,

            "width_cv": (
                std / mean
                if mean > 0
                else 0
            ),

        }

    # ---------------------------------------------------------------------

    def _build_geodataframe(
        self,
        segments,
    ):

        records = []

        for segment in segments:

            feature = self._build_feature(
                segment,
            )

            if feature is None:
                continue

            records.append(
                feature
            )

        gdf = gpd.GeoDataFrame(
            records,
            crs=self.crs,
        )

        gdf.insert(
            0,
            "segment_id",
            np.arange(
                1,
                len(gdf) + 1,
            ),
        )

        return gdf

    # ---------------------------------------------------------------------
    def _clip(
        self,
        gdf: gpd.GeoDataFrame,
        buffer: float = 5.0,
    ):

        aoi = gpd.GeoDataFrame(

            geometry=[
                self.dataset.favela.geometry
            ],

            crs=gdf.crs,

        )

        aoi = aoi.buffer(
            buffer
        )

        return gpd.clip(
            gdf,
            aoi,
        )

    def _save(
        self,
        gdf: gpd.GeoDataFrame,
    ):

        output = (
            self.dataset.path.parent
            / "pedestrian_network.gpkg"
        )

        gdf.to_file(
            output,
            driver="GPKG",
        )