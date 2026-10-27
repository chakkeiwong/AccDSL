# Complete native whole-lot sale through the declared company book

NativeCompanySale/1 accepts a complete NativeReturnBookReference/1 before-state
and one native kind=sell event, each with an expected digest. The adapter validates
the full native state against its pinned structural schema and native invariant;
it validates the native sale domain without calling native.transition. Non-sale
methods and partial fractions remain unsupported. Native Rejected statuses are
preserved. The imported native profile remains narrow; no arbitrary-owner native
admission follows from the generic book's separate two-owner evidence.

Import all native account balances with explicit native classifications. The book
context maps native book_role to book and adds synthetic mode. Memory contains all
existing lots, other_inventory and tax_closed_until. Every lot uses a closed record
and explicitly typed units, carrying, tax base, identifiers, acquisition date and
disposition. The fixed set of lot IDs defines the schema; a sale creates no lot.
All other native fields are retained in a before-state complement bound to the
request. Prefix cash flows acquire stable projection identities that disappear
when exported to the native schema; their original fields and ordering remain.

The selected method reads the chosen lot and derives cash/revenue/inventory/cost
entries using MethodMonetaryEffects/1. Only that lot's units,carrying,tax_base and
disposed scalar leaves change. A predicate reconciles total inventory with
other_inventory plus every lot's carrying value before and after. Native close
date is compared with metadata-bound event date. Export replaces only balances,
date,seen,flows,lots in the captured complement, then revalidates the full native
schema and invariant. The runtime never calls native.transition to obtain effects.

Propose returns the complete generic binding result and restored native after-state,
journal and flows. Apply recomputes the whole result using canonical JSON equality.
All admission/commit/durability flags stay false. The native transition is used only
in independent tests and comparison recording. Direct-event timing only; no new
reporting, closing, partial-sale, collection-insertion or source-admission contract.
