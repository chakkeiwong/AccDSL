# AccDSL internal source-to-report evidence companion

This companion reproduces two bounded pieces of evidence: the retained source
parent and selected debt reading, followed by 37 declared source/history,
synthetic opening, continuation, reporting and carry exchanges. It is an
internal research companion, separate from the current manuscript package.

Verify the archive against preservation.json, extract into a new directory,
and run with the recorded Python 3.11.15 environment:

```sh
python3 -I -B /absolute/new-bundle/reproduce.py --output /absolute/new-bundle/new-output
```

The output directory must not already exist. The launcher checks all file
identities, runs each unchanged driver with isolated Python, captures logs and
saves complete results beneath new-output. No dependency installation, network
access or original archival writer is used. Keep the whole directory structure.
Expected installed distributions: z3-solver 4.16.0.0, jsonschema 4.26.0,
attrs 26.1.0, referencing 0.37.0, rpds-py 0.30.0 and
jsonschema-specifications 2025.9.1. The component environment locks record
observed installed files; this is not a clean-install recipe.

The source reconstruction compares the complete parent and selected reading
exactly, including the original unresolved PDF dash. It checks 30 raw XBRL
facts and their contexts/units against the retained ZIP. The downstream
component preserves 236 observations, 101 equations and 180 issuer obligations.
Synthetic openings do not identify an issuer opening. See the component
result and execution-review records for exact scope and expectations.

The downstream comparison excludes seven recorded solver timings and handles
one independently checked nonunique existential certificate plus two reorderings
of identical conflict labels. Every financial result, status, premise, budget,
source identity and obligation remains checked. Both raw results and the exact
comparison details are saved. Unexpected differences fail.

Each child installs its file-access audit before project imports and requires
successful reads to belong to its own component manifest or the declared
installed environment. The audit covers Python-visible calls, not interpreter
startup or arbitrary native syscalls. Source documents and authored readings
remain explicit inputs; original acquisition/whole-filing interpretation,
other runtime families and independent acceptance are not reproduced here.

The bundle contains retained issuer documents for internal use. Reproduction
does not grant source redistribution rights or establish historical availability,
source truth, accounting admission, forecasting accuracy or release readiness.
No publication or external transmission accompanies this component.
