# Vielas

Morphological inference of pedestrian alleys (vielas) in informal settlements using airborne LiDAR.

## Overview

Vielas is a scientific framework developed during the PhD research of Fernando Gomes to infer pedestrian alley networks in Brazilian informal settlements (favelas) from airborne LiDAR point clouds.

Unlike traditional mapping approaches, the project treats alleyways as **emergent morphological structures** rather than directly observable objects. The framework extracts and analyzes the geometry of open spaces between buildings to reconstruct pedestrian circulation networks.

Although initially designed for São Paulo's municipal LiDAR datasets (2017, 2020 and 2024), the architecture is intended to remain generic enough to support future datasets.

---

## Current Pipeline

Dataset Builder

↓

Ground Model

↓

Open Space

↓

Distance Transform

↓

Skeleton

↓

Graph

↓

Cleaning

↓

Validation

↓

Figures & Tables

---

## Project Principles

- Scientific reproducibility comes first.
- Every processing step is explicit.
- Intermediate products are preserved.
- Code follows the scientific workflow.
- Simplicity is preferred over abstraction.

---

## Project Status

🚧 Under active development.