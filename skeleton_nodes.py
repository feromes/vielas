import geopandas as gpd
import numpy as np
import rasterio

from scipy.ndimage import label, center_of_mass
from shapely.geometry import Point

from dataset import Dataset


JUNCTION = 3


class SkeletonNodes:

    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    def build(self):

        topology_path = self.dataset.path.parent / "skeleton_topology.tif"
        output = self.dataset.path.parent / "nodes.gpkg"

        with rasterio.open(topology_path) as src:
            topology = src.read(1)
            transform = src.transform
            crs = src.crs

        junctions = topology == JUNCTION

        labels, n = label(junctions, structure=np.ones((3, 3)))

        if n == 0:
            gdf = gpd.GeoDataFrame(
                {"node_id": [], "pixels": [], "geometry": []}, crs=crs
            )
            gdf.to_file(output, driver="GPKG")
            return output

        # pixels por rótulo, vetorizado (sem loop)
        pixel_counts = np.bincount(labels.ravel())[1:]

        # centroide (linha, coluna) de cada rótulo, vetorizado (sem loop)
        centroids_rc = center_of_mass(
            junctions, labels, index=np.arange(1, n + 1)
        )

        records = [
            {
                "node_id": node_id,
                "pixels": int(pixels),
                "geometry": Point(*(transform * (col + 0.5, row + 0.5))),
            }
            for node_id, (row, col), pixels in zip(
                range(1, n + 1), centroids_rc, pixel_counts
            )
        ]

        gdf = gpd.GeoDataFrame(records, crs=crs)
        gdf.to_file(output, driver="GPKG")

        return output