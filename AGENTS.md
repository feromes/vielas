# Agent Guidelines

These guidelines apply to every AI agent contributing to this repository.

---

## Objective

The goal of this project is not to produce code.

The goal is to produce reliable scientific software.

---

## Never

- Overengineer.
- Introduce unnecessary abstractions.
- Duplicate logic.
- Hide parameters.
- Change project architecture without discussion.

---

## Always

- Preserve reproducibility.
- Prefer explicit code.
- Keep functions small.
- Keep classes cohesive.
- Keep modules independent.

---

## Scientific First

Scientific clarity always has higher priority than software elegance.

When both conflict:

choose the scientific solution.

---

## Data

Intermediate datasets are valuable scientific products.

Do not remove them.

Do not overwrite them without explicit request.

---

## Reviews

Whenever implementing new functionality:

- verify consistency with ARCHITECTURE.md
- verify consistency with MANIFESTO.md
- keep the pipeline deterministic

---

## Philosophy

Write software that another researcher can understand five years from now.
