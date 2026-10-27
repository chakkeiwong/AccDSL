# Company operating inputs and reports: checked documentary meaning

23 October 2026. Plan: docs/plans/accounting-company-input-closure-20261023.md.
S3/S4; MC13–16/18/23–26/28. Final check: 254 assertions pass across 18
rate/share/borrowing-cost paths, with 23 retained mutation/adverse witnesses.
Command: env CUDA_VISIBLE_DEVICES=-1 python3 -B
data/accounting-master/company-inputs-20261023/verify.py. Measured runtime and
environment, commit and input/output hashes are in manifest.json. CPU only;
GPU intentionally hidden. Seeds are inapplicable to this exact diagnostic.

CompanyYearInputsDraft/1 has a closed schema and separately authored text and
typed examples. The pure evaluator imports a historical CompanyState and its
Context, then derives operating events, claims, journals, taxes and closing
from explicit quantities, prices, asset cohorts and contract terms. It does
not import forecast journals. A separate test removes every Projection record
and obtains the same result. The retained funded-year diagnostic supplies
independent expected outputs; its writer is never run or altered.

Every path matches all journals, cash prefixes, closing accounts and 29 report
lines. Asset memory, inventory, claim controls, indirect CFO, cash and equity
bridges reconcile. Gross borrowing and repayment remain visible. A report
rejects a changed input body paired with an old run. Failed payroll preserves
the prior draw and supplier payment as a dated prefix; requested annual cash
and profit remain unresolved. Unknown dates/eligibility/control remain unknown.

Economic mutations discriminate actual calculation from copied answers:
price11 raises revenue30, profit24, cash21 and receivables3; demand31 raises
purchase5, cost of sales5, profit4 and cash8; delaying the unused12-cost asset
reduces depreciation1, raises profit0.8 and increases cash tax0.2.

The first run matched all18 baselines but failed an erroneous handwritten
price-change cash expectation of21.6. The independent relation is additional
collections27 minus additional tax6 =21. Only that expectation was corrected.
The original check, witness and manifest are preserved. Additional review
added record-hash, fiscal-end, service-date and bridge-settlement guards before
the 179-check run, then reporting increased coverage to254.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain the input successor | Exact traces and changed-input consequences pass | No baseline mutation, imbalance, lost claims or mixed-input report | Initial profile remains a single-cycle annual teaching case | Connect broader operation/admission and repeated-period design | Whole-company language closure |
| Retain partial reporting | Failed/unknown paths do not claim annual totals | Earlier events preserved; missing lines unresolved | General dependency-aware partial execution and durable recovery absent | Specify shared report/status bindings beyond this case | Production transaction semantics |

Red-team: the strongest alternative explanation is agreement caused by shared
assumptions and a narrow case. Mutation cases and absence of projection imports
reduce the copied-answer risk but do not establish general support. A valid
in-scope counterexample to the operation formulas or refusal rules requires
repair. Source-to-method admission, periods/revisions, arbitrary event
multiplicity, broader methods and sectors remain open. This is documentary
reference execution, not an empirical forecast or product runtime.
