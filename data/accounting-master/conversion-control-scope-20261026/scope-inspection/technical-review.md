# Control and reporting-scope technical review

26 October 2026. MC17/19/20/24/25/28/30/33–35; W05/06/07/08/16/17.
Bounded primary reading for the conversion example, not full standards review.
Paragraph anchors below refer to physical PDF pages in source-attempt-02.

## Control cannot be inferred from the cap table alone

AASB10 §§5–8 (pp6–7) requires power, exposure/rights to variable returns and the
ability to use power to affect those returns. §§10–14 (p7) links power to the
current ability to direct relevant activities. A 120/160 vote fraction is useful
context but does not complete those assessments. B35–B37 (p17) states the
majority-vote case and its exceptions: substantive votes, direction of relevant
activities, other parties' rights and external direction all matter.

B22–B25 (pp14–16) requires practical ability to exercise substantive rights and
considers the timing of relevant decisions. B26–B28 (p16) separates protective
rights. B47–B50 (pp19–20) requires assessment of substantive potential voting
rights, including convertible instruments. B53 (p20) explains why rights over
activities arising only on a contingency are not automatically protective.
Examples11–12 (pp20–21) illustrate the reasoning in their receivables setting;
they do not decide control of the different project in this fixture.

Consequently, a claim that control begins exactly when the shares are legally
issued is unsupported without an earlier control assessment. AASB10 §20 (p7)
and AASB3 §§8–9 (p7) tie consolidation/acquisition timing to control. The legal
conversion date is an event date, not a substitute for that accounting finding.
The earlier economic controller assumption remains a separate model premise.

## Reporting contexts require different methods

AASB10 §4 (pp5–6) requires parent consolidation subject to all relevant
exemption conditions; §4(a) and Australian paragraphs are not interchangeable.
§§27–33 (pp8–9) define investment-entity assessment and the FVTPL exception,
including the non-investment service-subsidiary exception and treatment by an
investment entity's own parent. Investor identity and entity status are missing
from the current fixture, so none of those exceptions is assumed.

AASB127 §§2–4 (p5) describes separate statements; it does not mandate which
entities prepare them. §§8–11B (p6) separates ordinary category-consistent
cost/AASB9/equity-method choices from required investment-entity treatment.
A permitted cost policy does not establish initial cost or authorize retention
of the pre-conversion debt amount. Recognition and measurement on conversion
remain distinct dependencies. A user of the DSL must identify which reporting
entity and which statements a supplied amount belongs to.

AASB10 B86–B93 (pp31–32) specifies combination, elimination, policy alignment,
control-date income/expenses, ownership allocations and reporting-date issues.
B89–B91 distinguishes ownership allocations from potential voting rights and
preserves an exception for instruments already providing ownership returns.
It would be wrong to treat the 75% voting fraction as a universal 75% multiplier
for every group line, period profit or acquisition-date net-asset amount.

## A project is not automatically a business

AASB3 §2(b)–(c) (p6) separates asset acquisitions and common-control cases.
§§3–10 (p7) identifies the business-combination, acquirer, acquisition-date,
recognition and measurement dependencies. B7A–B12D (pp22–24) distinguishes the
optional concentration screen from the input/substantive-process assessment,
including with/without outputs and workforce or replacement conditions.
The synthetic project value100 contains none of that evidence. No goodwill,
NCI value or acquisition allocation is computed from it in this review.

## Dated amendments remain separate

AASB10's retained compilation covers annual starts from2026-01-01 to before
2027-01-01; AASB3 covers2026-07-01 to before2027-01-01. AASB127's cover starts
2022-01-01 without an end date, but the cover alone cannot prove absence of
later amendments. The complete2027/2028 rule set is not admitted.

AASB2024-4 §§6–8 (pp5–6) defers/reverses the specified AASB2014-10 changes for
the stated intervening periods, with early application. These changes concern
sale/contribution and loss-of-control transactions; they do not supply a new
rule that75% alone establishes control. AASB2014-10 §§8–10 (pp7–9) must be
read together with that subsequent instrument.

AASB2026-3 application and amended AASB128 §18 (pp5–6) add a future-dated
associate/JV election dependency. This is not authority for treating a
controlled subsidiary as an associate. AASB2026-4 §3 (p5) and §16 (p10) were
also inspected. The p10 redline changes the AASB1056 title reference, leaving
the displayed2027/2028 commencement dates in place. Future amendments to
presentation and entity scope still need a complete chain.

Rendered redlines inspected: AASB2024-4 p5, AASB2026-3 p5 and AASB2026-4 p10.
Text extraction alone merges insertions and deletions. Preserved HTTP metadata
includes one negative wall-clock interval for aasb127-index.html; retain the
record as a clock-order anomaly, not a negative download duration or fabricated
timestamp correction. Hash integrity is checked independently.

## Existing implementation boundary

Inspection of scripts/group_period_report_v1.py found an explicit stable
full-ownership restriction and no NCI, goodwill, FX, tax or intragroup-profit
methods in that profile. Its prepare() requires the same control edges and
book population at opening and closing. scripts/native_group_binding_v1.py
resolves already supplied synthetic ownership records; it does not decide
accounting control from these sources. Neither interface can silently admit
the conversion-date75% acquisition or make it a complete period group report.

The next dependency specification should therefore preserve control-assessment
dates, earlier potential rights, investor role, reporting view, exceptions,
business status and measurement unknowns. A selected route is preparation for
an accounting method, not an authorization to post journals or declare source
truth. A new period/group bridge needs explicit changing-perimeter and NCI
semantics before using this example.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain conditional scope analysis | Relevant definitions, exceptions and technical guidance inspected | No actual control or future-edition admission | Contract rights, earlier control, reporting entity, business and measurement | Verify typed dependency/refusal cases, then specify changing-perimeter methods | Actual consolidation, fair value, goodwill or whole-company readiness |

The strongest alternative explanation is that explicit contract and entity
facts could justify one of several different routes. The source review rules
out silently choosing a route; it does not reject the company simulator.
