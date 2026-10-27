# Lease and tax method preparation — audited execution plan

Date: 5 October 2026, Hong Kong. This packet executes packet 1 of
`../WORK_PACKETS.md` and the isolation rules in `../EXECUTION_PLAN.md`.
All generated files remain in this directory. The main worktree is read-only.

The question is whether a bounded lessee method and temporary-difference tax
method can be specified with exact source conditions, dated journals and
reconstructible balances before P16 has fixed final interfaces. The baseline is
the eight-group AccountingMethodSpec in original repository path
`docs/design/proposal/methods/standards-mapping-v1.md`, not Claude's unadopted
pseudocode. Address MC16/MC17/MC20/MC23/MC29/MC35, with directly relevant
MC13/MC15/MC19/MC28 and gaps G4/G7. Source work contributes to MC29; it does not
complete the broad literature survey or accounting-domain acceptance.

## Work and evidence contract

1. Reuse retained primary authority where available; obtain official AASB 16
   and AASB 112 compilations covering a for-profit FY beginning 1 January 2024.
   Retain bytes, conversion, URL, hashes, version/application windows and exact
   inspected provisions. Coordinate the same facts with packet 2; ASC/ASBE
   conclusions belong to its separate source investigation.
2. Specify a two-year equipment lease: possession/use begins 1 January 2024,
   annual end-year fixed payments 121, discount rate 10%, no optional term,
   purchase/ownership transfer, incentives, advance payment, initial direct
   cost or restoration obligation. Derive initial PV 210 and the full two-year
   liability/ROU/cash/expense movements. Add missing-control/rate failures and
   a dated subsequent modification example with a revised discount rate.
3. Specify cost-1000 PPE, book depreciation 200/year, illustrative tax deductions
   400,300,100,100,100, and 25% enacted rate. Derive current versus deferred tax
   for explicitly assumed taxable profits; add reversal, enacted rate change,
   loss-recognition failure and the post-2023 lease initial-recognition issue.
4. Preserve exact rational fixtures and one short deterministic arithmetic
   oracle. Its comparator uses independent present-value and balance formulas,
   not journal line equality alone. Include deliberately wrong negative controls.
5. Review the actual dossiers for source overclaims, journals, date/rate timing,
   semantic identity and missing branches. Deliver reconstructed answers and a
   precise residual queue. P17 acceptance and product runtime remain pending.

Pass: retained sources support each attributed rule within the stated version;
independent arithmetic agrees with every asserted journal/roll-forward; negative
controls expose intended defects; missing facts remain unresolved. A wrong source,
unsupported key premise, unbalanced journal or incompatible carrying amount vetoes
the affected example. Current-authority gaps block current/general claims rather
than otherwise useful historical examples. Source count/test count is explanatory
only. There is no empirical superiority, live product, professional acceptance,
tax-law opinion or full-domain completion claim. Artifacts: dossiers, JSON fixtures,
source register/notes, diagnostic script/result and execution note in this packet.

## Defaults and assumptions

| Choice | Provenance and justification | Failure and earliest check | Status |
| --- | --- | --- | --- |
| FY begins 2024; no later early adoption | Matches the preceding repaired standards proposal and packet 2 | Wrong compilation period; inspect cover/transition and incorporation comparison | Illustrative scenario |
| 121 payments and 10% annual rate | Author-selected rational example yields PV 210 | Mistake for a sourced market rate; clearly label assumption, inspect rate selection rule | Arithmetic convenience |
| Two years/non-specialised equipment/no transfer or options | Bounded base case to isolate recognition and amortisation | Incorrect US GAAP classification from absent life/FV; packet 2 keeps that branch explicit | Restricted case |
| Five-year book life, assumed tax deductions/rates/profit | Synthetic timing-difference example, no jurisdiction tax statute | Invented deductibility treated as law; make tax facts assumptions and separate current/deferred | Restricted case |
| Exact fractions, whole-year periods | Avoid hidden rounding or day-count defaults | Arithmetic used as accounting proof; inspect source eligibility separately | Diagnostic choice |
| Primary AASB incorporating texts | Public authoritative Australian standards with IFRS comparison sections | Unrestricted IFRS or current-2026 claim; record jurisdiction/version/for-profit scope | Bounded authority |

## Skeptical audit and stop conditions

The stated facts, source windows and independent formulas are the comparator.
Journal balance alone cannot pass treatment; missing lease control, unsubstantiated
rate selection, tax recoverability or current tax-law evidence remains visible.
The tax initial-recognition exception changed before this example period, so the
single-transaction amendment must be read before connecting lease and tax cases.
No product interface is fixed by these examples. An exact-rational synthetic case
cannot establish estimation quality, legal applicability or numerical capacity.
The files remain outside the controller inventory; no phase state is mutated.

Pre-mortem: the packet could appear complete while copying an obsolete exception,
ignoring tax-in-profit versus OCI allocation, hiding classification uncertainty or
calculating all interest at the initial balance. The earliest defenses are source
inspection, a dated balance schedule, alternative assumptions and negative controls.
Stop the first packet investigation once its two methods, source record, fixtures
and independent checks are reviewable; record missing domain operations for P17.
The audit passes for this bounded internal preparation. It authorizes no change to
scope, campaign deadline, product implementation or professional engagement.

## Root-review correction: run defective payloads through the same oracle

The first negative-control loop merely compared author-entered wrong and expected
numbers. That does not establish detection by the accounting invariants. The
reviewed repair is to copy the valid fixture set, inject one balanced-journal
defect at a time, and run each complete copied payload through the exact same
independent PV/tax checks used for the valid set. Record the mutated bytes and
first actual failed invariant, actual/expected quantity and return status. Run an
unchanged copied baseline through that entry point as a control. The defective
journals remain balanced, so failure must arise from the independent economic or
tax-basis condition. A survivor or an unrelated execution error vetoes the claimed
detection. This is bounded verification of the specification oracle, not a product
implementation or extra accounting acceptance. The audit passes with this repair.
