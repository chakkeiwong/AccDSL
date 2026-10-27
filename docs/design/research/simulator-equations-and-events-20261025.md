# From financial equations to company events

A company simulator must explain how a proposed sale, investment or borrowing
changes the company's economic position and then its accounts. A system of
financial equations can describe dependencies among annual amounts, but it
leaves another task: deciding which dated transactions produce those amounts.
Gentry and Hoque's *A Simultaneous Equation Approach to Financial Planning
Using Cash Flow Components* (1990) makes that distinction useful for AccDSL.
Its recovered working paper is a separate comparator, not a replacement for
the still-uninspected Francis/Rowell paper or the missing Gentry derivation.

Gentry and Hoque organize twelve cash-flow components from income statements
and changes in balance sheets. Their convention gives inflows positive signs
and payments negative signs. Dividing by total cash flow produces relative
components, denoted by a star. Their equation (1) requires the non-cash
components to sum to the change in cash and marketable securities. Their
free cash flow after working capital adds nine components, including
investment, dividends and fixed coverage expenditures. These definitions
must travel with the quantities: neither NOF nor FCF can be imported merely
because an AccDSL report uses a similar name. [1, printed pp. 4–6]

Let S be the sum of those nine normalized components, N the normalized
financing flow, O the normalized other-asset/liability flow, and C the
normalized cash change. Then the source's reconciliation reads

[S + N + O - C = 0,qquad S = C - N - O.]

The second equality follows by moving N and O to the right. It defines no
borrowing choice and supplies no payment date. A negative S could be reconciled
by different combinations of financing, other flows and cash changes, each
with different future consequences. The source's equation (7) prints an
unstarred cash term; the equation here explicitly normalizes every term.
The discrepancy remains recorded in the technical reading rather than being
treated as a silently corrected edition. [1, equation (1), PDF 13;
equation (7), PDF 19; 2]

The paper also proposes five behavioral equations. It motivates feedback
between receivables, inventory, operating flows, payables and investment, then
estimates relationships using OLS and three-stage least squares. Its sample
contains 117 December-year-end companies, with complete statements for the
two pairs of years used in the comparison. The exhibits report selected
significant estimates; the discussion also describes specification changes
based on system performance. Reported weighted R-squared describes those
sample fits. It does not demonstrate a held-out prediction result or establish
that the estimated responses can govern interventions in a company simulator.
The retained working paper does not supply the instrument matrix, complete
firm-level data and estimation code needed for local reproduction.
[1, printed pp. 10–13, 19–20; Exhibits 3–4; 2]

For AccDSL, the useful distinction is between three jobs. A definition
calculates a quantity from its inputs. An identity checks whether amounts
reconcile. A behavioral rule proposes a decision under stated information and
assumptions. Only the last can lead toward generating economic events, and
even then recognition, measurement and atomic posting remain separate. A
simultaneous system would additionally require solution existence, selection,
failure and information-time rules. The present pure-expression engine
provides no such solver. [2; 3]

Reusable functions are the next small language step. A function can express
the same collection policy at several call sites while preserving declared
types, units, company context and unknown inputs. Its expansion should agree
with the existing expression graph and the resulting complete financial
statements. That establishes reuse of an authored assumption; it does not
estimate customer behavior. Recursive functions and endogenous simultaneous
decisions stay outside this extension until their semantics are specified.
[3; 4]

The software comparison remains similarly conditional. The inspected ACTUS
service expects a local core that is absent from its retained public tree.
Its README and Gradle dependency identify different versions, and the official
developer route requests registration. These observations prevent admission
of a matched implementation here. They do not establish that ACTUS cannot
supply one. Earlier event-ordering, day-count and maturity differences remain
questions for a properly matched adapter. [5]

Sources and checked support:

1. [Gentry and Hoque (1990), retained 46-page working paper](../../../data/accounting-master/simulator-survey-source-recovery-20261025/gentry-hoque1990.pdf).
2. [Technical reading and exact-source boundary](../../../data/accounting-master/simulator-survey-source-recovery-20261025/technical-reading.md), with the predeclared arithmetic check in the same directory.
3. [Existing pure-expression design](../../../data/accounting-master/company-expressions-20261023/design.md).
4. [Audited next function-extension plan](../../plans/accounting-company-functions-20261025.md).
5. [Source recovery and version findings](../../../data/accounting-master/simulator-survey-source-recovery-20261025/source-findings.md).
