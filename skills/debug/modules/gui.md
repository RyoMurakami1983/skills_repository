# GUI Debug Module

Use this module when the failure involves rendering, layout, focus, selection, input handling, or editor behavior.

This module starts slightly ahead of the others because the first source material came from GUI debugging, but it should still grow only from real sessions.

## Current Focus

- **Evidence**: screenshots, DOM or HTML snapshots, input scripts, bounding boxes, visual diffs
- **Fault boundaries**: input handling, selection or caret state, document mutation, layout recomputation, persistence, CSS layer
- **Repro levers**: same key sequence, same mode, same browser, same viewport, same local state
- **Quality gate**: the same visible scenario behaves the same way before and after in every affected mode

## Growth Policy

Append new rules only after a real session proves they matter.

When you add a lesson, record:

1. The trigger shape that made the bug reproducible
2. The evidence that made the difference undeniable
3. The boundary that actually owned the bug
4. The verification step that prevented recurrence
