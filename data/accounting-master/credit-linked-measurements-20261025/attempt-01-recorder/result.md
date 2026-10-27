# Recorder failure, 25 October 2026

All23 focused checks,44 regression checks, nine full schedules and retained
native refusals completed. Source-lock assembly then attempted to reopen the
deleted small.txt fixture created by test_sector_reference_binding_v1.py.
The fixture contains bytes abc and is intentionally temporary. The failed
verifier, complete computed outputs, refusal outputs and log are preserved here.
No evidence.json or source-lock.json was frozen.

Repair: capture temporary fixture bytes and their hash while they exist; bind
the resulting deterministic fixture record alongside persistent sources. A
missing nonfixture still fails. Existing computed cases must compare equal
before the new record accepts them. No algebra, tolerance or test is changed.
This failure invalidated the recorder, not the exact-expression candidate.
