# A promise and its fulfillment need different records

An order can constrain a company's future deliveries before any inventory has
left the warehouse. A reservation may reduce what can be offered to another
customer while leaving the stock physically unchanged. A company simulator
that records only completed purchases, sales and payments can reproduce an
accounting balance yet miss those restrictions on its next action.

Geerts and McCarthy's extended REA analysis makes commitments distinct from
economic events. In Section 4.1, commitments describe obligations to trading
or production partners, with differing degrees of enforceability; events
describe actual acquisition or consumption. The examples are flight and hotel
reservations (author manuscript, physical page 7). This is a conceptual
distinction. The article does not turn every promise into an enforceable
liability or prescribe when accounting recognition occurs.

The associated relationships make the distinction usable for state design.
Section 4.2 links a commitment to its executing event, involved agent, reserved
resource and reciprocal commitment (physical page 8; Figure 4 on page 17).
An order and the sale that fulfills it are therefore linked records with
different meanings. A reservation can identify a resource, and commitments
on opposite sides of an exchange can identify each other. Section 4.3 treats
contracting as bundling commitments for exchanges and scheduling as bundling
commitments within conversion processes (pages 9–10). These descriptions
identify relationships that a simulator may need; they leave the particular
contract terms and execution rules to be specified.

The current native company path covers a different part of that chain. A
delivery creates a named trade claim after its supplied control-transfer
condition passes. Collections settle those claims through explicit allocations.
The relationship inspector preserves recognition, settlement and remaining
amounts over the executed history. Its schema supplies neither an order
population nor reservation, amendment or cancellation operations. Calling
those existing claims commitments would obscure what has already occurred
and what is merely promised. Conversely, inventing an opening receivable for
every proposed order would add an accounting effect that the native contract
does not justify.

The policy distinction also matters here. A target says what management
plans; a commitment records a particular obligation or undertaking. The
2006 policy patterns compare planned and actual quantities or restrict
permitted combinations. The earlier extended ontology places commitments
alongside events in its account of what has occurred or been committed to
(Section 2.2; physical page 4 and Figure 2). These uses are compatible when
their meanings remain explicit. Neither a target comparison nor the existing
settlement-path generator establishes that a counterparty undertook an
obligation.

For AccDSL, the next definition should consequently identify the commitment,
its parties, subject, units, dates and evidence separately from the operations
that fulfill it. A fulfillment link needs an allocation rule: whether one
event can fulfill several commitments, whether fulfillment can be partial,
and how the remaining obligation is computed. A resource reservation needs
its own availability rule and release conditions. Amendments and cancellations
need dated versions so that a query about the original promise is not
answered with only the latest terms. These are local requirements derived
from the intended historical and action queries; the article does not provide
their algorithms.

The same care applies to responsibility and knowledge. The article separates
custody, participation and stable agent relationships (Section 4.2). Knowing
which employee is responsible for a resource does not establish that this
employee could authorize its sale or had received a revised order. A usable
actor decision rule must name its information and authority independently.
The existing audit-only requests continue to refuse actor views until those
meanings are supplied.

The source's limits are explicit. It excludes task-level components from its
ontological analysis, calls important mediating categories tentative, and says
that procedural axioms for derivable accounting conclusions require substantial
further development (Sections 2.2, 4.3 and 5; pages 4, 9–11). It therefore
supports the relationship distinctions without proving that its categories
form a complete executable company model. The published discussion by James
C. Lampe is a direct critical source that remains unread: its repository
record was retrieved, but the available routes supplied no full text. No
view is attributed to that discussion from its title alone.

Source: Guido L. Geerts and William E. McCarthy, An ontological analysis of
the economic primitives of the extended-REA enterprise information architecture.
The corresponding publication is International Journal of Accounting
Information Systems 3(1), 2002, 1–16, DOI 10.1016/S1467-0895(01)00020-3.
The retained author-hosted version has 19 physical pages with figures collected
at the end. All text and six figures were inspected. Its title and authors
match the published metadata; exact textual equivalence to the publisher's
16-page version has not been checked. References here use sections and
physical author-manuscript pages, preserving that version distinction.
