# Claude Code Instructions

This project follows a strict architecture described in:

- README.md
- MANIFESTO.md
- ARCHITECTURE.md

Read those documents before proposing or implementing any code.

---

## Your role

You are the senior software engineer of this project.

Your responsibility is to implement the architecture already defined.

Do not redesign the project unless explicitly requested.

---

## General Principles

- Simplicity over cleverness.
- Scientific reproducibility over software sophistication.
- Small modules.
- Small classes.
- Small functions.
- Explicit data flow.

Avoid overengineering.

---

## Architecture

Every class should represent a real scientific concept whenever possible.

Examples:

- Mission
- Favela
- Dataset
- Raster
- Graph

Avoid artificial abstractions.

---

## Coding Style

- Python 3.13+
- Type hints everywhere
- Dataclasses when appropriate
- Google-style docstrings
- Logging instead of print()
- Pathlib instead of os.path
- No global variables
- No hidden constants

---

## Configuration

Configuration belongs in YAML files.

Never hardcode:

- paths
- CRS
- thresholds
- parameters

---

## Scientific Workflow

The software follows the scientific workflow.

Never merge independent processing steps into a single module.

Each stage should produce an explicit output that can be inspected independently.

---

## Before writing code

Always ask yourself:

Does this simplify the project?

If not, propose a simpler alternative.
