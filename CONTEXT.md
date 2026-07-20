# Project Structure

## Workspace

Project root

/Users/fernandogomes/MacLab/vielas

---

## External datasets

LiDAR datasets are stored outside the repository.

Location

/Users/fernandogomes/dev/ogdc

---

## LiDAR Missions

LiDAR-Sampa-2017

LiDAR-Sampa-2020

LiDAR-Sampa-2024

---

## Tile Indexes

articulacao_2017.zip

articulacao_2020.zip

articulacao_2024.gpkg

---

## Favela polygons

download/

habita2geosampa_habi_favela2geosampa.gpkg

---

## Study Areas

The project currently processes ten informal settlements described in the manuscript.

All study areas are contained in the GeoPackage above.

---

## Expected Output

output/

datasets/

    Sao_Remo/

        2017/

            sao_remo_2017.laz

        2020/

            ...

        2024/

            ...

---

The DatasetBuilder is responsible only for producing merged LAZ datasets.

No raster generation occurs at this stage.

## Current Decisions

✓ Python 3.13
✓ PDAL
✓ GeoPandas
✓ Rasterio
✓ Shapely
✓ Pathlib
✓ YAML configuration

## Decisions that should not be changed

* Mission is a core object.
* Dataset is a core object.
* Favela is a core object.
* The pipeline follows the scientific workflow.
* Intermediate outputs are preserved.
* LiDAR data remain outside the repository.