# Post-run call-chain repair

The first company run passed242 checks and all independently expected values.
The numerical target passed, but the report wrapper accepted a separately
supplied internal base replay. Its source bytes were pinned without enforcing
that this argument was reconstructed from them. The final endpoint must build
that base itself. Remove the base argument and replay after source resolution;
preserve the initial implementation under the first attempt directory.

The EPS selector actually loads `record-schemas.json`; pinning only its schema
generator was insufficient dependency evidence. Add a separate runtime-input
lock using the existing immutable3.15 packet's schema hash. Keep the original
authored input lock unchanged. Verify the loaded schema plus base/source inputs
before accepting a report. These are provenance/call-chain repairs, not changed
fiscal assumptions or expectations. Retry within the same authorised plan.
