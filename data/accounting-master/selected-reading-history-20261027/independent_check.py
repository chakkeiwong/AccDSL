"""Exact checks for the retained two-event, no-memory history candidates.

No production imports. Unsupported history constructs are refused explicitly.
"""
from fractions import Fraction as Q
import json


def interval(value, domain):
    row = domain["interval"] if "interval" in domain else domain
    assert row is not None, "missing interval"
    if row["lower"] is not None:
        assert value >= Q(row["lower"]) if row["lower_inclusive"] else value > Q(row["lower"])
    if row["upper"] is not None:
        assert value <= Q(row["upper"]) if row["upper_inclusive"] else value < Q(row["upper"])


def check(definition, witness, replay):
    h = definition["history"]
    assert h["memory"] == {} and h["state_constraints"] == [], "independent checker scope"
    history, measurements = {}, {}
    for name, value in witness.items():
        category, identifier = json.loads(name)
        if category == "history":
            kind, item = json.loads(identifier)
            assert (kind, item) not in history
            history[kind, item] = Q(value)
        else:
            assert category == "measurement" and identifier not in measurements
            measurements[identifier] = Q(value)
    expected = {("opening_account", name) for name in h["accounts"]}
    expected |= {("event_amount", row["id"]) for row in h["events"]}
    assert set(history) == expected, "complete independent history witness"
    assert set(measurements) == set(definition["measurements"]["observations"])
    balances = {name: history["opening_account", name] for name in h["accounts"]}
    for name, value in balances.items():
        interval(value, h["accounts"][name])
    assert sum(balances.values()) == 0, "opening balance"
    effects = []
    for event in h["events"]:
        amount = history["event_amount", event["id"]]
        interval(amount, event["amount"])
        template = h["templates"][event["template"]]
        assert template["memory"] == {}, "independent no-memory scope"
        postings = {name: Q(coefficient["value"]) * amount
                    for name, coefficient in template["postings"].items()}
        assert sum(postings.values()) == 0, "event journal balance"
        effects.append((event["date"], postings))
    snapshots = {}
    for day in [h["opening_date"], *h["dates"]]:
        current = dict(balances)
        for when, postings in effects:
            if when <= day:
                for name, amount in postings.items():
                    current[name] += amount
        assert sum(current.values()) == 0
        snapshots[day] = current
        actual = replay["history"]["snapshots"][day]
        assert {k: Q(v) for k, v in actual["accounts"].items()} == current
        assert actual["memory"] == {}
    for measurement in h["measurements"]:
        total = Q(0)
        for term in measurement["terms"]:
            assert term["kind"] == "account"
            total += Q(term["coefficient"]["value"]) * snapshots[measurement["date"]][term["field"]]
        interval(total, measurement["domain"])
    for name, item in definition["measurements"]["observations"].items():
        interval(measurements[name], item["interval"])
    for relation in definition["measurements"]["relations"]:
        if relation["kind"] == "same_time":
            lhs = sum((Q(t["coefficient"]) * measurements[t["observation"]] for t in relation["terms"]), Q(0))
            rhs = Q(relation["rhs"])
        else:
            assert relation["kind"] == "stock_flow"
            lhs = measurements[relation["opening"]] + sum((Q(t["coefficient"]) * measurements[t["observation"]] for t in relation["movements"]), Q(0))
            rhs = measurements[relation["closing"]]
        assert lhs == rhs, "source relation " + relation["id"]
    for name, binding in definition["bindings"].items():
        when = definition["measurements"]["observations"][name]["type"]["time"]
        total = Q(0)
        for term in binding["terms"]:
            assert term["kind"] == "account"
            if binding["kind"] == "snapshot":
                value = snapshots[when["at"]][term["field"]]
            else:
                assert binding["kind"] == "movement"
                value = sum((postings.get(term["field"], Q(0)) for day, postings in effects
                             if when["start"] <= day < when["end_exclusive"]), Q(0))
            total += Q(term["coefficient"]["value"]) * value
        assert total == measurements[name], "history mapping " + name
    return {"accounts": len(balances), "events": len(effects), "snapshots": len(snapshots),
            "observations": len(measurements), "source_relations": len(definition["measurements"]["relations"]),
            "history_mappings": len(definition["bindings"]), "measurements": len(h["measurements"])}
