# Declared company period reports

CompanyBookReport/1 request fields:profile,opening,closing,schemas,mapping,
expected_opening_sha256,expected_closing_sha256,expected_mapping_sha256,
equity_movements,notes. Both books pass CompanyBook/1 validation. Context,period,
account declarations and cash account agree. Each memory schema/types pair validates
independently: a period can add module memory without changing the statement map.
Reporting does not itself validate that intervening memory migration. Opening date equals
period.start,all opening income/expense balances are zero,and opening flows are
empty. Closing date is no earlier;opening seen IDs are an exact prefix. These
choices specify a bounded recorded-period report,not arbitrary comparative views.

CompanyStatementMap/1 fields:profile,context,lines. Each line declares id,label,
classification,accounts;every account appears exactly once and agrees with its
book classification. A line cannot mix assets/liabilities/equity/income/expense.
IDs and account memberships are unique;all five category totals exist,even when
a category has no account. Do not invent an account for an empty category.

Let b be debit-positive balances. Reported assets A=sum asset b;liabilities
L=-sum liability b;direct equity E=-sum equity b;income R=-sum income b;expenses
X=sum expense b;profit P=R-X. The trial balance implies A-L-E-P=0. Reported
equity including profit is E+P. Contra balances remain signed,not forced positive.
Line balances use the corresponding category sign. Opening income is closed.

Gross cash flows retain every recorded row and origin. For each declared activity,
receipts=sum(max(amount,0)),payments=-sum(min(amount,0)),net=receipts-payments.
Their aggregate must equal closing cash minus opening cash. No classification is
inferred from account names and no missing flow is manufactured.
Every flow must refer to an event in the closing history after the opening prefix;
a historical event identity cannot be reused to explain this period's cash change.

Equity_movements is a list of id,event_id,date,account,amount,description. Amount is
credit-positive direct equity change. Each account is classified equity;event_id
must occur in the closing seen suffix;date lies in the report interval. For each
equity account,declared movements equal -(closing balance-opening balance). Then
opening direct equity + movements + profit equals closing equity including profit.
The engine never substitutes a residual movement. These supplied explanations are
not journal-level proof of their economic cause,which remains a separate lineage
obligation until event-level journals are included.

Notes are explicit diagnostic requirements,not asserted disclosures. Each row has
id,label,status,reason,where status is missing,unsupported or unresolved. Preserve
their exact content in the report. This initial profile cannot mark a note complete
or claim a full note package. Output always states recorded_period_only and
fiscal_complete:false,source_admission:false,accounting_admission:false.

Output includes company/period/as-of,all account-mapped statement lines,category
totals,profit,gross cash-flow activities,opening/closing cash,equity rollforward,
all exact reconciliation residuals,notes and source/request hashes. Every required
residual must be zero or the report is invalid. Replay is canonical JSON equality.
Indirect cash-flow reconciliation,OCI classification,comparatives,closing and carry
remain separate;reporting performs no mutation.
