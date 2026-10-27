# Carry verifier serialization repair

26 October 2026. Attempt-01 is preserved and is not a successful run.

The verifier tried to hash a Python set when checking which method component
changed during the explicit schema extension. The project's canonical JSON
digest correctly rejects sets. The run stopped before its first financial
transition. This is a harness serialization error, not an economic or carry
failure. Attempt-02 compares sorted JSON lists instead. The selected carry
implementation, economic expectations and frozen predecessors are unchanged.
