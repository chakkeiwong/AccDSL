# AccDSL 5.54-R3 — internal review candidate

The governing proposal has 836 pages. The simulation volume has 265 total pages
and 244 body pages. The release remains **not_ready**. This protected successor
clarifies midpoint-grid convergence, proves its exact threshold-error bound and
adds a reproducible teaching-arithmetic companion. All four earlier executable
components are retained byte for byte. Whole-document, source, specification and
independent acceptance work remains open.

Run integrity verification from this directory with
python3 -I -B verify_package.py.
package-manifest.json pins every included file; its hash is retained outside
the package. This checks integrity against that record, not independent
authenticity. Generated TeX intermediates, caches and run outputs are excluded.
PACKAGE-REVISION.json is the unchanged historical record of predecessor
5.54-R2 package revision2, not this successor's build record. Current source,
build and relocation records are in
data/accounting-master/release-pursuit-20261027/midpoint-reference/.

| Component | Reproduced scope | Instructions |
| --- | --- | --- |
| historical-core0 | Historical language and reference fixtures | companions/historical-core0 |
| selected-term | Bounded modern term execution | companions/selected-term |
| refinancing-domain | Dated cash examples and two counterexamples | companions/refinancing-domain/README.md |
| source-history-replay | 37 retained source/history/opening/report exchanges | companions/source-history-replay/README.md |
| reference-computations | 169 retained arithmetic checks and exact midpoint cases | companions/reference-computations/README.md |

Each component has its own environment, fresh-output rule and exact comparison
scope. Follow its README; never execute archived preparation writers. The
source/history archive must be validated and extracted before replay.

Build both documents in a writable copy with the recorded TeX Live 2026 tools.
Create .tex-cache in that copy and set TEXMFVAR and TEXMFCACHE to its absolute
path. Run latexmk -g -lualatex -interaction=nonstopmode -halt-on-error
-no-shell-escape accounting-product-proposal.tex; then use the same options
for simulation-foundations.tex. Exact executed command arrays are retained
in the current build records.

LuaLaTeX, BibTeX, latexmk and the imported TeX packages must already be
available. No installation is implicit. PDF bytes can differ with build
metadata; full normalized page-text comparison is recorded separately.

Historical contracts under spec/ and fixtures/ retain their original identities.
Later profile definitions govern their stated extensions. Repository evidence
paths in the text are not all included: the package contains only its declared
subset. Original issuer filings, papers and accounting standards remain separately
held. DEPENDENCIES.md states remaining access and reproduction limits.
This is an internal review package, with no publication or redistribution grant.
