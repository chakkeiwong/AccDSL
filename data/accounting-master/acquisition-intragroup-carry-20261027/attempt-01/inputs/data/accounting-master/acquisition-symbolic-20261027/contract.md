# Conditional acquisition expressions /1

27 October2026. This companion implements only the affine dependence described
by the inspected acquisition-period requirements. It preserves legal books and
the core group reporter. All source/accounting/posting/report flags remain false.

A closed envelope binds its complete payload by SHA256. The payload contains
the original group-scope request, acquisition route, prior-interest disposition,
ownership/rights premise, acquisition currency/date/unit, amount descriptors and
source records. The reference recomputes the original scope and preserves the
whole result. Only one no-to-yes transition with no unresolved atom is supported.
An equal-endpoint loss/regain, continuous control, outside-group or unresolved
history requires another method. The acquisition timestamp must equal the exact
conditional transition. The source records bind text, subjects, actor and exact
availability; unknown or future availability remains unresolved for that actor.

Each amount is an unknown symbol, with role, unit, currency, timing, basis and
source reference. No numeric measurement enters this reference. Asset/liability
aggregates and consideration/NCI/prior-equity are acquisition-date quantities.
Profit/OCI/adjustment/distribution/movement inputs cover exactly the post-control
interval. Missing descriptors remain dependencies; malformed descriptors refuse.
Different amount roles may not silently share a symbol. This is a deliberately
limited representation; item-level measurement and related-quantity graphs are
still required for the full method.

Let A,L,T,P,Q mean acquired recognised assets, assumed liabilities,
consideration transferred, qualifying prior equity and NCI. P=0 only under an
explicit supplied no-prior-interest premise. Debt and unresolved prior interests
remain pending financial-instrument/separate-transaction analysis. Let q be the
supplied non-controlling fraction, consistent with the scope request's ownership
fraction and supported by a constant ordinary-present-rights premise. Partial
ownership selects either independently measured Q or proportional Q=q(A-L).
Full ownership requires the explicit no-NCI branch. None selects actual facts.
That branch has zero NCI throughout and refuses NCI distribution/movement slots;
otherwise formally unmeasured movements could create NCI despite full ownership.

Write R for post-control legal profit, D for the signed expense adjustment from
the acquisition/group basis, O for post-control legal OCI and U for its signed
group-basis adjustment. Thus profit=R-D and OCI=O+U. Let V be distributions to
NCI (positive outflow) and M be all other signed supported NCI changes. The
selected reconciliation is NCI_close=Q+q(R-D+O+U)-V+M. This does not prove that
M, eliminations, taxes, acquisition measurements or reports are complete.
The constant-rights scope excludes subsequent ownership transactions.

Acquisition excess E=T+Q+P-A+L remains an excess expression regardless of sign.
No goodwill or bargain gain is automatically recognised. The two algebraic
identities checked independently are E+A-L-T-Q-P=0 and
owners_profit+NCI_profit=R-D (likewise OCI), with the stated NCI roll-forward.
Negative NCI_close is retained rather than clipped. No closing group balance
sheet, cash-flow report or worksheet is fabricated from these expressions.

The output retains complete descriptors and original scope, SHA identities,
typed missing dependencies, conditional expressions when structurally feasible,
and outstanding item measurement/tax/elimination/recognition/report duties.
Synthetic numeric substitutions in verification test algebra only; they are
not valuations or inferred observations about the financial fixture.
