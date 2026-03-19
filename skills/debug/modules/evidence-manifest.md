# Evidence Manifest Module

Use this module when you need a consistent way to record what was captured, how it was generated, and how before and after should be compared.

This module is intentionally thin. Grow it only when real sessions show which manifest fields save time downstream.

## Current Focus

- **Minimum fields**: case ID, observed behavior, expected behavior, stimulus, environment, evidence list, result
- **Evidence item fields**: type, path, command or method, compare method, notes
- **Comparison rule**: before and after must reference the same stimulus and environment assumptions
- **Quality gate**: another person can inspect the manifest and understand how the conclusion was reached

## Growth Policy

Append new guidance only after a real session proves a missing field caused confusion, delay, or a weak handoff.
