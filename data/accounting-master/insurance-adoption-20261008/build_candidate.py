"""Create the separate V2.6 source candidate once, preserving V2.5."""
from pathlib import Path
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / "docs/design/proposal/manuscript-insurance-20261008"
NEW = ROOT / "docs/design/proposal/manuscript-adoption-20261008"
NEW.mkdir(exist_ok=False)
for src in OLD.rglob("*"):
    if src.suffix in {".tex", ".bib", ".lark"}:
        dst = NEW / src.relative_to(OLD)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def replace(path, old, new):
    p = NEW / path
    text = p.read_text()
    assert text.count(old) == 1, (path, old)
    p.write_text(text.replace(old, new))


replace("accounting-product-proposal.tex", "Version 2.5", "Version 2.6")
replace("chapters/08-modules.tex", r"""with the retained AASB~17 text \citep{mofasbe25}; the full ASBE~25 adoption
schedule and later implementation conditions remain unverified. Current ASC
access is also unresolved.""", r"""with the retained AASB~17 text \citep{mofasbe25}. The Ministry's 2025
explanation supports the stated entity-class timetable, while Ping An's
reports supply an actual adoption and comparative-restatement example
(Section~\ref{sec:insurance-adoption}). Direct verification of the operative
issuance and implementation notices remains open, including the detailed
conditions of the later simplifications. Current ASC access is also unresolved.""")
replace("sections/insurance-methods.tex", r"""This comparison uses identified editions. The Ministry page reproduces the
2020 ASBE~25 text; Article~120 states 1 January 2023, but that sentence does
not settle every entity group's adoption schedule. The original issuance
schedule and a later 2025 implementation notice remain unverified here. The
retained December 2022 AASB~17 compilation applies to annual periods beginning
on or after 1 January 2023 but before 1 July 2026. The shared result in this
example establishes a scoped measurement comparison, while actual applicability,
later amendments and broader equivalence still require their own evidence.""", r"""This comparison uses identified editions. The Ministry page reproduces the
2020 ASBE~25 text; Article~120 states 1 January 2023, but that sentence does
not settle every entity group's adoption schedule.
Section~\ref{sec:insurance-adoption} distinguishes the Ministry's later
explanation of that timetable from a company's reported adoption. The retained
December 2022 AASB~17 compilation applies to annual periods beginning on or
after 1 January 2023 but before 1 July 2026. The shared result in this example
establishes a scoped measurement comparison. Applying it to a particular entity
still requires its applicable rules and contract facts; later amendments and
broader equivalence require separate evidence.""")

