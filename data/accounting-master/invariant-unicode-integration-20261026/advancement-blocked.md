# Shared baseline changed before advancement

The local 728-page Version 5.12 candidate was built and reviewed but was never
advanced. The advancement guard failed before any control writes when the stable
standalone link no longer matched the expected Version 5.5 hash. Investigation
found a concurrent literature integration: the stable main link selects the
741-page literature Version 5.12 (87da6f2a6bd7c56ea7718202047b9722b3de0b4e22e7f3aa4638d0a7fcb64622),
and the standalone selects its 183-page Version 5.12
(63bad80014136b6fa6e3cf1c984aa11df797fd33ac66ea56fb7ddbe7451846d5).
The original standalone file remains unchanged. No corruption is inferred.

The literature successor preserves the complete-claims work and leaves both
Unicode target sections byte-identical to Version 5.11. Its 234 source files
are the new baseline. Reapply only the same two Unicode prose corrections and
advance the cover to Version 5.13 in a new directory. Preserve both earlier
candidates and all literature changes. Do not rerun this advance.py.

The concurrent update changed stable links and some prose controls, while the
two JSON execution controls and recovery memo still name Version 5.11. Reconcile
those current pointers after the combined candidate passes; preserve all prior
control contents and literature residuals. This is a repairable concurrency
condition, not a scientific or user-decision blocker.
