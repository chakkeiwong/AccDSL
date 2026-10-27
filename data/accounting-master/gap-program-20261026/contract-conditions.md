# Payment failure, default conditions and remedies

26 October 2026. E03; W01/W05/W06/W07/W08/W16;
MC01/03/05/13/16/17/19/28/35. Conditional design reference and source reading.

A simulation can preserve every cash payment and still apply the wrong remedy.
The missing distinction is between an unpaid amount, satisfaction of a specified
contractual event-of-default clause, and the exercise or automatic operation of
an acceleration provision. Each depends on different facts. The retained Apple
2024 annual report makes those differences concrete without establishing an
actual default or a complete operative contract.

## Source and scope

The inspected source is Exhibit 4.1 in the retained issuer report, PDF pages
63 and 69–73, printed exhibit pages 3 and 9–13. Its SHA256 is
`ec74758cd767465362c641cf2fd5d8fedd477aed2bf7f62117e67610435dcb88`.
The bytes match `docs/design/cases/apple/annual-2024.pdf`. The existing
collection manifest records acquisition from an AnnualReports mirror on
2 October 2026 and does not establish an exact historical EDGAR acceptance
instant. The new `apple-contract-source/manifest.json` preserves provenance,
extracted pages, render hashes and library version. The six substantive pages
were inspected as rendered images as well as text; page 61 supplies the exhibit
start. No new online source was admitted: built-in search/open returned no
usable content.

The qualification on PDF63 matters. This is an incomplete summary qualified by
the 29 April 2013 and 5 November 2018 indentures. The debt description's issuer
references are to Apple Inc., not automatically its subsidiaries. Its statements
of outstanding amounts are dated, and its listed notes do not establish a
complete group obligation population. Neither consolidated cash nor the generic
indenture description establishes a legal entity's ability to fund a payment.

The existing result at
`data/accounting-master/apple-2018-indenture-source-20261012/result.md` records
failed attempts to acquire the 2018 instrument, identified by accession
0001193125-18-317844, Exhibit 4.1, `d644900dex41.htm`. That result is preserved;
this summary does not close the incorporated-document dependency. The remaining
work needs a new evidenced source lead, actual-series terms and subsequent
amendments, not another unchanged request to a refused host.

## Conditions that the source requires us to distinguish

The following rows are a dependency inventory, not executable legal opinions.
They paraphrase the named historical passages. Facts and applicability are
separate from the reading of the source. The complete extracted pages preserve
qualifications that this inventory cannot replace.

| ID | Source anchor | Consequence for representation | Unresolved premise or implementation limit |
|---|---|---|---|
| C01 | PDF63, Description of Debt Securities, opening paragraph | Bind source edition, issuer and applicable indenture to each series | Underlying instruments, actual mapping, amendments and availability remain to be admitted |
| C02 | PDF63, The Notes | Additional issuance can change outstanding principal and the relevant series population | No fixed denominator or actual issue history follows from a closing balance |
| C03 | PDF69, Events of Default (1) | Interest-payment failure has a 30-day duration condition | Continuous nonpayment, due time and exact boundary order must be established |
| C04 | PDF69, (2) | Principal and premium use due-and-payable status, including stated maturity, redemption or declaration | Do not import the interest grace period; redemption and declaration validity remain separate facts |
| C05 | PDF69, (3) | Covenant failure requires the applicable covenant, continuing breach and 90 days after qualifying written notice | Separately treated and other-series-only covenants are excluded from this route |
| C06 | PDF69, (3) | Trustee notice and holder notice are separate routes; holder thresholds are 25% for 2013 and 33% for 2018 | Aggregate outstanding principal, recipients, receipt, series mapping and notice validity cannot be inferred |
| C07 | PDF69, (4) | Specified voluntary/consensual bankruptcy actions are distinct legal events | The listed actions include proceedings, orders, custodians, assignment, petitions and comparable foreign action; negative equity does not establish them |
| C08 | PDF69, (5) | Specified court orders require the unstayed/effective duration; 2018 says consecutive days | Court competence, order category, stays and interval continuity are unimplemented findings, not a simple distress Boolean |
| C09 | PDF70, (6) and definitions | Other series-specific defaults and the Bankruptcy Law/Custodian definitions remain dependencies | This packet neither closes the default vocabulary nor implements statutory tests |
| C10 | PDF70, acceleration paragraph | Continuing nonbankruptcy events permit declaration through specified trustee/holder routes | Permission, holder request, trustee obligation, actual declaration and delivery are different events |
| C11 | PDF70, same paragraph | Certain specified bankruptcy events accelerate without a declaration | The category must be established from applicable terms; the implementation accepts a supplied finding only |
| C12 | PDF70, rescission paragraph | Rescission requires the specified holder action, deposit and cure/waiver conditions | Cure alone does not reverse acceleration; the exception for amounts due solely by acceleration must be checked |
| C13 | PDF70, cross-series paragraph | A default in one series does not automatically determine another series | Neither global contagion nor universal independence follows; consult each target series |
| C14 | PDF70, annual officer statement | Annual reporting to the trustee has its own deadline and knowledge qualification | An officer statement is evidence with scope, not an omniscient truth oracle |
| C15 | PDF70–71, proceedings and trustee paragraphs | Collective proceedings require continuing event, notice, threshold request, indemnity, trustee inaction and no inconsistent direction over specified periods | The two 60-day conditions, trustee duties and procedural findings are retained but not implemented |
| C16 | PDF71, payment enforcement paragraph | Individual payment enforcement has a separately stated right | Collective-action prerequisites cannot silently replace this route; judicial enforceability is not decided here |
| C17 | PDF71, Modification and Waivers | Protected changes include maturity, amounts/rates, redemption, currency, suit rights, voting, waiver protections and specified conversion/exchange rights | Each-affected-holder consent differs from a majority; applicable exceptions and actual valid consent remain facts |
| C18 | PDF71–72, no-consent amendments | Covenant additions, succession, guarantees, security, trustees, issuance, form, depository rules and specified technical changes have distinct routes | Restrictions on existing series, material adverse effects and the 2013/2018 differences prevent a blanket no-consent rule |
| C19 | PDF72, final paragraph | The general majority waiver excludes payment and individually protected defaults; a waiver is specific to the past default | A legal cure can change current contract status while the historical payment event remains in the record |
| C20 | PDF73, discharge and defeasance | Legal discharge and covenant defeasance differ; scheduled-maturity funding may not cover accelerated amounts | Deposits, irrevocability, eligible assets, currency/series substitutions, opinions and surviving duties remain unimplemented dependencies |

