# Company policies constrain, describe and guide activity

A sales target and a credit limit can have the same numerical value while
having different consequences. Missing the target calls for an explanation;
exceeding the limit may prohibit the transaction. A rule that sets a price has
a third role: it supplies an input used to calculate the transaction. These
distinctions belong in company-state construction because they determine what
an operation reads, what it changes and when it may proceed.

Geerts and McCarthy's 2006 extension to REA develops this distinction through
three kinds of enterprise policy: descriptions from which information can be
derived, validation rules, and targets such as standards and budgets (39–40,
54–62). Its contribution is a conceptual account of how policies relate to
resources, events and agents. The authors explicitly set aside differences
between database models and models with integrated procedures (38). Their
policy patterns therefore help specify a simulator, but do not supply its
transition algorithm or a theory of how managers choose actions.

The extension distinguishes a type from a collection. An aircraft can be an
instance of a specified aircraft type and a member of an airline's fleet. The
type describes shared characteristics; the fleet records membership and
properties of that particular collection (41–45, Figures 2–5). Some systems
combine the two, as when an inventory record stores both a product's
specifications and the quantity held. The combination does not remove the
difference between a definition and an observed population. In particular,
the paper's choice to record only a quantity for inexpensive, mass-produced
items is an implementation compromise (46, Figure 6). It is not a proof that
individual identities can be discarded for any future question.

For AccDSL, grouping therefore requires a declared membership rule, dates and
population scope. A year-qualified operation identifier can support a query
about executed events; it does not identify the legal owner of all similar
events in a published report. Nor does membership automatically propagate
through every relationship. The paper illustrates this with aircraft, fleets
and airline alliances (43–45): an alliance has airlines as members, not each
aircraft in those airlines' fleets. Treating every link as transitive would
silently change the population being queried. This is a local implementation
consequence of the inspected distinction.

Policy relations also need explicit endpoints. A carrier may be approved for
a shipment type, or an employee category for a project team (56–58, Figures
13–15). A successful match establishes conformity with that supplied policy.
It does not establish that the policy came from an authorized person, that it
was effective at the transaction date, or that the decision-maker knew it.
Those questions remain separate source and information requirements in AccDSL.
The paper supplies examples of authorization relationships; actual authority
must still be evidenced for the company and action under study.

The same diagram can encode different policy meanings. Geerts and McCarthy
use the relation between aircraft types and flight types both to restrict
permitted assignments and to attach a fuel-consumption target (49–52). They
explicitly describe their five patterns as heuristic and nonexhaustive (52).
Consequently, the shape of a relation cannot tell an implementation whether
to reject an action, derive a quantity or report a discrepancy. The requested
effect must be part of the declaration.

Their pricing example makes the assumption behind a derivation especially
clear. A product inherits its type's price only under a company rule that
allows no discounts or discrepancies (54, Figure 11). Reusing such a rule for
a company that negotiates prices would compute the wrong transaction input.
Likewise, a minimum-price rule checks an actual price; it does not replace
that price with the minimum (55–56). A budget stores a planned amount beside
a running total of actual sales, and a variance compares the two (60–62,
Figures 17–18). No probability distribution for future sales follows from
that comparison.

AccDSL already contains a useful but narrower policy mechanism.
`SettlementPolicyDraft/1` names delivery claims, collection operations, a
fraction and installment shares. Its generator creates a conditional child
path by changing specified allocation amounts. It requires execution of that
path and explicitly leaves information admission unresolved. It is therefore
an input-generating scenario rule. It is neither a collection target checked
against an unchanged history nor evidence that customers will pay the
specified fraction. The retained test that fully settles year-two claims and
then encounters an over-settlement in year three illustrates why generation
and execution must remain separate.

For this native owner, three operations should consequently stay distinct.
A generator produces proposed inputs while retaining parent and child
identities. A constraint inspects a supplied value or relationship and returns
its scoped validity result. A target comparison reports actual and planned
quantities without rewriting the history or treating a variance as an
execution failure. The common definition must also state units, membership,
effective dates, observation status and unknown-input behavior. These are
AccDSL design deductions, not functionality delivered by the paper.

Commitments require their own further reading. This article develops policy
descriptions and their links to actual events; it does not provide an account
of contract formation, fulfillment, cancellation and enforceability sufficient
to implement those processes here. Its 2000 ontological-foundation reference,
the extended-REA economic-primitives article and the later monograph remain
separate technical-reading items. Sedbrook and Newmark's 2008 automation paper
is also a direct implementation lead found in the title search, with its
method and software still uninspected. The present comparison sharpens the
simulator's specification without closing those omissions.

Source: Guido L. Geerts and William E. McCarthy, Policy-Level Specifications
in REA Enterprise Information Systems, Journal of Information Systems 20(2),
2006, 37–63, DOI 10.2308/jis.2006.20.2.37. All 27 pages of the retained
author-hosted published article were read, including examples, qualifications,
footnotes and references. Selected figures and tables were checked in rendered
pages. Source identity, reading scope and dated metadata are retained under
data/accounting-master/company-state-rea-policy-reading-20261028/. The native
comparison inspects company-policy-20261023/policy.py and its retained
relationship-policy continuation; it does not import an external implementation.
