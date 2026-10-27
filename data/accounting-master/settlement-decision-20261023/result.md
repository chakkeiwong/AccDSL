# Explicit claims and funding plans

23 October 2026. S3/S4; MC13–18/23–26/28. All 28 documentary cases and
74 checks pass. The proposed SettlementDecisionDraft/1 schema and its pure
checker distinguish an identified payable, available cash, a chosen credit
draw and the later settlement events. They register no production operation.

The source context is preserved: Northstar, DemoCorporate, USD, one currency
unit. The retained opening supplies cash 74.6 and payables 30; the existing
purchase adds 170, producing the 200 payable control. The split into a claim
of 160 and other payables of 40 is an explicit authored scenario, not an
invoice recovered from a filing. The hypothetical facility and draw are also
scenario assumptions. They change no retained source or frozen profile.

In the principal case, an authorised draw of 85.4 settles before the payment.
Conditional on the two events succeeding without other intervening movements,
cash becomes zero, payables become 40, the identified claim is fully paid,
total debt becomes 185.4 and facility drawings become 85.4. The draw produces
financing cash of 85.4; the payment produces operating cash of -160. Neither
event creates revenue or profit in this declared example. Both journal
proposals balance, and every input remains unchanged.

Capacity tests include existing drawings and reservations. Time tests reject
late funding, expiry at the draw instant, draws before availability or decision,
future information, stale snapshots and unordered simultaneous settlement.
Unknown eligibility/access remains unresolved when needed. Existing cash can
support a cash-only payment despite unknown external financing. A deficient
cash-only decision is classified under that policy, not as company default.
Missing authorisation references, source-as-authorisation substitution,
currency mismatch, claim/control inconsistency and noncanonical amounts reject.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain the proposed payment subprofile | Exact selected draw/payment consequences and refusal cases pass | Journal/control reconciliation, information timing, nonmutation and source preservation pass | Claim generation, interest/fees and downstream debt schedule are not integrated | Join dated purchase/collection claims and borrowing schedules before a full-period funded scenario | Complete DSL, empirical lending access, accounting compliance or working runtime |

There is no stochastic comparison or supported ranking. Counts are coverage
summaries; the discriminating evidence is that the same payable changes from
cash-only infeasible to conditionally payable under an explicit timely facility.

Red-team review: authorisation here is a documentary scenario decision, not
an externally verified legal right or production admission. An actual draw
could succeed and a later payment fail; the borrowing would remain. The pure
proposal checks do not test that runtime recovery path, idempotent commits or
concurrent reservations. Full-period effects of new interest and fees remain
open, so the funded prefix must not be spliced into the old annual forecast
without a new debt-service schedule and accounting assessment.

Successor evidence now supplies one explicitly authored full-year schedule:
../funded-year-20261023/result.md. It accounts for new interest, repayment and
the retained synthetic tax method. That example does not change this schema's
scope or supply general long-dated/revolving-credit semantics.

Safe replay is verify.py. prepare.py is one-time construction and refuses
overwrite. run-manifest.json records the actual verification environment,
command, input hashes and measured duration; source data remain unchanged.
