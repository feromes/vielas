from mission import Mission

from dataset_builder import DatasetBuilder
from ground_model import GroundModel
from dataset_enricher import DatasetEnricher
from open_space import OpenSpace
from second_return_density import SecondReturnDensity
from edt import EuclideanDistance
from medial_axis import MedialAxis
from medial_distance import MedialDistance
from width_histogram import WidthHistogram
from skeleton_topology import SkeletonTopology
from skeleton_nodes import SkeletonNodes
from node_raster import NodeRaster
from pedestrian_network import PedestrianNetwork

mission = Mission.from_year(2020)

dataset = DatasetBuilder().build(
    mission,
    "SÃO REMO",
)

mdt = GroundModel(dataset).build()

dataset = DatasetEnricher().add_hag(
    dataset,
    mdt,
)

open_space = OpenSpace(dataset).build()

edt = EuclideanDistance(dataset).build()

medial_axis = MedialAxis(dataset).build()

medial_distance = MedialDistance(dataset).build()

topology = SkeletonTopology(dataset).build()

nodes = SkeletonNodes(dataset).build()

node_raster = NodeRaster(dataset).build()

pedestrian_network = PedestrianNetwork(dataset).build()

histogram_csv, histogram_png, width_stats = WidthHistogram(
    dataset,
    buffer=12,
    bins=60,
    max_width=20,
).build()

print(width_stats)