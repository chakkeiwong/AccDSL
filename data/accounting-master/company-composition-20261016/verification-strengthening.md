# P5 verification strengthening after attempt01

Attempt01 passed680 checks with no failures. Post-run audit found that the
request byte files were hash-bound but were not independently decoded into the
corresponding registered requests. The verifier now decodes each actual file,
rejects noncanonical bytes and unknown fields, and checks its exact registry
identity. This strengthens the exchange evidence; it does not change accounting.

Additional diagnostics exercise stale heads/views, unpublished report receipts,
unpublished replay decisions and noncanonical fractions. Proposal output must
also bind the exact requested basis and authorization. Attempt01 stays intact;
attempt02 snapshots the stronger verifier and all current input bytes.
No failure criterion was relaxed, and no continuation veto fired.

A second final audit found the opening group-equity/NCI bridge still used642
and20 as constants. They now derive from the declared legal opening capital,
retained amounts and investment, removing a self-confirming shortcut. Attempt03
preserves this stronger independent derivation; the numerical target is unchanged.
