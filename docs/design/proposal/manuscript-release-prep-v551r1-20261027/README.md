# AccDSL 5.51-R1 release-preparation candidate

This is a protected successor to 5.51. It repairs the repeated floating-share
notation, links the earlier temporal profile to its resumable successor, and
includes exact historical normative references. It remains not_ready. It is not
a completed software release or a grant of public redistribution rights.

Run from this directory with the recorded TeX Live/LuaLaTeX environment.
Create a writable local font cache first. LuaLaTeX needs its absolute path:

    mkdir -p .tex-cache

    env TEXMFVAR="$(pwd)/.tex-cache" TEXMFCACHE="$(pwd)/.tex-cache" latexmk -g -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex
    env TEXMFVAR="$(pwd)/.tex-cache" TEXMFCACHE="$(pwd)/.tex-cache" latexmk -g -lualatex -interaction=nonstopmode -halt-on-error simulation-foundations.tex

Both roots include the same simulation files. LuaLaTeX, BibTeX, latexmk and the
packages named in each root are required. The accompanying environment record
states the versions used; there is no implicit installation step. Output is
written beside these copied sources, never into the protected 5.51 directory.
A relocated copy can use the same commands. PDF byte identity additionally
requires control of timestamps and toolchain metadata; financial/text fidelity
must be checked separately.

The spec directory retains historical Core 0 contracts and supplementary design
profiles. reference-map.json identifies their original files and exact hashes.
These do not override later portable profile definitions. References starting
with data/, docs/ or scripts/ are relative to the AccDSL repository root;
contextual attempt paths are relative to the evidence directory named nearby.
The complete evidence dependency closure is still under review.

Two executable components are included under companions/historical-core0 and
companions/selected-term. From this candidate directory, in the recorded Python
environment, run:

    env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B companions/historical-core0/scripts/verify_relocated.py "$(pwd)/companions/historical-core0/output-01"
    env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B companions/selected-term/scripts/verify_relocated.py output-01

Use a new output name each time. The historical command resolves output relative
to the working directory, while the selected-term command resolves it within its
bundle; the explicit historical absolute path prevents ambiguity. Each component
retains its observed environment, exact reference manifest and limitations. Do
not run archival writer main functions. Neither component covers all modern
company/sector interfaces. The top-level fixtures directory preserves the exact
historical records referenced by spec/core-contract.md; runnable source code and
its original repository layout live in the historical component.

No retained paper, standard, private credential or external service is included
here. Source access/redistribution dispositions remain a separate release duty.

Detailed changes and verification are recorded in
 data/accounting-master/release-plan-execution-20261027/.
