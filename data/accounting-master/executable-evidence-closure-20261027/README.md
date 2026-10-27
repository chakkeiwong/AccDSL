# Internal bounded replay component

This component starts from retained complete requests and source decisions.
It does not acquire issuer filings or reproduce the extraction/interpretation
that produced those inputs. Source rights, original acquisition, unexecuted
runtime paths and a clean installation remain outside this component.

The frozen successful bundle is replay-bundle.tar.gz. Verify its digest using
preservation.json, extract into a new directory outside the original worktree,
and run with the recorded Python 3.11.15 environment:

```sh
python3 -I -B /absolute/new-bundle/data/accounting-master/executable-evidence-closure-20261027/replay.py --root /absolute/new-bundle --output /absolute/new-bundle/new-output
```

The output directory must not exist. The driver hides GPU devices before
project imports. It uses Z3 solver 4.16.0.0, jsonschema 4.26.0, attrs 26.1.0,
referencing 0.37.0, rpds-py 0.30.0 and jsonschema-specifications 2025.9.1 from
the recorded installed environment. No package installation or source download
occurs. environment-lock.json records observed environment identities.

The original 234 included inputs are checked before and after execution.
Native implementations are unchanged. A Python audit rejects undeclared reads,
writes outside the fresh output directory and network/subprocess activity.
The hook does not inspect interpreter startup or arbitrary native OS syscalls.
The recorder's final write of its own audit file is necessarily after the
snapshot of accesses that the file contains.

Successful reproduction uses the narrow semantic comparisons described in
execution-review.md. Financial results and statuses compare exactly; timings,
the one independently checked existential certificate and the two conflict-set
orders receive explicit treatment. Complete raw outputs always remain saved.
Unanticipated differences fail and require investigation. No earlier one-shot
writer is run or imported.

For a future protected document package, add this archive as a separately
identified internal component and link its manifest, environment and exclusions.
Do not mutate the existing 5.54-R1 package or imply redistribution permission.
