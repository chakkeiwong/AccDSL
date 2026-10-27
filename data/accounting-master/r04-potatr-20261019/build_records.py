"""One-time source evidence construction; no third-party imports."""
import hashlib
import json
from pathlib import Path
import re
import shlex

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
S = UNIT / "sources"


def bind(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write(name, value):
    with (UNIT / name).open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    assert not (UNIT / "source-ledger.json").exists(), "one-time construction"
    acquisitions = []
    stems = ["01-arxiv", "02-paper", "03-publisher", "04-repository", "05-published"]
    for stem in stems:
        receipt = json.loads((S / (stem + ".receipt.json")).read_text())
        body = ROOT / receipt["filename_effective"]
        header = S / (stem + ".headers")
        assert body.stat().st_size == receipt["size_download"]
        command = ["curl", "--silent", "--show-error", "--location", "--connect-timeout", "10", "--max-time", "35", "--max-filesize", "12582912", "--proto", "=https", "--proto-redir", "=https", "--dump-header", str(header.relative_to(ROOT)), "--output", str(body.relative_to(ROOT)), "--write-out", "%{json}\\n", receipt["url"]]
        acquisitions.append({"url": receipt["url"], "effective_url": receipt["url_effective"], "status": receipt["http_code"], "redirects": receipt["num_redirects"], "bytes": receipt["size_download"], "curl_seconds": receipt["time_total"], "content_type": receipt["content_type"], "body": bind(body), "headers": bind(header), "receipt": bind(S / (stem + ".receipt.json")), "command": shlex.join(command)})
    needles = [
        ("version", "arXiv:2606.09788v1 [cs.CV] 8 Jun 2026"),
        ("text-supply", "page-level TE when paired with accurate text extraction."),
        ("classes", "for a total of 16 classes"),
        ("queries", "double the number of object queries from 125 to 250"),
        ("parent", "table object to always be the parent"),
        ("mlp", "relation head is implemented as a three-layer MLP"),
        ("domain", "document-level TE sourced from over one million PubMed articles"),
        ("training", "train for 100 epochs"),
        ("tail-training", "additional 35 epochs"),
        ("hardware", "8 Nvidia T4 GPUs with a batch size of 2 per"),
        ("default-transfer", "We use the default"),
        ("relation-weight", "weight of 0.05"),
        ("pretraining", "Most weights are initialized from TATR-v1.1-Pub"),
        ("matching", "uses the Hungarian algorithm to determine the one-to-one correspondence"),
        ("edge-iou", "IoU threshold of 0.8"),
        ("comparison-losses", "each model’s default losses and loss weights"),
        ("zero-shot", "seven specialized document"),
        ("direct-text", "its structure predictions are combined with text either extracted directly from"),
        ("ocr-results", "POTATR + docTR [12]             0.9601    0.8799"),
        ("direct-results", "POTATR + DT                    0.9665    0.9636"),
        ("gpu-timing", "All local models use a single NVIDIA A10G GPU (24 GB)"),
        ("cost-basis", "on-demand cloud instance priced at $2.45/hr"),
        ("throughput", "POTATR                     29M        52,031           $47"),
        ("model-timing", "POTATR’s inference time is constant at ∼21 ms"),
        ("postprocessing", "Only post-processing (text assignment)"),
        ("selection", "is not intended to assess TE performance across a typical distribution of docu-"),
        ("generalisation", "generalization to other document types and languages remains"),
        ("license-intent", "We plan to open source models and code under the MIT license."),
        ("unmerged", "POTATR                 0.6973    0.6710"),
        ("merged", "POTATR + merging       0.8507    0.8269"),
        ("continuation-model", "ViT-B-16, 86M pa-"),
        ("recall", "Cross-page table continuation prediction is near-optimal (0.995 recall)"),
        ("within-page", "within-page table part merging, which the current pipeline"),
        ("data-lead", "arXiv preprint arXiv:2512.10888"),
    ]
    paper = (S / "02-paper.txt").read_text()
    lines = paper.splitlines()
    passages = []
    for name, needle in needles:
        hits = [i + 1 for i, line in enumerate(lines) if needle in line]
        assert hits, name
        passages.append({"id": name, "path": str((S / "02-paper.txt").relative_to(ROOT)), "needle": needle, "first_line": hits[0]})
    references_text = paper[paper.index("\nReferences\n"):paper.index("\f14 ")]
    matches = list(re.finditer(r"(?m)^\s*(\d{1,2})\. (?=[A-Z])", references_text))
    assert [int(m.group(1)) for m in matches] == list(range(1, 32))
    classified = {
        "FOUNDATIONAL": {4, 24, 31}, "COMPETITOR": {2, 3, 5, 7, 8, 10, 13, 14, 15, 17, 18, 19, 20, 26, 27, 28, 29, 30},
        "DIRECT_METHOD": {21, 22, 23}, "IMPLEMENTATION_OR_SOFTWARE": {6, 9, 12}, "BACKGROUND_ONLY": {1, 11, 16, 25},
    }
    references = []
    for i, match in enumerate(matches):
        number = int(match.group(1))
        text = references_text[match.start():matches[i + 1].start() if i + 1 < len(matches) else len(references_text)]
        text = re.sub(r"\f\d+[^\n]*\n", " ", text)
        label = next(key for key, numbers in classified.items() if number in numbers)
        references.append({"reference": number, "entry": " ".join(text.split()), "classification": label, "status": "bibliographic/role triage only in this unit", "action": "inspect primary next: benchmark, page-set metrics and continuation source" if number == 21 else "retain prior scope where available; no new technical support from this citation"})

    write("source-ledger.json", {"scope": "POTATR v1 technical source and actual publisher/code-route disposition", "acquisitions": acquisitions, "passages": passages, "source_version": "arXiv2606.09788v1, 8 June 2026", "reading": {"text": bind(S / "02-paper.txt"), "pages": 16, "read_sections": ["1 introduction", "2.1–2.3 related work", "3.1 architecture", "3.2 training", "4.1–4.5 metrics/comparisons/evaluation/cost", "5.1–5.2 discussion", "6 conclusion", "7 limitations", "references1–31", "appendicesA–C"], "rendered_pages": [4, 7, 8, 15], "images": [bind(S / ("paper-%02d.png" % p)) for p in (4, 7, 8, 15)], "figure_policy": "Figures1/3/4 described from captions and associated text; no numerical curve extraction claimed"}, "lead_bindings": [bind(ROOT / name) for name in ("docs/design/research/raw/smock2022-citing-recent.json", "docs/design/research/raw/zheng2021-citing-recent.json", "docs/design/research/omissions.json", "docs/design/proposal/manuscript-early-conversion-20261018/chapters/03-literature.tex")], "publication": {"first_online": "28 August 2026", "citation_year": 2027, "venue": "Document Analysis Systems, DAS2026, LNCS16851", "metadata_conflict": "Retained OpenAlex says27 August2026; primary landing says28 August and citation2027", "technical_edition": "not acquired: nominal PDF returned HTML", "publisher_extracted": bind(S / "03-publisher.txt")}, "code": {"author_link": "https://github.com/kensho-technologies/POTATR", "status": "404 at acquired route; global availability unknown", "code_inspected": False}, "held_actions_executed": False})
    values = {"single_page_direct_grits": "0.9636", "single_page_doctr_grits": "0.8799", "multi_page_plain": "0.6710", "multi_page_merged": "0.8269", "multi_page_gemini": "0.9309", "multi_page_gpt": "0.8847", "pages_per_hour": "52031", "gemini_pages_per_hour": "393", "hourly_usd": "2.45", "gemini_usd_per_million": "15000", "reported_local_usd_per_million": "47"}
    write("arithmetic-inputs.json", {"scope": "Exact rational reconstructions of printed numbers; descriptive only", "values": values, "expressions": {"ocr_direct_gap": "837/10000", "multi_page_score_gain": "1559/10000", "relative_complement_reduction": "1559/3290", "gap_fraction_to_gemini": "1559/2599", "gap_fraction_to_gpt": "1559/2137", "throughput_ratio": "52031/393", "cost_from_hourly": "2450000/52031", "reported_cost_ratio": "15000/47", "throughput_implied_seconds_per_page": "3600/52031"}, "interpretation": "No paired uncertainty, causal error decomposition or resource-complete pipeline timing is inferred"})
    write("source-support-ledger.json", {"metadata_date": "2026-10-19", "entries": [{"title": "POTATR: A Lightweight Image-to-Graph Model for Page-Level Table Extraction", "authors": ["Brandon Smock", "Libin Liang", "Max Sokolov", "Amrit Ramesh", "Valerie Faucon-Morin", "Tayyibah Khanam", "Maury Courtland"], "source_version": "arXiv2606.09788v1", "local": bind(S / "02-paper.pdf"), "publication_status": "Preprint technical text; independently matched publisher landing,2027 citation year/2026 first online; published technical PDF not acquired", "retraction_quarantine_status": "No notice in inspected arXiv/publisher pages; no comprehensive registry check", "full_text_status": "16-page technical text including appendices read; key rendered pages4/7/8/15", "support_class": "PRIMARY_TECHNICAL_SUPPORT", "allowed": "Source-specific architecture, supplied inputs, evaluation conditions and descriptive tables", "forbidden": "Local ranking, replication, code equivalence, financial generalisation or full licensing clearance"}]})
    write("citation-venue-ledger.json", {"metadata_date": "2026-10-19", "venue": "DAS2026, LNCS16851", "venue_source": "acquired Springer chapter landing", "first_online_primary": "28 August2026", "citation_year_primary": 2027, "doi": "10.1007/978-3-032-36207-0_1", "citation_count": "not available in this inquiry", "citation_source": "existing OpenAlex retained as discovery evidence only; counts not refreshed", "venue_metric": "not available", "caveat": "Publication identity/metadata are not scientific validation"})
    write("backward-snowball-ledger.json", {"scope": "All31 references considered after related-work/method/comparison reading", "entries": references})
    write("forward-snowball-ledger.json", {"scope": "A previously nominated recent citing work is now technically read", "seed_queries": ["retained smock2022-citing-recent.json", "retained zheng2021-citing-recent.json"], "candidate_id": "https://openalex.org/W7164049321", "primary_checked_date": "2026-10-19", "new_citing_work_query": "none; POTATR follow-on coverage unperformed", "status": "Specific forward lead resolved; broad forward coverage remains incomplete"})
    claims = [
        ("POTATR performs page-level graph prediction", "PRIMARY_TECHNICAL_SUPPORT", "3.1/Fig2", "16 classes,250 queries,directed parent-child predictions; no external code checked"),
        ("POTATR independently recognises cell text", "SOURCE_CLAIM_REJECTED", "4.3/Table2", "Wrong relative to paper: PDF text or external OCR supplies text"),
        ("Reported headline establishes method superiority for the target application", "UNSUPPORTED", "3.2/4.2–4.3/7", "Trained versus zero-shot, differing text supply and English PubMed task; no paired uncertainty or financial validation"),
        ("Warm-start comparison isolates the causal benefit of pretraining", "UNSUPPORTED", "4.2/Table1", "Architecture,initialisation and default losses vary together; small10-epoch comparison is descriptive"),
        ("Cost table includes every possible OCR/merging deployment cost", "UNSUPPORTED", "4.5/Table4/AppendixC", "Page model,external text and86M continuation classifier must be distinguished; no complete deployment manifest"),
        ("Continuation recall0.995 proves near-optimal merging", "UNSUPPORTED", "AppendixC", "Recall alone does not establish precision,false merges or optimality"),
        ("Existing 3.44 extraction qualifications are contradicted", "NOT_ESTABLISHED", "chapter3 lines201–240 versus3.1/4.3/7/AppendixC", "Page graph and context support staged extraction; accounting correctness remains separate"),
    ]
    write("claim-support-ledger.json", {"entries": [{"claim": claim, "support_class": status, "anchor": anchor, "verdict": meaning} for claim, status, anchor, meaning in claims]})
    write("omission-risk-ledger.json", {"entries": [
        {"item": "PubTables-v2,arXiv2512.10888,reference21", "status": "inspect next", "reason": "Needed for split construction,set metrics,full-document sampling and continuation evaluation"},
        {"item": "Author-linked code and published technical PDF", "status": "route blocked", "reason": "404 repository and HTML access page; no execution/edition equivalence"},
        {"item": "Related competitors ETT,EGTR,Relationformer and current document models", "status": "triaged only through this paper", "reason": "Source-specific comparison is not comprehensive primary competitor reading"},
        {"item": "Generalisation/paired uncertainty/end-to-end cost", "status": "not established", "reason": "No local target-specific experiment; held empirical work"},
    ], "manuscript_action": "No confirmed defect; retain3.44 and consider an additive literature update only after source dependencies are resolved"})
    print(json.dumps({"constructed": True, "acquisitions": 5, "passages": len(passages), "references_triaged": len(references), "literature_ledgers": 6}))


if __name__ == "__main__":
    main()
