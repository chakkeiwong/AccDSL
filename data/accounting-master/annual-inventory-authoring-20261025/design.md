# Annual inventory authoring, finite profile 1

AnnualInventoryAuthoring/1 uses the existing annual_program/import_root/
operations grammar. It lowers to AnnualInventoryProgram/1. Old operation syntax,
field validation and assembly delegate to the frozen annual authoring module.

A partial_inventory_sale block requires sale_profile, date, method, lot_id,
sold_units and proceeds singleton declarations, plus six named finding entries.
The operation header supplies the event id; sale_profile lowers to event.profile
and must equal RecoveredLotSale/1. Method names are data: unsupported methods
compile but stop in evaluation. Findings must have known boolean values with
nonempty text provenance, or unknown status with a reason. All six are mandatory. Findings are
never inferred from stock, price, proceeds or another declaration.

Compilation accepts only explicit digest-bound root imports and produces the
exact runtime request, program/request digests, raw text hash, source spans and
executed=false. It performs no root or financial execution. Rendering is
canonical; blank lines, CRLF and map ordering can alter raw hashes/spans while
retaining the same typed program. Program names retain the legacy identifier
restriction. Operation identities and provenance remain Unicode strings.
Financial refusals, prefix results and unavailable future activity are retained
by the existing evaluator. This interface assigns no probabilities or accounting
admission and does not extend the scenario-family profile.
