# Authored scenarios and joint company results

CompanyScenarioFamilyDraft/1 groups named exogenous scenarios for one company
opening and reporting horizon. Each member embeds the existing complete
CompanyOperationPathDraft/1 input. The family adds identity and selection; it
does not change the accounting of any member. Text places each existing path
inside a named member block. Typed constructors use the same closed structure.

The common opening binds the source bytes and path, opening record, legal
entity/book/currency, assets, claims, drawn facility balance and opening debt
principal. Every member uses that opening and exactly the declared consecutive
periods. Future operation amounts, policy assumptions and resulting balances
may differ. Opening agreement means agreement of these declared fields; it
does not establish that an unknown real company state has been reconstructed.

Members are unweighted. Two differently named assumptions remain distinct even
if their paths or results agree. Their count gives no probability. An empty
family is an empty authored selection, not evidence that the set of feasible
histories is empty. The only coverage statement is authored_members_only.
The reference does not establish historical-family, temporal or forecast
admission and cannot make an exhaustive-futures claim.

Structural validation precedes execution. A duplicate identity or incompatible
opening makes the family invalid. Once admitted, each member executes through
the protected company engine. An accounting failure stays in that member's
result, while the other members retain their own outcomes. A partial annual
report keeps its unresolved lines and known opening balances. A later blocked
year remains an explicit unavailable result, never a zero report or a removed
scenario.

A joint report returns the complete report vector for every member at a
requested authored period, bound to the member's path and full result. It
does not combine a cash result from one member with profit from another or
construct componentwise extrema. The full result also retains the complete
multi-period paths, so dependence between years is not lost. Queries outside
the authored horizon are invalid.

Result verification recomputes every member with the trusted local engine.
Changing a report and recomputing its content hash is insufficient. This is
reference recomputation, not a durable transaction or saved historical run.

## Identity convention

The existing company draft engine hashes sorted compact JSON with Python's
ASCII escape convention. This wrapper uses that same convention for company
path/result identities, including non-ASCII names. These are draft raw-content
identities, not accdsl.portable.v1 typed record digests. The portable contract
uses a different domain-prefixed encoding and a declared legacy mapping is
still required before claiming that portable record identity. Neither encoding
normalizes Unicode code points.

General expressions, endogenous branching, reconstruction of alternative
histories, sector module imports, portable family admission and persistence
remain separate design work. The next extension adds typed policy expressions
whose outputs drive the existing settlement generator, with exact input and
dependency records.
