# OrderedEPS/1 — closed documentary report contract

16 October 2026. The accompanying JSON schemas define exact fields; objects
reject extra fields. This is a versioned proposed report interface and a
documentary reference calculation, not an implemented AccDSL runtime module.
FinancingComponents/2 remains frozen and has no inferred migration to this
contract. The existing book, authorization and evidence-view contracts still
govern any future integration.

## Inputs and bindings

A request contains `wire=OrderedEPS/1`, `operation=report`, one `context`, one
`context_ref`, `inventory`, `scope`, `basic`, and `series`. The context fixes
entity, book, dated head and evidence view, reporting population, start and
exclusive end dates, ordinary class, retrospective share basis, currency,
currency scale and historical rule version. `context_ref` is SHA256 of UTF-8
JSON for that context, keys sorted, no extra spaces, ASCII escaping, no trailing
newline. Basic and every series carry that same reference. A future report
resolver must verify head/view and the referenced source bytes; a matching
string does not establish source truth or current-law applicability.

Every premise cites a support record (`path`, SHA256 and exact `anchor`). The
documentary verifier resolves these references locally and checks the bytes.
An application must resolve them before accepting any conditional output.
The reference calculator tests structure, binding and arithmetic; it cannot
infer the truth of an attribution, completeness or independence finding.

Rational quantities use reduced strings `n` or `n/d`, positive denominator,
no leading zeros, plus sign, decimal, exponent or negative zero. The schema
recognizes the string shape; semantic validation additionally checks reduction
and sign. Earnings may be signed. The basic weighted denominator is positive.
Calculations retain exact fractions; presentation rounding is downstream.

`basic` is either a ready, supplied continuing/total ordinary-earnings numerator
and weighted-share denominator, with completed attribution/chronology findings,
or an explicit unresolved record. Readiness means these premises have been
supplied for this context; it does not turn this report into an attribution or
share-history engine. Discontinued earnings equal total minus continuing.

The inventory records its independently supplied completeness finding and the
exact list of series IDs. The list and series records must agree bijectively;
duplicates or an omitted inventoried item reject the request. An empty complete
inventory is permitted only with its own support. No result implies discovery
of omitted instruments outside that supplied finding.

`scope` explicitly supplies nonparticipating ordinary rights, independent
additive effects, and fixed conversion consequences, with support. A false
finding prevents the diluted calculation. This does not assert that every
real instrument fits these assumptions.

## Four series dispositions

Each inventory member is exactly one of the following:

* `candidate`: supplied signed continuing/total earnings increments and a
  strictly positive, already time-weighted share increment, plus complete
  earnings and time-weighting findings. Potential windows lie within the
  report period and do not overlap. A converted series also supplies the
  subsequent actual-share window and a finding that its actual shares are
  already in basic; potential and actual windows cannot overlap. A lapse or
  period-end series has no actual window. The selector neither constructs
  these increments nor double-weights them.
* `no_effect`: separately supported zero continuing/total earnings and share
  increments. It remains visible without dividing by zero. A zero-share,
  nonzero-earnings effect does not fit this disposition or the candidate scope.
* `unresolved`: the exact missing input or finding and its support are retained.
* `unsupported`: known terms require a named further method; their support and
  reason remain visible.

Actual/lapse dates and earnings effects must be prepared by instrument methods
under IAS33.33–40 and 45 onward. Window checks reject geometric overlap; they
do not prove a share increment or its valuation. Separate source-bound
preprocessing remains necessary for options, rights, awards and conversions.

## Calculation and result

For eligible candidates, sort exact continuing increment/share increment
ascending, then ID for equal ratios. Beginning with basic N,D, include a series
only if aD<Nb, using the *current* N,D. Update both after inclusion. Equality is
excluded. Negative N or a needs no special sign shortcut. Selected continuing
and total increments accumulate separately over the same selected population.
The source note derives this rule and its finite-subset minimum under the
fixed additive premises.

A result binds the complete canonical request hash and context reference. It
has `status`, `basic`, `diluted`, `trace`, `issues`, `mutations=[]`, and
`acceptance=conditional_documentary_only`. Every EPS bundle includes continuing,
total and discontinued earnings, one denominator and all three exact EPS
amounts. The trace preserves every ID, resolution, incremental ratio where
defined, before/after-if-included N,D and the strict inclusion result/reason.
It is ordered for candidates; no-effect entries follow in ID order.

`conditional_complete` means arithmetic completed on supplied premises. An
incomplete inventory, unresolved series or unresolved basic yields `unresolved`;
known unsupported scope/series yields `unsupported`. If both apply, status is
`blocked` and all issues remain. Basic may be returned when independently ready,
but diluted is null and no partial selection is presented as a result. Shape,
binding, duplicate-ID, rational, sign or chronology violations yield `rejected`.
These statuses have an empty trace except for a completed result. Issues are
ordered deterministically. No silently skipped item and no automatic zero
substitution is permitted. A failed request cannot publish or mutate a book.

The reference calculator consumes and returns in-memory records without book
write access. Its file wrapper writes only documentary evidence. Repeated
requests are deterministic; live head/view freshness and runtime publication
remain outside this oracle. Completion does not establish issuer compliance,
current authority, general participation, a whole-company join or human review.
