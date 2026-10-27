"""One-time documentary construction; standard library, no acquired imports."""
import hashlib
import json
from pathlib import Path
import shlex

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
BASE = UNIT.parent
COMMIT = "e6bb2bd509d7c89cdf1fb9608f9db9a044413bed"


def bind(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write(name, value):
    with (UNIT / name).open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    assert not (UNIT / "source-ledger.json").exists(), "one-time construction"
    specs = [
        ("01-datasets.py", "01-datasets.py.headers", "datasets.py", 8691, 0.918461),
        ("02-utils.py", "02-utils.py.headers", "utils.py", 10898, 1.333752),
        ("03-metric.py", "03-metric.py.headers", "metric.py", 10339, 0.872208),
        ("04-requirements.txt", "04-requirements.txt.headers", "requirements.txt", 92, 0.920348),
        ("05-index.body", "05-index.headers", "https://www.ecva.net/papers.php", 3600315, 3.919189),
        ("06-supplement.pdf", "06-supplement.headers", "https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123660562-supp.pdf", 1002875, 2.198349),
    ]
    acquisitions = []
    for body, header, remote, size, seconds in specs:
        url = remote if remote.startswith("https:") else "https://raw.githubusercontent.com/ibm-aur-nlp/EDD/" + COMMIT + "/" + remote
        body_path, header_path = UNIT / "sources" / body, UNIT / "sources" / header
        assert body_path.stat().st_size == size
        command = ["curl", "--silent", "--show-error", "--location", "--connect-timeout", "10", "--max-time", "35", "--max-filesize", "12582912", "--proto", "=https", "--proto-redir", "=https", "--dump-header", str(header_path.relative_to(ROOT)), "--output", str(body_path.relative_to(ROOT)), "--write-out", "%{json}\\n", url]
        acquisitions.append({"url": url, "effective_url": url, "status": 200, "redirects": 0, "bytes": size, "curl_seconds": seconds, "body": bind(body_path), "headers": bind(header_path), "command": shlex.join(command), "receipt_provenance": "Transcribed prior tool curl JSON fields; retained body/header bytes independently hashed; raw JSON not retained"})

    anchors = [
        ("loader-hdf5", "01-datasets.py", "self.split + '_IMAGES_' + data_name + '.hdf5'"),
        ("loader-shuffle", "01-datasets.py", "self.ind = np.random.permutation(self.dataset_size)"),
        ("loader-padding", "01-datasets.py", "samples = np.hstack((self.ind[self.pointer:self.pointer + step], np.array(range(lack))))"),
        ("loader-getitem", "01-datasets.py", "image_size = self.imgsizes[i]"),
        ("loader-scaling", "01-datasets.py", "img = torch.FloatTensor(self.imgs[sample] / 255.)"),
        ("private-parallel-api", "02-utils.py", "from torch.nn.parallel._functions import Scatter, Gather"),
        ("clipping", "02-utils.py", "param.grad.data.clamp_(-grad_clip, grad_clip)"),
        ("checkpoint", "02-utils.py", "def save_checkpoint_dual("),
        ("resize", "02-utils.py", "im = im.resize(new_size, Image.Resampling.LANCZOS)"),
        ("channel-assumption", "02-utils.py", "if img.shape[2] > 3:"),
        ("metric-distance", "03-metric.py", "return float(distance.levenshtein(*sequences)) / self.maximum(*sequences)"),
        ("metric-global", "03-metric.py", "global __tokens__"),
        ("metric-zip", "03-metric.py", "for i, cell in zip(to_insert[::-1], cells[::-1]):"),
        ("metric-denominator", "03-metric.py", 'n_nodes_pred = len(pred.xpath(".//*"))'),
        ("metric-parser", "03-metric.py", "html.fromstring(prediction),"),
        ("thresholds", "03-metric.py", "thresholds = np.linspace(0.6, 0.95, 8)"),
        ("external-java", "03-metric.py", "dataset-tools-fat-lib.jar"),
        ("ssh-example", "03-metric.py", "from paramiko import SSHClient"),
        ("requirements", "04-requirements.txt", "torch>=1.0"),
        ("supplement-authors", "06-supplement.txt", "Xu Zhong, Elaheh ShafieiBavani, and Antonio Jimeno Yepes"),
        ("supplement-thresholds", "06-supplement.txt", "(0.5, 0.6, · · · , 0.9)"),
        ("supplement-runtime", "06-supplement.txt", "running TEDS with 28 parallel threads on a 28 core1 Linux machine."),
        ("supplement-runtime-value", "06-supplement.txt", "EDD                     88.3                 13.7"),
        ("supplement-encoder", "06-supplement.txt", "EDD-S1S1     91.3      85.4   88.4"),
        ("supplement-attention", "06-supplement.txt", "F    Visualization of attention"),
    ]
    passages = []
    for name, filename, needle in anchors:
        path = UNIT / "sources" / filename
        lines = path.read_text().splitlines()
        hits = [i + 1 for i, line in enumerate(lines) if needle in line]
        assert hits, (name, needle)
        passages.append({"id": name, "path": str(path.relative_to(ROOT)), "needle": needle, "first_line": hits[0]})

    index = (UNIT / "sources/05-index.body").read_text()
    target = "papers/eccv_2020/papers_ECCV/papers/123660562-supp.pdf"
    offset = index.index(target)
    excerpt = index[max(0, offset - 2400):offset + 200]
    assert "Image-based Table Recognition: Data, Model, and Evaluation".lower() in excerpt.lower()
    write("source-ledger.json", {
        "scope": "Pinned EDD loader/helper/metric/dependency declaration and complete six-page published supplement",
        "commit": COMMIT, "acquisitions": acquisitions, "passages": passages,
        "official_supplement_link": {"index": bind(UNIT / "sources/05-index.body"), "relative_href": target, "character_offset": offset, "entry_excerpt": excerpt, "doi": "10.1007/978-3-030-58589-1_34"},
        "read_boundaries": [
            {"file": str((UNIT / "sources" / name).relative_to(ROOT)), "lines": [1, len((UNIT / "sources" / name).read_text().splitlines())], "status": "complete text read"}
            for name in ("01-datasets.py", "02-utils.py", "03-metric.py", "04-requirements.txt", "06-supplement.txt")
        ],
        "rendered_read": {"pages": [3, 4], "observations": "Five printed adjacency thresholds; S1 mean scores; S2 metric evaluation with 28 threads; S3 five encoder rows and validation heading", "images": [bind(UNIT / "sources" / name) for name in ("supplement-3.png", "supplement-4.png")]},
        "prior_bindings": [bind(BASE / name) for name in (
            "r04-edd-edition-20261019/completion.json", "r04-pubtabnet-20261019/sources/05-metric.py", "r04-edd-edition-20261019/sources/03-models.py", "r04-edd-edition-20261019/sources/04-training.py", "r04-edd-edition-20261019/sources/05-preparation.py")],
        "uninspected": ["parallel.py", "installed dependency versions/semantics", "Java evaluator source/JAR", "EDD experiment-era source and artifacts", "unread model alternatives identified in predecessor"],
        "acquired_code_executed": False,
    })
    write("witnesses.json", {"scope": "Fictional index arithmetic deduced from loader source; no NumPy or dataset execution", "cases": [
        {"n": 5, "batch_size": 4, "permutation": [4, 3, 2, 1, 0], "batches": [[4, 3, 2, 1], [0, 0, 1, 2]], "padding": [0, 1, 2], "shuffled_prefix": [4, 3, 2], "invalid_indices": []},
        {"n": 1, "batch_size": 4, "permutation": [0], "batches": [[0, 0, 1, 2]], "padding": [0, 1, 2], "shuffled_prefix": [0], "invalid_indices": [1, 2]},
    ], "thresholds": {"supplement": ["1/2", "3/5", "7/10", "4/5", "9/10"], "code_default": ["3/5", "13/20", "7/10", "3/4", "4/5", "17/20", "9/10", "19/20"]}})
    write("source-support-ledger.json", {"metadata_date": "2026-10-19", "entries": [
        {"title": "Image-based table recognition: data, model, and evaluation — supplemental material", "authors": ["Xu Zhong", "Elaheh ShafieiBavani", "Antonio Jimeno Yepes"], "year": 2020, "doi": "10.1007/978-3-030-58589-1_34", "publication_status": "ECVA-hosted ECCV 2020 main/supplement pair linked in official index", "local": bind(UNIT / "sources/06-supplement.pdf"), "full_text_status": "six pages read; physical pages 3–4 inspected", "inspected": ["A/S1/S2", "B/S3", "C/Table S1", "D/Table S2", "E/Table S3", "F/S4", "four references"], "support_class": "PRIMARY_TECHNICAL_SUPPORT", "allowed": "Reported perturbations, metric settings, metric runtime conditions and validation encoder scores", "forbidden": "Local model replication, financial correctness, statistically supported ranking, model-inference timing", "retraction_quarantine_status": "No notice in inspected index/PDF; independent retraction/erratum registry not checked; no comprehensive clearance"},
        {"title": "IBM EDD selected implementation dependencies", "classification": "IMPLEMENTATION_OR_SOFTWARE", "commit": COMMIT, "local_files": [bind(UNIT / "sources" / row[0]) for row in specs[:4]], "support_class": "IMPLEMENTATION_EVIDENCE", "allowed": "Static source observations at pinned commit", "forbidden": "Installed equivalence or experiment-era identity"},
    ]})
    write("citation-venue-ledger.json", {"metadata_date": "2026-10-19", "venue": "ECCV 2020", "source": "acquired ECVA index and linked supplement", "doi": "10.1007/978-3-030-58589-1_34", "citation_count": "not available", "citation_source": "not queried in this bounded dependency unit", "venue_metric": "not available", "caveat": "Venue and counts establish no correctness or ranking"})
    write("backward-snowball-ledger.json", {"scope": "All four supplementary references triaged; no technical reading credit", "inherited": bind(BASE / "r04-pubtabnet-20261019/backward-snowball-ledger.json"), "entries": [
        {"reference": 1, "work": "Gao et al., ICDAR 2019 competition on table detection and recognition (2019)", "classification": "DIRECT_METHOD", "action": "inspect next if adjacency-threshold justification is required"},
        {"reference": 2, "work": "Hurst, A constraint-based approach to table structure derivation (2003)", "classification": "FOUNDATIONAL", "action": "adjacency-method lead; primary technical reading pending"},
        {"reference": 3, "work": "Lin et al., Microsoft COCO: Common objects in context (2014)", "classification": "BACKGROUND_ONLY", "action": "analogy for averaging thresholds; does not validate table thresholds"},
        {"reference": 4, "work": "Qasim et al., Rethinking table recognition using graph neural networks (2019)", "classification": "COMPETITOR", "action": "synthetic-table and rival-method lead; technical reading pending"},
    ]})
    write("forward-snowball-ledger.json", {"scope": "Supplement-to-current-source correspondence; not citing-work coverage", "entries": [{"id": "same-paper-code", "commit": COMMIT, "status": "threshold mismatch and wrapper differences recorded; experiment identity unresolved"}, {"id": "broad-citing-works", "status": "incomplete; no new index query or fabricated citation coverage", "next": "separate targeted forward/competitor inquiry"}]})
    claims = [
        ("Preparation and selected loader disagree on hdf5 extension", "wrong relative to inspected source", "loader-hdf5", "Both use .hdf5; README .h5 is documentary drift"),
        ("EDD and PubTabNet whole metric implementations are interchangeable", "unsupported", "metric-parser", "CustomConfig syntax agrees; wrappers/parser settings/state differ"),
        ("Published adjacency thresholds equal pinned default", "wrong", "thresholds", "Supplement specifies five 0.5–0.9 thresholds, code eight 0.6–0.95"),
        ("13.7 minutes measures EDD model inference", "wrong", "supplement-runtime", "Table S2 measures TEDS evaluation with 28 threads"),
        ("Requirements identify the published reproducible environment", "unsupported", "requirements", "Lower bounds and unpinned entries; installed versions unknown"),
        ("Loader pads the final batch with the shuffled prefix", "wrong", "loader-padding", "Uses raw indices range(lack); two fictional consequences are separate deductions"),
        ("Checkpoint restores a fully reproducible random stream", "unsupported", "checkpoint", "Inspected saved state has no RNG field; no restored-run test"),
        ("Gradient clipping is norm clipping", "wrong", "clipping", "Elementwise clamp in inspected helper"),
        ("Encoder table establishes an uncertainty-supported ranking", "unsupported", "supplement-encoder", "Reported validation scores are descriptive under current evidence"),
    ]
    write("claim-support-ledger.json", {"scope": "Documentary/static findings; no empirical evidence", "entries": [{"claim": claim, "verdict": verdict, "anchor": anchor, "meaning": meaning} for claim, verdict, anchor, meaning in claims]})
    write("omission-risk-ledger.json", {"entries": [
        {"item": "parallel.py / exact installed dependencies / Java evaluator", "status": "requires source expansion", "objection": "Selected-source inspection cannot certify full runtime or concurrency"},
        {"item": "Four supplementary references", "status": "triaged only", "objection": "Citing a reference is not a technical comparison"},
        {"item": "Experiment revision and source of published thresholds", "status": "unresolved", "objection": "Current default mismatch alone cannot invalidate published numbers"},
        {"item": "Broad competitors, forward citations, four historical blocked originals", "status": "open", "objection": "Dependency closure is not comprehensive literature coverage"},
    ], "manuscript_action": "No confirmed 3.44 defect; retain existing extraction qualifications"})
    print(json.dumps({"constructed": True, "acquisitions": len(acquisitions), "passages": len(passages), "literature_ledgers": 6, "finite_cases": 2}))


if __name__ == "__main__":
    main()