addition = r"""\section{Adoption dates and the restatement of 2022}
\label{sec:insurance-adoption}

A standard's effective date and the economic date of a reported balance need
not coincide. An insurer adopting new rules in 2023 may report a revised
balance for December 2022 while retaining the earlier report as a record of
what it originally disclosed. The system must preserve both versions and
explain which one a calculation uses.

The Ministry of Finance's explanation dated 12 June 2025 describes the original
ASBE~25 timetable. It specifies application from 1 January 2023 for enterprises
listed both domestically and overseas, and for overseas-listed enterprises
preparing financial statements under IFRS or ASBE. Other enterprises applying
ASBE were scheduled to apply the revised standard from 1 January 2026.
Its account of the
2025 notice says existing adopters, including enterprises that had adopted
early under the 2020 notice, must continue applying it. Insurers facing genuine
difficulties and seeking deferral must submit written reasons to the Ministry's
Accounting Department and the relevant institutional supervision departments
of the National Financial Regulatory Administration. That statement does not
establish an automatic deferral merely because preparation is difficult
\citep[answers on background and implementation arrangements]{mofinsurance2025qa}.

The same explanation limits the new simplification choices to unlisted
enterprises; matters outside those choices remain subject to ASBE~25. It names
grouping, measurement, presentation and transition as affected areas, including
comparative information and the transition date. These are source-supported
descriptions of the Ministry's explanation. The operative 2020 and 2025 notices
have not yet been directly verified in this collection, so the explanation
does not supply the detailed conditions needed to implement those choices
\citep[answer on the relationship between the notice and the standard]{mofinsurance2025qa}.

Ping An provides a concrete adoption history. Its 2022 ASBE annual report
states that the group would adopt the revised insurance standard for accounting
years beginning on 1 January 2023. Its 2023 report confirms adoption on that
date and restatement of comparative information
\citep[Note XIV.2, pp.~315--316]{pingan2022asbe}
\citep[Note IV.34, p.~192]{pingan2023asbe}. The following balances all refer
to the consolidated group at 31 December 2022, in RMB millions. The first
column comes from the 2022 report; the second is the restated comparative in
the 2023 report. Changes are calculated from those columns; the asset,
liability and parent-equity changes also match the three rows of Note IV.34's
reported bridge \citep[pp.~146--148]{pingan2022asbe}
\citep[pp.~141--143 and 192]{pingan2023asbe}.

\begin{center}
\small
\begin{tabularx}{\linewidth}{@{}Xrrr@{}}
\toprule
Balance & Original & Restated & Change\\
\midrule
Assets & 11,137,168 & 11,009,940 & $-127,228$\\
Liabilities & 9,961,870 & 9,823,944 & $-137,926$\\
Total equity & 1,175,298 & 1,185,996 & $10,698$\\
Parent shareholders' equity & 858,675 & 869,191 & $10,516$\\
Non-controlling interests & 316,623 & 316,805 & $182$\\
\bottomrule
\end{tabularx}
\end{center}

The distinction between total equity and equity attributable to the parent
matters. Assets less liabilities rise by
$-127,228-(-137,926)=10,698$. Of that increase, 10,516 belongs to parent
shareholders and 182 to non-controlling interests. Treating the parent-equity
row as total equity would leave an unexplained difference of 182. These are
changes between reported accounting bases for the same date, not cash received
in a later period.

The transition also changes how later growth is calculated. Ping An reports
assets of 11,583,417 at the end of 2023. Subtracting its restated 2022
comparative gives a reported-balance increase of
$11,583,417-11,009,940=573,477$. Subtracting the original 2022 amount instead
gives 446,249, mixing the old and new bases and understating that comparable
movement by 127,228 \citep[p.~141]{pingan2023asbe}. The first difference is
a movement in reported asset balances; it is not a cash-flow measure or an
explanation of every economic cause of growth.

An original-source query for assets at 31 December 2022, explicitly selecting
the 2022 report, therefore returns 11,137,168. A query selecting the 2023
report's restated comparison for that date returns 11,009,940. Each assertion
retains its report identity, consolidated scope, RMB-million scale, accounting
basis and economic date. A link records that the later assertion restates the
comparison; it does not delete the original. A request for a comparable annual
movement must reject the mixed-basis pair unless an explicit reconciliation
has first aligned it. Because the basis and disclosure version differ, these
two amounts are not a same-context source conflict.

The information date remains a separate question. The 2023 report says its
board authorised the statements on 21 March 2024
\citep[Note I, p.~154]{pingan2023asbe}. Neither that authorisation nor the
31 December reporting date establishes when the exact retained document became
public. The corpus has archive-date leads but no verified publication date or
historical byte vintage for either selected report. A query for information
available to investors at 31 December 2023 must therefore retain an unresolved
availability result for this source selection; it cannot silently import the
later restated balance. The corpus's October 2026 revalidation timestamps
describe local evidence handling, not investor knowledge in 2023.

Finally, Note IV.34 reports financial-asset reclassification, including use of
the classification overlay for relevant assets derecognised during 2022. It
also states that some insurance groups used modified-retrospective or
fair-value transition because retrospective application was impracticable.
The headline bridge consequently cannot be reconstructed by applying one
percentage to every insurance liability. The example establishes how to retain
and compare disclosed histories; reconstructing the transition itself still
requires the affected groups, asset classifications and underlying measurement
inputs \citep[Note IV.34, p.~192]{pingan2023asbe}.

"""
replace("sections/insurance-methods.tex", "\\hypertarget{interfaces-exclusions-and-acceptance-cases}{%", addition + "\\clearpage\n\\hypertarget{interfaces-exclusions-and-acceptance-cases}{%")

p = NEW / "references.bib"
p.write_text(p.read_text() + r"""
@misc{mofinsurance2025qa,
 author={{Ministry of Finance of the People's Republic of China, Accounting Department}},
 year={2025},
 title={{Questions and Answers on the Notice on Further Implementing the New Insurance Contracts Accounting Standard}},
 url={http://kjs.mof.gov.cn/zhengcejiedu/202506/t20250612_3965540.htm},
 note={Official Chinese explanation dated 12 June 2025 of Cai Kuai [2025] No. 12. All seven answers inspected; the operative notice remains separately unverified. Retrieved 8 October 2026}
}
@misc{pingan2022asbe,
 author={{Ping An Insurance (Group) Company of China, Ltd.}}, year={2023},
 title={{2022 Annual Report: Chinese ASBE Edition}},
 url={https://www.pingan.com/app_upload/images/info/upload/2091cada-04c0-443f-be50-0b1396c10575.pdf},
 note={Consolidated balance sheet, printed pp. 146--148; preparation basis, p. 159; Note XIV.2, pp. 315--316. Bibliographic year refers to the subsequent reporting cycle, not a verified publication date. Retained corpus copy revalidated 2 October 2026}
}
@misc{pingan2023asbe,
 author={{Ping An Insurance (Group) Company of China, Ltd.}}, year={2024},
 title={{2023 Annual Report: Chinese ASBE Edition}},
 url={https://www.pingan.com/app_upload/images/info/upload/55e017c8-da54-42f5-81cc-b4ff9586b461.pdf},
 note={Consolidated balance sheet, printed pp. 141--143; Notes I--III, p. 154; Note IV.34, p. 192. Bibliographic year refers to the subsequent reporting cycle, not a verified publication date. Retained corpus copy revalidated 2 October 2026}
}
""")
print(NEW.relative_to(ROOT))
