# Resource control and empty-map validation repair

The first verification run completed the retained/new request and transition
comparisons, then an intended operation-count control hit the earlier record
structure limit. The control now uses compact nodes to isolate operation-count
refusal. No limit was relaxed. During review, empty maps exposed a broader
obligation: row expressions were type-checked but an invalid operation shape or
destination could otherwise disappear because there were no emitted rows.
The expander now validates each declared operation shape, literal replace kind,
map/key/field path and target value type before iteration, including empty maps.
Two explicit empty-map controls retain that repair.
