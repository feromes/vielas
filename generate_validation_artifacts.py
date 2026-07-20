from pathlib import Path

from dataset_builder import DatasetBuilder
from mission import Mission
from validation.validation import Validation


# =====================================================
# Configuração
# =====================================================

FAVELA = "São Remo"

YEAR = 2020

WIDTH_THRESHOLD = 5.0

REFERENCE = Path(
    "download/vielas comunidade são remo.gpkg"
)


# =====================================================
# Programa principal
# =====================================================

def main():

    print("=" * 80)
    print("Community validation")
    print("=" * 80)

    mission = Mission.from_year(YEAR)

    FAVELA_GID = 542

    favelas = DatasetBuilder().list_favelas()

    favela = (
        favelas[
            favelas.gid == FAVELA_GID
        ]
        .iloc[0]
    )

    dataset = DatasetBuilder().build(
        mission,
        favela,
    )

    validation = Validation(
        dataset=dataset,
        reference=REFERENCE,
    )

    #
    # Curva de sensibilidade
    #

    print("\nGenerating sensitivity analysis...")

    sensitivity = validation.sensitivity(
        start=2,
        stop=8,
        step=0.5,
    )

    print(sensitivity)

    #
    # Geração do raster utilizado no artigo
    #

    print(
        f"\nGenerating validation map "
        f"(threshold = {WIDTH_THRESHOLD:.1f} m)..."
    )

    metrics = validation.run(
        width_threshold=WIDTH_THRESHOLD,
        export_map=True,
    )

    #
    # Resultados
    #

    print("\nValidation metrics")

    for key, value in metrics.items():

        print(
            f"{key:>10}: {value}"
        )

    print("\nGenerated files")

    print(
        f"Validation raster : {dataset.validation_classes}"
    )

    print(
        "Sensitivity table : "
        f"{dataset.validation_summary.with_suffix('.csv')}"
    )

    print(
        f"\nFigure threshold: {WIDTH_THRESHOLD:.1f} m"
    )

    print("\nDone.")


if __name__ == "__main__":

    main()