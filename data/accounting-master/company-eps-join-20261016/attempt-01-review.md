# First-attempt post-run audit and repair

Attempt01 passes all1470 recorded financial/projection checks; its files and
input code are retained. This does not complete the interface audit. Inspection
found two material omissions: the base packet reference was calculated afresh
and compared as a string, without checking its current bytes against the
predecessor manifest; and an explicitly incomplete inventory was classified
as unsupported instead of unresolved. Both defects require repair despite
correct numeric results. The request/result also needed published closed schemas.

The second run (directory `attempt-03`) pins the base digest to the P5 run-manifest's attempt03 hash, checks
resolved base/premise bytes, adds independent missing/corrupt-byte resolver
challenges, and publishes closed schemas. Incomplete inventory/share/consequence
findings return unresolved. The independent financial expectations are unchanged.
These are harness/contract defects, not evidence against the accounting idea.

The attempt-directory counter originally included this review note among its
glob matches, so the second run was named `attempt-03`; there is no missing
`attempt-02` run. The counter now examines numbered directories only. This
filename-only repair does not change the accepted financial or schema checks.
