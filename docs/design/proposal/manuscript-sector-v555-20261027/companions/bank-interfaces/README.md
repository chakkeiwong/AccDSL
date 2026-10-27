# Retained bank interface reproduction

This internal companion rechecks complete retained bank exchanges. The AU
accounting profiles remain distinct from the historical conditional US capital
profile. BankAssessmentExactTime/1 changes information-time handling and request
identity; it has no accounting effect. No model builder or one-shot writer runs.

Run the copied replay.py with --root pointing to the copied root and --output
pointing to a new directory. Python 3.11 and jsonschema 4.26.0 are the observed
environment; dependency installation and other environments are not tested.
GPU devices are intentionally hidden. This is documentary conformance, not a
deployed bank service, calibrated loss model, current-law or actual-bank admission.

The replay preserves every frozen record and independently derives the retained
financial effects. Full response and world checks include original/revised
requests, refusals, retries, lost acknowledgements and atomic-publication cases.
Exact-time expected outputs come from frozen predecessor outputs with declared
reference substitution and canonical dependency-set ordering; numeric values
are unchanged. The financial implementation is shared between time profiles.

The original auditors also checked a historical Git HEAD/index and thousands
of unrelated predecessor files. Those historical workspace checks cannot be
repeated as recipient checks in a separate directory without that Git state.
They remain preserved results, explicitly excluded from this replay. All
declared copied inputs are checked by SHA256 before and after replay instead;
this does not reproduce or replace the old Git-preservation claim.

Retained source materials require their own access/redistribution decisions.
The archive is for internal preparation only and is separate from the selected
manuscript package. Full MC21 and independent acceptance remain open.
