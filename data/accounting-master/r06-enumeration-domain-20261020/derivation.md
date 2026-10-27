# Why the retained simple graph answers this bounded question

The source-defined allowed domain consists of usable members reached through
effective domain-member relationships in the declared role, including the
head only when headUsable is true. The selected declarations all state
headUsable=false.

The retained-map inventory checks every one of its 27 resources. The relevant
base set has two extended links, 718 arcs, one link/arc QName pair and one
arcrole/role pair. All source/target locators resolve to retained direct
xbrli:item declarations. No XML Base, directed cycle, use, priority, usable,
targetRole or other unreviewed arc attribute is present.

Under XBRL 2.1 section 3.5.3.9.7, absent use means optional and absent priority
means zero. Within an equivalent-relationship class, one highest-priority
optional relationship survives. Equivalent relationships have the same
source and target fragments; selecting one cannot change reachability.
Non-equivalent relationships have no prohibiting/higher-priority competitor
under this inspected profile, so their endpoint edges remain represented.
The actual 718 endpoint pairs are unique, although the argument does not
require that stronger observation.

Dimensions section 2.5.3.3 makes absent usable true. No targetRole changes
the role followed by a consecutive relationship. Therefore the effective
usable reachable member names, within this retained base set, equal ordinary
directed reachability from each declared head, excluding the head itself.
The checker retains a path witness for every reached member and rejects
scope expansion when any exceptional arc attribute appears. It is not a
general effective-relationship implementation.

The resulting four retained domain sizes are 14, 5, 4 and 9 for AssetsAbstract,
LiabilitiesAbstract, LiabilitiesCurrentAbstract and LiabilitiesNoncurrentAbstract.
Each actual expanded-name URI maps exactly to a member in its own domain.
No URI rewriting, case folding, percent decoding or namespace substitution
is part of that comparison.

After XML whitespace collapse, an enumeration-set spelling is split into its
ordered tokens. Sections 3 and 6.1 distinguish the unordered semantic set
from the required unique, lexicographically ordered representation. The
actual names are ASCII, so code-point lexicographic comparison supplies the
stated order without a locale or Unicode collation assumption. The source
permits an empty set. Sorting or deduplicating a failed source spelling would
change the reported evidence and is not performed.

The equality established here is between the selected source-defined
retained-network membership/set conditions and the local finite calculation.
It does not identify an installed DTS, complete discovery behavior, full
schema validity or financial correctness. Unknown resources or a different
effective type/network require a new result.
