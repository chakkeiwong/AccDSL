# Additive completion recording repair

The first completion call passed strict validation, saved the pre-completion
ledgers, bound the document synthesis and refreshed the four live controls.
It then stopped at exclusive creation of run-manifest.json because the initial
review manifest already exists. That file was not overwritten. No completion
binding file was produced, and no candidate or previous evidence changed.

Preserve the attempted helper as completion-attempt-1.py. The corrected helper
uses completion-run-manifest.json and binds the original initial manifest.
An explicit finish action checks the already-completed ledger/control state
and executes only the remaining manifest/binding creation. It does not rerun
initialization, page recording, synthesis binding or control mutation. The
normal complete action now preflights its exclusive destinations. Default
invocation remains read-only verification. This is a recording-path repair,
not a new manuscript defect or a reason to repeat the reading.
