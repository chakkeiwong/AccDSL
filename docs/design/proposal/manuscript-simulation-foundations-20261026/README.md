# AccDSL Version 5.0 source package

`accounting-product-proposal.pdf` is the 714-page governing design candidate.
`simulation-foundations.pdf` is the 170-page reading edition of the 26 new
chapters (154 body pages). Both roots include the same `simulation/*.tex` files.

From this directory, build either root with LuaLaTeX via latexmk:

```sh
TEXMFVAR=/tmp/accdsl-texmf-cache TEXMFCACHE=/tmp/accdsl-texmf-cache latexmk -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex
TEXMFVAR=/tmp/accdsl-texmf-cache TEXMFCACHE=/tmp/accdsl-texmf-cache latexmk -lualatex -interaction=nonstopmode -halt-on-error simulation-foundations.tex
```

Version 4.50 chapter/section/grammar sources are preserved byte for byte; only
the root integration, new chapters and bibliography additions change the
argument. Verification and review are under
`data/accounting-master/simulation-monograph-20261026/` from the repository root.
Stable reader links are `docs/AccDSL-latest.pdf` and
`docs/AccDSL-simulation-foundations.pdf`. The candidate remains not_ready for
full product, domain and human acceptance.
