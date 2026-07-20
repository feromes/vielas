from dataclasses import dataclass
from pathlib import Path
import re

@dataclass(slots=True)
class Favela:

    gid: int
    name: str
    geometry: object



    @property
    def slug(self):

        name = self.name.lower()

        name = (
            name
            .replace(" ", "_")
            .replace("/", "_")
        )

        name = re.sub(
            r"[^a-z0-9_à-ú]",
            "",
            name,
        )

        return f"{self.gid:06d}_{name}"