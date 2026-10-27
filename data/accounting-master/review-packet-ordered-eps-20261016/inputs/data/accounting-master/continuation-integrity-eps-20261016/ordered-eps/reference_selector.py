"""Documentary OrderedEPS/1 oracle. No runtime module or book write access."""
from datetime import date
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
SCHEMA = json.loads((OUT / "record-schemas.json").read_text())
REQUEST_VALIDATOR = Draft202012Validator(SCHEMA["$defs"]["Request"], format_checker=FormatChecker())
RESULT_VALIDATOR = Draft202012Validator(SCHEMA["$defs"]["Result"], format_checker=FormatChecker())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def bundle(n, total, d):
    return {k: str(v) for k, v in dict(continuing_numerator=n,
        total_numerator=total, discontinued_numerator=total-n, denominator=d,
        continuing_eps=n/d, total_eps=total/d, discontinued_eps=(total-n)/d).items()}


def calculate(request, root=ROOT):
    """Validate supplied premises, then select with exact current-ratio tests.

    Support hashes establish bytes only: finding truth and anchor interpretation
    remain explicit caller responsibilities. No filesystem content is modified.
    """
    context_ref = request.get("context_ref") if isinstance(request, dict) else None
    if not isinstance(context_ref, str) or not re.fullmatch(r"[0-9a-f]{64}", context_ref):
        context_ref = None
    result = dict(wire="OrderedEPS/1", request_sha256=digest(request),
        context_ref=context_ref, status="rejected", basic=None, diluted=None,
        trace=[], issues=[], mutations=[], acceptance="conditional_documentary_only")
    groups = {"rejected": [], "unresolved": [], "unsupported": []}

    def issue(kind, code, path, sid=None):
        groups[kind].append(dict(code=code, path=path, series_id=sid))

    def finish(status):
        result["status"] = status
        result["issues"] = sorted(
            [i for values in groups.values() for i in values],
            key=lambda i: (i["path"], i["code"], i["series_id"] or ""))
        RESULT_VALIDATOR.validate(result)
        return result

    errors = list(REQUEST_VALIDATOR.iter_errors(request))
    if errors:
        for error in errors:
            issue("rejected", "schema", "/" + "/".join(map(str, error.absolute_path)))
        return finish("rejected")
    if digest(request["context"]) != context_ref:
        issue("rejected", "context_hash_mismatch", "/context_ref")

    def support(node, path, sid=None):
        record = node["support"]
        try:
            source = (root / record["path"]).resolve()
            source.relative_to(root.resolve())
            actual = hashlib.sha256(source.read_bytes()).hexdigest()
        except (OSError, ValueError):
            issue("unresolved", "evidence_unavailable", path + "/support", sid)
            return False
        if actual != record["sha256"]:
            issue("rejected", "evidence_hash_mismatch", path + "/support", sid)
            return False
        return True

    def binding(node, path, sid=None):
        if node["context_ref"] != context_ref:
            issue("rejected", "context_mismatch", path + "/context_ref", sid)

    def rational(node, key, path, sid=None):
        value = Fraction(node[key])
        if str(value) != node[key]:
            issue("rejected", "noncanonical_rational", path + "/" + key, sid)
        return value

    period = request["context"]["period"]
    p_start, p_end = date.fromisoformat(period["start"]), date.fromisoformat(period["end_exclusive"])
    if p_start >= p_end:
        issue("rejected", "invalid_period", "/context/period")
    inventory = request["inventory"]
    support(inventory, "/inventory")
    if inventory["status"] != "complete":
        issue("unresolved", "incomplete_inventory", "/inventory/status")
    ids = [s["id"] for s in request["series"]]
    if len(ids) != len(set(ids)):
        issue("rejected", "duplicate_series", "/series")
    if sorted(ids) != sorted(inventory["ids"]):
        issue("rejected", "inventory_mismatch", "/inventory/ids")
    scope = request["scope"]
    support(scope, "/scope")
    for key in ("nonparticipating_rights", "independent_additive_effects", "fixed_effects"):
        if not scope[key]:
            issue("unsupported", "unsupported_scope", "/scope/" + key)
    basic = request["basic"]
    binding(basic, "/basic")
    basic_supported = support(basic, "/basic")
    basic_ready = basic["status"] == "ready"
    if not basic_ready:
        issue("unresolved", "unresolved_basic", "/basic")
    else:
        n = rational(basic, "continuing_numerator", "/basic")
        total = rational(basic, "total_numerator", "/basic")
        d = rational(basic, "denominator", "/basic")
        if d <= 0:
            issue("rejected", "nonpositive_basic_denominator", "/basic/denominator")
        for key in ("attribution_complete", "chronology_complete"):
            if not basic[key]:
                issue("unresolved", "incomplete_basic", "/basic/" + key)
                basic_ready = False

    candidates, no_effects = [], []
    for index, series in enumerate(request["series"]):
        sid, resolution = series["id"], series["resolution"]
        path = "/series/" + str(index)
        binding(series, path, sid)
        support(series, path, sid)
        if resolution in ("unresolved", "unsupported"):
            issue(resolution, resolution + "_series", path, sid)
            continue
        a = rational(series, "continuing_increment", path, sid)
        t = rational(series, "total_increment", path, sid)
        b = rational(series, "share_increment", path, sid)
        if resolution == "no_effect":
            if (a, t, b) != (0, 0, 0):
                issue("rejected", "nonzero_no_effect", path, sid)
            no_effects.append(series)
            continue
        if b <= 0:
            issue("rejected", "nonpositive_share_increment", path + "/share_increment", sid)
        for key in ("earnings_complete", "time_weighting_complete"):
            if not series[key]:
                issue("unresolved", "incomplete_effects", path + "/" + key, sid)
        windows = []
        split = {}
        for key in ("potential_windows", "actual_windows"):
            split[key] = []
            for wi, window in enumerate(series[key]):
                start = date.fromisoformat(window["start"])
                end = date.fromisoformat(window["end_exclusive"])
                if not p_start <= start < end <= p_end:
                    issue("rejected", "invalid_window", path + "/" + key + "/" + str(wi), sid)
                windows.append((start, end))
                split[key].append((start, end))
        windows.sort()
        if any(left[1] > right[0] for left, right in zip(windows, windows[1:])):
            issue("rejected", "overlapping_windows", path, sid)
        actual = split["actual_windows"]
        potential = split["potential_windows"]
        if series["end_kind"] == "converted":
            if not actual:
                issue("rejected", "missing_actual_window", path, sid)
            if not series["actual_in_basic"]:
                issue("rejected", "conversion_not_in_basic", path, sid)
            if actual and max(end for _, end in potential) > min(start for start, _ in actual):
                issue("rejected", "conversion_order", path, sid)
        elif actual or series["actual_in_basic"]:
            issue("rejected", "unexpected_actual_window", path, sid)
        if series["end_kind"] == "period_end" and max(end for _, end in potential) != p_end:
            issue("rejected", "period_end_mismatch", path, sid)
        candidates.append((a, t, b, series))

    if groups["rejected"]:
        return finish("rejected")
    if basic_ready and basic_supported:
        result["basic"] = bundle(n, total, d)
    if groups["unresolved"] or groups["unsupported"]:
        status = "blocked" if groups["unresolved"] and groups["unsupported"] else (
            "unresolved" if groups["unresolved"] else "unsupported")
        return finish(status)

    for a, t, b, series in sorted(candidates, key=lambda row: (row[0]/row[2], row[3]["id"])):
        left, right = a*d, n*b
        included = left < right
        result["trace"].append(dict(id=series["id"], resolution="candidate",
            continuing_increment=str(a), total_increment=str(t), share_increment=str(b),
            incremental_ratio=str(a/b), before=dict(continuing_numerator=str(n), denominator=str(d)),
            after_if_included=dict(continuing_numerator=str(n+a), denominator=str(d+b)),
            included=included, reason="strictly_dilutive" if included else (
                "neutral" if left == right else "antidilutive")))
        if included:
            n, total, d = n+a, total+t, d+b
    for series in sorted(no_effects, key=lambda s: s["id"]):
        state = dict(continuing_numerator=str(n), denominator=str(d))
        result["trace"].append(dict(id=series["id"], resolution="no_effect",
            continuing_increment="0", total_increment="0", share_increment="0",
            incremental_ratio=None, before=state.copy(), after_if_included=state.copy(),
            included=False, reason="no_effect"))
    result["diluted"] = bundle(n, total, d)
    return finish("conditional_complete")