These conditions have an immediate implication for the earlier settlement
example. E01's retained missed-payment amount is an economic history under
supplied terms. It is not a universal event-of-default label. Adding a remedy
requires the relevant clause, evidence and action. Conversely, a later waiver
may remove a current legal default without making the old payment occur on time.
Economic history, current contract status and what an observer knows about each
must remain distinct.

## A conditional classifier and its tests

`contract_conditions.py` is an executable design reference for selected
conditions, separate from the common company runtime. The input table supplies
hypothetical facts and literal expected classifications independently of the
evaluating functions. It accepts three-valued findings, exact rational periods
and holder fractions, plus explicit edition and applicability fields. A result
of `not_satisfied` refers only to the selected condition. It does not certify
that the company has no other default. `unresolved`, `unsupported` and
`invalid_input` remain distinct. No actual-issuer admission flag is enabled.

For example, a principal amount known to be due and unpaid satisfies the selected
principal clause in the supplied applicable description. Interest one day past
due does not yet satisfy its 30-day clause. Interest continuously unpaid for
31 days satisfies that duration condition; a day-level observation at exactly
30 days remains unresolved because the packet has not supplied the event order.
The same distinction is used at the 90-day covenant boundary. This deliberate
information restriction does not assert that the contract itself lacks an
answer at the boundary.

A hypothetical 25% holder notice after 91 days satisfies the selected 2013
route but not the selected 2018 route. A known valid trustee notice does not
require that holder threshold. A missing notice is unresolved, while evidence
that no notice was given leaves this route unsatisfied. These statements use
supplied actual-principal fractions and valid delivery findings; neither
validity nor the denominator is manufactured by the calculation.

A continuing nonbankruptcy event with no declaration does not produce a new
acceleration through that route. A supplied qualifying automatic category can
do so without declaration inputs. The implementation review caught a dependency
mistake here: eagerly evaluating the unused notice route could reject a known
automatic case because its notice edition was uninspected. The corrected
reference evaluates only the relevant route, with two explicit regression cases.
An existing acceleration is assessed separately: curing an event is insufficient
to establish that a rescission has taken effect. The remaining examples keep
protected amendment consent, the limited majority waiver and target-series
status separate.

The completed run checks 58 cases and 12 explicit contrary-policy controls.
These controls compare wrong-policy outputs with the expected table; they are
not mutations of an external legal engine. They detect conflating every arrear
with default, using one holder threshold, manufacturing acceleration, treating
cure as rescission, allowing majority changes to protected maturity terms,
erasing unknowns, inferring bankruptcy from negative equity and making all
series either jointly defaulted or independent. `contract-condition-results.json`
retains every input, expected and observed result, source page and scope.
`contract-run-manifest.json` records the exact command, source/script hashes,
environment, elapsed time and check count. The standard-library calculation
runs with `CUDA_VISIBLE_DEVICES=-1`; no stochastic comparison or external
contract runtime is executed.

## What the result changes

The claimed target is selected conditional logic implied by the inspected
historical summary under supplied applicability and event findings. The
computed quantity is that condition's three-valued truth, or a typed refusal.
Equality with the independently written expected cases is checked. Equality
with an actual issuer's legal status is not established. The hardest remaining
dependency is establishing valid inputs and the applicable amended instrument,
not the arithmetic comparison of 25 with 33.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain the source dependency inventory | Exact source bytes/pages and adjacent qualifications retained | Source drift would invalidate the packet; none observed | Complete instruments, series facts, later amendments and precise availability | Admit an evidenced contract/series dependency into a partial history | Operative legal authority or full package completeness |
| Retain the selected conditional reference | All expected case classifications and input preservation checked | Wrong-policy outputs differ; unused-route defect repaired before final run | Validity of supplied findings; boundary order; omitted procedures | Bind these conditions to explicit event/state semantics and the common runtime | Complete legal classifier or actual Apple default |
| Extend financing and group gaps | Missed amount, event, remedy and legal owner kept distinct | A generic overdue flag cannot certify the stronger states | General cure, waiver, modification, priority and funding mechanisms | W05/W06/W07/W08/W16 source-supported composition | Whole financing or group requirement closed |

The strongest alternative explanation for a passing test is that both the
authored functions and expected cases share a mistaken reading of the summary.
Page inspection, explicit qualifications and counterexamples reduce that risk
but do not replace the underlying instruments or independent domain review.
A contrary applicable clause, excluded series, later amendment or different
valid event order would overturn the corresponding conditional application.
The direction remains viable; the result rejects broad shortcuts, not the use
of history families. No program-wide continuation veto occurred.

The new work is companion evidence. It is not integrated into the frozen
Version 5.13 manuscript or the Version 5.12 simulation volume. Their source
and PDF hashes remain protected. The master program retains actual-source
admission, method composition and manuscript integration as open work.
