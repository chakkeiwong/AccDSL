# Pricing and conversion do not supply the missing measurement rule

26 October 2026. W01/W02/W05/W06/W07/W16;
MC13/14/17/19/24/25/28/30/33/34/35.

The existing admitted compound-bond package cannot govern the new contingent
conversion example as currently specified. Its authority register admits
reporting-period starts from 1 January 2023 to before 1 July 2026. Its code
only supports the declared maturity-only fixed-for-fixed ordinary conversion
profile. The new fixture finances in 2027 and converts conditionally in 2028,
before terminal cash in 2029. Reusing the old admission is wrong relative to
the package's stated contract. This is a scope finding, not a claim that the
underlying accounting law ceased to apply in July 2026.

The source reading inspected the following retained primary passages, beyond
the authority-register summaries:

| Source and exact anchor | Inspected point | Consequence for this example |
| --- | --- | --- |
| AASB132, physical13, paragraphs25–28 | Contingent cash settlement, settlement options and assessment of instrument components | The actual conversion trigger, discretion, genuineness and alternatives matter; a signal label is insufficient for classification |
| AASB132, physical14, paragraphs29–32 | Holder conversion option, continuing obligation and liability-first residual split | The selected contingent conversion is not automatically the ordinary optional compound-bond example |
| AASB132, physical25, AG30–AG32 | Issuer-only compound guidance, comparable-credit nonconvertible yield, and conversion at maturity | Holder accounting needs its own AASB9 analysis; the maturity rule and pricing discount cannot be silently transferred |
| AASB9, physical44–45, AppendixA definitions | Amortised-cost roll-forward and effective interest based on the specified instrument's estimated contractual cash flows, with stated exclusions | No effective rate or unchanged-carrying path follows from the finite pricing law alone |

The original local sources remain at docs/design/research/standards/aasb132.txt
and docs/design/research/p08-v1/aasb9.txt with their retained PDF counterparts.
The source lock preserves exact versions. These readings do not establish a
2027 reporting edition, an actual issuer's jurisdiction or a complete contract.
AUD is a default fixture currency, not an unconditional code restriction:
the code requires matching currency and functional currency. No unsupported
claim that all USD instruments are excluded is made.

Fifteen exact/source-boundary checks pass in the one-shot attempt. A different
plain zero-coupon promise of 80, discounted twice at 21/20, has present value
32000/441. Subtracting that from the contingent-security price 17000/441
gives negative residual equity of -5000/147. The existing validator correctly
refuses that inconsistent split. Accreting the full price twice at five
percent reaches 85/2, not 80. These calculations reject silent substitution
of a different promise or rate. They do not value the contingent liability.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Refuse automatic reuse of the existing accounting package | Dates, terms and exact source meanings do not match | Current admission rejects future-period and unsupported-conversion cases; wrong-rate/split controls discriminate | Complete contract, applicable source edition, issuer and holder classification, measurement inputs | Prepare dated authority and conditional term/measurement alternatives before joining issuance to conversion | Rejection of the simulator or proof of one correct replacement treatment |
| Retain checked economic and typed mechanics | Their synthetic premises were explicit | No claim was made that their carrying amounts were standards-derived | Actual applicability and intervening events | Keep those results as companions while resolving the separate source/measurement layer | A compliant full issuance-to-liquidation history |

Post-run red-team: a fully specified genuine contingent instrument may support
a liability or other treatment under an applicable source. A complete term
sheet, current dated primary authority and a checked issuer/holder analysis
could resolve the missing path. Changing a yield until numbers balance would
not supply that evidence. No paid referral is needed while this internal
source and alternative-treatment preparation remains feasible.

Attempt-01 completes in about 0.03 seconds using exact fractions and intentionally
hidden GPU devices. The command correction sidecar records an extra unused
environment variable in the actual launch; it changes no calculation. No
stochastic ranking, source-rule update or evidence rerun occurred.

Version 5.19 remains governing. Funding and this audit are later companions.
All 53 obligations, six interactions, 46 operations and 18 packages remain;
S1–S5 partial, S6 held, E3 deferred. No whole requirement closes.
