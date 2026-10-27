"""Read-only source binding and exact printed-value reconstruction."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]


def check():
    count = 0

    def require(value, label):
        nonlocal count
        assert value, label
        count += 1

    def load(name):
        return json.loads((UNIT / name).read_text())

    def bound(item):
        return hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]

    sources = load("source-ledger.json")
    require(len(sources["acquisitions"]) == 5, "bounded acquisition count")
    for row in sources["acquisitions"]:
        for key in ("body", "headers", "receipt"):
            require(bound(row[key]), "acquisition binding")
        receipt = json.loads((ROOT / row["receipt"]["path"]).read_text())
        require(receipt["exitcode"] == 0 and receipt["time_total"] < 35 and receipt["size_download"] < 12582912, "acquisition limits")
        require((receipt["http_code"], receipt["num_redirects"], receipt["url_effective"], receipt["size_download"]) == (row["status"], row["redirects"], row["effective_url"], row["bytes"]), "exact receipt fields")
        statuses = re.findall(r"^HTTP/\S+ (\d+)", (ROOT / row["headers"]["path"]).read_text(), re.M)
        require(statuses[-1] == str(row["status"]), "terminal header")
    require([row["status"] for row in sources["acquisitions"]] == [200, 200, 200, 404, 200], "exact route dispositions")
    require((UNIT / "sources/02-paper.pdf").read_bytes().startswith(b"%PDF-"), "technical PDF signature")
    require(not (UNIT / "sources/05-published.body").read_bytes().startswith(b"%PDF-"), "publisher200 is not PDF")
    require("text/html" in sources["acquisitions"][4]["content_type"], "publisher body type")
    require(sources["acquisitions"][4]["redirects"] == 7, "record PDF-route redirects")
    for passage in sources["passages"]:
        require(passage["needle"] in (ROOT / passage["path"]).read_text().splitlines()[passage["first_line"] - 1], passage["id"])
    for item in sources["reading"]["images"] + sources["lead_bindings"] + [sources["reading"]["text"], sources["publication"]["publisher_extracted"]]:
        require(bound(item), "reading/lead binding")
    paper = (UNIT / "sources/02-paper.txt").read_text()
    require(paper.count("\f") == 16 and sources["reading"]["pages"] == 16, "16 physical pages")
    publisher = (UNIT / "sources/03-publisher.txt").read_text()
    require("28 August 2026" in publisher and "(2027).  POTATR" in publisher, "primary publication dates")
    require(sources["code"]["author_link"] in publisher, "actual author repository link")
    require(sources["code"]["code_inspected"] is False and sources["held_actions_executed"] is False, "no implementation execution admission")
    refs = load("backward-snowball-ledger.json")["entries"]
    require([r["reference"] for r in refs] == list(range(1, 32)), "all31 references triaged")
    require(all(r["classification"] in {"FOUNDATIONAL", "DIRECT_METHOD", "COMPETITOR", "BACKGROUND_ONLY", "IMPLEMENTATION_OR_SOFTWARE"} for r in refs), "reference roles")
    require("2512.10888" in refs[20]["entry"], "actual next dependency identity")

    def validate_arithmetic(data):
        v = {key: Fraction(value) for key, value in data["values"].items()}
        actual = {
            "ocr_direct_gap": v["single_page_direct_grits"] - v["single_page_doctr_grits"],
            "multi_page_score_gain": v["multi_page_merged"] - v["multi_page_plain"],
            "relative_complement_reduction": (v["multi_page_merged"] - v["multi_page_plain"]) / (1 - v["multi_page_plain"]),
            "gap_fraction_to_gemini": (v["multi_page_merged"] - v["multi_page_plain"]) / (v["multi_page_gemini"] - v["multi_page_plain"]),
            "gap_fraction_to_gpt": (v["multi_page_merged"] - v["multi_page_plain"]) / (v["multi_page_gpt"] - v["multi_page_plain"]),
            "throughput_ratio": v["pages_per_hour"] / v["gemini_pages_per_hour"],
            "cost_from_hourly": v["hourly_usd"] * 1000000 / v["pages_per_hour"],
            "reported_cost_ratio": v["gemini_usd_per_million"] / v["reported_local_usd_per_million"],
            "throughput_implied_seconds_per_page": 3600 / v["pages_per_hour"],
        }
        assert actual == {key: Fraction(value) for key, value in data["expressions"].items()}
        return actual

    arithmetic = load("arithmetic-inputs.json")
    arithmetic_result = validate_arithmetic(arithmetic)
    for value in arithmetic["values"].values():
        require(value in paper.replace(",", ""), "printed input exists")
    require(round(float(arithmetic_result["relative_complement_reduction"]) * 100, 1) == 47.4, "reported complement reduction rounded")
    require(round(float(arithmetic_result["gap_fraction_to_gemini"]) * 100) == 60 and round(float(arithmetic_result["gap_fraction_to_gpt"]) * 100) == 73, "reported gap fractions rounded")
    require(round(float(arithmetic_result["cost_from_hourly"])) == 47, "reported local cost rounded")
    rejected = 0
    for index in range(5):
        bad = deepcopy(arithmetic)
        if index == 0:
            bad["values"]["multi_page_merged"] = "0.9269"
        elif index == 1:
            bad["expressions"]["throughput_ratio"] = "130"
        elif index == 2:
            bad["values"]["hourly_usd"] = "24.5"
        elif index == 3:
            bad["expressions"]["relative_complement_reduction"] = "474/1000"
        else:
            bad["values"]["single_page_direct_grits"] = "0.964"
        try:
            validate_arithmetic(bad)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("altered printed-value reconstruction accepted")
    require(rejected == 5, "five invalid controls rejected")
    for name in ("source-support", "citation-venue", "backward-snowball", "forward-snowball", "claim-support", "omission-risk"):
        require(bool(load(name + "-ledger.json")), "six additive ledgers")
    return {"acquisitions": 5, "technical_pages_read": 16, "rendered_pages": 4, "passage_anchors": len(sources["passages"]), "assertions": count, "references_triaged": 31, "exact_arithmetic_relations": len(arithmetic_result), "rejected_altered_controls": rejected, "code_inspected": False, "published_technical_edition_acquired": False, "statistical_ranking_admitted": False, "runtime_admitted": False, "manuscript_changed": False}
