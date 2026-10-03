# Git checkpoint

Date: 3 October 2026 (Asia/Hong_Kong).
Scope: MC34 version-control provenance for the user's explicit request to
commit and push the current project.

The user supplied `https://github.com/chakkeiwong/AccDSL` as the destination.
The local `.git` directory was empty; both ordinary and elevated Git status
checks reported that it was not a repository. The remote `main` branch existed
at `2c8cd43cd52db3aef5381288545c662329faaa1c` and contained only `README.md`.
Git metadata was initialised, that history was fetched, and local `main` was
attached to `origin/main` without replacing the existing project files. The
remote README was restored because it had no local counterpart.

This user-directed operation supersedes earlier descriptions of the unusable
Git marker for the current version-control state. Those historical records and
their provenance remain unchanged. It does not alter the autonomous master's
permissions or establish new accounting, scientific, or human acceptance.

## Pre-commit audit and scope

The comparator is the actual remote `main` tree, not an invented local history.
The checkpoint includes the existing source, tests, design documents, retained
reports and papers, fixtures, review records, and run evidence. The initial
inventory was approximately 1.5 GiB, with no individual file reaching 50 MiB.
The ignore rules exclude Python caches, OS download metadata, transient LaTeX
files, local agent/credential directories, and the process-local runner lock.
They preserve compiled PDFs, recorded logs, and controller state/evidence.

The existing Git setting `core.autocrlf=input` initially normalised CRLF source
files while staging. Because the research records depend on exact byte hashes,
`.gitattributes` disables text conversion for this repository. The files are
restaged under that rule; the original working files are not rewritten.

The initial process scan found no controller, but later file comparisons showed
that a separate run, `20261003T013709-90c553a6`, was actively producing P05
planning and review records. This commit captures the staged files while that
run continues; it is not a quiescent controller checkpoint. Later output may
remain uncommitted. The initial byte comparison matched every staged file
except three changing controller/log files; all stable sources retained their
exact bytes. A targeted scan found no private-key blocks or recognised GitHub,
Anthropic, or AWS access
key patterns in the inspected text files; this is not an exhaustive credential
audit. Git author identity uses the existing user configuration.

The plan preserves remote ancestry and local research material. The checks
establish a repository checkpoint and bounded software regression status; they
do not promote test success into domain validity or mission completion. A
non-fast-forward remote update requires reconciliation before pushing; no
history rewrite or force push is part of this operation.

## Validation

From `/home/chakwong/python/AccDSL`, the existing regression suite was run with
the system `python3`:

```text
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

All 172 tests passed in 42.313 seconds. These are regression checks of the
current implementation, not a new research experiment. No numerical defaults,
source files, protected release hashes, or recorded acceptance decisions were
changed to obtain that result.
