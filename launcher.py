from pathlib import Path

import pandas as pd


progress = pd.read_csv(
    "progress.csv"
)

faltam = (
    progress
    .query("completed < 5")
    .sort_values("favela")
    ["gid"]
)

arquivo = Path(
    "logs/favelas_pendentes.txt"
)

arquivo.write_text(
    "\n".join(
        str(gid)
        for gid in faltam
    )
)

print(
    f"{len(faltam)} favelas pendentes."
)

print(
    arquivo
)