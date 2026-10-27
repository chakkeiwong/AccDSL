# Original-term early conversion: inspected source and competing reading

18 October 2026. P17/R03–R04; MC17/19/24/26/29/30/32–35.
This is documentary preparation, not current-law admission or independent
accounting acceptance. The retained predecessor is Version 3.43, not_ready.

## What the newly acquired source says

BDO, *IFRS Accounting Standards in Practice: IAS 32 Accounting for Convertible
Notes*, June 2026, 63 pages, is retained in `sources/bdo-convertible-june-2026.pdf`.
Its SHA256 is `3facd39f69fb3687c06e78be0282224ff7d7f24990a6446c2382911104c89df9`.
The publisher's retained index identifies publication on 6 July 2026. The
complete extracted text has physical-page markers. The acquisition manifest
records the actual bytes, URLs and unsuccessful discovery attempts separately.

Technical reading covers physical pages 1–21 and 24: the contents and
introduction, liability/equity/derivative definitions, component classification,
measurement, presentation qualifications, Example 1 and its transaction costs,
maturity conversion, tax, early conversion, inducement and repurchase, and the
contrasting derivative-conversion example. Pages 1–5, 14–21 and 24 were read
before the continuation handoff; pages 6–13 were read in this continuation.
The rest of the manual has not been read for this question.

The decisive passage is **section 4.5, printed/physical page 19**. It describes
an “American type” holder option allowing conversion at any time before the
stated maturity date. BDO reports that practice widely interprets an exercise
date permitted by those original terms as the instrument's maturity for this
purpose. On that interpretation, the liability's conversion-date carrying
amount transfers to equity, with no conversion gain or loss and **no
acceleration of remaining interest or accretion to face/redemption value**.
The example converts at the end of year two, debiting liability 945 and
crediting equity 945. This is explicit technical interpretive support for the
narrow pre-maturity case, rather than an inference from a maturity-only quote.

Sections 3.2–3.6 (pages 6–11) and Example 1 (14–16) establish the necessary
issuer/component context. The conversion right is equity; the debt is measured
at amortised cost and the original equity residual is not remeasured. The
example's liability 945 includes the effect of allocated issue costs and the
resulting effective rate. It is not simply principal less a coupon.

The source also distinguishes cases that the proposed profile must refuse:
additional consideration to induce conversion (4.5.1, 19–20), early repurchase
(4.6, 20), an issuer call requiring separate analysis (20), a derivative
conversion feature or whole-instrument fair-value accounting (3.6.2 and 5,
11–12, 21, 24). Section 5.6's derivative example remeasures the conversion
liability before conversion; it cannot support the equity-option treatment.
Section 4.4's tax assumptions (17–18) are expressly jurisdiction dependent.

**Local source defect:** the current/non-current table on page 16 says that
principal is payable in “five years”, whereas Example 1 on page 14 states a
three-year term and its cash/interest schedule uses three years. That table is
excluded from support. The narrow early-conversion statement and its year-two
carrying amount agree with the three-year schedule. The publisher's reputation
does not cure this inconsistency. No general endorsement of the manual follows.

## Comparison with the retained standards

The exact historical primary text is
`docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt`, SHA256
`37f207b1ecdde43e3971cf076f127576d3d7810c791385ba5b1c35f110f17664`.
The following clauses were read again in this continuation, not inferred from
the prior source note.

| Exact anchor | What it establishes | Limit for early conversion |
|---|---|---|
| IAS32.28–32, local lines 13840–13895 | Issuer separates the liability and equity components; liability value precedes residual equity. Paragraph 30 says the obligation continues until conversion, maturity or another extinguishing transaction. | It does not expressly state the measurement on an original-term pre-maturity exercise. |
| IAS32.AG30–32, 14791–14825 | Issuer perspective; liability reflects comparable contractual cash flows; original equity remains equity on maturity conversion and no conversion gain/loss arises then. | AG32 expressly says “at maturity”. Its text has not been silently extended. |
| IAS32.AG33–35, 14830–14854 | Repurchase/redemption consideration is allocated; induced conversion recognizes the additional-consideration difference as loss. | These are different transactions from exercise of the unchanged holder right. |
| IFRS9.3.3.1–3.3.3, 34774–34793; B3.3.1, 38486–38497 | Derecognize an extinguished contractual obligation; normally compare carrying amount with consideration paid in profit or loss. | This is the strongest competing general rule. A generic debt-for-equity exchange cannot be recast as original-term exercise merely to avoid a gain/loss. |
| IFRIC19.1–9, 61620–61723 | Covers renegotiated debt-for-equity exchanges and their fair-value measurement. Paragraph 3(c) excludes equity issuance under original liability terms. | The exclusion defeats automatic use of this interpretation's fair-value rule; it supplies no affirmative early-conversion measurement rule by itself. |
| IAS8.9–13, 3450–3508 | Policy judgement considers similar IFRS requirements before other literature/practice, with consistent application to similar transactions. | This hierarchy permits evaluation of an analogy; it does not prove that the analogy is correct or admit it for every jurisdiction/date. |

The proposed answer is therefore an **explicitly selected interpretive policy
for a bounded synthetic profile**: under unchanged original holder terms and
an admitted equity classification, use the AG32 maturity-conversion treatment
as interpreted in BDO 4.5. The distinction from a new debt-for-equity bargain
is substantive: the holder exercises the equity right already recognized at
issue, rather than receiving newly negotiated consideration. IFRIC19.3(c),
IAS32.29–30 and the existing equity component support that distinction. They
do not turn BDO's interpretation into new words in IAS32.

The strongest alternative is to apply IFRS9's general consideration comparison
to a settlement whose terms do not qualify for that original-right analysis.
The system must retain the actual terms, classification, effective date,
policy selection and authority decision. Unknown conditions are unresolved;
known incompatible rights require another method. It must not select this
policy merely because it avoids a loss. Actual issuer admission, jurisdiction,
subsequent amendments and independent domain review remain open.

## Claim disposition and next action

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | What is not concluded |
|---|---|---|---|---|---|
| The narrow source question now has inspected interpretive support | BDO 4.5 explicitly treats original-term pre-maturity exercise and conversion-date carrying value | No mismatch with that bounded question; page 16's unrelated classification-table inconsistency is quarantined | Whether the actual instrument and applicable authority admit the interpretation | Check the existing EPS example's terms and exact journal/tax/EPS consequences; integrate the narrow policy and source distinction in a new provisional candidate | A universal early-conversion rule, current-law approval, IFRS/US-GAAP/ASBE interchangeability or a completed financing module |

The source gap for this precise synthetic policy is repaired at documentary
level. Wider early conversion, modified terms, derivative conversion, actual
facts and accounting acceptance retain separate obligations. No global
continuation veto fired; internal preparation continues.
