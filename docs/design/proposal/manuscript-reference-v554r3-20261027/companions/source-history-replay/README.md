# Source, history, opening and report replay

This internal component reproduces 37 retained exchanges: 12 complete
opening/continuation/carry exchanges, 14 adverse cases, one selected-source/
history composition and its ten adverse cases. It starts from the retained
source decisions and requests. It preserves 236 observations, 101 equations
and 180 unresolved issuer obligations across two separate contexts. It does
not acquire filings, reconstruct the source decisions, identify the actual
issuer history or establish an executable issuer opening.

From this directory, using the recorded Python environment:

```sh
python3 -I -B unpack_replay.py --destination /tmp/accdsl-source-history-replay
python3 -I -B /tmp/accdsl-source-history-replay/data/accounting-master/executable-evidence-closure-20261027/replay.py --root /tmp/accdsl-source-history-replay --output /tmp/accdsl-source-history-replay/output-01
```

Both destinations must be new. The extractor validates all 235 regular archive
members before writing: 234 declared dependencies and their manifest. The native
driver requires extraction outside the original AccDSL worktree. Its only
writes are under the new output directory. Do not run the archived preparation,
verification or result-writing scripts included as identity dependencies.

The retained environment is Python 3.11.15, Z3 solver 4.16.0.0, jsonschema
4.26.0, attrs 26.1.0, referencing 0.37.0, rpds-py 0.30.0 and
jsonschema-specifications 2025.9.1. environment-lock.json records observed
environment identities; no dependencies are installed automatically. The
driver intentionally hides GPUs before project imports. The computation is
exact conformance evidence, not a stochastic performance comparison.

Financial quantities, statuses, premises, budgets and obligations compare
exactly. Seven diagnostic timing fields, one independently checked nonunique
existential witness and two conjunct-label orders follow the precise rules in
execution-review.md. Raw results are always retained; new differences fail.
The source witness and financial expectations receive independent rational
checks. The original accepted result is retained in upstream-result.md.

The driver audits Python-visible reads before project imports and refuses
undeclared reads, writes, network and subprocess calls. Interpreter startup
and arbitrary native-library system calls are outside that audit. This is
neither a clean-install promise nor an operating-system isolation guarantee.

The archive contains repository code, retained structured inputs, expectations
and review records. Original issuer filings, papers and accounting standards
are not included. Their acquisition and recipient rights remain separate
requirements. Inclusion here grants no redistribution permission and does not
close the wider manuscript's runtime or independent acceptance duties.
