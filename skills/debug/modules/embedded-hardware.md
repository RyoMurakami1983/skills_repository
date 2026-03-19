# Embedded and Hardware Debug Module

Use this module when the failure depends on sensors, waveforms, calibration state, fixtures, power conditions, environmental drift, or physical setup.

This module is intentionally thin. Grow it only from real hardware investigations that produce reusable measurement patterns.

Intermittent behavior is not a side note here. If the same setup sometimes passes and sometimes fails, treat that variance itself as evidence and look for the physical variable that moved.

## Current Focus

- **Evidence**: raw waveforms, sensor logs, calibration records, fixture photos, timestamps, location, ambient conditions, nearby equipment activity, spec compliance
- **Fault boundaries**: sensor chain, A/D stage, filtering, estimation logic, decision thresholds, mechanics, power quality, EMI or noise coupling, setup error
- **Repro levers**: same fixture, same unit class, same temperature, same power state, same calibration state, same time window, same nearby machine state
- **Quality gate**: the same measurement setup shows improved repeatability, lower occurrence rate, or expected signal behavior with an explainable cause

## When Intermittent Behavior Points to Hardware

Use this module first when the symptom changes with physical conditions such as:

- Time of day, shift, or production timing
- Location, fixture, bench, cable routing, or installation posture
- Nearby equipment switching on or off
- Temperature, vibration, airflow, grounding, or power quality
- Unit-to-unit variation or calibration state
- Operation outside the specified range, setup, or duty cycle

If the pass or fail pattern follows one of those conditions more than it follows code changes, hardware or environment is a strong first suspect.

## Isolation Hints

- **Cut the chain**: separate sensor, wiring, power, A/D, filtering, estimation, decision logic, and mechanics one boundary at a time.
- **Freeze one physical variable at a time**: change only temperature, power source, fixture, location, or neighboring equipment state per comparison.
- **Compare another unit or bench**: if the same software behaves differently on another unit, fixture, or location, the physical side becomes more likely.
- **Correlate with timestamps**: line up failures with machine activity, maintenance work, power events, or environmental changes.
- **Check spec compliance early**: confirm the device was used inside rated conditions before treating the behavior as a pure defect.
- **Prefer measurable cuts over intuition**: use waveforms, current, voltage, noise level, and calibration records to decide the next cut.

## Boundary with Nondeterminism

Start with `nondeterminism.md` instead when the instability mainly follows time, retries, scheduling, concurrency, or AI output variance without a clear physical correlation.

Use this module when the evidence points to the physical world moving underneath the software, or when the same software behaves differently across units, fixtures, power states, or environments.

## Growth Policy

Append new guidance only after a real session captures:

1. The physical condition that mattered
2. The measurement evidence that isolated the issue
3. The time, place, or neighboring condition that changed the outcome
4. The boundary that actually drifted or failed
5. The repeatable acceptance check
