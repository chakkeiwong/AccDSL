# Dated PAA example through the company book

The internal archive reproduces seven complete conditional cases and 21 controls
through the unchanged company-book/report engines. See contract.md for the exact
profile and result.md for its interpretation. Authored expectations were frozen
before the native calls. Both source and accounting admission remain false.

Check `paa-dated-book-bundle.tar.gz` against preservation.json and extract into a
new directory. With the recorded Python3.11.15/jsonschema environment, run:

```sh
python3 -I -B /absolute/copy/data/accounting-master/insurance-paa-dated-book-20261027/verify.py --output /absolute/copy/new-output
```

The output directory must not already exist. The driver intentionally hides GPUs,
uses a120-second CPU limit and preserves complete records. It verifies all declared
input hashes before and after execution. No installation, network service,
original archival writer or production-book commit is used. This run does not
claim OS/file-access isolation or clean installation. Keep retained accounting
sources for internal use; their inclusion grants no redistribution rights.

The first smoke's verifier misread the native journal shape; its failure and
correction remain in smoke-01 and smoke-review.md. Smoke-02 and attempt-01 pass.
Complete-record-checks.json additionally verifies all cash origin identities and
the exact stopped prefixes/current states/unexecuted suffixes. Do not rerun
preserve.py or overwrite successful output directories.
