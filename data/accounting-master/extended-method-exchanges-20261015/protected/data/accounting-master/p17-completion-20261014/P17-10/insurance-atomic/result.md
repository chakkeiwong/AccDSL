# Connected insurance atomic publication and recovery

14 October 2026. P17-10/11, scoped P18 integration; MC02/04/11/13/18/20/22/24/25/27/28/32–35;
E07/E14. Version 2.88 is a separate provisional 260-page candidate, not_ready:
docs/design/proposal/manuscript-insurance-atomic-20261014/accounting-product-proposal.pdf.
SHA256: 78317ab2612b9752f2e686f269c2a202ede9b0fef9e06d673ff12f59b2166050.

The specification preserves one insurer/book/branch while measuring issued
groups A and B and held group R separately. Finance, service, incurrence and
settlement have distinct event identities and intermediate company states.
Complete input binding, measurement and authorization precede receipt lookup;
exact historical replay precedes current-head freshness. Publication includes
the state, journals, component changes, immutable receipt and full dependency
closure. An unresolved group blocks the declared event while its diagnostic
candidates remain available outside the committed book.

The claimed numerical target is the retained timely-treaty year-one A/B/R
case under its historical AASB17 compilation and supplied assumptions.
The independent checker derives phase equations from the preserved inputs
and obtains exactly the same final cash173, coverage65.5/71/46.5 and equity83.
It also checks intermediate equity70 after finance and160 before incurrence,
and incurred balances44/66/33 before settlement. The loss components remain
inside the coverage values. A balanced extra entry for R's component is wrong
relative to this target and is rejected, as is a lost component-only change.
No actuarial measurement is estimated or new accounting permission created.

All **27 authored exchanges, 274 closed records and 22 blobs** pass **2,428
independent checks**. These include exact rational arithmetic, typed closure,
hashes, actual submission bytes, common schema preservation, source pins,
phase order, group identity, state reconciliation, validation/lookup/freshness
ordering, unchanged book domains on rejection/replay, and final-check races.
The global registry is distinct from the records published in each world.
A lost acknowledgement has two possible storage worlds and no fabricated
received OperationResult. The same request commits in the precommit world and
replays in the postcommit world. Different request identifiers/budgets conflict.

The verifier caught an authoring error: the three later packets accidentally
used the finance default, creating repeated business keys despite correct
standalone component states. Explicit phase arguments repaired the fixtures.
It also rejected an unnecessary change to the common result schema. Both were
preparation defects, not evidence against the accounting method. The earlier
registry-only storage trace was strengthened with published state/record/edge
sets before acceptance. These findings demonstrate why neither a plausible
table nor schema validation alone closes the interaction.

All **95 manuscript preservation/build checks** pass. All73 predecessor source
files and the prior PDF remain unchanged. The successor changes only its
version, one input location and the new section12.7. Displays88→88,
labels157→158, citations463→463; bibliography unchanged. All76 project build
inputs reside inside the successor. LuaLaTeX built260 pages in24.676 seconds
with no recorded diagnostics. Physical pages1,6,178–182 were visually inspected;
the table, formulas, headings, new explanation and surrounding material fit
without clipping. This is scoped author review, not whole-candidate or human
acceptance.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept finite insurance interaction specification | Exact phase calculations, complete records, adverse/recovery decisions pass | Authoring and schema defects repaired; no remaining scoped check failure | Actual storage isolation/durability and independent domain review | Retain contract/fixtures for later implementation tests | Runtime atomicity, real-insurer permission or whole insurance completion |
| Integrate section12.7 in Version2.88 | Material gap explained beside connected case; content preserved and pages inspected | No build, preservation or scoped rendering veto | Human comprehension and full P18 review | Refresh controls and execute bank prudential connection | Full P17/P18/P19 readiness |

The strongest alternative explanation is a future mismatch between these
finite expected worlds and an actual transactional store. Crash/fault tests
against the implementation could overturn runtime confidence; none was run
or claimed. The weakest present evidence is independent acceptance, followed
by coverage beyond this fixed single-book group set. No result invalidated
the retained source/target; repaired authoring defects do not veto the broader
direction. Continue the audited bank-prudential connection plan.

Latest full author assessment remains Version2.72; 2.73–2.88 are scoped
supplements. P17/P18/P19 and E07/E14 remain open. The100 unrelated staged
entries are preserved. No runtime campaign, installation, GPU operation,
professional contact, fees, publication or commit occurred.
