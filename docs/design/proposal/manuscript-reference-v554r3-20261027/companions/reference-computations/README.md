# Deterministic reference computations

From this component, run with an existing Python3.11+ interpreter:

```sh
python3 -I -B verify_reference.py --output-dir /tmp/accdsl-reference-new-output
```

Choose a new output directory. The verifier copies the exact historical
teaching checker into that output, executes the copy and compares its complete
result with teaching-expected.json. Never execute teaching-original.py in this
component: it is preserved with its original write-beside-source behavior.
The wrapper adds exact rational midpoint-grid cases and the n=4/5 and10/11
nonmonotonic-error examples. Its outputs include every threshold case, original
result, stdout/stderr and a run manifest. It refuses existing output directories.

The universal threshold error bound comes from the manuscript floor proof.
Finite rational checks alone do not prove it. The original169 checks cover
selected deterministic teaching examples throughout the simulation volume;
they are not a complete solver, company forecast or stochastic comparison.
The standard library is sufficient. No installation, network service or GPU
is used. provenance.json records original source/result identities.
