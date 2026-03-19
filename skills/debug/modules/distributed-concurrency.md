# Distributed and Concurrency Debug Module

Use this module when the failure depends on ordering, retries, race conditions, clock skew, eventual consistency, or state synchronization.

This module should stay thin until real distributed or concurrent failures teach stable patterns worth preserving.

## Current Focus

- **Evidence**: trace IDs, event timelines, retry counts, state transitions, causal logs
- **Fault boundaries**: ordering, at-least-once delivery, race windows, lock ownership, consistency boundaries
- **Repro levers**: fixed seeds, fake clocks, bounded parallelism, retry controls, fault injection
- **Quality gate**: the failure mode becomes reproducible enough to explain and verify, then stops under the same conditions

## Growth Policy

Append new guidance only after a real session captures:

1. The timing or ordering condition
2. The trace that proved causality
3. The design or code boundary that owned the bug
4. The reproducible verification setup
