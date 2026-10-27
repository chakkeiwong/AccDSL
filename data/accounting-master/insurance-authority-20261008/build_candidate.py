"""Create the bounded Version 2.5 candidate while preserving Version 2.4."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "docs/design/proposal/manuscript-authority-20261008"
NEW = ROOT / "docs/design/proposal/manuscript-insurance-20261008"
if NEW.exists():
    raise SystemExit("Candidate already exists; edit it deliberately instead of recopying.")
for source in OLD.rglob("*"):
    if source.is_file() and source.suffix in {".tex", ".bib", ".lark"}:
        target = NEW / source.relative_to(OLD)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def replace(relative, before, after):
    path = NEW / relative
    text = path.read_text()
    assert text.count(before) == 1, (relative, before)
    path.write_text(text.replace(before, after))


replace("accounting-product-proposal.tex", "Version 2.4", "Version 2.5")
replace("chapters/08-modules.tex",
        "chains and broader ASBE authority remain incomplete. Current ASC access is also\nunresolved.",
        "chains and broader ASBE authority remain incomplete. Chapter~\\ref{ch:insurance}\ncompares the dated ASBE~25 premium-allocation and incurred-claim provisions\nwith the retained AASB~17 text \\citep{mofasbe25}; the full ASBE~25 adoption\nschedule and later implementation conditions remain unverified. Current ASC\naccess is also unresolved.")

insertion = r"""A one-year policy can leave claims unpaid for several years. The distinction
between the period of insurance service and the period until settlement is
therefore essential even when PAA is available. The official ASBE~25 text
separates three timing tests. Article~50 permits PAA when each contract's
coverage is no longer than one year, or when the stated no-material-difference
condition holds. Article~54 concerns a different interval: the time between
each portion of service and the related premium due date. If that interval
does not exceed a year, the remaining-coverage liability need not be adjusted
for financing. Article~56 instead measures from claim incurrence to expected
payment or receipt. Its option to omit the time-value and financial-risk
adjustment requires settlement within a year of incurrence
\citep[Articles 50, 54, 56]{mofasbe25}. The retained AASB~17 compilation makes
the corresponding distinctions in paragraphs 53, 56 and 59(b).

Consider a separate group of issued policies with exactly one year of coverage.
All amounts are illustrative currency units. Premium 120 is due and received
when coverage starts, with no earlier onerous trigger; group recognition is
therefore at that date under Article~16. Assume valid insurance grouping,
uniform risk release, no acquisition costs, investment component, reinsurance,
tax, other expenses or other movements, and no facts indicating onerous
remaining coverage. Elect the permitted remaining-coverage financing exception.
After half a year, recognise revenue 60 and retain remaining coverage of 60.
Articles~53 and 57 support this roll-forward and time allocation; Article~57
requires a different allocation when risk release is not predominantly
time-based \citep{mofasbe25}. These assumptions isolate the claim measurement
from other changes in the group's result.

At that reporting instant a claim is first incurred, with an expected payment
of 60.5 exactly two years later. This is a mean estimate, not a certain
settlement. Assume an appropriate flat annual effective discount rate of
10\% and a separately estimated non-financial risk adjustment of 5 in current
measurement units. The inputs are authored for the example; applying them to
an insurer would require market and actuarial evidence. Articles~21, 23, 25
and 26 require current probability-weighted cash flows, appropriate discounting
and a separate non-financial risk adjustment \citep{mofasbe25}. The claim's
cash-flow present value is $60.5/1.1^2=50$, so its liability is $50+5=55$.
The risk adjustment is not discounted a second time. The claim has only just
been incurred, so no intervening finance accrual enters this measurement.

Record debit cash 120/credit remaining coverage 120 on premium receipt, then
debit remaining coverage 60/credit insurance revenue 60 for the service
provided. Recognising the claim gives debit insurance service expense 55/credit
incurred claims 55, consistent with Article~31. The group then has cash 120,
remaining coverage 60, incurred claims 55 and a cumulative result of 5:
$120-60-55=60-55=5$. These are balances attributable to the group at mid-year,
not a complete insurer forecast. Using the undiscounted $60.5+5=65.5$ for this
two-year claim would overstate the required liability by 10.5 and understate
the result by the same amount. The shortcut is wrong under the stated rules
and assumptions. A zero rate would remove that discounting difference while
leaving the separate risk adjustment intact. Articles~86(3) and 97 also require
disclosure of the distinct claim components and the PAA/financing choices
\citep{mofasbe25}.

This comparison uses identified editions. The Ministry page reproduces the
2020 ASBE~25 text; Article~120 states 1 January 2023, but that sentence does
not settle every entity group's adoption schedule. The original issuance
schedule and a later 2025 implementation notice remain unverified here. The
retained December 2022 AASB~17 compilation applies to annual periods beginning
on or after 1 January 2023 but before 1 July 2026. The shared result in this
example establishes a scoped measurement comparison, while actual applicability,
later amendments and broader equivalence still require their own evidence.

"""
marker = "Reinsurance has its own group, boundary, recognition time, counterparty risk, cash-flow, CSM/cost"
replace("sections/insurance-methods.tex", marker, insertion + marker)
replace("sections/insurance-methods.tex",
        "possibly loss-recovery component under 60--70A.",
        "possibly loss-recovery component under AASB~17 paragraphs 60--70A.")
replace("sections/insurance-methods.tex",
        "fair-value transition under Appendix C,",
        "fair-value transition under AASB~17 Appendix C,")

with (NEW / "references.bib").open("a") as stream:
    stream.write(r"""
@misc{mofasbe25,
 author={{Ministry of Finance of the People's Republic of China}}, year={2020},
 title={{Accounting Standard for Business Enterprises No. 25: Insurance Contracts}},
 url={http://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/202202/t20220224_3790240.htm},
 note={Cai Kuai [2020] No. 20; official page published 24 February 2022, retrieved 8 October 2026. Selected recognition, measurement, premium-allocation and disclosure articles inspected. Original Chinese retained; English title and interpretations translated. Article 120 alone does not establish the complete entity adoption schedule, later implementation conditions or amendment chain}
}
""")
print(NEW.relative_to(ROOT))
