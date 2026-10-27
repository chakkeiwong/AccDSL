# Exact retained source correspondence

24 October 2026. S1–S4; MC01/03/05/13/17/23/24/25/26/27/31.

## Inspected sources and gap

retained_fixture.from_source explicitly maps the retained packet's opening
returns and two events into the native authoring schema. bound_to_retained checks
the complete projection except the human-readable module name. It converts
legacy exact rational strings such as 2 to canonical 2/1. Interface identifiers
return_component, return_settlement, recovered_sale and the final period date
are authored mapping choices. The opening zero tax bases are conditional taxable
history premises, not observed values or universal rules.

retained_execution_context.load checks the original packet and financial method
bytes. event_for selects native return events or constructs tax/surrounding
events. adapter_for recomputes surrounding journals from the preceding retained
state, never saved expected journals. The original execution verifier replays
all 13 events and compares the independently recomputed retained method. These
existing mechanics should be reused, not replaced by a new guessed source map.

The original packet is 4,139,583 bytes and contains one floating-point field,
build_wall_seconds, outside all financial records. Passing it through the 1 MB
strict financial-record decoder would reject valid retained evidence. The
selected source adapter therefore accepts only the one pinned packet digest,
uses duplicate-key/nonfinite rejection, permits this one nonnegative finite
metadata float, and requires all financial records to remain string/Boolean/
integer structured data with no floating amounts. Its explicit packet bound is
8 MiB: a finite engineering capacity choice for this existing 4 MiB fixture,
not a new general source-decoder default. Changed metadata still changes the
whole packet hash and rejects this exact retained profile.

Record keys use the existing schema-prefixed record_digest, not a bare body
digest. Verify every registry entry and each selected alias kind/schema/key
before dereferencing the opening and events. Retain packet bytes and record
identities separately from canonical projected state/event bytes. Do not
identify a projection as original filing evidence: this packet is synthetic.

## Selected binding and replay

A finite adapter accepts original packet bytes plus caller-supplied native
before-state/event bytes. It reconstructs the authoring projection with the
existing locked fixture mapper, initializes the opening and replays each prior
event from the packet's declared order using the existing native methods and
pinned surrounding financial methods. It never adopts saved after-states or
journals. At the selected settlement/sale, require exact equality of the
reconstructed before-state and prescribed event, then call the recorded typed
transition. A candidate NRV stress differing from the source is a separate
scenario and must fail this exact historical-fixture binder.

The source result contains packet/record/raw-input identities and prefix event
identities. Authority flags remain false. Prefix replay validates this fixed
synthetic path; it does not solve ambiguous historical reconstruction, source
authority, real-company feasibility or alternative histories. This adapter is a
case-specific use of existing reusable byte/pointer helpers, not a general filing
importer. All selected interface constants and tax hypotheses remain explicit.

The additional packet walk permits at most 300,000 nodes and depth 48. This is
a bounded capacity choice for the fixed packet; the packet digest is checked
before parsing, so no alternate packet inherits that admission. Tests exercise
the byte bound, duplicate keys and the single allowed metadata-float location.

## Pre-run audit and criteria

Pass: the exact settlement and sale inputs bind, their typed transition equals
the independently recomputed native after-state, and changed source bytes,
record identity, pointer, value, context or preceding book rejects. Full prefix
recomputation is required because matching opening_sha256 alone would admit an
arbitrary balanced current book. Duplicate and floating financial data reject.
Original packet/implementation drift is a continuation veto until repaired;
candidate binding errors trigger repair. Counts are explanatory only.

Strongest alternative explanation: every comparator shares the retained native
prefix, so no independent accounting or historical-truth conclusion follows.
Native versus typed effects remain a separate exact implementation comparison.
No new professional review, source authority or forecast claim is made.
