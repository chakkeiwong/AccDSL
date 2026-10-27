# Two-event condition audit

The first event is the complete repaired ConditionalReturnStateFamily/1
settlement, including all original state, quantity, cash, funding and lot checks.
The second event is a whole-lot sale of the same newly created lot. Full starting
state and fixed event identities define collection topology; neither event is
selected from a witness. The scalar unknowns and all first branches remain.

| Condition | Exact enforcement before/within the joined formula |
| --- | --- |
| First settlement and complete opening | Unchanged first compiler, constraints and condition audit |
| Sale schema/method | Original closed event schema; explicit sell and inventory.sell |
| Sale event identity | Different from first event and every fixed opening seen ID |
| Sale lot identity | Exactly first event's new lot; existence follows from first settlement |
| Sale chronology | Canonical date >= first date and < fixed period end; first chronology already bounds opening/start/tax close |
| Performance and fraction | Fixed original finding true and exact fraction1; unknown unresolved, false/fractional unsupported |
| Sale proceeds | Known exact rational or domain for explicit unknown only; >=0 |
| Sale cost | Symbolic first carrying expression, same created lot, explicit dated continuity premise |
| Sale posting/flow arithmetic | Compile original checked sale definition's ref/const/add/sub expressions with shared cost/proceeds |
| Funding | First constraint retained; first cash plus sale cash >=0 |
| Inventory/lot allocation | Sale removes shared carrying amount from account and zeros same lot carrying,units,tax_base |
| Other state and lifetime records | Original memory operations; distinct event appends seen/flows; original two-event replay checks complete state |
| Intermediate/terminal observations | Explicit prefix account, exact type/date, original domain/premise/source; all constraints conjoined |

Settlement quantity and cost/NRV conditions imply nonnegative live lot values.
The later sale marks that lot disposed and zeros its numerical fields, preserving
all other lots and component/tax state. Equal terminal states do not erase earlier
states or their constraints. Complete original replay checks every feasible
assignment; a replay mismatch vetoes the implementation instead of proving
empty family. General structural branches and repeated arbitrary events remain
outside this explicit fragment. No unsupported context conversion is performed.
