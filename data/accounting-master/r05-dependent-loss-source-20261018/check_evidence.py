"""Read-only source integrity and exact illustrative algebra; no inference run."""
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from verify import preservation, sha

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]


def check():
    preservation()
    checks = []

    def require(label, condition):
        assert condition, label
        checks.append(label)

    manifest = json.loads((UNIT / "source-manifest.json").read_text())
    require("source-inventory-complete", set(manifest["entries"]) == {
        str(p.relative_to(ROOT)) for p in (UNIT / "sources").rglob("*") if p.is_file()})
    for path, info in manifest["entries"].items():
        p = ROOT / path
        require("source-sha:" + path, sha(p) == info["sha256"])
        require("source-size:" + path, p.stat().st_size == info["bytes"])
    sources = UNIT / "sources"
    paper = (sources / "forecomp-arxiv-v1.txt").read_text()
    require("primary-pdf-magic", (sources / "forecomp-arxiv-v1.body").read_bytes().startswith(b"%PDF"))
    require("primary-title", "ForeComp: An R Package for Comparing Predictive" in paper[:3000])
    require("primary-authors", "Minchul Shin" in paper[:3000] and "Nathan Schor" in paper[:3000])
    require("primary-pages", len([s for s in paper.split("\f") if s.strip()]) == 45)
    wrong = (sources / "dm2015-arxiv-route2.txt").read_text()[:5000].lower()
    require("wrong-source-excluded", "coarse-grid" in wrong and "incompressible" in wrong and "forecomp" not in wrong)
    code = sources / "forecomp-cran-source/cran-ForeComp-6354aea"
    desc = (code / "DESCRIPTION").read_text()
    require("package-version", "Version: 1.0.0" in desc and "https://github.com/mcmcs/ForeComp" in desc)
    plot = (code / "R/Plot_Tradeoff.R").read_text()
    require("package-default-zero", 'na_handling = c("zero", "drop", "error")' in plot and "match.arg(na_handling)" in plot)
    require("package-nonfinite-anchor", "bad = !is.finite(d)" in plot and "d[bad] = 0" in plot)
    require("package-fitted-simulation", "auto.arima" in plot and "arima.sim" in plot and "n_sim = 1000" in plot)
    acquired = json.loads((UNIT / "acquisition-manifest.json").read_text())["acquisitions"]
    require("acquisition-count", len(acquired) == 21)
    for row in acquired:
        require("terminal-http:" + row["id"], row["http_chain"][-1] == row["transfer"]["http"])
        require("transfer-bytes:" + row["id"], (ROOT / row["body"]).stat().st_size == row["transfer"]["bytes"])
    for name in ("dm1995", "hln1997", "dm2015"):
        c = json.loads((sources / (name + "-crossref.body")).read_text())["message"]
        o = json.loads((sources / (name + "-openalex.body")).read_text())
        require("metadata-doi:" + name, c["DOI"].lower() in o["doi"].lower())
        require("bounded-retraction-field:" + name, o["is_retracted"] is False)

    def covariance_variance(n, t, weights):
        cells = list(itertools.product(range(n), range(t)))
        return sum(weights[i, s] * weights[j, u] *
                   (int(i == j) + int(s == u) + int((i, s) == (j, u)))
                   for i, s in cells for j, u in cells)

    n, t = 9, 8
    w = {(i, s): F(1, n * t) for i in range(n) for s in range(t)}
    var = covariance_variance(n, t, w)
    require("nine-eight-exact-variance", var == F(1, 4))
    require("nine-eight-iid-variance", F(3, n * t) == F(1, 24))
    require("nine-eight-understatement-factor", var / F(3, n * t) == 6)
    require("common-shock-variance", var + 1 == F(5, 4))
    w2 = {(i, s): F(1 + 3 * i + s, 21) for i in range(2) for s in range(3)}
    coefficients = sum(sum(w2[i, s] for s in range(3))**2 for i in range(2))
    coefficients += sum(sum(w2[i, s] for i in range(2))**2 for s in range(3))
    coefficients += sum(v**2 for v in w2.values())
    require("arbitrary-weights-normalized", sum(w2.values()) == 1)
    require("arbitrary-weights-covariance-identity", coefficients == covariance_variance(2, 3, w2))
    enumerated = []
    for v in itertools.product((-1, 1), repeat=8):
        values = [v[i] + v[2 + s] + v[4 + 2 * i + s] for i in range(2) for s in range(2)]
        enumerated.append(F(sum(values), 4))
    require("enumerated-mean-zero", sum(enumerated) == 0)
    require("enumerated-variance", sum(x*x for x in enumerated)/256 == covariance_variance(2, 2, {(i,s): F(1,4) for i in range(2) for s in range(2)}))
    require("missing-zero-changes-mean", F(2, 1) != F(2 + 0, 2))
    return {"status": "passed", "checks": len(checks), "labels": checks,
            "source_files": len(manifest["entries"]), "acquisitions": len(acquired),
            "illustrative_assignments_enumerated": len(enumerated),
            "stochastic_experiments": 0, "empirical_admissions": 0,
            "whole_rows_closed": 0}


if __name__ == "__main__":
    result = check()
    print(json.dumps({k:v for k,v in result.items() if k != "labels"}))
