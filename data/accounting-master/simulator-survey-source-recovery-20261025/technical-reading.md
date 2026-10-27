# Gentry and Hoque (1990): technical reading

25 October 2026. A distinct primary comparator for S1–S2, MC13/14/23/29/30.
Title: *A Simultaneous Equation Approach to Financial Planning Using Cash Flow
Components*, BEBR Faculty Working Paper 90-1694, October 1990. The retained
46-page university-contributed scan has SHA256
`e2d52c3cb4c55dcaccc6648b52654b75f52d2a7b5174f3532b4faa12dbeabe8e`.
The main printed page number equals PDF page minus eight.

## Method and quantities

Section II (printed pp. 4–6; PDF 12–14) constructs twelve signed cash-flow
components from income statements and changes between balance sheets. Inflows
are positive and payments negative. A starred quantity divides a component by
total cash flow, which the authors define as total inflows or absolute total
outflows. Equation (1), PDF 13, makes the eleven non-cash components sum to the
change in cash and marketable securities. A positive, nonzero denominator is
necessary to evaluate this normalization; the inspected text supplies no rule
for a zero denominator. NOF and FCF are this paper's quantities, not automatic
synonyms for a contemporary statement's operating cash flow or a valuation
model's free cash flow.

The nine-component FCF after working capital comprises NOF, changes in
receivables, inventories, other current assets, payables and other current
liabilities, investment, dividends and fixed coverage expenditures (PDF 14).
The remaining financing and other-asset/liability components reconcile that
sum to cash. Equation (7), PDF 19, prints FCF* = ΔCash − ΔNFF* − ΔNOA&L*.
The cash term lacks the star used in equation (1). This is a visible notation
ambiguity. Our algebra below explicitly uses normalized cash; it does not
silently amend the source or claim the mixed-unit printed expression is equal
to a normalized expression. Equation (2), PDF 18, also prints ΔAR* where the
neighboring equation uses ΔARF*. Both forms remain recorded here.

Section III (PDF 15–19) motivates feedback through receivables, inventories,
production and payables. Equations (2)–(6) posit five behavioral relationships:
NOF depends on receivables, inventory, payables, fixed coverage, dividends and
other current liabilities; receivables depend on payables and NOF; inventory
depends on payables, fixed coverage, NOF and either FCF or cash change; payables
depend on receivables, NOF, inventory, fixed coverage and either FCF or cash
change; investment depends on NOF, fixed coverage and either FCF or cash change.
These relationships are economic hypotheses. The cash reconciliation and the
definition of FCF have a different logical status: they are identities or
defined composites. The paper supplies no contract-level schedule, economic
event generation, recognition policy or journal-state transition implementation.

## Estimation and reported evidence

Section IV (PDF 19) selects 117 companies with December year ends and complete
1982/1983 and 1986/1987 statement data from the annual Compustat Industrial File.
The authors call 1983 a recession period and 1987 a nonrecession period. Those
are their study labels. Section V compares OLS and three-stage least squares
for each year, using FCF versus the alternative cash-change construction.
Only significant estimates appear in the exhibits (PDF 21). PDF 27 describes
sequential removal of insignificant variables and selecting between inventory
and fixed coverage by the resulting system performance. Exhibits 3 and 4
(PDF 34–35) report weighted R-squared of .46 versus .36 for 1983 and .51 versus
.18 for 1987. These are reported sample-fit comparisons after specification
choices; no local replication has been performed.

The inspected method, analysis, references and exhibits do not specify a
reproducible instrument matrix, identification/rank checks, estimator code,
complete firm-level input dataset or a held-out forecast evaluation. A targeted
whole-text search for instruments, residuals, software and appendix found no
such section; the conclusion is limited to this retained version. Common
normalization and the use of a composite containing dependent components are
questions for any future identification audit, not evidence here that a
particular estimator is necessarily invalid. Reported fit and coefficient
signs do not establish causal feedback or future predictive accuracy.

Exhibit 1 (PDF 32) is an illustrative four-company calculation, not an estimated
risk model. The nine-component totals after working capital are 35, 7, −20 and
−25 percentage points. Its financing/other/cash cells contain dashes; the local
check must not fill them with zeros or inferred transactions. The authors' risk
ordering remains their interpretation of the illustration.

## Reading scope and source boundary

Main text, definitions, equations, estimation, interpretation, conclusions and
references: PDF 9–31. All exhibit text: PDF 32–43. Actual rendered checks:
13, 18, 19, 32, 34, 35, 42, 44–46. Pages 44 and 45 are blank scanned leaves;
46 is the library back cover. No appendix appears in this retained PDF. The
front title and metadata establish the working-paper identity. Discovery did
not produce an inspectable official-author code release; the blank built-in
search responses are not evidence that none exists. No external code ran.

The discussion of Francis/Rowell (1978) and Warren/Shelton in PDF 9–11 is
Gentry/Hoque's characterization. It cannot replace inspection of those papers.
This paper closes neither the Francis/Rowell method gap nor the missing
Gentry (1974) derivation and Gentry (1979) version-correspondence gaps.

## Consequence for AccDSL

AccDSL needs to distinguish a derived statement amount from an economic rule
that proposes an event. A definition can be evaluated from its dependencies;
an accounting identity checks their consistency. A behavioral equation needs
assumptions about decisions and information, and a simultaneous behavioral
system also needs a declared solution method and failure semantics. Journal
balance alone verifies none of those behavioral assumptions. This is a design
deduction from the inspected comparison and the existing event/accounting
separation, not an adoption of the paper's estimated relationships.

The next bounded repair should extend existing pure expressions with explicit
reusable functions and check their dependencies, units and unknown values. It
must continue to reject recursive/cyclic calculation and leave endogenous
simultaneous solving unsupported until a separate method is specified. No
fitted coefficients, automatic financing or new empirical default follows.
