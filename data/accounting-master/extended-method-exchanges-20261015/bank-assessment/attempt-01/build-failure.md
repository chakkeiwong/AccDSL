# Retained first build failure

15 October 2026. Command: `python3 data/accounting-master/extended-method-exchanges-20261015/bank-assessment/build_exchanges.py`.
The builder stopped before producing a packet: recursive adverse-record copying
computed an alias before adding its child and reused that alias at the parent.
Observed: `AssertionError: bad.closing-assets-average.746`. This is an authoring
failure, with no scientific conclusion or predecessor change. The repair adds
the child before choosing the parent's unique alias. A fresh numbered attempt
will retain the corrected input snapshot. No validator result exists for /01.
