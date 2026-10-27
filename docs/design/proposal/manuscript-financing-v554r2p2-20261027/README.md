# AccDSL 5.54-R2 — internal package revision 2

The governing manuscript remains 5.54-R2: 835 main pages and 264 total /
243 body pages in the simulation volume. Package revision 2 includes the checked
source/history/opening/report replay component. Every manuscript source and PDF
is byte-identical to the preceding 5.54-R2 package. PACKAGE-REVISION.json binds
the predecessor, unchanged documents and added component. The release remains
not_ready; source, specification, whole-document and independent acceptance
work continues under the master program.

Run the integrity verifier from this directory:

```sh
python3 -I -B verify_package.py
```

package-manifest.json lists included files and hashes. Its identity is recorded
outside the package; matching it establishes integrity against that record,
not independent authenticity. Generated caches, TeX intermediates and later
run outputs are excluded.

The four executable components have different scopes:

| Component | What it reproduces | Instructions |
| --- | --- | --- |
| Historical Core 0 | The retained historical language and reference fixtures | companions/historical-core0 |
| Selected term program | The bounded modern term-execution component | companions/selected-term |
| Refinancing domain | Conditional dated-cash examples and two counterexamples | companions/refinancing-domain/README.md |
| Source/history/opening/report | 37 complete retained exchanges and their independent checks | companions/source-history-replay/README.md |

Use a new output directory for every run. From this package directory the
first three commands are:

```sh
env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B companions/historical-core0/scripts/verify_relocated.py "$(pwd)/companions/historical-core0/output-01"
env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B companions/selected-term/scripts/verify_relocated.py output-01
python3 -I -B companions/refinancing-domain/verify_refinancing.py --output-dir /tmp/accdsl-refinancing-new-output
```

The historical component requires an output path within its copied bundle;
follow its README when preparing a fresh copy. The selected-term command
resolves its output inside that component. The source/history component has
an explicit extraction step because its native code uses a retained repository
layout. Its README gives both commands, required environment and exact scope.
Do not run archived one-shot preparation or evidence-writing main functions.

Build the documents from this directory in the recorded TeX Live 2026 environment:

```sh
mkdir -p .tex-cache
env TEXMFVAR="$(pwd)/.tex-cache" TEXMFCACHE="$(pwd)/.tex-cache" latexmk -g -lualatex -interaction=nonstopmode -halt-on-error -no-shell-escape accounting-product-proposal.tex
env TEXMFVAR="$(pwd)/.tex-cache" TEXMFCACHE="$(pwd)/.tex-cache" latexmk -g -lualatex -interaction=nonstopmode -halt-on-error -no-shell-escape simulation-foundations.tex
```

LuaLaTeX, BibTeX, latexmk and the packages named by the roots must already be
available. No installation is implicit. Both roots use the same simulation
sources. Build in a writable copied package with its own absolute cache path.
The exact 5.54-R2 manuscripts already reproduce all normalized page text in a
separate directory; PDF byte identity also depends on timestamps/toolchain
metadata. The historical build-environment.json is an earlier environment
observation; the current document build records are linked by PACKAGE-REVISION.json.

The spec directory retains historical Core 0 contracts and selected design
profiles. reference-map.json identifies their original files; those historical
records do not override later profile definitions. The fixtures directory
contains their exact referenced records. Evidence paths beginning data/, docs/
or scripts/ in the manuscript generally refer to the AccDSL repository root.
The new archive supplies its explicitly listed subset of those paths after
extraction; other manuscript evidence remains outside this package.

DEPENDENCIES.md states environment and source limits. Original issuer filings,
papers and accounting standards remain separately held. This is an internal
review package; no licence grant, publication, redistribution clearance or
complete executable-evidence claim is inferred from inclusion.
