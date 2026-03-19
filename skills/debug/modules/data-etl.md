# Data and ETL Debug Module

Use this module when the failure lives in ingestion, transformation, aggregation, schema drift, joins, null handling, or output quality.

This module starts thin on purpose. Add to it only when a real data or ETL incident produces a reusable pattern.

## Current Focus

- **Evidence**: input snapshots, output diffs, row counts, schema diffs, summary statistics
- **Fault boundaries**: schema change, timezone handling, join keys, aggregation logic, null policy
- **Repro levers**: same extraction window, same source data, same seed dataset, same config
- **Quality gate**: the expected metric, distribution, or schema returns to the intended state

## Growth Policy

Append new guidance only after a real session captures:

1. The failing data slice
2. The comparison that exposed the drift
3. The owning transformation boundary
4. The regression check worth keeping
