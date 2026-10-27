"""Source-only replay and exact fictional metric counterexamples."""
import ast
from copy import deepcopy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import re

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]


def lcs_count(a, b):
    previous = [0] * (len(b) + 1)
    for x in a:
        current = [0]
        for j, y in enumerate(b):
            current.append(max(previous[j] + int(x == y), previous[j + 1], current[-1]))
        previous = current
    return previous[-1]


def exhaustive_lcs(a, b):
    # Enumerate every possible equal-character index chain; at most two edges
    # in the selected witnesses, with a hard bound protecting future replay.
    edges = [(i, j) for i, x in enumerate(a) for j, y in enumerate(b) if x == y]
    assert len(edges) <= 16
    best = 0
    for size in range(len(edges) + 1):
        for chain in itertools.combinations(edges, size):
            if all(i < k and j < l for (i, j), (k, l) in zip(chain, chain[1:])):
                best = max(best, size)
    return best


def validate_witnesses(w):
    grids = w["grids"]
    true, pred = [grids["A1"], grids["A2"]], [grids["B1"], grids["B2"]]
    raw, norm = [], []
    for a in true:
        raw_row, norm_row = [], []
        for b in pred:
            assert all(len(x) == 1 for x in a + b), "declared binary LCS reward domain"
            score = lcs_count(a, b)
            assert score == exhaustive_lcs(a, b)
            raw_row.append(score)
            norm_row.append(str(Fraction(2 * score, len(a) + len(b))))
        raw.append(raw_row)
        norm.append(norm_row)
    assert raw == w["pair_true_positive_scores"]
    assert norm == w["pair_normalised_scores"]
    denominator = sum(map(len, true)) + sum(map(len, pred))
    scores = {}
    for assignment in itertools.permutations(range(2)):
        name = "diagonal" if assignment == (0, 1) else "cross"
        numerator = sum(raw[i][j] for i, j in enumerate(assignment))
        scores[name] = {"raw_sum": numerator, "normalised_sum": str(sum(Fraction(norm[i][j]) for i,j in enumerate(assignment))), "downstream_micro": str(Fraction(2 * numerator, denominator))}
    assert scores == w["matching"]
    assert scores["cross"]["raw_sum"] > scores["diagonal"]["raw_sum"]
    assert Fraction(scores["diagonal"]["normalised_sum"]) > Fraction(scores["cross"]["normalised_sum"])
    samples = w["macro_micro"]["samples"]
    macro = sum(Fraction(2 * r["tp"], r["true"] + r["pred"]) for r in samples) / len(samples)
    micro = Fraction(2 * sum(r["tp"] for r in samples), sum(r["true"] + r["pred"] for r in samples))
    assert str(macro) == w["macro_micro"]["macro"] and str(micro) == w["macro_micro"]["micro"]
    assert macro != micro
    dup = w["unmatched_duplicate"]
    assert str(Fraction(2 * dup["tp"], dup["true_cells"] + dup["pred_cells"])) == dup["f1"]
    assert str(Fraction(1, dup["true_tables"])) == dup["exact_table_recall"]
    for values in w["source_count_sums"].values():
        assert sum(values[:-1]) == values[-1]
    merge = w["merging_values"]
    assert Fraction(merge["potatr"]) - Fraction(merge["pubtablesv2"]) == Fraction(merge["difference"])
    return {"grid_pairs": 4, "exhaustive_matching_alternatives": 2, "matching_objectives_diverge": True, "macro_micro_diverge": True, "unmatched_prediction_f1": dup["f1"], "exact_table_recall": dup["exact_table_recall"]}


