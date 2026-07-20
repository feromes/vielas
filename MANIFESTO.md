# Manifesto

## Why this project exists

Urban morphology contains structures that cannot be directly observed, but can be inferred from the spatial organization of the built environment.

Pedestrian alleys in informal settlements are one example of such structures.

This project exists to develop transparent, reproducible and scientifically grounded methods capable of inferring those hidden urban infrastructures from airborne LiDAR.

The objective is not simply to detect paths.

The objective is to understand urban morphology.

---

## Philosophy

Every module of this project must represent a scientific concept.

Software architecture should emerge from scientific reasoning, not the opposite.

Whenever possible:

- simplicity beats cleverness;
- explicit is better than implicit;
- reproducibility beats performance;
- scientific clarity beats software elegance.

---

## Design Principles

- One responsibility per module.
- One concept per class.
- Every intermediate product must be reproducible.
- Parameters belong to configuration files.
- The pipeline should be deterministic.
- Every output should be explainable in the paper.

---

## Scope

This project is not intended to become a generic LiDAR framework.

It exists to support scientific research on urban morphology.

New functionality should only be added if it directly contributes to that objective.

When in doubt:

remove instead of adding.