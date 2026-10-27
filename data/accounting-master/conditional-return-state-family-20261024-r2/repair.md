# Serialized result repair

The first recorded candidate passed in-memory checks but its saved fixed-settlement
result failed semantic replay. Native input paths were Python tuples; JSON reload
converted them to lists. Exact native outputs and canonical result bytes agreed,
but direct result comparisons rejected the serialized structure. This is a real
engineering serialization defect, not a funding/mathematical counterexample.

Preserve the original package and v1 code/tests. The separate v2 implementation
emits lists for method_input_paths and adds full JSON request/result round-trip
checks on known and variable settlement/sale cases. Both use the same public
profile semantics; this is an implementation repair. The successor must pass
saved-file semantic replay before any active control is advanced. No new solver,
source, accounting assumption or numerical target changes.
