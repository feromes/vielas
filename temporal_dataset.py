from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dataset import Dataset


@dataclass(slots=True)
class TemporalDataset:

    before: Dataset
    after: Dataset

    @property
    def before_year(self) -> int:
        return self.before.mission.year

    @property
    def after_year(self) -> int:
        return self.after.mission.year

    @property
    def folder(self) -> Path:

        # Exemplo:
        # output/datasets/são_remo/2020/arquivo.laz
        #
        # self.after.path.parent        -> .../são_remo/2020
        # self.after.path.parent.parent -> .../são_remo

        output = (
            self.after.path.parent.parent
            / "temporal"
            / f"{self.before_year}_{self.after_year}"
        )

        output.mkdir(
            parents=True,
            exist_ok=True,
        )

        return output

    @property
    def delta_dsm(self) -> Path:
        return self.folder / "delta_dsm.tif"

    @property
    def delta_hag(self) -> Path:
        return self.folder / "delta_hag.tif"

    @property
    def open_space_change(self) -> Path:
        return self.folder / "open_space_change.tif"