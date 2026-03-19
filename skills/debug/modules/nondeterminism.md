# Nondeterminism Module

Use this module when a bug changes with time, seed, retries, parallelism, scheduling, or environment noise.

This is a cross-cutting module. Keep it thin and promote only the controls that real sessions prove useful.

AI application intermittency belongs here first unless the evidence clearly ties the failures to a physical condition, device setup, or measurement environment.

## Current Focus

- **Evidence**: run-to-run variance, seeds, timestamps, retry counts, worker counts, environment deltas
- **Fault boundaries**: clock usage, randomization, queue timing, retries, scheduling, hidden shared state
- **Repro levers**: fixed seeds, fake time, controlled retries, bounded concurrency, isolated environments
- **Quality gate**: the failure becomes more reproducible before the fix and reliably absent after it

## Boundary with Embedded Hardware

Stay in this module when the symptom tracks timing, control flow, model variance, retries, or scheduling more strongly than it tracks unit, fixture, power, location, or ambient conditions.

Move to `embedded-hardware.md` when the same software result changes with physical setup, neighboring equipment activity, power quality, or other environmental factors.

## Growth Policy

Append new guidance only after a real session captures:

1. The source of instability
2. The control that made the bug reproducible
3. The fix that removed the unstable behavior
4. The repeatable verification setting
