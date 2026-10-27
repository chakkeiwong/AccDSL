# Saved audit serialization repair

The first lease audit's mathematical checks passed, but finish stopped before
any active-control edit because saved replay compared live tuple refusal pairs
with their JSON list representation. A localized diagnostic found the first
mismatch at /probes/6/actual and confirmed json.loads(json.dumps(live)) equals
the saved audit. No amount, status or scientific conclusion changed.

Preserve the original package unchanged. This r2 successor explicitly encodes
tuples as lists and asserts a full JSON round-trip before any recording. It
protects every original package file in addition to the source inputs. Saved
replay remains required before controls advance. This is an audit serialization
repair, not evidence against the original lease arithmetic or simulator direction.
