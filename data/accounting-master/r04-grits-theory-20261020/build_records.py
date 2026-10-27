"""Construct the bounded original GriTS source audit once."""
import hashlib
import json
from pathlib import Path
import re
import shlex
from compare import calculate

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
PRIOR = UNIT.parent / "r04-pubtablesv2-20261019"
COMMIT = "16d124f616109746b7785f03085100f1f6247575"


def bind(p):
    return {"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


def write(name, value):
    with (UNIT / name).open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    assert not (UNIT / "source-ledger.json").exists(), "one-time construction"
    acquisitions = []
    for stem in ("01-arxiv", "02-paper", "03-repository", "04-tree", "05-metric", "06-eval"):
        receipt = UNIT / "sources" / (stem + ".receipt.json")
        r = json.loads(receipt.read_text())
        header = UNIT / "sources" / (stem + ".headers")
        body = ROOT / r["filename_effective"]
        command = ["curl", "--silent", "--show-error", "--location", "--connect-timeout", "10",
                   "--max-time", "35", "--max-filesize", "16777216", "--proto", "=https",
                   "--proto-redir", "=https", "--dump-header", str(header.relative_to(ROOT)),
                   "--output", str(body.relative_to(ROOT)), "--write-out", "%{json}\\n", r["url"]]
        acquisitions.append({"url": r["url"], "effective_url": r["url_effective"], "status": r["http_code"],
            "redirects": r["num_redirects"], "bytes": r["size_download"], "curl_seconds": r["time_total"],
            "command": shlex.join(command), "body": bind(body), "headers": bind(header), "receipt": bind(receipt)})
    paper = UNIT / "sources/02-paper.txt"
    metric = UNIT / "sources/05-metric.py"
    caller = UNIT / "sources/06-eval.py"
    newer = PRIOR / "sources/05-metric.py"
    needles = {
        paper: [
            ("version", "arXiv:2203.12555v3 [cs.LG] 23 May 2023"),
            ("topology-scope", "necessary but not sufficient for successful TSR"),
            ("repeat-spans", "its text content logically repeats at every grid cell location"),
            ("relax-exact-cells", "extension to 2D-LCS is to relax the exact match constraint"),
            ("reward-bounds", "0 ≤ f (e1 , e2 ) ≤ 1"),
            ("content-lcs", "common subsequence (LCS) to compute similarity between text sequences"),
            ("separate-axes", "rows and the optimal subsequences of columns independently"),
            ("nested-dp", "The inner DP is executed over all pairs of predicted"),
            ("rowcol-comparator", "RowColAlign attempts to"),
            ("lower-bound", "by this procedure is a lower bound on their true similarity"),
            ("reported-definition", "We define GriTS as the value of the lower bound"),
            ("training-scope", "million tables, for 20 epochs"),
            ("subset-no-spans", "we use the 44,381 tables that do not have any spanning cells"),
            ("teds-comparator", "all header information"),
        ],
        metric: [
            ("original-import", "from difflib import SequenceMatcher"),
            ("tie-preference", "if diag_score == max_score:"),
            ("original-upper", "min(row_pos_match_score, col_pos_match_score)"),
            ("original-cartesian", "for true_column_num, pred_column_num in zip(true_column_nums, pred_column_nums):"),
            ("original-return", "return fscore, precision, recall, upper_bound_score"),
            ("matcher-default", "s = SequenceMatcher(None, string1, string2)"),
            ("matching-blocks", "for block in s.get_matching_blocks()"),
            ("original-box-union", "union = Rect(bbox1).include_rect(bbox2)"),
            ("zero-fill", "cell_grid = np.zeros((num_rows, num_columns)).tolist()"),
            ("parse-error", "tree = ET.fromstring(table_html)"),
        ],
        caller: [
            ("caller-upper", "metrics['grits_con_upper_bound']"),
            ("macro-summary", "metrics_summary['all'][metric_name] = np.mean"),
            ("shared-word-input", "true_page_tokens, structure_class_names"),
            ("caller-accuracy", "metrics['acc_con'] = int(metrics['grits_con'] == 1)"),
        ],
        newer: [
            ("new-shortcut-one", "true_positive_score >= (max(true_shape) - 1) * min(true_shape)"),
            ("new-shortcut-two", "true_positive_score >= len(true_row_nums) * true_shape[1] - 1"),
            ("new-lcs", "lcs_length = pylcs.lcs_sequence_length(string1, string2)"),
            ("new-union", "union = area_1 + area_2 - intersection"),
        ],
    }
    passages = []
    for path, rows in needles.items():
        lines = path.read_text().splitlines()
        for identifier, quote in rows:
            matches = [i for i,line in enumerate(lines, 1) if quote in line]
            assert matches, (identifier, quote)
            passages.append({"id": identifier, "path": str(path.relative_to(ROOT)),
                             "line": matches[0], "quote": quote})
    witness = calculate()
    refs_text = paper.read_text().split("\nReferences\n", 1)[1]
    refs_text = re.sub(r"^\s*GriTS: Grid table similarity\s+15\s*$", "", refs_text, flags=re.M)
    refs = re.findall(r"^\s*(\d+)\.\s+(.+?)(?=^\s*\d+\.\s|\Z)", refs_text, re.M | re.S)
    assert len(refs) == 18
    write("source-ledger.json", {"date_local": "2026-10-20", "paper_version": "2203.12555v3,23 May2023",
        "author_commit": COMMIT, "current_wrapper_commit": "8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1",
        "acquisitions": acquisitions, "passages": passages,
        "reading": {"paper": "All15 physical pages; no appendices", "rendered": [7,8,9],
            "original_metric": "Entire file", "original_caller": "Only lines266-331 and394-485",
            "current_wrapper": "Selected comparison spans274-437; predecessor records wider read"},
        "stdlib_dependency": witness["stdlib"], "historical_run_identity": "not established"})
    write("witnesses.json", witness)
    write("source-support-ledger.json", {"title": "GriTS: Grid table similarity metric for table structure recognition",
        "authors": ["Brandon Smock", "Rohith Pesala", "Robin Abraham"], "year": 2023,
        "arxiv": "2203.12555v3", "doi": "10.48550/arXiv.2203.12555", "classification": "DIRECT_METHOD",
        "publication_status": "Read arXiv v3; current wrapper cites ICDAR2023 pp535-549; published edition not separately acquired",
        "retraction_quarantine": "No notice observed on inspected arXiv landing/version history; independent publisher/global correction search not performed",
        "full_text": bind(UNIT / "sources/02-paper.pdf"), "technical_scope": "Sections2–4,eqs1–6,Table2,Figs2–5,all18 references; no appendix",
        "allowed": ["exact objective and heuristic distinction", "bounded-reward lower/upper argument", "reported experiment scope"],
        "forbidden": ["universal tightness", "original code implements exact LCS", "all published results reproduced", "accounting correctness", "current dependency verified"],
        "code": {"metric": bind(metric), "caller": bind(caller), "commit": COMMIT}})
    write("citation-venue-ledger.json", {"access_date": "2026-10-20", "citation_count": "not available",
        "citation_source": "No new citation-index query in six-request source bound", "venue": "ICDAR2023 from retained author citation",
        "venue_metric": "not available", "caveat": "Venue metadata is not independent technical evidence or a quality ranking."})
    actions = {1: ("FOUNDATIONAL", "Inspect original complexity source before independently asserting hardness"),
               2: ("COMPETITOR", "Spreadsheet-diff alternative; technical follow-up remains open"),
               3: ("SURVEY_OR_TUTORIAL", "Coverage context; no technical claim imported"),
               4: ("COMPETITOR", "DARLoc benchmark definition needs primary-source audit before adoption"),
               5: ("FOUNDATIONAL", "Table abstraction context; retain as uninspected dependency"),
               6: ("COMPETITOR", "DAR metric source needs separate technical reading"),
               7: ("EMPIRICAL_EXAMPLE", "Competition context; no new performance inference"),
               8: ("DIRECT_METHOD", "Inspect RowColAlign original before equality or complexity claims"),
               9: ("SURVEY_OR_TUTORIAL", "Evaluation context; uninspected primary source"),
               10: ("FOUNDATIONAL", "Ground-truth ambiguity source remains a substantive lead"),
               11: ("IMPLEMENTATION_OR_SOFTWARE", "Memoization citation; no runtime guarantee imported"),
               12: ("COMPETITOR", "TableBank already represented in manuscript; original scope remains separate"),
               13: ("COMPETITOR", "TREX scope distinct; no technical claim imported"),
               14: ("BACKGROUND", "Extraction history; no theorem or comparison imported"),
               15: ("DIRECT_METHOD", "PubTables-1M already locally read; preserve its source scope"),
               16: ("FOUNDATIONAL", "Tabular abstraction original remains uninspected"),
               17: ("COMPETITOR", "pdf2table historical approach; separate technical reading needed for comparison"),
               18: ("DIRECT_METHOD", "PubTabNet/EDD inquiry already completed; do not repeat")}
    write("backward-snowball-ledger.json", [{"number": int(n), "reference": " ".join(text.split()),
        "classification": actions[int(n)][0], "action": actions[int(n)][1],
        "status": "Bibliographic triage; not a new full-text read"} for n,text in refs])
    write("forward-snowball-ledger.json", {"new_query": "None in bounded source inquiry",
        "retained_followups": ["PubTables-v2 arXiv2512.10888v3", "POTATR arXiv2606.09788v1", "Kensho GriTS source at pinned commit"],
        "source": "Completed prior units and their retained provenance", "status": "Specific inspected followups; no exhaustive forward-coverage claim"})
    write("claim-support-ledger.json", {"candidate": "3.44", "manuscript_changed": False,
        "entries": [
            {"claim": "L<=OPT<=min(Ur,Uc) for declared bounded rewards", "class": "PROJECT_DERIVATION", "support": "execution-audit.md plus source Section3.5; finite independent oracle"},
            {"claim": "The implemented lower bound need not approximate OPT closely", "class": "PROJECT_DERIVATION", "support": "2x2 alternating-grid witness has0 versus1/2"},
            {"claim": "Original SequenceMatcher expression is exact LCS", "verdict": "wrong relative to stated target", "support": "Fixed string witnesses; original source anchor matcher-default", "limit": "Current pinned source and local stdlib; no historical score reconstruction"},
            {"claim": "Current wrapper's two shortcuts are justified", "class": "PROJECT_DERIVATION", "support": "execution-audit.md; rewards must be in[0,1]; finite2x2 oracle", "limit": "Not validation of dependency outputs/floating point"},
            {"claim": "Paper comparisons generalise to financial accounting", "class": "SOURCE_GAP_BLOCKER", "support": "Experiments on PubTables-1M and44,381 no-span tables do not test that target"}]})
    write("omission-risk-ledger.json", {"entries": [
        {"gap": "Original Generalized LCS/RowColAlign technical arguments", "status": "open primary-source reading", "risk": "Do not turn GriTS's references into independently checked theorems"},
        {"gap": "Geometry Rect.include_rect and newer bbox dependency", "status": "next static-source inquiry", "risk": "Current source formulas differ; exact dependency semantics not inspected"},
        {"gap": "New pylcs dependency and exact runtime versions", "status": "open", "risk": "A function name does not establish downstream correctness"},
        {"gap": "Historical evaluator and published result impact", "status": "open", "risk": "Current commits do not date source behavior to experiments"},
        {"gap": "Exact dataset splits/failure/merging protocol", "status": "open", "risk": "Unresolved by original metric theory"}],
        "reviewer_risk": "No comprehensive extraction survey or readiness promotion follows from this unit."})
    print(json.dumps({"constructed": True, "anchors": len(passages), "references": len(refs),
        "string_results": [{k:v for k,v in x.items() if k in ("name","claimed_lcs_reward","computed_block_reward","count_without_autojunk")} for x in witness["strings"]],
        "grid_witness": witness["grid_witness"], "finite_domain": witness["binary_2x2_domain"]}))


if __name__ == "__main__":
    main()
