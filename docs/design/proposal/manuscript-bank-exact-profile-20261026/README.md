# AccDSL Version 5.1 source package

The governing PDF has 715 pages. The 170-page standalone simulation volume
shares the 26 simulation chapters (154 body pages) with Part I of that PDF.
Both are available through the stable links in docs/README.md.

From this source directory:

```sh
TEXMFVAR=/tmp/accdsl-bank-profile-tex-cache TEXMFCACHE=/tmp/accdsl-bank-profile-tex-cache latexmk -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex
TEXMFVAR=/tmp/accdsl-bank-profile-tex-cache TEXMFCACHE=/tmp/accdsl-bank-profile-tex-cache latexmk -lualatex -interaction=nonstopmode -halt-on-error simulation-foundations.tex
```

The simulation sources, standalone root and bibliography are unchanged from
Version 5.0. The integrated manuscript adds exact bank-profile timing; its
source, build and review evidence is under
data/accounting-master/bank-time-manuscript-integration-20261026/ at the
repository root. Simulation source and arithmetic evidence is under
data/accounting-master/simulation-monograph-20261026/.

The design remains not_ready. Independent reading, domain acceptance and full
implementation validation remain pending.
