# Pre-implementation skeptical audit — 25 October 2026

The comparator is the complete frozen annual inventory evaluator; a projected
25-account book would answer a different question. The implementation is an
explicit new profile, with a local parser and unchanged legacy validators. The
copied parser has no execution hooks; pure compilation is checked with evaluator
calls forbidden. Existing immutable profiles continue rejecting optional sales.

The event profile is a structural requirement. A supported record can still
contain unknown/false findings, excessive quantity or an unsupported method;
those remain semantic decisions. Canonical rational/calendar validation is
structural. No default findings are supplied. The only parser extension is an
explicit field schema for partial_inventory_sale, with all six findings required.
Root and boundary digests remain exact. Counts and round trips alone cannot
establish financial equality; full results and retained failures are compared.
No material unexamined default remains for this bounded engineering increment.
General language, accounting and scientific conclusions remain unestablished.

The first smoke exposed a schema mismatch: inventory provenance is a string,
whereas tax declarations use structured provenance. The failed implementation is
preserved in attempt-01. The optional validator now follows the inventory schema
exactly; old operations retain their tax validators. Fifteen focused and 26
regression methods pass after this repair. The failure rejected the candidate
implementation, not the authoring direction.
