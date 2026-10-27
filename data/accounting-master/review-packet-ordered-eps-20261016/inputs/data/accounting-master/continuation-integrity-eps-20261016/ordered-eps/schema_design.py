"""Closed proposed OrderedEPS/1 records; no runtime installation."""
import json
from pathlib import Path


def obj(fields):
    return {"type": "object", "properties": fields,
            "required": list(fields), "additionalProperties": False}


def enum(*values):
    return {"enum": list(values)}


def array(item):
    return {"type": "array", "items": item}


TEXT = {"type": "string", "minLength": 1}
BOOL = {"type": "boolean"}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
Q = {"type": "string", "pattern": "^(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?$"}
DATE = {"type": "string", "format": "date"}
SUPPORT = obj({"path": TEXT, "sha256": HASH, "anchor": TEXT})
WINDOW = obj({"start": DATE, "end_exclusive": DATE})
CONTEXT = obj({k: TEXT for k in (
    "entity", "book", "head", "view", "population", "ordinary_class",
    "share_basis", "currency", "currency_scale", "rule_version")}
    | {"period": WINDOW})
BASE_BINDING = {"context_ref": HASH, "support": SUPPORT}
BASIC = {"oneOf": [
    obj(BASE_BINDING | {"status": enum("ready"), "continuing_numerator": Q,
        "total_numerator": Q, "denominator": Q,
        "attribution_complete": BOOL, "chronology_complete": BOOL}),
    obj(BASE_BINDING | {"status": enum("unresolved"), "reason": TEXT})]}
SERIES_BINDING = BASE_BINDING | {"id": TEXT}
SERIES = {"oneOf": [
    obj(SERIES_BINDING | {"resolution": enum("candidate"),
        "continuing_increment": Q, "total_increment": Q, "share_increment": Q,
        "earnings_complete": BOOL, "time_weighting_complete": BOOL,
        "potential_windows": array(WINDOW) | {"minItems": 1},
        "actual_windows": array(WINDOW),
        "end_kind": enum("period_end", "lapsed", "converted"),
        "actual_in_basic": BOOL}),
    obj(SERIES_BINDING | {"resolution": enum("no_effect"),
        "continuing_increment": Q, "total_increment": Q, "share_increment": Q,
        "reason": TEXT}),
    obj(SERIES_BINDING | {"resolution": enum("unresolved", "unsupported"),
        "reason": TEXT})]}
REQUEST = obj({"wire": enum("OrderedEPS/1"), "operation": enum("report"),
    "context": CONTEXT, "context_ref": HASH,
    "inventory": obj({"status": enum("complete", "incomplete"),
        "ids": array(TEXT) | {"uniqueItems": True}, "support": SUPPORT}),
    "scope": obj({"nonparticipating_rights": BOOL,
        "independent_additive_effects": BOOL, "fixed_effects": BOOL,
        "support": SUPPORT}), "basic": BASIC, "series": array(SERIES)})
BUNDLE = obj({k: Q for k in ("continuing_numerator", "total_numerator",
    "discontinued_numerator", "denominator", "continuing_eps", "total_eps",
    "discontinued_eps")})
STATE = obj({"continuing_numerator": Q, "denominator": Q})
nullable = lambda s: {"anyOf": [s, {"type": "null"}]}
TRACE = obj({"id": TEXT, "resolution": enum("candidate", "no_effect"),
    "continuing_increment": Q, "total_increment": Q, "share_increment": Q,
    "incremental_ratio": nullable(Q), "before": nullable(STATE),
    "after_if_included": nullable(STATE), "included": BOOL,
    "reason": enum("strictly_dilutive", "neutral", "antidilutive", "no_effect")})
RESULT = obj({"wire": enum("OrderedEPS/1"), "request_sha256": HASH,
    "context_ref": nullable(HASH),
    "status": enum("conditional_complete", "unresolved", "unsupported", "blocked", "rejected"),
    "basic": nullable(BUNDLE), "diluted": nullable(BUNDLE), "trace": array(TRACE),
    "issues": array(obj({"code": TEXT, "path": TEXT,
                          "series_id": nullable(TEXT)})),
    "mutations": {"type": "array", "maxItems": 0},
    "acceptance": enum("conditional_documentary_only")})


def write_schema():
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:accdsl:documentary:ordered-eps:1",
        "$defs": {"Request": REQUEST, "Result": RESULT},
        "oneOf": [{"$ref": "#/$defs/Request"}, {"$ref": "#/$defs/Result"}]}
    (Path(__file__).parent / "record-schemas.json").write_text(
        json.dumps(schema, indent=2) + "\n")


if __name__ == "__main__":
    write_schema()
