"""Bounded P06 context, chronology, uncertainty and resolution runtime.

The profile is intentionally explicit: it uses exact ``Fraction`` arithmetic,
Gregorian half-open periods, finite populations, and a fixed-rate unhedged bullet
debt resolver.  Every rejection has a stable ``P06Error.code``.  This module
checks structural and computational contracts; it does not certify accounting
eligibility or the truth of retained source evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone
from fractions import Fraction
import hashlib
import json
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class P06Error(ValueError):
    """A rejected P06 operation with a stable diagnostic code."""
    def __init__(self, code: str, message: str, *, location: str = ""):
        self.code, self.location, self.message = code, location, message
        suffix = f" at {location}" if location else ""
        super().__init__(f"{code}{suffix}: {message}")


def fail(code: str, message: str, location: str = "") -> None:
    raise P06Error(code, message, location=location)


def _fraction(value: Any, where: str = "value") -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        fail("INVALID_RATIONAL", "boolean is not a scalar", where)
    try:
        if isinstance(value, int):
            return Fraction(value)
        if isinstance(value, str):
            return Fraction(value)
        if isinstance(value, float):
            # Floats are rejected to keep exactness explicit.
            fail("INEXACT_RATIONAL", "float input is not accepted", where)
        if isinstance(value, Mapping) and set(value) == {"n", "d"}:
            q = Fraction(int(value["n"]), int(value["d"]))
            if int(value["d"]) <= 0:
                fail("INVALID_RATIONAL", "denominator must be positive", where)
            if {"n": str(q.numerator), "d": str(q.denominator)} != {
                "n": str(value["n"]), "d": str(value["d"])
            }:
                fail("NONCANONICAL_RATIONAL", "fraction must be reduced", where)
            return q
    except (ValueError, ZeroDivisionError) as exc:
        fail("INVALID_RATIONAL", str(exc), where)
    fail("INVALID_RATIONAL", "expected an integer or canonical rational", where)


def _iso_date(value: Any, where: str) -> date:
    if not isinstance(value, str):
        fail("INVALID_DATE", "date must be YYYY-MM-DD", where)
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        fail("INVALID_DATE", str(exc), where)
    if parsed.isoformat() != value:
        fail("INVALID_DATE", "noncanonical ISO date", where)
    return parsed


def _instant(value: Any, where: str) -> datetime:
    if not isinstance(value, str):
        fail("INVALID_TIMESTAMP", "timestamp must be an ISO string", where)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        fail("INVALID_TIMESTAMP", str(exc), where)
    if parsed.tzinfo is None:
        fail("MISSING_TIMEZONE", "timestamp requires an explicit timezone", where)
    return parsed


@dataclass(frozen=True)
class Context:
    concept: str
    entity: str
    perimeter: str
    perimeter_version: str
    basis: str
    measurement: str
    unit: str
    currency: str
    calendar: str
    dimensions: tuple[tuple[str, str], ...] = ()
    gross_net: str = "gross"
    parent: str | None = None
    group: str | None = None
    scale: Any = None
    sign: Any = None
    precision: Any = None

    def __post_init__(self):
        for key in ("concept", "entity", "perimeter", "perimeter_version", "basis", "measurement", "unit", "currency", "calendar"):
            if not isinstance(getattr(self, key), str) or not getattr(self, key):
                fail("INVALID_CONTEXT_FIELD", key, "context")
        if self.calendar != "gregorian":
            fail("CALENDAR_MISMATCH", "only Gregorian calendar is implemented")
        if self.gross_net not in {"gross", "net"}:
            fail("INVALID_GROSS_NET", "gross or net required")
        if not isinstance(self.dimensions, tuple) or len(dict(self.dimensions)) != len(self.dimensions):
            fail("INVALID_DIMENSIONS", "unique immutable dimension pairs required")
        if any(isinstance(v, (list, dict, set)) for v in (self.scale, self.sign, self.precision)):
            fail("INVALID_DISPLAY_METADATA", "display metadata must be scalar")

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "Context":
        required = ("concept", "entity", "perimeter", "perimeter_version", "basis",
                    "measurement", "unit", "currency", "calendar", "dimensions", "gross_net")
        for key in required:
            if key not in row:
                fail("MISSING_CONTEXT_FIELD", f"missing {key}", "context")
        dims = row["dimensions"]
        if not isinstance(dims, Mapping):
            fail("INVALID_DIMENSIONS", "dimensions must be an object", "context.dimensions")
        if any(not isinstance(k, str) or not isinstance(v, str) for k, v in dims.items()):
            fail("INVALID_DIMENSIONS", "dimension keys and values must be strings", "context.dimensions")
        if row["gross_net"] not in {"gross", "net"}:
            fail("INVALID_GROSS_NET", "gross_net must be gross or net", "context.gross_net")
        return cls(*(row[k] for k in required[:9]),
                   tuple(sorted((str(k), str(v)) for k, v in dims.items())),
                   str(row["gross_net"]), row.get("parent"), row.get("group"),
                   row.get("scale"), row.get("sign"), row.get("precision"))

    def as_dict(self) -> dict[str, Any]:
        return {
            "concept": self.concept, "entity": self.entity, "perimeter": self.perimeter,
            "perimeter_version": self.perimeter_version, "basis": self.basis,
            "measurement": self.measurement, "unit": self.unit, "currency": self.currency,
            "calendar": self.calendar, "dimensions": dict(self.dimensions),
            "gross_net": self.gross_net, "parent": self.parent, "group": self.group,
            "scale": self.scale, "sign": self.sign, "precision": self.precision,
        }


@dataclass(frozen=True)
class MappingRule:
    source_concept: str
    target_concept: str
    kind: str = "equivalent"
    source_context: str | None = None
    target_context: str | None = None
    effective_start: date | None = None
    effective_end: date | None = None
    conversion: str | None = None
    provenance: tuple[str, ...] = ()

    def __post_init__(self):
        if self.kind not in {"equivalent", "component", "reclassification"}:
            fail("UNSUPPORTED_MAPPING", self.kind)
        if not self.source_concept or not self.target_concept or not self.provenance:
            fail("MAPPING_PROVENANCE_REQUIRED", "concept IDs and provenance required")
        if self.conversion not in (None, "", "none"):
            fail("UNSUPPORTED_MEASUREMENT_CONVERSION", self.conversion)
        if self.effective_start and self.effective_end and self.effective_end <= self.effective_start:
            fail("INVALID_MAPPING_WINDOW", "end must follow start")

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "MappingRule":
        if not row.get("provenance"):
            fail("MAPPING_PROVENANCE_REQUIRED", "mapping provenance is required", "mapping")
        start = _iso_date(row["effective_start"], "mapping.effective_start") if row.get("effective_start") else None
        end = _iso_date(row["effective_end"], "mapping.effective_end") if row.get("effective_end") else None
        if start and end and end <= start:
            fail("INVALID_MAPPING_WINDOW", "effective end must follow start", "mapping")
        kind = row.get("kind", "equivalent")
        if kind not in {"equivalent", "component", "reclassification"}:
            fail("UNSUPPORTED_MAPPING", f"unsupported mapping kind {kind}", "mapping")
        return cls(str(row["source_concept"]), str(row["target_concept"]), kind,
                   row.get("source_context"), row.get("target_context"), start, end,
                   row.get("conversion"), tuple(str(x) for x in row["provenance"]))

    def active(self, when: date | None) -> bool:
        if when is None:
            return self.effective_start is None and self.effective_end is None
        return ((self.effective_start is None or when >= self.effective_start) and
                (self.effective_end is None or when < self.effective_end))


def _context_mismatch(a: Context, b: Context) -> tuple[str, str] | None:
    fields = ("entity", "perimeter", "perimeter_version", "basis", "measurement", "unit",
              "currency", "calendar", "dimensions", "gross_net", "parent", "group",
              "scale", "sign", "precision")
    for field_name in fields:
        if getattr(a, field_name) != getattr(b, field_name):
            return field_name, getattr(a, field_name).__repr__() + " != " + getattr(b, field_name).__repr__()
    if a.concept != b.concept:
        return "concept", repr(a.concept) + " != " + repr(b.concept)
    return None


def _check_mapping_graph(rules: Sequence[MappingRule]) -> None:
    graph: dict[str, set[str]] = {}
    for rule in rules:
        graph.setdefault(rule.source_concept, set()).add(rule.target_concept)
    state: dict[str, int] = {}
    def visit(node: str) -> None:
        state[node] = 1
        for nxt in graph.get(node, ()):
            if state.get(nxt) == 1:
                fail("MAPPING_CYCLE", "mapping graph contains a cycle", node)
            if state.get(nxt) != 2:
                visit(nxt)
        state[node] = 2
    for node in graph:
        if state.get(node, 0) == 0:
            visit(node)


def compatible_context(source: Context | Mapping[str, Any], target: Context | Mapping[str, Any],
                       rules: Sequence[MappingRule | Mapping[str, Any]] = (),
                       *, at: str | date | None = None) -> dict[str, Any]:
    """Return a mapping witness or reject a context mismatch."""
    a = source if isinstance(source, Context) else Context.from_dict(source)
    b = target if isinstance(target, Context) else Context.from_dict(target)
    when = _iso_date(at, "mapping.at") if isinstance(at, str) else at
    parsed = [x if isinstance(x, MappingRule) else MappingRule.from_dict(x) for x in rules]
    _check_mapping_graph(parsed)
    mismatch = _context_mismatch(a, b)
    if mismatch is None:
        return {"status": "compatible", "kind": "identity", "source": a.as_dict(), "target": b.as_dict()}
    field_name, detail = mismatch
    if field_name == "concept":
        eligible = [r for r in parsed if r.source_concept == a.concept and r.target_concept == b.concept and r.active(when)]
        if not eligible:
            fail("CONTEXT_MISMATCH", f"concept mismatch {detail} requires an explicit active mapping", field_name)
        if len(eligible) != 1:
            fail("AMBIGUOUS_MAPPING", "multiple active direct mappings")
        rule = eligible[0]
        if rule.kind != "equivalent":
            fail("PARTITION_WITNESS_REQUIRED", "use map_components for component/reclassification mappings")
        if rule.kind == "equivalent" and (rule.conversion or "") not in {"", "none"}:
            fail("UNSUPPORTED_MEASUREMENT_CONVERSION", "equivalent mapping cannot convert measurements", field_name)
        if rule.source_context and rule.source_context != a.entity:
            fail("MAPPING_SOURCE_CONTEXT_MISMATCH", "mapping source context does not match", field_name)
        if rule.target_context and rule.target_context != b.entity:
            fail("MAPPING_TARGET_CONTEXT_MISMATCH", "mapping target context does not match", field_name)
        return {"status": "compatible", "kind": rule.kind, "source": a.as_dict(), "target": b.as_dict(),
                "provenance": list(rule.provenance)}
    codes = {"perimeter": "PARENT_GROUP_MISMATCH", "perimeter_version": "PERIMETER_VERSION_MISMATCH",
             "basis": "BASIS_MISMATCH", "measurement": "MEASUREMENT_MISMATCH", "currency": "CURRENCY_MISMATCH",
             "calendar": "CALENDAR_MISMATCH", "gross_net": "GROSS_NET_MISMATCH", "dimensions": "DIMENSION_MISMATCH",
             "scale": "UNSUPPORTED_MEASUREMENT_CONVERSION", "sign": "DISPLAY_METADATA_MISMATCH", "precision": "DISPLAY_METADATA_MISMATCH",
             "entity": "ENTITY_MISMATCH", "unit": "UNIT_MISMATCH", "parent": "PARENT_GROUP_MISMATCH", "group": "PARENT_GROUP_MISMATCH"}
    fail(codes.get(field_name, "CONTEXT_MISMATCH"), f"context field mismatch: {detail}", field_name)


def map_context(source: Context | Mapping[str, Any], target: Context | Mapping[str, Any],
                rules: Sequence[MappingRule | Mapping[str, Any]] = (), *, at: str | date | None = None) -> dict[str, Any]:
    return compatible_context(source, target, rules, at=at)


def check_partition(population: Iterable[str], members: Mapping[str, Iterable[str]], *,
                    residual: Mapping[str, Any] | None = None, axis: str = "") -> dict[str, Any]:
    pop = list(population)
    if len(pop) != len(set(pop)):
        fail("DUPLICATE_POPULATION", "population identifiers must be unique", axis)
    universe = set(pop)
    seen: dict[str, str] = {}
    normalized: dict[str, list[str]] = {}
    for label, values in members.items():
        vals = list(values)
        if len(vals) != len(set(vals)):
            fail("DUPLICATE_MEMBER", f"member repeated in {label}", axis)
        unknown = set(vals) - universe
        if unknown:
            fail("UNKNOWN_MEMBER", f"members outside population: {sorted(unknown)}", axis)
        for value in vals:
            if value in seen:
                fail("OVERLAPPING_PARTITION", f"{value} occurs in {seen[value]} and {label}", axis)
            seen[value] = label
        normalized[label] = vals
    missing = universe - set(seen)
    if missing:
        if not residual:
            fail("INCOMPLETE_PARTITION", f"uncovered members: {sorted(missing)}", axis)
        residual_values = set(residual.get("members", ()))
        if residual_values != missing:
            fail("INVALID_RESIDUAL", "residual must identify exactly uncovered members", axis)
        if not residual.get("known", False):
            fail("UNKNOWN_RESIDUAL", "unknown residual cannot yield an exact total", axis)
    if residual and not missing and residual.get("members"):
        fail("INVALID_RESIDUAL", "complete population cannot have additional residual members")
    if residual and len(residual.get("members", ())) != len(set(residual.get("members", ()))):
        fail("DUPLICATE_MEMBER", "residual members repeated")
    if residual and set(residual.get("members", ())) & set(seen):
        fail("OVERLAPPING_PARTITION", "residual overlaps a named member", axis)
    return {"status": "partitioned", "axis": axis, "population": pop, "members": normalized,
            "residual": dict(residual) if residual else None, "covered": len(universe), "complete": True}


def map_components(source: Context, target: Context, rule: MappingRule, *,
                   population: Sequence[str], members: Mapping[str, Sequence[str]],
                   values: Mapping[str, Any], axis: str, at: str) -> dict[str, Any]:
    """Finite exact sum/reclassification; each atomic value occurs once."""
    if rule.kind not in {"component", "reclassification"}:
        fail("UNSUPPORTED_MAPPING", "finite component rule required")
    witness = compatible_context(source, target, [MappingRule(
        rule.source_concept, rule.target_concept, source_context=rule.source_context,
        target_context=rule.target_context, effective_start=rule.effective_start,
        effective_end=rule.effective_end, provenance=rule.provenance)], at=at)
    partition = check_partition(population, members, axis=axis)
    if set(values) != set(population):
        fail("INCOMPLETE_COMPONENT_VALUES", "one value per population member required")
    amounts = {k: _fraction(v) for k, v in values.items()}
    return {"kind": rule.kind, "mapping": witness, "partition": partition,
            "amount": sum(amounts.values(), Fraction()),
            "components": {k: sum((amounts[i] for i in ids), Fraction()) for k, ids in members.items()}}


def combine_partitions(partitions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Only disjoint populations may be added, even across different axes."""
    seen = set()
    for p in partitions:
        check_partition(p["population"], p["members"], residual=p.get("residual"), axis=p["axis"])
        if seen.intersection(p["population"]):
            fail("OVERLAPPING_CLASSIFICATIONS", "alternative classifications count the same population")
        seen.update(p["population"])
    return {"population": sorted(seen), "complete": True}


