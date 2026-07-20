# Architecture

## General Philosophy

The project follows the scientific workflow instead of the software workflow.

Each processing stage corresponds to one scientific operation.

The output of each stage becomes the input of the next stage.

---

## Core Objects

Mission

Represents one LiDAR acquisition campaign.

Examples:

- 2017
- 2020
- 2024

Responsible for:

- articulation layer
- tile naming
- dataset location

---

Favela

Represents one study area.

Responsible for:

- geometry
- buffered geometry
- metadata

---

Dataset

Represents one merged LiDAR dataset corresponding to one favela in one mission.

Example:

São Remo + 2024

↓

Dataset

---

Future Objects

Raster

Graph

Footpath Network

Validation Report

---

## Pipeline

Mission

+

Favela

↓

DatasetBuilder

↓

Dataset

↓

Processing

↓

Results

---

## Rules

Objects represent real-world entities whenever possible.

Avoid unnecessary abstraction.

Classes should remain small.

Each module has one responsibility.

No hidden parameters.

No duplicated logic.

No hardcoded paths.

Configuration belongs outside the code.