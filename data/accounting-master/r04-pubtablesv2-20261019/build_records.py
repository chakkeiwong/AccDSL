"""One-time source-ledger construction; no acquired module imports."""
import hashlib
import json
from pathlib import Path
import re
import shlex

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
S = UNIT / "sources"
COMMIT = "8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1"


def bind(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write(name, value):
    with (UNIT / name).open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    assert not (UNIT / "source-ledger.json").exists(), "one-time construction"
    acquisitions = []
    for stem in ("01-arxiv", "02-paper", "03-grits", "04-tree", "05-metric", "06-conversion"):
        receipt_path = S / (stem + ".receipt.json")
        receipt = json.loads(receipt_path.read_text())
        body, header = ROOT / receipt["filename_effective"], S / (stem + ".headers")
        assert body.stat().st_size == receipt["size_download"]
        command = ["curl", "--silent", "--show-error", "--location", "--connect-timeout", "10", "--max-time", "35", "--max-filesize", "12582912", "--proto", "=https", "--proto-redir", "=https", "--dump-header", str(header.relative_to(ROOT)), "--output", str(body.relative_to(ROOT)), "--write-out", "%{json}\\n", receipt["url"]]
        acquisitions.append({"url": receipt["url"], "effective_url": receipt["url_effective"], "status": receipt["http_code"], "redirects": receipt["num_redirects"], "bytes": receipt["size_download"], "curl_seconds": receipt["time_total"], "body": bind(body), "headers": bind(header), "receipt": bind(receipt_path), "command": shlex.join(command)})
    needles = {
        "02-paper.txt": [
            ("version", "arXiv:2512.10888v3 [cs.CV] 2 Jun 2026"),
            ("author-html", "created by leveraging XML (HTML) table annotations given by authors"),
            ("quality-mean", "strict with α = 0.02"),
            ("quality-max", "cannot exceed β = 0.2"),
            ("whole-article-filter", "article is discarded from the dataset"),
            ("word-inputs", "bounding boxes, are extracted from the original PDF document and included"),
            ("new-dates", "new set of PubMed documents from 2023-2025"),
            ("hidden-test", "contains 5,804 of the 135,578 total samples"),
            ("page-splits", "three public sets—a train, test, and validation set"),
            ("selected-documents", "at least one table that either continues across multiple pages"),
            ("matching", "The generalizations of TEDS and GriTS both use the Hungarian algorithm"),
            ("unmatched-penalty", "penalize poor precision in addition to recall"),
            ("linked-code", "https://github.com/kensho-technologies/grits"),
            ("zero-shot", "all evaluated zero-shot"),
            ("doc-context", "entire document at once"),
            ("positive-pairs", "PubTables-v2 contains 9,866 positive pairs"),
            ("negative-pairs", "This constraint yielded 5,964 negative pairs"),
            ("continuation-precision", "of 0.987"),
            ("merge-columns", "continuation is predicted and the adjacent tables have matching column counts"),
            ("merge-result", "dots.ocr + merging        0.7206         0.6844"),
            ("domain", "scientific articles in English"),
            ("dataset-license", "Agreement (CDLA) – Permissive, Version 2.0"),
            ("parts-counts", "9,492 multi-page tables, 630"),
            ("part-box-scope", "we do not annotate bounding boxes for rows or columns"),
            ("detector-selection", "We run this model on over a million PubMed articles"),
            ("all-xml-match", "tables in the XML/HTML annotation must be matched in the PDF"),
        ],
        "05-metric.py": [
            ("fscore-empty", "Precision is 1 when there are no predicted instances"),
            ("factored-scope", "This is a polynomial-time heuristic"),
            ("identity-cutoff", "if true_positive_score >= (max(true_shape) - 1) * min(true_shape):"),
            ("lcs-reward", "return 2 * lcs_length / (len(string1) + len(string2))"),
            ("raw-score-objective", "score_matrix[true_idx, pred_idx] = grits_result.true_positive_score"),
            ("hungarian", "linear_sum_assignment(score_matrix, maximize=True)"),
            ("cell-denominator", "num_pred_cells = sum(len(g) * _get_n_cols(g) for g in pred_grids_con)"),
            ("micro", "total_true_positive_score = sum(self.true_positive_scores)"),
            ("exact-recall", "The exact match accuracies are the fractions of ground truth cells and tables"),
            ("macro", 'f"mean_grits_{m}_per_sample": sum(f1s) / len(f1s)'),
            ("html-failure", 'raise ValueError(f"Failed to parse pred_html: {pred_html!r}")'),
            ("sample-count-check", 'if len(ev.true_positive_scores) > 0'),
        ],
        "06-conversion.py": [
            ("first-table", "the first is used"),
            ("parser", "html.fromstring(table_html, parser=html.HTMLParser(remove_comments=True))"),
            ("span-clamp", "return min(span, maximum)"),
            ("text-spaces", 'cell_text=" ".join(current.itertext())'),
            ("empty-grid", "return [[]]"),
            ("hole-topology", "default_value = [0, 0, 1, 1]"),
            ("conversion-separate", "HTML conversion is provided for convenience and is not part of the GriTS metric"),
        ],
    }
    passages = []
    for filename, anchors in needles.items():
        lines = (S / filename).read_text().splitlines()
        for name, needle in anchors:
            hits = [i + 1 for i, line in enumerate(lines) if needle in line]
            assert hits, (name, needle)
            passages.append({"id": name, "path": str((S / filename).relative_to(ROOT)), "needle": needle, "first_line": hits[0]})
    paper = (S / "02-paper.txt").read_text()
    refs_text = paper[paper.index("\nReferences\n"):paper.index("\f18 ")]
    matches = list(re.finditer(r"(?m)^\s*(\d{1,2})\. (?=[A-Z])", refs_text))
    assert [int(m.group(1)) for m in matches] == list(range(1, 37))
    refs = []
    for i, match in enumerate(matches):
        n = int(match.group(1))
        text = refs_text[match.start():matches[i + 1].start() if i + 1 < len(matches) else len(refs_text)]
        text = re.sub(r"\f\d+[^\n]*\n", " ", text)
        role = "BACKGROUND_ONLY" if n in {1, 5, 12, 18, 27} else "FOUNDATIONAL" if n in {4, 7, 25} else "IMPLEMENTATION_OR_SOFTWARE" if n in {3, 8, 9, 13, 22} else "DIRECT_METHOD" if n in {21, 23, 24, 35} else "COMPETITOR"
        refs.append({"reference": n, "entry": " ".join(text.split()), "classification": role, "status": "bibliographic/role triage only here; preserve prior technical reads separately", "action": "original GriTS theorem/heuristic source is a concrete future dependency" if n == 25 else "retain lead without importing its claims"})

    write("source-ledger.json", {"source_version": "arXiv2512.10888v3,2 June2026", "metric_commit": COMMIT, "acquisitions": acquisitions, "passages": passages, "reading": {"paper": bind(S / "02-paper.pdf"), "extracted": bind(S / "02-paper.txt"), "physical_pages": 28, "text_read_pages": list(range(1, 21)), "rendered_read_pages": list(range(21, 29)), "rendered_notes": bind(UNIT / "rendered-reading.md"), "images": [bind(S / ("paper-%d.png" % p)) for p in range(21, 29)], "warning": "Mismatched EMC operator; pdftotext omitted21–28; all eight pages read from actual renders", "code_reads": [{"file": bind(S / name), "lines": [1, len((S / name).read_text().splitlines())]} for name in ("05-metric.py", "06-conversion.py")], "readme_scope": "About/aggregation/default and quick-start sections inspected; no complete README read claim"}, "bindings": [bind(ROOT / name) for name in ("data/accounting-master/r04-potatr-20261019/completion.json", "data/accounting-master/r04-potatr-20261019/sources/02-paper.txt", "docs/design/proposal/manuscript-early-conversion-20261018/chapters/03-literature.tex")], "uninspected": ["dataset card/exact split IDs and cross-collection overlap", "published edition", "bbox.py and dependency/runtime behavior", "experiment-era metric/code identity", "exact failure-case scoring in experiments", "original GriTS theory paper"], "acquired_code_executed": False})
    write("witnesses.json", {
        "scope": "Exact fictional one-row content-grid algebra, independent of acquired execution",
        "grids": {"A1": ["a", "b"], "B1": ["a", "c"], "A2": ["a", "c"] + ["x"] * 18, "B2": ["a", "b"] + ["y"] * 18},
        "pair_true_positive_scores": [[1, 2], [2, 1]],
        "pair_normalised_scores": [["1/2", "2/11"], ["2/11", "1/20"]],
        "matching": {"diagonal": {"raw_sum": 2, "normalised_sum": "11/20", "downstream_micro": "1/11"}, "cross": {"raw_sum": 4, "normalised_sum": "4/11", "downstream_micro": "2/11"}},
        "macro_micro": {"samples": [{"tp": 1, "true": 1, "pred": 1}, {"tp": 0, "true": 9, "pred": 9}], "macro": "1/2", "micro": "1/10"},
        "unmatched_duplicate": {"tp": 1, "true_cells": 1, "pred_cells": 2, "f1": "2/3", "true_tables": 1, "pred_tables": 2, "exact_table_recall": "1"},
        "source_count_sums": {"document_tables": [9492, 630, 14740, 24862], "training_pairs": [9866, 5964, 15830]},
        "merging_values": {"pubtablesv2": "0.6844", "potatr": "0.7495", "difference": "651/10000"},
    })
    write("source-support-ledger.json", {"metadata_date": "2026-10-19", "entries": [{"title": "PubTables-v2: A new large-scale dataset for full-page and multi-page table extraction", "authors": ["Brandon Smock", "Valerie Faucon-Morin", "Max Sokolov", "Libin Liang", "Tayyibah Khanam", "Amrit Ramesh", "Maury Courtland"], "version": "2512.10888v3,2 June2026", "local": bind(S / "02-paper.pdf"), "publication_status": "arXiv technical preprint; no published-edition check in this unit", "retraction_quarantine_status": "No withdrawal notice in inspected arXiv page; comprehensive registry/erratum check not performed", "read_sections": ["1–6", "Tables1–12", "AppendicesA–F", "references1–36 triaged"], "full_text_status": "28 pages read using extraction1–20 and actual renders21–28", "allowed": "Exact version's dataset/metric/protocol/source-descriptive results", "forbidden": "Data-ID separation, empirical reproduction, financial transfer, whole-source equivalence or statistical ranking"}, {"title": "Kensho GriTS implementation", "commit": COMMIT, "files_read": ["grits/grits.py", "grits/conversion.py"], "support_class": "IMPLEMENTATION_EVIDENCE", "allowed": "Scoped static current-source behavior", "forbidden": "Transitive/runtime and historical experiment equivalence"}]})
    write("citation-venue-ledger.json", {"metadata_date": "2026-10-19", "source": "acquired arXiv landing", "version_date": "2 June2026", "original_submission": "11 December2025", "citation_count": "not available", "citation_source": "not queried in this dependency unit", "venue": "arXiv preprint", "venue_metric": "not available", "note": "v3 separates POTATR and adds frontier results; no version-equivalence claim"})
    write("backward-snowball-ledger.json", {"scope": "Related work and all36 reference entries considered; not36 primary technical reads", "entries": refs})
    write("forward-snowball-ledger.json", {"scope": "Concrete dependency link from separately read POTATR", "entries": [{"id": "potatr-v1", "status": "POTATR's later merging table differs; preserve both exact versions and conditions"}, {"id": "broad-citing-works", "status": "not queried; incomplete coverage"}]})
    claims = [
        ("Literal summed normalised pair scores equal the current Hungarian objective", "wrong under stated literal interpretation", "rendered C.3 versus metric raw-score-objective", "finite one-row counterexample; intended/history resolution still open"),
        ("Macro and micro GriTS evaluate the same aggregation objective", "wrong", "rendered C.4 and compute_grits/compute_mean_grits_per_sample", "finite one-cell/nine-cell example gives1/2 versus1/10"),
        ("Unmatched predictions are ignored by GriTS", "wrong for cell denominator", "hungarian_grits_con and evaluator", "all predicted grid cells count; table-exact accuracy is recall-like and alone omits this penalty"),
        ("Near-perfect continuation recall is the only reported evidence", "wrong for expanded source", "4.6/Table6/rendered F.3/F.4", "precision0.987,F10.991,AUC0.996 and20/1862 failures reported; no target-domain optimality"),
        ("PDF/HTML filters prove every visible table is annotated", "unsupported", "3.1/B.2", "coverage is relative to supplied author annotation and detector/alignment selection"),
        ("New dates and hidden tests prove contamination-free splits", "unsupported", "3.2", "exact grouped IDs/inter-collection overlap and unknown model training data uninspected"),
        ("Two source merging scores describe one verified identical experiment", "unsupported", "Table7 versus POTATR Table5", "0.6844 versus0.7495; column-count condition explicit only in inspected benchmark description"),
        ("Full financial report extraction is established", "unsupported", "6/Appendices and3.44 chapter3", "domain,task,source labels and accounting semantics remain separate"),
    ]
    write("claim-support-ledger.json", {"entries": [{"claim": a, "verdict": b, "support": c, "limit": d} for a,b,c,d in claims]})
    write("omission-risk-ledger.json", {"entries": [
        {"item": "Exact split/card/IDs", "status": "open", "reason": "No group/inter-collection overlap conclusion; a small official dataset-card/source inquiry is next"},
        {"item": "Original GriTS proof and historical implementation", "status": "open", "reason": "Current factored routine labels itself heuristic; no general optimality or historical equivalence"},
        {"item": "Experiment failure scoring and merging settings", "status": "open", "reason": "Counts/precision known; complete denominator and later result difference unresolved"},
        {"item": "Current parser/bbox/dependency behavior", "status": "partial static inspection", "reason": "Conversion can repair spans/use first table; no installed or full transitive audit"},
    ], "manuscript_action": "No confirmed3.44 defect; preserve existing extraction qualifications"})
    print(json.dumps({"constructed": True, "acquisitions": 6, "text_anchors": len(passages), "rendered_pages_read": 8, "references_triaged": 36, "literature_ledgers": 6}))


if __name__ == "__main__":
    main()
