# API and Backend Debug Module

Use this module when the failure crosses HTTP, authentication, service boundaries, transactions, persistence, or cache behavior.

This module is intentionally thin. Grow it only after real backend debug sessions teach patterns worth repeating.

## Current Focus

- **Evidence**: request and response pairs, headers, payloads, service logs, DB diffs
- **Fault boundaries**: validation, authz, service boundaries, transactions, cache, background jobs
- **Repro levers**: fixed payloads, stable fixtures, explicit clocks, retry policy, request order
- **Quality gate**: the same request path is explainable before and after the fix

## Growth Policy

Append new guidance only after a real session captures:

1. The failing request or sequence
2. The proof that isolated the owner
3. The smallest safe fix
4. The repeatable verification rule
