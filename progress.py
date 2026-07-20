from pathlib import Path

import geopandas as gpd
import pandas as pd


DATASETS = Path("output/datasets")


class Progress:

    def __init__(self):

        self.favelas = gpd.read_file(
            "download/habita2geosampa_habi_favela2geosampa.gpkg"
        )

    def exists(
        self,
        path: Path,
    ) -> bool:

        return path.exists()

    def dataset_folder(
        self,
        row,
    ) -> Path:

        return (
            DATASETS
            / f"{int(row.gid):06d}_{row.nome.lower().replace(' ','_')}"
        )

    def year_status(
        self,
        folder: Path,
        year: int,
    ) -> bool:

        return self.exists(
            folder
            / str(year)
            / "width_histogram.csv"
        )

    def osm_status(
        self,
        folder: Path,
    ) -> bool:

        return self.exists(
            folder
            / "osm_validation.csv"
        )

    def temporal_status(
        self,
        folder: Path,
    ) -> bool:

        return self.exists(
            folder
            / "temporal"
            / "2017_2020"
            / "open_space_change.tif"
        )

    def build(self):

        rows = []

        for _, favela in self.favelas.iterrows():

            folder = self.dataset_folder(
                favela
            )

            rows.append(
                {
                    "gid": favela.gid,
                    "favela": favela.nome,
                    "2017": self.year_status(folder, 2017),
                    "2020": self.year_status(folder, 2020),
                    "2024": self.year_status(folder, 2024),
                    "osm": self.osm_status(folder),
                    "temporal": self.temporal_status(folder),
                }
            )

        df = pd.DataFrame(rows)

        df["completed"] = (
            df[
                [
                    "2017",
                    "2020",
                    "2024",
                    "osm",
                    "temporal",
                ]
            ]
            .sum(axis=1)
        )

        return df


if __name__ == "__main__":

    progress = Progress().build()

    progress.to_csv(
        "progress.csv",
        index=False,
    )

    print(progress)

    print()

    print(
        f"{len(progress)} favelas"
    )

    print(
        f"Concluídas: {(progress.completed == 5).sum()}"
    )

    print(
        f"Pendentes: {(progress.completed < 5).sum()}"
    )