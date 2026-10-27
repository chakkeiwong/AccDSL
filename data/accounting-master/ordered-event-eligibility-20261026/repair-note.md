# Author audit repair after first passing verification

The first run passed 38 complete events, 34 refusals, 51 controls and 612
assertions. Its results remain under attempt-01. A subsequent identity audit
found that canonical JSON hashes ignore input-map iteration order, whereas the
native unresolved result preserves unknown-input order. The original call bound
the event content but not that order. The implementation now binds a separate
input-order digest, preserving native order rather than sorting the output.
The new control reverses two unknown inputs while retaining the canonical event
hash: the order digest must change, the native names must retain their order,
and reuse of the original call must refuse. This changes no accounting rule.
