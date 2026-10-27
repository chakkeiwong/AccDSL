"""Read-only verification of the active-panel documentary reconciliation."""
import copy
import json
import subprocess
import sys

from reconcile import (
    ROOT, OUT, BASE, COVERAGE, PANEL, QA, PROTOCOL, INVENTORY, EVENTS,
    ALTERNATES, MUNICH, HENKEL, HSBC, LABELS, SELECTION, SEMANTIC,
    CONTROLS, FROZEN, construct, load, binding, digest, pointer,
)


def require(condition, name):
    if not condition:
        raise ValueError(name)


def validate(document, data):
    checks = []

    def check(name, condition):
        require(condition, name)
        checks.append(name)

    def ref(item, path, ptr=None):
        source = item["source"]
        check("REFERENCE_PATH", source["path"] == path)
        if ptr is not None:
            check("REFERENCE_POINTER", source["json_pointer"] == ptr)
        check("REFERENCE_HASH", source["sha256"] == digest(path))
        check("REFERENCE_RECORD", item["record"] == pointer(data[path], source["json_pointer"]))

    active = data[COVERAGE]["rows"]
    rows = document["rows"]
    check("ACTIVE_192", len(active) == len(rows) == 192)
    check("ACTIVE_ORDER", [r["document_id"] for r in rows] == [r["document_id"] for r in active])
    ids = {r["document_id"] for r in rows}
    check("ACTIVE_UNIQUE", len(ids) == len(rows))
    check("NINE_PANEL_FAMILIES", {r["issuer_id"] for r in rows} ==
          {r["issuer_id"] for r in data[PANEL]["issuers"]} and len(data[PANEL]["issuers"]) == 9)
    for path, key in [(INVENTORY, None), (EVENTS, None), (ALTERNATES, None),
                      (SELECTION, "records"), (MUNICH, "primary"), (HENKEL, "primary"), (HSBC, "primary")]:
        records = data[path] if key is None else data[path][key]
        check("SOURCE_UNIQUE:" + path, len({r["document_id"] for r in records}) == len(records))
        check("SOURCE_ACTIVE_ONLY:" + path, {r["document_id"] for r in records} <= ids)
    for i, (row, coverage) in enumerate(zip(rows, active)):
        key, issuer = coverage["document_id"], coverage["issuer_id"]
        check("ROW_ISSUER:" + key, row["issuer_id"] == issuer)
        ref(row["active_coverage"], COVERAGE, "/rows/" + str(i))
        expected_identity = {"path": coverage["local_path"], "sha256": coverage["sha256"],
                             "source_url": coverage["source_url"]}
        check("SELECTED_IDENTITY:" + key, row["selected"] == expected_identity)
        ref(row["frozen_date_metadata"], INVENTORY, "/" + str(i))
        original = row["frozen_date_metadata"]["record"]
        check("FROZEN_IDENTITY:" + key,
              original["selected_path"] == coverage["local_path"] and original["selected_sha256"] == coverage["sha256"])
        check("NO_BYTE_OR_SPLIT_ADMISSION:" + key,
              row["selected_byte_available_at"] is None and row["as_of_admission"] is False
              and row["untouched_model_or_test_status"] == "not_established")
        for item in row["official_filing_events"]:
            ref(item, EVENTS)
            event = item["record"]
            check("EVENT_SELECTED_IDENTITY:" + key, event["document_id"] == key and
                  event["selected_pdf"] == {"path": coverage["local_path"], "sha256": coverage["sha256"]})
            check("EVENT_NO_BYTE_TRANSFER:" + key,
                  event["selected_byte_available_at"] is None and event["as_of_admission"] is False)
        expected_events = [r for r in data[EVENTS] if r["document_id"] == key]
        check("EVENTS_ALL_RETAINED:" + key, [e["record"] for e in row["official_filing_events"]] == expected_events)
        expected_declarations = []
        for path in [MUNICH, HENKEL, HSBC]:
            expected_declarations += [r for r in data[path]["primary"] if r["document_id"] == key]
        check("DECLARATIONS_ALL_RETAINED:" + key,
              [e["record"] for e in row["attributed_publication_declarations"]] == expected_declarations)
        for item in row["attributed_publication_declarations"]:
            source, declaration = item["source"], item["record"]
            check("DECLARATION_PRIMARY_ONLY:" + key,
                  source["path"] in [MUNICH, HENKEL, HSBC] and source["json_pointer"].startswith("/primary/"))
            ref(item, source["path"])
            check("DECLARATION_SELECTED_IDENTITY:" + key, declaration["document_id"] == key and
                  declaration["pdf"] == coverage["local_path"] and declaration["pdf_sha256"] == coverage["sha256"])
            check("DECLARATION_PRECISION:" + key, declaration["date_precision"] == "day"
                  and declaration["time_of_day"] is None and declaration["timezone"] is None)
        candidates = row["alternate_source_date_candidates"]
        check("ALTERNATES_ALL_RETAINED:" + key,
              [e["record"] for e in candidates] == [r for r in data[ALTERNATES] if r["document_id"] == key])
        for item in candidates:
            ref(item, ALTERNATES)
            check("ALTERNATE_SELECTED_URL:" + key, item["record"]["selected_source"] == coverage["source_url"])
        for item in row["other_or_excluded_date_roles"]:
            source = item["source"]
            check("OTHER_DATE_NOT_PRIMARY:" + key, source["path"] in [MUNICH, HSBC]
                  and not source["json_pointer"].startswith("/primary/"))
            ref(item, source["path"])
            check("OTHER_DATE_DOCUMENT:" + key, item["record"]["document_id"] == key)
        exposure = row["known_exposure"]
        check("EXPOSURE_NONEXHAUSTIVE:" + key, exposure["scope"] == "nonexhaustive_lower_bound_no_absence_inference")
        qa, qa_ref = data[QA]["documents"][key], exposure["acquisition_qa"]
        check("QA_ANCHOR:" + key, pointer(data[QA], qa_ref["source"]["json_pointer"]) == qa
              and qa_ref["source"]["path"] == QA and qa_ref["source"]["sha256"] == digest(QA))
        check("QA_IDENTITY:" + key, qa_ref["document_id"] == key and
              qa_ref["path"] == qa["local_path"] == coverage["local_path"] and
              qa_ref["sha256"] == qa["sha256"] == coverage["sha256"])
        labels = exposure["pilot_annotations"]
        check("PILOT_ALL_RETAINED:" + key,
              [e["record"] for e in labels] == [r for r in data[LABELS] if r["document_id"] == key])
        check("PILOT_NOT_GOLD:" + key, exposure["pilot_label_status"] ==
              "author_development_answers_not_independent_gold")
        for item in labels:
            ref(item, LABELS)
            check("PILOT_SELECTED_BYTES:" + key, item["record"]["original_sha256"] == coverage["sha256"])
        if exposure["pilot_selection"] is not None:
            ref(exposure["pilot_selection"], SELECTION)
            choice = exposure["pilot_selection"]["record"]
            check("PILOT_SELECTION_IDENTITY:" + key,
                  choice["document_id"] == key and choice["sha256"] == coverage["sha256"]
                  and choice["local_path"] == coverage["local_path"])
        check("READING_EXPOSURE_ANCHORS:" + key,
              exposure["publication_reading_sources"] == [e["source"] for e in row["attributed_publication_declarations"]]
              and exposure["filing_event_check_sources"] == [e["source"] for e in row["official_filing_events"]])
        sem = exposure["complete_issuer_semantic"]
        if sem is not None:
            ref(sem["package"], SEMANTIC)
            package = sem["package"]["record"]
            selected_role = package["roles"]["selected_annual"]
            check("SEMANTIC_SELECTED_COUNTERPART:" + key, selected_role["path"] == coverage["local_path"]
                  and selected_role["sha256"] == coverage["sha256"])
            check("SEMANTIC_DISTINCT_ACTUAL_SOURCE:" + key,
                  sem["exposed_source"] == package["roles"]["complete_issuer_10k"]
                  and sem["exposed_source"]["sha256"] != coverage["sha256"]
                  and sem["exact_selected_byte_annotations"] is False
                  and sem["scope"] == "issuer_family_complete_10k_source")
            check("SEMANTIC_NOT_GOLD:" + key, sem["label_status"] == "author_review_only_not_independent_gold")
            for group, list_name in [(sem["assertions"], "assertions"), (sem["quotes"], "quotes")]:
                check("SEMANTIC_ALL_RETAINED:" + key,
                      [e["record"] for e in group] == [r for r in data[SEMANTIC][list_name]
                                                     if r["year"] == package["year"]])
                for item in group:
                    ref(item, SEMANTIC)
        role = row["family_role"]
        check("ROLE_SOURCE:" + key, role["source"]["path"] == PROTOCOL and
              role["source"]["sha256"] == digest(PROTOCOL) and
              pointer(data[PROTOCOL], role["source"]["json_pointer"]) == role["value"]
              == data[PROTOCOL]["provisional_issuer_family_roles"][issuer])
        check("UNPROMOTED_ROLE:" + key, role["promoted"] is False and
              role["split_status"] == data[PROTOCOL]["split_status"]
              and role["split_status"].startswith("not_promoted;"))
    # Totals detect omissions that a per-record identity check alone cannot find.
    check("FROZEN_56_136", sum(bool(r["frozen_date_metadata"]["record"]["selected_date"]) for r in rows) == 56)
    check("EVENT_12", sum(len(r["official_filing_events"]) for r in rows) == 12)
    check("DECLARATION_35", sum(len(r["attributed_publication_declarations"]) for r in rows) == 35)
    check("PILOT_31", sum(len(r["known_exposure"]["pilot_annotations"]) for r in rows) == 31)
    semantic_rows = [r for r in rows if r["known_exposure"]["complete_issuer_semantic"]]
    check("SEMANTIC_FOUR_AND_40", len(semantic_rows) == 4 and
          sum(len(r["known_exposure"]["complete_issuer_semantic"]["assertions"]) for r in semantic_rows) == 40)
    return checks


