# Internal retained-source reconstruction component

Verify reconstruction-bundle.tar.gz against preservation.json, extract into
a new directory, then run with the recorded Python 3.11.15 environment:

```sh
python3 -I -B /absolute/new-bundle/data/accounting-master/retained-source-reconstruction-20261027/replay.py --root /absolute/new-bundle --output /absolute/new-bundle/new-output
```

The output directory must not exist. The code hides GPUs before project imports,
uses the same recorded Z3/jsonschema environment as the preceding 37-exchange
component, and runs no network call or archival writer. The read audit begins
before project imports and writes only to the new output directory. It covers
Python-visible calls, not interpreter startup or arbitrary native syscalls.

Inputs include the retained packet, authored statement readings/relationships,
reviewed source binding, original issuer PDF and XBRL ZIP. Reproducing them does
not grant redistribution rights, reproduce their original construction, prove
source truth or establish historical availability. This archive is for internal
use. Complete declared reconstruction results compare exactly, with no timing
or witness normalization. All original input hashes are checked before and
afterward. Do not rerun the original historical verification scripts.
