# Successor replay and record status

23 October 2026. Correction 01's digest/completeness interpretation reproduces
from retained bytes. No new request was made. The old completion hashes for
`archive-record.json` and `result.md` are stale after Correction 01. Historical
control snapshots reproduce their hashes, but later live controls need not
match those snapshots. The old verifier's live-control equality requirement
is superseded by `../r05-consistency-recovery-20261023/replay.py`.

The initial `request-plan.json` lists two requests. The successor inventory
records the five performed requests with retained body hashes and header
presence. Exact dedicated transport metadata for all requests is not retained
as claimed in the initial result; it has not been reconstructed or invented.
Old completion records and raw responses remain unchanged.