def preservation():
    baseline = load(BASE + "r06-duty-reconciliation-20261018/run-manifest.json")["git_baseline"]
    git = lambda *args: subprocess.check_output(["git", *args], cwd=ROOT)
    require(git("rev-parse", "HEAD").decode().strip() == baseline["git_commit"], "HEAD_CHANGED")
    require(digest(".git/index") == baseline["index_sha256"], "INDEX_CHANGED")
    require(not git("diff", "--cached", "--name-only"), "STAGING_CHANGED")
    dirty = [p.decode() for p in git("diff", "--name-only", "-z").split(b"\0") if p]
    require(set(dirty) == {r["path"] for r in baseline["tracked_dirty"]}, "DIRTY_PATH_SET_CHANGED")
    for row in baseline["tracked_dirty"]:
        if row["path"] not in CONTROLS:
            require(binding(row["path"]) == row, "UNRELATED_DIRTY_CHANGED:" + row["path"])
    for path, expected in FROZEN.items():
        require(digest(path) == expected, "FROZEN_CHANGED:" + path)
    return {"git_commit": baseline["git_commit"], "index_sha256": baseline["index_sha256"],
            "tracked_dirty_count": len(dirty), "staged_diff": "empty"}


def fixtures(document, data):
    def find(d, key):
        return next(r for r in d["rows"] if r["document_id"] == key)

    probes = {
        "dropped_active_report": lambda d: d["rows"].pop(),
        "duplicate_active_report": lambda d: d["rows"].__setitem__(1, copy.deepcopy(d["rows"][0])),
        "reordered_active_reports": lambda d: d["rows"].reverse(),
        "selected_hash_substitution": lambda d: d["rows"][0]["selected"].update(sha256="0" * 64),
        "invented_selected_byte_vintage": lambda d: d["rows"][0].update(selected_byte_available_at="2018-01-01"),
        "unsupported_as_of_admission": lambda d: d["rows"][0].update(as_of_admission=True),
        "test_role_promoted": lambda d: find(d, "jpmorgan-2018-annual")["family_role"].update(promoted=True),
        "event_clock_rewritten": lambda d: find(d, "jpmorgan-2018-annual")["official_filing_events"][0]
            ["record"]["filing_event"].update(acceptanceDateTime="2019-02-26T00:00:00.000Z"),
        "declaration_timezone_invented": lambda d: find(d, "henkel-2018-annual")
            ["attributed_publication_declarations"][0]["record"].update(timezone="UTC"),
        "excluded_date_promoted": lambda d: find(d, "hsbc-2023-annual")
            ["attributed_publication_declarations"].append(copy.deepcopy(
                find(d, "hsbc-2023-annual")["other_or_excluded_date_roles"][0])),
        "pilot_called_independent_gold": lambda d: find(d, "apple-2025-q1")["known_exposure"]
            .update(pilot_label_status="independent_gold"),
        "complete_10k_called_selected_bytes": lambda d: find(d, "jpmorgan-2022-annual")["known_exposure"]
            ["complete_issuer_semantic"].update(exact_selected_byte_annotations=True),
        "exposure_absence_claim": lambda d: d["rows"][0]["known_exposure"].update(scope="exhaustive"),
        "alternate_date_transferred": lambda d: find(d, "apple-2018-annual").update(as_of_admission=True),
        "superseded_issuer_leaks": lambda d: d["rows"][0].update(document_id="allianz-2024-annual", issuer_id="allianz"),
    }
    rejected = []
    for name, mutate in probes.items():
        candidate = copy.deepcopy(document)
        mutate(candidate)
        try:
            validate(candidate, data)
        except (ValueError, KeyError, IndexError):
            rejected.append(name)
        else:
            raise ValueError("CORRUPTION_ACCEPTED:" + name)
    return rejected


def verify():
    expected, data, inputs = construct()
    observed = load(str((OUT / "reconciliation.json").relative_to(ROOT)))
    checks = validate(observed, data)
    require(observed == expected, "EXACT_DOCUMENTARY_REPLAY")
    manifest = load(str((OUT / "run-manifest.json").relative_to(ROOT)))
    require(manifest["inputs"] == inputs, "INPUT_BINDINGS")
    for row in manifest["artifacts"]:
        require(binding(row["path"]) == row, "OUTPUT_CHANGED:" + row["path"])
    recorded = load(str((OUT / "checks.json").relative_to(ROOT)))
    rejected = fixtures(observed, data)
    require(recorded["checks"] == checks and recorded["rejected_corruptions"] == rejected, "CHECK_REPLAY")
    state = preservation()
    return {"read_only_replay": "passed", "reports": len(observed["rows"]),
            "source_bindings": len(inputs), "checks": len(checks),
            "rejected_corruptions": len(rejected), **state}


if __name__ == "__main__":
    print(json.dumps(verify()))
