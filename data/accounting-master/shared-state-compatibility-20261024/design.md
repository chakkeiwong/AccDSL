# Compatibility of native book views

SharedStateCompatibility/1 accepts left and right closed views, each containing
module_id, state and state_sha256. Only typed_return and shared_lease are
registered. It validates exact state bytes through canonical identity, then
uses each original structural/invariant validator. It compares owner, legal
book label, currency, date and period without renaming values.

Compatible means two valid identical snapshots of the same native profile. It
does not authorize combining events. Incompatible means a known contradiction
or invalid native state. Unresolved means missing context or a native unresolved
condition without an overriding contradiction. Malformed outer requests and
stale state digests are invalid. Known invalidity is not hidden by an unrelated
unknown field. All execution, admission and composition flags remain false.

Different profiles always lack an implemented cross-profile state adapter.
The report lists overlapping account names and each side's additional accounts;
overlapping names prove no semantic equivalence. The return profile has 22
accounts, while lease uses the 26-account corporate registry. Returns store
recovered lots, tax adjustments and fiscal history; leases store named rights
and allocation membership. Their flow records differ too.

The retained examples disagree on owner, book spelling, start date, current
date and profile. Both are USD. Lease fixes its original source scope, while
return validates source/owner labels structurally. Even relabeling the lease
fixture to look like the return fixture cannot establish valid composition.

Original positive proposals remain separate comparators. Their exact journal
deltas sum to zero, cash equals gross-flow totals, and all unaffected top-level
state fields remain byte-equivalent. This confirms the small method controls;
it supplies no cross-book mapping, issuer facts or durable transaction.
