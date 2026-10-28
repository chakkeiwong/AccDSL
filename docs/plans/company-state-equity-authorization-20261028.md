# Equity authorization, settlement and value: SIM-F030/033/034

28 October 2026. C04/T08, supporting T03; MC08/09/10/11/13/18/19/20/25/28/33.

Research intent: distinguish a valid share issue from an authorized or settled
issue, and distinguish percentage ownership from investor value. Primary original
target SIM-F033 is the fifteen-share cap and failed subscription. SIM-F030 uses
fair issue at10 versus discounted issue at8; SIM-F034 separates economic value
from carrying amount. No actual issuer, pricing model or legal opinion is supplied.

Skeptical audit: the existing generic synthetic issue method posts shares times
price and tracks shares but does not discover approvals or cash settlement.
Adding a balanced posting or replay test alone cannot establish those facts.
Reuse that unchanged method as baseline; add explicit immutable typed
preconditions to a separate fixture. Keep its existing share memory update and
account mappings. Settlement inputs are externally supplied premises, not facts
inferred from the posting being tested. A supplied economic asset value is an
independent valuation premise, not a transformation of book equity.

Evidence contract: limit15 applies to newly issued shares in this one approved
raise; approval, accepted offer and settled receipt must be true. Offer price
must equal issue price and received cash must equal shares times price. Unknown
evidence returns unresolved; false or inconsistent inputs refuse atomically.
Test14/15/16 shares, failed/unknown subscriptions, underpayment, changed offer,
duplicates and removed requirements under two account maps. Correct success
must reconcile cash, equity, profit, share memory and financing cash origins.
Baseline acceptance and balanced negative controls are explanatory only.

For SIM-F030/034, use100 old shares, economic assets1000 and15 new shares, with
no debt, fees, tax or project-value change apart from the received cash. These
are explicit authored illustrative assumptions, not calibrated defaults. At
price10 old investors retain1000 of value; at8 their value is22400/23 and loss
600/23, despite identical ownership20/23. New investors' gain is600/23. Book
opening equity10 remains distinct; its0.1 per-share value does not prescribe an
issue price. The baseline ladder compares native accounting output, exact
independent ownership/value equations and deliberate book-price/value shortcuts.

Primary pass: exact native states/refusals match independent expectations and
ownership/value arithmetic conserves the supplied total value. Veto incorrect
bindings, lost atomicity, fabricated receipt, wrong denominator or silently
derived price. Continuation veto protected-source corruption until repaired.
Missing source authority blocks real admission, not this explicit synthetic
test. No stochastic ranking, empirical forecast, default change or broad equity
library completeness. Record full native results and manifest under
company-state-equity-authorization-20261028, preserve original failure rows,
then refresh navigation after protected verification.
