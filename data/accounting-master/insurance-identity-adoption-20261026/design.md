# Native identity adoption audit

26 October 2026. MC17/20/24/25/33/34; S2/S4. Audit passes for the narrowed
execution-policy successor below; a financial-profile rewrite was rejected.

Inspected native build_exchanges.py lines 71–146, verify_exchanges.py request,
exchange, crash, proposal, state and result methods, schema_design.py, and the
full semantic-contract.md. The packet retains 43 cases, 84 publications, 672
exchanges, 168 loss-of-acknowledgement worlds and 84 adverse cases. The isolated
identity helper previously checked 85 distinct indexes. Counts are coverage
diagnostics; complete results and state transitions are the evidence.

Four independent owners are issued, replacement, held and accounts. Commit
validates the full opening set, context, source/evidence, lineage and immutable
proposal. A resolved result advances each changed owner once, includes the
journal, and publishes its exact response/receipt closure. Reports publish
metadata without changing financial heads. Unresolved results can publish a
decision but have no changed head or journal. Thus additional_commit means a
publication decision, not necessarily a financial posting.

The native identity is client_id + '/' + request_id. Slash is schema-valid in
both fields. A valid new (a,b/c) request conflicts after (a/b,c), even if it has
the current correct owner heads. This is a false conflict; it does not establish
that historical examples double-posted or had wrong financial arithmetic.

The native canonical request body and its hash remain the exact-byte identity.
A new financial profile reference would change those bytes. Therefore use the
new InsuranceComponentsIdentity/1 execution policy bound to the original
financial Profile record. The world explicitly names the new identity policy.
The financial schemas, operations, sources, facts, proposals, requests, journals
and receipts retain their original references. The only migration changes are
canonical pair keys and that explicit world binding. The retained helper's
format and base-profile binding remain authoritative for index conversion.

Native financial evaluation remains in financial_checks.py and inherited audit
methods. Generate a separately inspectable adaptation of only the two native
protocol methods, changing their key expression. Assert the source delta exactly;
do not silently change arithmetic, refusal order or publication behavior. The
documentary executor implements publication separately and its complete results
are checked against saved native exchanges and the adapted auditor. This is
independence of protocol construction, not a new independent accounting engine.

Migration validates every supplied retained decision's original publication,
reference/byte closure and full before/after world. Missing supplied decisions,
ambiguous keys, conflicts, foreign profiles or changed records refuse with no
input mutation. Completeness of historical publications is still an assumption:
if both an old decision and all independent evidence were erased, no local
converter can infer it. Current heads and journals are preserved, not recovered
from nowhere. The new executor requires the explicit identity-policy binding
before validating request or replay. Retry restores the original output,
receipt and publication list and changes no world. Freshness remains after
identity replay; new identities must satisfy full native eligibility.

| Choice | Provenance/status | Failure mode | Earliest diagnostic |
|---|---|---|---|
| Canonical JSON pair | Isolated helper; reviewed mechanism within retained ASCII ID domain | Concatenation collision or changed string meaning | Two eligible consecutive postings with the collision pair; exact retries |
| Retained native arithmetic | Frozen financial baseline | Protocol repair conceals financial drift | All saved publication/result/journal comparisons plus original financial auditor |
| Explicit identity-policy world | Derived design choice | Old callers accidentally use new semantics or cross-profile evidence | Missing/wrong policy and altered-lock refusal before replay |
| Complete supplied decision history | Conditional assumption | Previously erased event cannot be recovered | Known omitted/conflicting/ambiguous history refusals; explicit limitation |
| Finite synthetic evidence | Existing documentary fixtures | Mistaken actual-insurer or production claim | Labels and result decision table retain documentary-only scope |

Promotion requires preserved complete financial worlds and exact retry results.
Missing records, changed bytes, invalid financial proposals or partial publication
veto the candidate. A broken baseline/lock is a continuation veto until repaired.
Case counts and runtime are explanatory. No performance ranking, production
durability, actual accounting admission or common-profile state adapter follows.
No primary-source research is added; existing authority restrictions stay intact.
