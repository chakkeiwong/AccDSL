# Guard successor audit

Initial row requirements included declarations used only by collection identity
and reference rules. The native guarded manifest correctly refused unused
inputs. Remove only those unused row-manifest declarations; retain the fields
in the collection and their native uniqueness/reference checks.

The first successful deterministic run preserved all 22 commands and rejected
all sixteen counterexamples. A final code inspection found that generic exception
handling would label unsupported/unresolved invariant findings invalid. Preserve
the evaluator's status in both opening and after-state refusal paths; explicitly
test missing capability and a declared unsupported false consequence. Also validate
seen-event declaration types when the event list is empty.

These are reference implementation repairs, not changes to the frozen native
engines or prior results. Existing source locks remain intact.

A deliberately false known predicate cannot declare an unresolved consequence
in the retained grammar; it permits invalid or unsupported. The initial status
test incorrectly requested unresolved and was correctly refused. Use unsupported
for the known-false post-state test. Unknown/partial input tests exercise the
actual unresolved path directly in the unchanged collection evaluator.
