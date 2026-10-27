# AccDSL 5.53-R1 source-reading candidate

This is a protected successor to 5.53. It adds the independently selected
reported-zero reading and its complete conditional source-network consequences. It preserves the explained complementary
share conventions and ordered-term program, repairs three stale scope statements,
and includes exact historical normative references and two runnable components.
It remains not_ready. Full release acceptance and redistribution rights remain open.

Run from this directory with the recorded TeX Live/LuaLaTeX environment.
Create a writable local font cache first. LuaLaTeX needs its absolute path:

    mkdir -p .tex-cache

    env TEXMFVAR="$(pwd)/.tex-cache" TEXMFCACHE="$(pwd)/.tex-cache" latexmk -g -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex
    env TEXMFVAR="$(pwd)/.tex-cache" TEXMFCACHE="$(pwd)/.tex-cache" latexmk -g -lualatex -interaction=nonstopmode -halt-on-error simulation-foundations.tex

Both roots include the same simulation files. LuaLaTeX, BibTeX, latexmk and the
packages named in each root are required. The accompanying environment record
states the versions used; there is no implicit installation step. Output is
written beside these copied sources, never into the protected predecessor directory.
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

Package verification (no third-party Python dependency):

    python3 -I -B verify_package.py

package-manifest.json lists the included sources, normative companions, fixtures,
component files and two built PDFs. It excludes generated caches and TeX
intermediates. Its identity is fixed in the external execution record; a hash
manifest proves integrity relative to that record, not authenticity by itself.
The predecessor has retained source-relocation evidence; this successor
requires its own relocation comparison in the external execution record. TeX/font
installation files are recorded separately, not included or installed here.
DEPENDENCIES.md distinguishes the reproducible subset from remaining evidence
and distribution work. This package is for internal review; no licence grant
or public redistribution clearance is inferred.

The inherited source-reading addition is verified under data/accounting-master/debt-reading-integration-20261027/.
The retained two executable companions are unchanged. Their checks do not
reproduce the new source-reading/network evidence, whose exact repository paths
and limitations are stated in the manuscript. The full evidence closure remains open.

This protected successor incorporates the checked initial-pairing/common-loss
coupling repair, explicit joint scenario admissibility, opening cash and date
clarifications, the sign-dependent EPS comparison, a reading guide and an inspected arXiv edition pin. Its own
package and relocation results are recorded under release-pursuit-20261027/
opening-repair; predecessor verification is not silently inherited. It remains
not_ready and is for internal review only.