def _availability(value: Any, *, timezone_name: str | None, date_only_policy: str | None, where: str) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            fail("MISSING_TIMEZONE", "timestamp requires timezone", where)
        return value
    if isinstance(value, date):
        value = value.isoformat()
    if not isinstance(value, str):
        fail("INVALID_AVAILABILITY", "availability must be date or timestamp", where)
    if "T" in value or " " in value:
        return _instant(value, where)
    d = _iso_date(value, where)
    if date_only_policy != "next_local_midnight":
        fail("DATE_ONLY_POLICY_REQUIRED", "date-only availability requires next_local_midnight", where)
    if not timezone_name:
        fail("TIMEZONE_REQUIRED", "named timezone required for date-only availability", where)
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        fail("UNKNOWN_TIMEZONE", timezone_name, where)
    return datetime.combine(d + timedelta(days=1), time.min, zone)


def _validate_assertions(assertions: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    if any(not isinstance(a.get("id"), str) or not a["id"] for a in assertions):
        fail("INVALID_ASSERTION_ID", "nonempty assertion IDs required")
    rows = {a["id"]: a for a in assertions}
    if len(rows) != len(assertions):
        fail("DUPLICATE_ASSERTION", "assertion identifiers must be unique", "assertions")
    for row in assertions:
        if not row.get("source"):
            fail("MISSING_SOURCE", "assertion source is required", str(row.get("id")))
        for parent in row.get("supersedes", []):
            if parent not in rows:
                fail("DANGLING_SUPERSESSION", f"unknown superseded assertion {parent}", str(row.get("id")))
            for key in ("concept", "period", "context", "lineage"):
                if row.get(key) != rows[parent].get(key):
                    fail("SUPERSESSION_SCOPE_MISMATCH", key, row["id"])
            if parent == row["id"]:
                fail("SUPERSESSION_CYCLE", "assertion cannot supersede itself", str(row["id"]))
    state: dict[str, int] = {}
    def visit(key: str) -> None:
        state[key] = 1
        for parent in rows[key].get("supersedes", []):
            if state.get(parent) == 1:
                fail("SUPERSESSION_CYCLE", "supersession graph contains a cycle", key)
            if state.get(parent) != 2:
                visit(parent)
        state[key] = 2
    for key in rows:
        if state.get(key, 0) == 0:
            visit(key)
    return rows


def select_evidence(assertions: Sequence[Mapping[str, Any]], cutoff: str | datetime | date, *,
                    mode: str = "latest_available", system_as_of: str | datetime | date | None = None,
                    timezone_name: str | None = None, date_only_policy: str | None = None,
                    harmonisations: Sequence[Mapping[str, Any]] = (), require_known_bytes: bool = False) -> dict[str, Any]:
    rows = _validate_assertions(assertions)
    if mode not in {"original", "latest_available", "harmonised"}:
        fail("UNSUPPORTED_EVIDENCE_VIEW", mode, "mode")
    if isinstance(cutoff, datetime):
        cut = cutoff if cutoff.tzinfo else fail("MISSING_TIMEZONE", "cutoff requires timezone", "cutoff")
    else:
        cut = _availability(cutoff, timezone_name=timezone_name, date_only_policy=date_only_policy, where="cutoff")
    asof = None
    if system_as_of is not None:
        asof = _availability(system_as_of, timezone_name=timezone_name, date_only_policy=date_only_policy, where="system_as_of")
    eligible = []
    unresolved = []
    for row in assertions:
        if row.get("available") in (None, "unknown", "not_established"):
            unresolved.append({"id": row["id"], "reason": "source_availability_unestablished"})
            continue
        try:
            available = _availability(row["available"], timezone_name=timezone_name, date_only_policy=date_only_policy, where=f"{row['id']}.available")
            ingested = _availability(row.get("ingested", row["available"]), timezone_name=timezone_name, date_only_policy=date_only_policy, where=f"{row['id']}.ingested")
        except P06Error:
            raise
        known_bytes = row.get("historical_byte_vintage") == "established"
        if available <= cut and (asof is None or ingested <= asof) and (not require_known_bytes or known_bytes):
            eligible.append(row)
        if not known_bytes:
            unresolved.append({"id": row["id"], "reason": "historical_byte_vintage_unestablished"})
    eligible_ids = {x["id"] for x in eligible}
    if mode == "original":
        # Original means the root assertion in each declared lineage.  A later
        # eligible revision must not erase that root from the historical view;
        # it is the latest view that removes superseded ancestors.
        selected = [x for x in eligible if not x.get("supersedes")]
    else:
        superseded = set()
        def ancestors(key):
            for parent in rows[key].get("supersedes", []):
                if parent not in superseded:
                    superseded.add(parent)
                    ancestors(parent)
        for x in eligible:
            ancestors(x["id"])
        selected = [x for x in eligible if x["id"] not in superseded]
    transformations = []
    derived = []
    if mode == "harmonised":
        targets = set(rows)
        for h in harmonisations:
            source = h.get("source_id")
            original = next((x for x in selected if x["id"] == source), None)
            if original is None:
                fail("HARMONISATION_SOURCE_UNAVAILABLE", str(source))
            if h.get("review_decision") != "Accept" or not h.get("provenance"):
                fail("HARMONISATION_NOT_REVIEWED", "accepted review and provenance required")
            if h.get("changes_basis") or h.get("changes_measurement"):
                fail("HARMONISATION_CONTEXT_CHANGE", "basis/measurement changes unsupported")
            if h.get("operation", "identity") != "identity":
                fail("UNSUPPORTED_HARMONISATION", "only reviewed identity is implemented")
            target = h.get("target_id")
            if not target or target in targets:
                fail("DUPLICATE_ASSERTION", "new harmonised ID required")
            targets.add(target)
            new = deepcopy(original)
            new.update(id=target, dependencies=[source], transformation=deepcopy(h))
            derived.append(new)
            transformations.append(deepcopy(h))
    return {"mode": mode, "cutoff": str(cutoff), "selected": deepcopy(selected),
            "selected_ids": [x["id"] for x in selected], "eligible_ids": sorted(eligible_ids),
            "unresolved": unresolved, "transformations": transformations, "derived": derived}


def _row_context(row: Mapping[str, Any]) -> str:
    return json.dumps(row.get("context", {}), sort_keys=True, separators=(",", ":"))


def subtract_cumulative(total: Mapping[str, Any], earlier: Mapping[str, Any], *,
                        revision_compatibility: Mapping[str, Any] | None = None) -> dict[str, Any]:
    for label, row in (("total", total), ("earlier", earlier)):
        if row.get("kind") != "cumulative":
            fail("YTD_REQUIRES_CUMULATIVE", f"{label} must be cumulative", label)
        if row.get("period", {}).get("end") is None:
            fail("INVALID_PERIOD", "cumulative period requires exclusive end", label)
    if total.get("concept") != earlier.get("concept"):
        fail("CONCEPT_MISMATCH", "flow concepts differ", "ytd")
    if _row_context(total) != _row_context(earlier):
        fail("CONTEXT_MISMATCH", "cumulative contexts differ", "ytd")
    if total.get("calendar") != earlier.get("calendar") or total.get("calendar") != "gregorian":
        fail("CALENDAR_MISMATCH", "calendars differ", "ytd")
    tp, ep = total["period"], earlier["period"]
    if tp.get("start") != ep.get("start"):
        fail("PERIOD_START_MISMATCH", "cumulative periods must share a start", "ytd")
    tend, eend = _iso_date(tp["end"], "total.period.end"), _iso_date(ep["end"], "earlier.period.end")
    if eend >= tend:
        fail("NONNESTED_PERIOD", "earlier period must end before total", "ytd")
    tstart = _iso_date(tp["start"], "total.period.start")
    if _iso_date(ep["start"], "earlier.period.start") != tstart:
        fail("PERIOD_START_MISMATCH", "period starts differ", "ytd")
    if not tstart < eend:
        fail("INVALID_PERIOD", "cumulative intervals must have positive length")
    tr = total.get("revision_id"); er = earlier.get("revision_id")
    if revision_compatibility is not None:
        expected = {"total_id": total.get("id"), "earlier_id": earlier.get("id"),
                    "total_revision": tr, "earlier_revision": er,
                    "concept": total.get("concept"), "context": total.get("context"),
                    "total_period": tp, "earlier_period": ep}
        if revision_compatibility.get("scope") != expected or not revision_compatibility.get("evidence") or revision_compatibility.get("accepted") is not True:
            fail("REVISION_COMPATIBILITY_SCOPE", "exception must match exact observations, revisions, context and periods")
    if not tr or not er:
        allowed = revision_compatibility and revision_compatibility.get("accepted")
        if not allowed or not revision_compatibility.get("scope") or not revision_compatibility.get("evidence"):
            fail("REVISION_UNKNOWN", "subtraction requires explicit revision identities or a reviewed scoped exception", "ytd")
    if tr != er:
        allowed = revision_compatibility and revision_compatibility.get("accepted")
        if not allowed or not revision_compatibility.get("scope") or not revision_compatibility.get("evidence"):
            fail("REVISION_INCOMPATIBLE", "subtraction requires a common revision or reviewed scoped exception", "ytd")
    amount = _fraction(total["amount"], "total.amount") - _fraction(earlier["amount"], "earlier.amount")
    return {"kind": "flow", "amount": amount, "period": {"start": ep["end"], "end": tp["end"]},
            "concept": total["concept"], "context": deepcopy(total.get("context")), "calendar": total["calendar"],
            "provenance": {"operation": "cumulative_subtraction", "total_id": total.get("id"), "earlier_id": earlier.get("id"),
                           "revision_id": tr or er}}


_SUPPORTED_MEASUREMENT_METHODS = {"direct", "discounted_cash_flow", "observable_input"}
_SUPPORTED_MEASURES = {"real_world", "pricing"}


def _validate_joint_law(law: Any, where: str) -> list[dict[str, Any]]:
    if not isinstance(law, Mapping):
        fail("INVALID_JOINT_LAW", "joint law must be an object with finite atoms", where)
    atoms = law.get("atoms")
    if not isinstance(atoms, list) or not atoms:
        fail("INVALID_JOINT_LAW", "finite joint law needs atoms", where)
    ids = [a.get("id") for a in atoms]
    if any(not isinstance(x, str) for x in ids) or len(ids) != len(set(ids)):
        fail("INVALID_JOINT_LAW", "atom IDs must be distinct", where)
    hypotheses = [a.get("hypothesis") for a in atoms]
    if any(not isinstance(h, Mapping) or not h or any(isinstance(v, (Mapping, list, tuple)) for v in h.values()) for h in hypotheses):
        fail("INVALID_JOINT_LAW", "complete scalar hypotheses are required", where)
    if len({json.dumps(h, sort_keys=True) for h in hypotheses}) != len(hypotheses):
        fail("INVALID_JOINT_LAW", "joint hypotheses overlap", where)
    if any(set(h) != set(hypotheses[0]) for h in hypotheses):
        fail("INVALID_JOINT_LAW", "all atoms must assign the same variables", where)
    weights = [_fraction(a.get("weight"), where) for a in atoms]
    if any(w < 0 for w in weights) or sum(weights, Fraction()) != 1:
        fail("INVALID_JOINT_LAW", "weights must be nonnegative and sum to one", where)
    return [dict(a) for a in atoms]


def admit_uncertainty(record: Mapping[str, Any], *, known_records: Mapping[str, Mapping[str, Any]] | None = None,
                      available_information: Iterable[str] = ()) -> dict[str, Any]:
    kind = record.get("kind")
    fields = {
        "ExtractionReading": ("source", "locator", "review_decision"),
        "HistoricalFact": ("evidence", "reason"),
        "AccountingElection": ("package", "permitted_treatments", "election", "effective_date", "eligibility_evidence"),
        "MeasurementEstimate": ("method", "measurement_date", "inputs"),
        "BehaviourPolicy": ("policy", "information_set", "decision_time"),
        "FutureInnovation": ("driver", "future_period", "scenario", "joint_law", "measure"),
    }
    if kind not in fields:
        fail("UNKNOWN_UNCERTAINTY_CATEGORY", f"unsupported category {kind!r}", "kind")
    structured_fields = {"joint_law", "future_period", "inputs", "information_set", "permitted_treatments"}
    for key in ("id", "scope", "provenance", "dependencies") + fields[kind]:
        if key not in record or (key != "dependencies" and key not in structured_fields and not record[key]):
            fail("MISSING_ADMISSION_FIELD", f"missing admission field {key}", str(record.get("id", "")))
    if not isinstance(record["provenance"], list) or not isinstance(record["dependencies"], list):
        fail("INVALID_ADMISSION_LIST", "provenance and dependencies must be lists", str(record["id"]))
    known_records = known_records or {}
    for dep in record["dependencies"]:
        if dep not in known_records:
            fail("DANGLING_DEPENDENCY", f"unknown dependency {dep}", str(record["id"]))
    graph = {key: list(value.get("dependencies", ())) for key, value in known_records.items()}
    graph[str(record["id"])] = list(record["dependencies"])
    state: dict[str, int] = {}
    def visit(node: str) -> None:
        state[node] = 1
        for dep in graph.get(node, ()):
            if dep not in graph:
                fail("DANGLING_DEPENDENCY", dep, node)
            if state.get(dep) == 1:
                fail("CYCLIC_DEPENDENCY", "uncertainty dependencies contain a cycle", str(record["id"]))
            if state.get(dep) != 2:
                visit(dep)
        state[node] = 2
    for node in graph:
        if state.get(node, 0) == 0:
            visit(node)
    def resolve(identifier, expected_kind=None):
        row = known_records.get(identifier)
        if row is None:
            fail("UNRESOLVED_ADMISSION_REFERENCE", str(identifier), record["id"])
        if expected_kind and row.get("kind") != expected_kind:
            fail("ADMISSION_REFERENCE_KIND", str(identifier), record["id"])
        return row

    def evidence(identifier):
        row = resolve(identifier)
        if row.get("review_decision") != "Accept":
            fail("EVIDENCE_NOT_ACCEPTED", str(identifier))
        return row

    if kind == "ExtractionReading":
        if record["review_decision"] != "Accept":
            fail("READING_NOT_ACCEPTED", "reading requires accepted review")
        source = resolve(record["source"], "Source")
        if record["locator"] not in source.get("locators", ()):
            fail("UNRESOLVED_LOCATOR", record["locator"])
    elif kind == "HistoricalFact":
        for ref in record["evidence"] if isinstance(record["evidence"], list) else [record["evidence"]]:
            evidence(ref)
        domain = record.get("domain")
        constraints = record.get("evidence_constraints")
        if not isinstance(domain, list) or not domain or not isinstance(constraints, list) or not constraints:
            fail("HISTORICAL_DOMAIN_REQUIRED", "finite domain and evidence constraints required")
        values = [_fraction(x) for x in domain]
        if len(set(values)) != len(values):
            fail("INVALID_HISTORICAL_DOMAIN", "domain values must be distinct")
        for c in constraints:
            if not isinstance(c, Mapping) or not c.get("evidence"):
                fail("HISTORICAL_CONSTRAINT_INVALID", "each constraint needs an evidence reference")
            evidence(c.get("evidence"))
            lo, hi = _fraction(c.get("lower")), _fraction(c.get("upper"))
            if lo > hi or any(not lo <= x <= hi for x in values):
                fail("HISTORICAL_CONSTRAINT_VIOLATION", "domain violates retained evidence constraint")
    elif kind == "AccountingElection":
        if not isinstance(record["permitted_treatments"], list) or not all(isinstance(x, str) and x for x in record["permitted_treatments"]):
            fail("INVALID_TREATMENT_LIST", "permitted treatments must be a nonempty string list")
        if record["election"] not in record["permitted_treatments"]:
            fail("TREATMENT_NOT_PERMITTED", "election is outside declared permissions")
        package = resolve(record["package"], "AccountingPackage")
        when = _iso_date(record["effective_date"], "election.date")
        if not (_iso_date(package["start"], "package.start") <= when < _iso_date(package["end"], "package.end")):
            fail("PACKAGE_NOT_EFFECTIVE", "election outside package dates")
        if package.get("scope") != record["scope"] or package.get("review_decision") != "Accept":
            fail("PACKAGE_SCOPE_MISMATCH", "reviewed package must match scope")
        if set(record["permitted_treatments"]) != set(package.get("permitted_treatments", ())) or record["election"] not in package.get("permitted_treatments", ()):
            fail("TREATMENT_NOT_PERMITTED", "permission is not supplied by referenced package")
        eligibility = evidence(record["eligibility_evidence"])
        if eligibility.get("package") != record["package"] or eligibility.get("scope") != record["scope"] or record["election"] not in eligibility.get("eligible_treatments", ()):
            fail("ELECTION_INELIGIBLE", "eligibility does not support this treatment/scope")
    elif kind == "MeasurementEstimate":
        if record["method"] not in _SUPPORTED_MEASUREMENT_METHODS:
            fail("UNSUPPORTED_ESTIMATION_METHOD", record["method"])
        if not isinstance(record["inputs"], Mapping) or any(v is None for v in record["inputs"].values()):
            fail("MISSING_ESTIMATE_INPUT", "measurement inputs must resolve")
        when = _iso_date(record["measurement_date"], "measurement.date")
        inputs = {}
        for name, identifier in record["inputs"].items():
            inp = evidence(identifier)
            if _iso_date(inp["available_date"], "input.available_date") > when:
                fail("ESTIMATE_INPUT_UNAVAILABLE", identifier)
            inputs[name] = _fraction(inp["value"])
        required = {"direct": {"value"}, "observable_input": {"value"}, "discounted_cash_flow": {"cash_flow", "rate", "years"}}[record["method"]]
        if set(inputs) != required:
            fail("MISSING_ESTIMATE_INPUT", "wrong method inputs")
        if record["method"] == "discounted_cash_flow":
            if inputs["rate"] <= -1 or inputs["years"] < 0 or inputs["years"].denominator != 1:
                fail("UNSUPPORTED_ESTIMATE_DOMAIN", "DCF requires integer nonnegative years and rate > -1")
            value = inputs["cash_flow"] / (1 + inputs["rate"]) ** int(inputs["years"])
        else:
            value = inputs["value"]
        record = dict(record, admitted_value=value)
    elif kind == "BehaviourPolicy":
        if record["policy"] != "hold":
            fail("UNSUPPORTED_BEHAVIOUR_POLICY", "bounded hold policy only")
        if not isinstance(record["information_set"], list):
            fail("INVALID_INFORMATION_SET", "information_set must be a list")
        when = _iso_date(record["decision_time"], "policy.decision_time")
        for identifier in record["information_set"]:
            inp = resolve(identifier, "Information")
            if identifier not in available_information or _iso_date(inp["available_date"], "information.date") > when or inp.get("information_kind") == "future_realised":
                fail("FUTURE_INFORMATION_LEAKAGE", identifier)
            if _iso_date(inp["event_date"], "information.event_date") > when and inp.get("information_kind") != "announced_stress":
                fail("FUTURE_INFORMATION_LEAKAGE", identifier)
    elif kind == "FutureInnovation":
        if not isinstance(record["joint_law"], Mapping):
            fail("INVALID_JOINT_LAW", "joint law must be an object with finite atoms", str(record["id"]))
        if record["measure"] not in _SUPPORTED_MEASURES:
            fail("INCOMPATIBLE_PROBABILITY_MEASURE", "real_world or pricing required")
        _validate_joint_law(record["joint_law"], str(record["id"]))
        if record["joint_law"].get("measure") != record["measure"]:
            fail("INCOMPATIBLE_PROBABILITY_MEASURE", "law measure differs from innovation measure")
        if record["scenario"] not in {"base", "announced_stress"}:
            fail("UNSUPPORTED_SCENARIO", record["scenario"])
        period = record["future_period"]
        if not isinstance(period, Mapping):
            fail("INVALID_FUTURE_PERIOD", "explicit half-open period required")
        if not (_iso_date(record.get("decision_time"), "innovation.decision_time") < _iso_date(period.get("start"), "innovation.start") < _iso_date(period.get("end"), "innovation.end")):
            fail("INVALID_FUTURE_PERIOD", "innovation must follow decision time")
        if any(record["driver"] not in a["hypothesis"] for a in record["joint_law"]["atoms"]):
            fail("INVALID_JOINT_LAW", "driver missing from joint atom")
        for dep in record["dependencies"]:
            if known_records[dep].get("measure", record["measure"]) != record["measure"]:
                fail("INCOMPATIBLE_PROBABILITY_MEASURE", "dependency measure differs")
    return deepcopy(record)


def guard_information_view(view: Mapping[str, Any], *, event_time: str | date, request: str = "exogenous_stress") -> dict[str, Any]:
    if request != "exogenous_stress":
        fail("UNSUPPORTED_INFORMATION_OPERATION", request, "information_view")
    visible = set(view.get("visible", ()))
    announced = set(view.get("future_announced", ()))
    hidden = set(view.get("future_realised", ()))
    if hidden & visible or any(str(x).startswith("future_realised:") for x in visible):
        fail("FUTURE_INFORMATION_LEAKAGE", "future realised outcomes cannot be visible")
    when = _iso_date(event_time, "event_time") if isinstance(event_time, str) else event_time
    records = view.get("records", {})
    for identifier in visible | announced:
        row = records.get(identifier)
        if row is None:
            fail("UNRESOLVED_INFORMATION", identifier)
        if _iso_date(row["available_date"], "information.available_date") > when:
            fail("FUTURE_INFORMATION_LEAKAGE", identifier)
        future = _iso_date(row["event_date"], "information.event_date") > when
        if row.get("information_kind") == "future_realised" or (future and (identifier not in announced or row.get("information_kind") != "announced_stress")):
            fail("FUTURE_INFORMATION_LEAKAGE", identifier)
    if not view.get("measure_id"):
        fail("MISSING_PROBABILITY_MEASURE", "information view needs a measure")
    if view.get("pricing_measure_id") == view["measure_id"]:
        fail("INCOMPATIBLE_PROBABILITY_MEASURE", "pricing and real-world IDs must differ")
    return {"status": "accepted", "event_time": str(event_time), "visible": sorted(visible),
            "future_announced": sorted(announced), "future_realised_hidden": sorted(hidden),
            "measure_id": view["measure_id"], "selection_changes_history": False}


@dataclass(frozen=True)
class DebtConstituent:
    id: str
    principal: Fraction
    rate: Fraction
    maturity: Fraction
    reset: str = "fixed"
    hedge: str = "unhedged"

    def __post_init__(self):
        for key in ("principal", "rate", "maturity"):
            object.__setattr__(self, key, _fraction(getattr(self, key), key))
        if self.principal < 0:
            fail("NEGATIVE_PRINCIPAL", self.id)
        if self.maturity <= 0 or not self.id:
            fail("INVALID_DEBT", "positive maturity and ID required")

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "DebtConstituent":
        principal = _fraction(row.get("principal"), f"{row.get('id')}.principal")
        if principal < 0:
            fail("NEGATIVE_PRINCIPAL", "principal must be nonnegative", str(row.get("id")))
        return cls(str(row["id"]), principal, _fraction(row.get("rate"), f"{row.get('id')}.rate"),
                   _fraction(row.get("maturity"), f"{row.get('id')}.maturity"), str(row.get("reset", "fixed")), str(row.get("hedge", "unhedged")))


def _query_signature(query: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(query, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()


def interest_certificate(constituents: Sequence[DebtConstituent], target_rate: Fraction | str | int,
                         horizon: Fraction | str | int) -> dict[str, Fraction]:
    T = _fraction(horizon, "horizon")
    if T < 0:
        fail("INVALID_HORIZON", "horizon must be nonnegative", "horizon")
    rstar = _fraction(target_rate, "target_rate")
    exact = sum((c.principal * c.rate * T for c in constituents), Fraction())
    approx = sum((c.principal * rstar * T for c in constituents), Fraction())
    bound = T * sum((c.principal * abs(c.rate - rstar) for c in constituents), Fraction())
    difference = abs(exact - approx)
    if difference > bound:
        fail("INVALID_APPROXIMATION_CERTIFICATE", "triangle-inequality bound is violated", "approximation")
    return {"exact": exact, "approximate": approx, "error": difference, "bound": bound}


def resolve_bullet_debt(constituents: Sequence[DebtConstituent | Mapping[str, Any]], query: Mapping[str, Any], *,
                       previous: Mapping[str, Any] | None = None,
                       approximation: Mapping[str, Any] | None = None) -> dict[str, Any]:
    rows = [x if isinstance(x, DebtConstituent) else DebtConstituent.from_dict(x) for x in constituents]
    if not rows:
        fail("EMPTY_DEBT_SET", "at least one constituent is required", "debt")
    required = ("contract", "context", "evidence_view", "horizon", "scenario", "requested_outputs", "accrual_convention", "group_by")
    for key in required:
        if key not in query:
            fail("MISSING_QUERY_FIELD", f"missing {key}", "query")
    if len({c.id for c in rows}) != len(rows):
        fail("DUPLICATE_CONSTITUENT", "debt IDs must be unique")
    signature = _query_signature({"query": query, "constituents": [vars(c) for c in rows]})
    if previous is not None and previous.get("query_signature") != signature:
        fail("STALE_RESULT", "query changed; grouping sufficiency must be revalidated", "query")
    horizon = _fraction(query["horizon"], "query.horizon")
    if horizon < 0:
        fail("INVALID_HORIZON", "horizon must be nonnegative", "query.horizon")
    if query["scenario"] not in {"base", "announced_stress"}:
        fail("UNSUPPORTED_SCENARIO", str(query["scenario"]), "query.scenario")
    if query["accrual_convention"] != "simple_actual_fraction":
        fail("UNSUPPORTED_ACCRUAL", str(query["accrual_convention"]), "query.accrual_convention")
    if not isinstance(query["requested_outputs"], list) or not query["requested_outputs"]:
        fail("MISSING_OUTPUT_REQUEST", "requested_outputs must be nonempty", "query")
    unsupported_outputs = set(query["requested_outputs"]) - {"interest", "principal"}
    if unsupported_outputs:
        fail("UNSUPPORTED_OUTPUT", f"unsupported outputs: {sorted(unsupported_outputs)}", "query.requested_outputs")
    dimensions = ("rate", "maturity", "reset", "hedge")
    group_by = set(query["group_by"])
    if not group_by <= set(dimensions):
        fail("UNSUPPORTED_GROUP_DIMENSION", "group_by contains unsupported dimension", "query.group_by")
    for dim in dimensions:
        values = {getattr(c, dim) for c in rows}
        if len(values) > 1 and dim not in group_by:
            fail("GROUPING_INSUFFICIENT", f"dimension {dim} varies but is not grouped", "query.group_by")
    for c in rows:
        if c.hedge != "unhedged":
            fail("HEDGED_DEBT_UNSUPPORTED", "only unhedged debt is supported", c.id)
        if c.reset != "fixed":
            fail("RESET_UNSUPPORTED", "only fixed reset is supported", c.id)
        if c.maturity <= horizon:
            fail("MATURITY_CROSSING", "maturity crosses the requested horizon", c.id)
    groups: dict[tuple[Any, ...], list[DebtConstituent]] = {}
    for c in rows:
        key = tuple(getattr(c, dim) if dim in group_by else "homogeneous" for dim in dimensions)
        groups.setdefault(key, []).append(c)
    output: dict[str, Any] = {}
    if "interest" in query["requested_outputs"]:
        output["interest"] = sum((c.principal * c.rate * horizon for c in rows), Fraction())
    if "principal" in query["requested_outputs"]:
        output["principal"] = sum((c.principal for c in rows), Fraction())
    result = {"status": "resolved", "query_signature": signature,
              "query": json.loads(json.dumps(query, default=str)), "groups": [
                  {"key": [str(x) for x in key], "constituent_ids": [c.id for c in members],
                   "principal": sum((c.principal for c in members), Fraction()),
                   "interest": sum((c.principal * c.rate * horizon for c in members), Fraction())}
                  for key, members in groups.items()],
              "outputs": output, "constituent_ids": [c.id for c in rows], "constituents": deepcopy(rows), "fresh": True}
    if approximation is not None:
        if not approximation.get("scope") or approximation.get("scope") != "fixed_rate_interest" or not approximation.get("evidence"):
            fail("APPROXIMATION_EVIDENCE_REQUIRED", "declared scope and evidence are required", "approximation")
        if approximation.get("query_signature", signature) != signature:
            fail("STALE_APPROXIMATION", "error evidence is for different query/constituents")
        cert = interest_certificate(rows, approximation.get("target_rate"), horizon)
        tolerance = _fraction(approximation.get("tolerance"), "approximation.tolerance")
        declared = _fraction(approximation.get("error_bound"), "approximation.error_bound")
        if tolerance < 0 or declared < cert["error"] or declared > tolerance or declared < cert["bound"]:
            fail("APPROXIMATION_BOUND_INVALID", "declared bound must cover exact error and certificate within tolerance", "approximation")
        result["approximation"] = {k: str(v) for k, v in cert.items()} | {"tolerance": str(tolerance), "declared_error_bound": str(declared), "query_signature": signature, "evidence": deepcopy(approximation["evidence"])}
    return result


def adapt_core_context(row: Mapping[str, Any], *, perimeter_version: str, gross_net: str,
                       calendar: str, display: Mapping[str, Any] | None = None) -> Context:
    """Core 0 omits perimeter version/gross-net; require explicit supplements."""
    dimensions = row.get("dimensions", [])
    if len({d["axis"] for d in dimensions}) != len(dimensions):
        fail("INVALID_DIMENSIONS", "duplicate Core 0 axis")
    return Context.from_dict({k: row[k] for k in ("concept", "entity", "perimeter", "basis", "measurement", "unit", "currency")} |
                             {"perimeter_version": perimeter_version, "gross_net": gross_net,
                              "calendar": calendar, "dimensions": {d["axis"]: d["member"] for d in dimensions}} | dict(display or {}))


def adapt_p03_reading(binding: Any, context: Context, *, historical_byte_vintage: str = "unknown") -> dict[str, Any]:
    if binding.currency != context.currency:
        fail("CURRENCY_MISMATCH", "reading and context differ")
    return {"id": binding.key, "kind": "instant", "amount": _fraction(binding.amount),
            "concept": context.concept, "context": context.as_dict(), "calendar": context.calendar,
            "period": {"start": binding.instant, "end": None}, "available": binding.available,
            "ingested": binding.ingested, "source": binding.filing_id, "supersedes": [],
            "historical_byte_vintage": historical_byte_vintage, "literal": binding.literal,
            "review": {"reviewer": binding.reviewer, "date": binding.review_date, "reason": binding.review_reason, "action": binding.action},
            "uri": binding.uri, "uncertainty": "ExtractionReading"}


def adapt_p01_source(row: Mapping[str, Any]) -> dict[str, Any]:
    # Filing metadata cannot establish availability of the retained bytes.
    return {"id": row["document_id"], "source": row["document_id"], "supersedes": [],
            "available": "unknown", "historical_byte_vintage": row.get("historical_byte_vintage", "unknown"),
            "publication_metadata": deepcopy(row.get("publication_metadata")),
            "original_path": row["original_path"], "original_sha256": row["original_sha256"]}


@dataclass
class P06Engine:
    contexts: dict[str, Context] = field(default_factory=dict)
    mappings: list[MappingRule] = field(default_factory=list)
    assertions: list[dict[str, Any]] = field(default_factory=list)
    uncertainty: dict[str, dict[str, Any]] = field(default_factory=dict)
    current_results: dict[str, dict[str, Any]] = field(default_factory=dict)
    preserved_results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def add_context(self, identifier: str, context: Context | Mapping[str, Any]) -> None:
        if identifier in self.contexts:
            fail("DUPLICATE_CONTEXT", identifier)
        self.contexts[identifier] = context if isinstance(context, Context) else Context.from_dict(context)

    def add_mapping(self, rule: MappingRule | Mapping[str, Any]) -> None:
        rules = self.mappings + [rule if isinstance(rule, MappingRule) else MappingRule.from_dict(rule)]
        _check_mapping_graph(rules)
        self.mappings = rules
        self.current_results.clear()

    def add_assertion(self, row: Mapping[str, Any]) -> None:
        rows = self.assertions + [deepcopy(row)]
        _validate_assertions(rows)
        self.assertions = rows
        self.current_results.clear()

    def revise(self, assertion_id: str, replacement: Mapping[str, Any]) -> None:
        rows = {x["id"]: x for x in self.assertions}
        if assertion_id not in rows:
            fail("UNKNOWN_ASSERTION", assertion_id)
        replacement = deepcopy(replacement)
        replacement.setdefault("supersedes", [assertion_id])
        if replacement.get("id") in rows or assertion_id not in replacement["supersedes"]:
            fail("INVALID_REVISION", "revision needs new ID and explicit supersession")
        candidate = self.assertions + [replacement]
        _validate_assertions(candidate)
        self.assertions = candidate
        for key in list(self.current_results):
            if assertion_id in self.current_results[key]["dependencies"]:
                del self.current_results[key]

    def preserve_result(self, result_id: str = "current") -> dict[str, Any]:
        if result_id not in self.current_results:
            fail("UNKNOWN_RESULT", result_id)
        self.preserved_results[result_id] = deepcopy(self.current_results[result_id])
        return deepcopy(self.preserved_results[result_id])

    def evaluate(self, request: Mapping[str, Any]) -> dict[str, Any]:
        evidence = select_evidence(self.assertions, request["cutoff"], mode=request.get("evidence_view", "latest_available"),
                                   system_as_of=request.get("system_as_of"), timezone_name=request.get("timezone"),
                                   date_only_policy=request.get("date_only_policy"), harmonisations=request.get("harmonisations", ()),
                                   require_known_bytes=request.get("require_known_bytes", True))
        for key in ("source_context", "target_context"):
            if request[key] not in self.contexts:
                fail("UNKNOWN_CONTEXT", request[key])
        mapping = compatible_context(self.contexts[request["source_context"]], self.contexts[request["target_context"]], self.mappings, at=request.get("as_of"))
        rows = {x["id"]: x for x in self.assertions}
        def descends(row, identifier):
            return row["id"] == identifier or any(descends(rows[p], identifier) for p in row.get("supersedes", ()))
        def choose(identifier):
            options = [x for x in evidence["selected"] if descends(x, identifier)]
            if len(options) != 1:
                fail("EVIDENCE_UNAVAILABLE_OR_CONFLICTING", identifier)
            return options[0]
        derived = None
        if request.get("derive"):
            d = request["derive"]
            total, earlier = choose(d["total"]), choose(d["earlier"])
            for row in (total, earlier):
                compatible_context(row["context"], self.contexts[request["source_context"]])
            derived = subtract_cumulative(total, earlier, revision_compatibility=d.get("revision_compatibility"))
            derived["mapped_concept"] = mapping["target"]["concept"]
        registry = deepcopy(self.uncertainty)
        for key, value in request.get("registry", {}).items():
            if key in registry and registry[key] != value:
                fail("DUPLICATE_ADMISSION_ID", key)
            registry[key] = deepcopy(value)
        information = None
        if request.get("information_view"):
            information = guard_information_view(request["information_view"], event_time=request["decision_time"], request=request.get("scenario_mode", "exogenous_stress"))
        elif request.get("scenario_mode", "exogenous_stress") != "exogenous_stress":
            fail("UNSUPPORTED_INFORMATION_OPERATION", request["scenario_mode"])
        admitted = []
        for row in request.get("uncertainty", ()):
            value = admit_uncertainty(row, known_records=registry, available_information=information["visible"] if information else ())
            if row["id"] in registry and registry[row["id"]] != value:
                fail("DUPLICATE_ADMISSION_ID", row["id"])
            admitted.append(value)
            registry[row["id"]] = value
        constituents = deepcopy(request["constituents"])
        for row in constituents:
            if "principal_from" in row:
                ref = row.pop("principal_from")
                if ref == "derived":
                    if derived is None:
                        fail("MISSING_DERIVATION", "principal references derived period")
                    row["principal"] = derived["amount"]
                else:
                    row["principal"] = choose(ref)["amount"]
        query = deepcopy(request["query"])
        if query["evidence_view"] != evidence["mode"] or query["context"] != request["target_context"]:
            fail("QUERY_CONTEXT_MISMATCH", "query must match selected view and mapped context")
        if query["scenario"] == "announced_stress" and information is None:
            fail("MISSING_INFORMATION_VIEW", "announced stress requires dated information")
        query["evidence_digest"] = _query_signature(evidence)
        resolution = resolve_bullet_debt(constituents, query, approximation=request.get("approximation"))
        result = {"evidence": evidence, "mapping": mapping, "derived": derived, "uncertainty": admitted,
                  "information": information, "resolution": resolution, "dependencies": list(rows),
                  "input_sha256": _query_signature({"request": request, "assertions": self.assertions, "contexts": {k:v.as_dict() for k,v in self.contexts.items()}, "registry": registry})}
        self.uncertainty = registry
        self.current_results[request.get("result_id", "current")] = deepcopy(result)
        return result


__all__ = ["P06Error", "Context", "MappingRule", "compatible_context", "map_context", "map_components", "combine_partitions",
           "select_evidence", "subtract_cumulative", "admit_uncertainty", "guard_information_view",
           "DebtConstituent", "interest_certificate", "resolve_bullet_debt", "P06Engine",
           "adapt_core_context", "adapt_p03_reading", "adapt_p01_source"]
