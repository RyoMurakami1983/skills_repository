# Performance Debug Module

Use this module when the feature works functionally but misses latency, memory, throughput, or allocation expectations.

This module is intentionally thin. Grow it from measured sessions, not from generic optimization advice.

## Current Focus

- **Evidence**: timings, profiles, flame graphs, memory snapshots, p95 or p99 metrics
- **Fault boundaries**: hot paths, allocations, I/O, locking, N+1 patterns, GC pressure
- **Repro levers**: warm-up policy, sample count, workload shape, hardware class, noise controls
- **Quality gate**: the same workload shows a measurable and explainable improvement

## Growth Policy

Append new guidance only after a real session captures:

1. The measured baseline
2. The bottleneck that actually dominated
3. The fix tied to that bottleneck
4. The workload used to verify improvement
