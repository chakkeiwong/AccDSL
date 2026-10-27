# Full statement observation and relation meaning

RetainedStatementContextDraft/1 binds all original statement observations and
relations in a selected annual/interim/combined view. The combined case has
256 readings and 143 relation declarations. Typed and named text authoring are
equivalent. Text contains explicit observation references, economic dates or
intervals, units, relation roles, operands, coefficients, omitted source rows
and required dependencies. It does not run code or supply missing financial data.

Source period and measurement time are separate. An equity endpoint can be
printed in an annual statement and measured at its opening or closing date.
The adapter follows the original reading pointer to recover measurement_date,
keeping the portable context unchanged. Opening comparison aliases map to
original opening.balance.* observation IDs; original IDs, source pointers,
amounts, literals, admission and precision remain intact. Per-share and
weighted-share observations remain represented even where no relation uses them.

## Relation roles

Snapshot sums and same-date endpoint comparisons require compatible instants.
Period sums and same-period identities require compatible intervals. Stock-flow
bridges retain opening and closing dates plus flows over their stated period;
they are not normalized to a single instant. The net-asset-change comparison
uses the two equity endpoints rather than a saved numeric difference.
Cross-period endpoint comparisons preserve the annual and interim source bases
and compare only their named equal-date endpoints. They do not harmonize those
bases or admit a general equivalence. Cash population comparisons remain
displayed amount comparisons, not proofs of unrestricted cash identity.

Explanatory differences compute signed arithmetic with the declared stock,
flow or expense populations; they never create a journal or force residual zero.
The three derived-subtotal families retain no independent target or residual.
Their original ledger targets remain in provenance. The audit explains why
the old annual pass/fail role was too strong for an independent identity claim.

Every relation is bound to its exact original ledger row; context-role rules
are meaningful only for these selected source definitions. Unit, perimeter and
issuer agree for the arithmetic; intentional time and measurement-kind
differences are explained by the relation role and preserved operand records.
A global label match or a successful schema check is not accounting admission.

## Missing terms and evidence

The annual financing total and term-debt difference include a reported dash.
They remain unresolved in this baseline. The old zero-contribution convention
is preserved but not adopted silently. Absent annual rows in the interim
source remain explicit omissions; arithmetic over the listed interim rows
does not establish zero transactions for an omitted concept. An interim-only
view cannot evaluate the five annual-to-quarter comparisons, although those
original entries remain in its disposition list. A combined view supplies
both original endpoint observations without later-source leakage.

Results include all original ledgers, their exact records and diagnostic roles,
all selected observation records and reading pointers, context dispositions,
recomputed arithmetic and the same missing-state requirements. There is no
underlying-balance equality, joint-history feasibility, executable opening or
probability model. Full result recomputation rejects changed context, coefficient,
alias, date, omission, diagnostic role or inferred company result.

## Acceptance and remaining scope

Use independent retained-reading calculations and explicit endpoint/derived
subtotal discriminators, all-view and both-target round trips, adversarial
requests/results and protected hashes. This closes the former 125 unspecified
deferrals at the displayed relation/explicit-disposition level, not at actual
company reconstruction. General source readers, concept mapping, legal/group
history and admissible accounting methods remain open. The next design decision
must distinguish this now-explicit source layer from still-missing execution
capabilities instead of adding another wrapper around the same example.