def check():
    assertions = 0

    def require(value, label):
        nonlocal assertions
        assert value, label
        assertions += 1

    def load(name):
        return json.loads((UNIT / name).read_text())

    def bound(item):
        return hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]

    ledger = load("source-ledger.json")
    require(len(ledger["acquisitions"]) == 6, "six request ceiling")
    for row in ledger["acquisitions"]:
        for key in ("body", "headers", "receipt"):
            require(bound(row[key]), "exact acquisition binding")
        receipt = json.loads((ROOT / row["receipt"]["path"]).read_text())
        require(receipt["exitcode"] == 0 and receipt["time_total"] < 35 and receipt["size_download"] < 12582912, "bounded request")
        require((row["status"], row["redirects"], row["bytes"], row["effective_url"]) == (receipt["http_code"], receipt["num_redirects"], receipt["size_download"], receipt["url_effective"]), "receipt fields")
        require(row["status"] == 200 and row["redirects"] == 0, "response disposition")
        statuses = re.findall(r"^HTTP/\S+ (\d+)", (ROOT / row["headers"]["path"]).read_text(), re.M)
        require(statuses[-1] == "200", "header status")
    for row in ledger["passages"]:
        require(row["needle"] in (ROOT / row["path"]).read_text().splitlines()[row["first_line"] - 1], row["id"])
    reading = ledger["reading"]
    for item in ledger["bindings"] + reading["images"] + [reading["paper"], reading["extracted"], reading["rendered_notes"]]:
        require(bound(item), "source/reading binding")
    require(reading["text_read_pages"] + reading["rendered_read_pages"] == list(range(1, 29)), "exact disjoint reading coverage")
    paper = (UNIT / "sources/02-paper.txt").read_text()
    require(paper.count("\f") == 28, "PDF physical page separators")
    require(all(not page.strip() for page in paper.split("\f")[20:28]), "text extraction omission is real")
    for row in reading["code_reads"]:
        require(bound(row["file"]), "code reading binding")
        require(row["lines"] == [1, len((ROOT / row["file"]["path"]).read_text().splitlines())], "complete selected file line boundary")
    tree = json.loads((UNIT / "sources/04-tree.json").read_text())
    require(tree["sha"] == ledger["metric_commit"] and tree["truncated"] is False, "pinned complete tree")
    for remote, local in (("grits/grits.py", "05-metric.py"), ("grits/conversion.py", "06-conversion.py")):
        data = (UNIT / "sources" / local).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        row = next(row for row in tree["tree"] if row["path"] == remote)
        require(blob == row["sha"] and len(data) == row["size"], "downloaded code matches pinned Git blob")
    metric = (UNIT / "sources/05-metric.py").read_text()
    conversion = (UNIT / "sources/06-conversion.py").read_text()
    mtree, ctree = ast.parse(metric), ast.parse(conversion)
    require(any(isinstance(n, ast.FunctionDef) and n.name == "_hungarian_grits_matching" for n in mtree.body), "static parse without import")
    require("score_matrix[true_idx, pred_idx] = grits_result.true_positive_score" in metric, "raw assignment objective")
    require("linear_sum_assignment(score_matrix, maximize=True)" in metric, "assignment maximisation")
    require("dtype=np.float32" in metric, "assignment score storage precision")
    require("num_pred_cells = sum(len(g) * _get_n_cols(g) for g in pred_grids_con)" in metric, "all predicted cells counted")
    require("total_num_positives = sum(self.num_pred_cells)" in metric, "micro total denominator")
    require("sum(self.num_exact_grid_matches) / total_num_true_grids" in metric, "exact table score is recall-like")
    require('raise ValueError(f"Failed to parse pred_html: {pred_html!r}")' in metric, "parser failure does not silently become scored sample")
    require("metrics = [\"con\", \"top\"]" in metric, "location metric not selected by default")
    require("_MAX_COLSPAN = 1000" in conversion and "_MAX_ROWSPAN = 65534" in conversion, "explicit span caps")
    require(any(isinstance(n, ast.FunctionDef) and n.name == "html_to_cell_list" for n in ctree.body), "conversion parsed only")
    refs = load("backward-snowball-ledger.json")["entries"]
    require([r["reference"] for r in refs] == list(range(1, 37)), "36 references considered")
    w = load("witnesses.json")
    finite = validate_witnesses(w)
    require(True, "finite DP/exhaustive proof checks")
    require("0.6844" in paper and "0.7495" in (ROOT / "data/accounting-master/r04-potatr-20261019/sources/02-paper.txt").read_text(), "exact different merging scores")
    rejected = 0
    for i in range(8):
        bad = deepcopy(w)
        if i == 0:
            bad["grids"]["A1"][1] = "c"
        elif i == 1:
            bad["pair_true_positive_scores"][0][0] = 2
        elif i == 2:
            bad["matching"]["diagonal"]["downstream_micro"] = "2/11"
        elif i == 3:
            bad["macro_micro"]["micro"] = "1/2"
        elif i == 4:
            bad["unmatched_duplicate"]["pred_cells"] = 1
        elif i == 5:
            bad["source_count_sums"]["document_tables"][-1] += 1
        elif i == 6:
            bad["merging_values"]["difference"] = "0"
        else:
            bad["pair_normalised_scores"][0][1] = "1"
        try:
            validate_witnesses(bad)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("altered witness accepted")
    require(rejected == 8, "altered controls rejected")
    for name in ("source-support", "citation-venue", "backward-snowball", "forward-snowball", "claim-support", "omission-risk"):
        require(bool(load(name + "-ledger.json")), "six additive ledgers")
    require(ledger["acquired_code_executed"] is False, "no runtime admission")
    return {"acquisitions": 6, "paper_pages_read": 28, "rendered_pages_read": 8, "passage_anchors": len(ledger["passages"]), "assertions": assertions, "references_triaged": 36, "selected_code_files_read": 2, "finite": finite, "rejected_altered_controls": rejected, "runtime_admitted": False, "manuscript_changed": False}
