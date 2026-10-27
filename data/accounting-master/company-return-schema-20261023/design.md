# Closed native return-module authoring

The first new profile is ReturnModuleAuthoringDraft/1, a component declaration
for one legal book, not a complete CompanyOperationPath replacement. It
specifies component memory, lots, account roles, source identity, tax premises
and dated settlement/whole-lot-sale events. The old company grammar is invoked
unchanged in legacy mode. Successful parsing means structurally and statically
checked authoring; accounting execution and annual reporting remain separate.

The matched example projects P's opening and selected events from the retained
CompanyComposition packet. Its entity and currency come from that source;
book_role=legal and case_id=retained_company_composition are explicit interface
labels, not newly discovered historical identifiers. The exact packet and
opening state digest remain bound. Component/lot/event ids are authored labels
with named pointers to the retained source fields. Original 2025 dates and
synthetic tax facts are retained. No 2024 owner migration or Northstar renaming.

The fixed account-role map names shared-book accounts; it imports no balances
as an independently funded wallet. Opening allocations for refund/recovery and
their tax bases must match the supplied component and tax values. Other company
balances remain outside this component record. Recovered lots keep exact
carrying value and tax base separately from homogeneous stock. Source trust
and complete-company tax inventory are explicit findings, never inferred from
the syntax or a known amount.

Text uses line-oriented named declarations with explicit fields and blocks,
the same modest style as the existing company frontend. It does not wrap an
opaque JSON body in a text command. Schema validation, canonical rationals,
strict Booleans, unique ids, reference checks and chronological event rules
precede method eligibility. Unknown inputs parse but return unresolved;
known false required findings parse but return unsupported. Neither becomes a
zero or a fabricated complete report. Unknown cannot be the name of an id.
Known contradictions take precedence over unsupported premises, which take
precedence over missing inputs. Each arithmetic check uses only its known
dependencies. Typed strings must be representable on one text line. Source
pointers use a digest and valid JSON-pointer escapes; valid syntax alone is
not correspondence to a source. Zero-return settlement needs a separate
no-lot method and cannot create a phantom recovered lot in this subset.

Static evaluation checks arithmetic correspondence of authored facts (cash
refund, handling, lot amounts and opening tax differences) but does not post
their journals. The actual stock/tax accounting still belongs to the selected
checked method. Unsupported methods/fields fail explicitly. The first subset
settles one component and sells one whole recovered lot; general rights
updates, partial sales, native tax close/report/carry and other module types
remain open. Promotion requires exact text/typed identity and preserved source
bindings, not syntax coverage counts alone.
