# Verification recovery

The first read-only preflight on 23 October failed in the new verifier's
assertion that the predecessor `unselected` dictionary had six entries.
Direct inspection showed six null scientific choices plus a seventh entry,
`empirical_execution: false`. The successor had correctly preserved that
dictionary. The verifier now checks the six named choices and the execution
hold separately, including exact equality to the predecessor. No calculation,
user choice, input, historical record or expected result changed. No completion
or control refresh had run when the assertion failed.

The command was the same default CPU-only `verify.py` command recorded in
the run manifest. Preparation, calculation and choice recording were not rerun.
