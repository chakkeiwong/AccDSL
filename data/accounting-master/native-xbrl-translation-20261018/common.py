"""Portable L1 primitives and the explicitly limited documentary type checker."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(path):
    raw = path.read_bytes()
    return {"kind": "blob", "algorithm": "sha256", "digest": sha(raw), "byte_length": len(raw)}


def canonical(value):
    # validate_tree excludes floats, duplicate-key inputs and invalid scalar strings.
    validate_tree(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def validate_tree(value):
    if isinstance(value, str):
        value.encode("utf-8", "strict")
    elif type(value) in (int, bool) or value is None:
        return
    elif isinstance(value, list):
        for child in value:
            validate_tree(child)
    elif isinstance(value, dict):
        for key, child in value.items():
            require(isinstance(key, str) and key.isascii(), "NON_ASCII_KEY")
            validate_tree(child)
    else:
        raise ValueError("NON_PORTABLE_VALUE")


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def reject_number(value):
    raise ValueError("NON_INTEGER_JSON_NUMBER")


def decode(raw):
    value = json.loads(raw, object_pairs_hook=unique_pairs,
                       parse_float=reject_number, parse_constant=reject_number)
    validate_tree(value)
    return value


def read(path):
    return decode(path.read_bytes())


def write_once(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def require(predicate, code):
    if not predicate:
        raise ValueError(code)


def unknown(reason):
    return {"tag": "Unknown", "reason": reason, "obligation_refs": []}


def rational(value):
    return {"n": str(value.numerator), "d": str(value.denominator)}


def refs(value):
    if isinstance(value, dict):
        if set(value) == {"kind", "schema", "digest"}:
            return [value]
        return [ref for child in value.values() for ref in refs(child)]
    if isinstance(value, list):
        return [ref for child in value for ref in refs(child)]
    return []


def ref_set(items):
    by_bytes = {canonical(item): item for item in items}
    return [by_bytes[key] for key in sorted(by_bytes)]


def record_ref(record):
    digest = sha(("accdsl.portable.v1/" + record["schema"]).encode() + b"\0" + canonical(record))
    return {"kind": record["kind"], "schema": record["schema"], "digest": digest}


def pointer(value, path):
    require(path == "" or path.startswith("/"), "BAD_POINTER")
    for part in path.split("/")[1:]:
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def typed(value, shape, profile):
    if isinstance(shape, str):
        if shape in profile["types"]:
            typed(value, profile["types"][shape], profile)
            if shape in ("Unknown", "NotApplicable"):
                require(bool(value["reason"].strip()), "EMPTY_REASON")
            if shape in ("Span", "Locator"):
                require(0 <= value["byte_start"] < value["byte_end"], "SPAN_RANGE")
            return
        if shape == "Text":
            require(isinstance(value, str), "TYPE_TEXT")
        elif shape == "Int":
            require(type(value) is int, "TYPE_INT")
        elif shape == "Bool":
            require(type(value) is bool, "TYPE_BOOL")
        elif shape == "Null":
            require(value is None, "TYPE_NULL")
        elif shape == "Ref":
            require(isinstance(value, dict) and set(value) == {"kind", "schema", "digest"}, "REF_SHAPE")
            require(all(isinstance(v, str) and v.isascii() and v for v in value.values()), "REF_IDENTIFIER")
            require(re.fullmatch(r"[0-9a-f]{64}", value["digest"]), "REF_DIGEST")
        elif shape == "BlobRef":
            require(isinstance(value, dict) and set(value) == {"kind", "algorithm", "digest", "byte_length"}, "BLOB_SHAPE")
            require(value["kind"] == "blob" and value["algorithm"] == "sha256", "BLOB_TAG")
            require(isinstance(value["digest"], str) and re.fullmatch(r"[0-9a-f]{64}", value["digest"]), "BLOB_DIGEST")
            typed(value["byte_length"], "Int", profile)
            require(value["byte_length"] >= 0, "BLOB_LENGTH")
        elif shape == "Rational":
            require(isinstance(value, dict) and set(value) == {"n", "d"}, "RATIONAL_SHAPE")
            require(isinstance(value["n"], str) and re.fullmatch(r"0|-[1-9][0-9]*|[1-9][0-9]*", value["n"]), "RATIONAL_NUMERATOR")
            require(isinstance(value["d"], str) and re.fullmatch(r"[1-9][0-9]*", value["d"]), "RATIONAL_DENOMINATOR")
            require(rational(Fraction(int(value["n"]), int(value["d"]))) == value, "RATIONAL_NOT_REDUCED")
        else:
            raise ValueError("UNKNOWN_TYPE:" + shape)
    elif "fields" in shape:
        require(isinstance(value, dict) and set(value) == set(shape["fields"]), "CLOSED_FIELDS")
        for key, child in shape["fields"].items():
            typed(value[key], child, profile)
    elif "list" in shape:
        require(isinstance(value, list), "TYPE_LIST")
        for child in value:
            typed(child, shape["list"], profile)
    elif "literal" in shape:
        require(type(value) is type(shape["literal"]) and value == shape["literal"], "LITERAL")
    elif "enum" in shape:
        require(any(type(value) is type(v) and value == v for v in shape["enum"]), "ENUM")
    elif "union" in shape:
        valid = 0
        for child in shape["union"]:
            try:
                typed(value, child, profile)
                valid += 1
            except ValueError:
                pass
        require(valid == 1, "UNION")
    else:
        raise ValueError("UNKNOWN_TYPE_EXPRESSION")
