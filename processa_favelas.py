import os

from mission import Mission
import traceback

from dataset_builder import DatasetBuilder
from ground_model import GroundModel
from dataset_enricher import DatasetEnricher
from open_space import OpenSpace
from edt import EuclideanDistance
from medial_axis import MedialAxis
from medial_distance import MedialDistance
from width_histogram import WidthHistogram
from skeleton_topology import SkeletonTopology
from skeleton_nodes import SkeletonNodes
from node_raster import NodeRaster
from pedestrian_network import PedestrianNetwork
from surface_model import SurfaceModel
from occupied_model import OccupiedModel
from temporal_dataset import TemporalDataset
from temporal_change import TemporalChange
from validation.validation import Validation
from pathlib import Path
from validation.osm_validation import OSMValidation
from pedestrian_network_distance import (
    PedestrianNetworkDistance,
)
from validation.network_validation import NetworkValidation
from vertical_context import VerticalContext
from centerline_network import CenterlineNetwork
from progress import Progress

DEBUG = False

# FAVELAS = [
#     "Heliópolis",
#     "Heliópolis - Viela Das Gaivotas",
#     "Cocaia I",
#     "Parque Cocaia II",
#     "Parque Cocaia III",
#     "Paraisópolis",
#     "Futuro Melhor",
#     "São Remo",
#     "Abacateiro",
# ]

FAVELAS = DatasetBuilder().list_favelas()

ANOS = [
    2017,
    2020,
    2024
]

DEBUG_FAVELAS = [
    "São Remo",
]

FAVELAS_PROCESSAR = DEBUG_FAVELAS if DEBUG else FAVELAS

import os
import time

PID = os.getpid()

print("=" * 80)
print(f"PID: {PID}")
print(f"INÍCIO: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

progress = (
    Progress()
    .build()
    .set_index("gid")
)

def process_favela(job):
    """
    Processa uma favela para um determinado levantamento.
    """

    ano, favela = job

    try:

        print(f"\n[{ano}] {favela}")

        mission = Mission.from_year(ano)

        print(">>> DatasetBuilder")

        dataset = DatasetBuilder().build(
            mission,
            favela,
        )

        print(">>> Dataset criado")

        mdt = GroundModel(dataset).build()

        dataset = DatasetEnricher().add_hag(
            dataset,
            mdt,
        )

        OpenSpace(dataset).build()

        SurfaceModel(dataset).build()

        OccupiedModel(dataset).build()

        EuclideanDistance(dataset).build()

        MedialAxis(dataset).build()

        MedialDistance(dataset).build()

        SkeletonTopology(dataset).build()

        SkeletonNodes(dataset).build()

        NodeRaster(dataset).build()

        PedestrianNetwork(dataset).build()

        PedestrianNetworkDistance(dataset).build()

        print(
            "  Building centerline network..."
        )

        CenterlineNetwork(
            dataset,
        ).build()

        vertical_context = VerticalContext(dataset)

        vertical_context.run(
            network=dataset.centerline_network,
            height_raster=dataset.occupied_hag,
        ).to_file(
            dataset.centerline_network,
            driver="GPKG",
        )

        if favela.nome == "São Remo":

            validation = Validation(
                dataset,
                Path("download/vielas comunidade são remo.gpkg"),
            )

            df = validation.sensitivity(
                start=2,
                stop=8,
                step=0.5,
            )

            print(df)

        _, _, width_stats = WidthHistogram(
            dataset,
            buffer=12,
            bins=60,
            max_width=20,
        ).build()

        print(f"✓ [{ano}] {favela.nome}")
        print(width_stats)

        import gc

        del mdt
        del vertical_context

        gc.collect()

        return dataset

    except Exception:

        print(f"✗ [{ano}] {favela.nome}")
        traceback.print_exc()
        return None

def processar_favela_completa(favela):

    print("=" * 80)
    print(favela.nome)
    print("=" * 80)

    import os

    inicio = time.time()

    print(
        f"[PID {os.getpid()}] Iniciando {favela.nome}"
    )

    datasets = {}

    for ano in ANOS:

        if progress.loc[favela.gid, str(ano)]:
            print(f"[{ano}] {favela.nome} já processada.")
            continue

        datasets[ano] = process_favela(
            (ano, favela)
        )

    #
    # Validação OSM
    #

    if 2020 in datasets:

        dataset2020 = datasets[2020]

        if dataset2020 is not None:

            osm = OSMValidation(
                dataset2020,
            )

            osm.run()

            NetworkValidation(
                dataset2020,
                osm.output,
            ).build()

    #
    # Mudança temporal
    #

    if (
        2017 in datasets
        and
        2020 in datasets
        and
        datasets[2017] is not None
        and
        datasets[2020] is not None
    ):

        temporal = TemporalDataset(
            before=datasets[2017],
            after=datasets[2020],
        )

        TemporalChange(
            temporal,
        ).build()

    tempo = time.time() - inicio

    print(
        f"[PID {os.getpid()}] Finalizada {favela.nome} "
        f"({tempo:.1f}s)"
    )

def main():

    import sys

    if len(sys.argv) != 2:

        print(
            "Uso:"
        )

        print(
            "python processa_favelas.py 'São Remo'"
        )

        return

    gid = int(sys.argv[1])

    favelas = DatasetBuilder().list_favelas()

    favela = favelas[
        favelas.gid == gid
    ].iloc[0]

    processar_favela_completa(
        favela
    )


if __name__ == "__main__":

    main()
