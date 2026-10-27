# Controller Git provenance repair

3 October 2026, Hong Kong. Scope: MC34 and master-program provenance.
Both supervised invocations have ended. P00–P07 are accepted internally;
P08 is next. No phase implementation or acceptance is changed by this repair.

The controller hard-codes that the Git marker is unusable even though the user
separately authorized repository initialization. P07's checker now observes Git
correctly. Correct the controller's future run manifests while preserving all
historical manifests and their hashes.

Skeptical audit: HEAD alone does not identify uncommitted work; existing content
hashes remain required. A failed or missing Git command must not invent a commit
or stop otherwise valid work. Use a bounded, read-only `git rev-parse --verify
HEAD` in the actual project directory, validate the returned object ID and record
an observed failure reason. The five-second bound matches the P07 metadata
probe and is an operational convenience, not a numerical default. No fetch,
initialization, index update, commit or permission change is part of the probe.

Question and primary criterion: do future manifests report the observed commit
or an accurate unavailable reason, while retaining content hashes and unchanged
phase behavior? Tests cover successful reads, invalid output, command failure,
missing executable, timeout and manifest wiring. Failed control-plane
regressions or changed accepted evidence veto completion. Test counts and
timings are descriptive; no new accounting or forecast conclusion follows.

Audit decision: proceed with this narrow controller/test change, run the full
controller suite, inspect the diff and exercise the actual local Git probe.
Record supervisor review of the changed metadata call chain in this note and
bind the existing supervisor-adjudication receipt to the new hashes. This is
supervisor review, not a new independent-model controller review. Refresh the
next plan only after verification. Preserve before files and results under
`data/accounting-master/provenance-repair/`.

## Verification and supervisor review

The changed call chain runs one fixed Git argument list in the project directory,
with a five-second timeout and no shell or repository mutation. Successful output
must be a 40- or 64-digit hexadecimal object ID. Missing executables, timeouts,
nonzero exits and invalid output produce a null commit and an observed reason.
The manifest still includes controller and catalog content hashes. Existing
historical run files are not rewritten.

All 95 controller tests passed in 14.791 seconds, including three new tests
covering the metadata probe and actual run-manifest wiring. The live probe
returned `8e3b2628df8c89f7315119170b82624d536bc3e5`, matching the repository HEAD.
The supervisor inspected the two-file diff and found no change to scheduling,
phase acceptance, repair, source protection or permissions. Python 3.11.15 and
standard-library CPU tests were used; no accelerator framework was imported.

| Decision | Primary criterion | Veto status | Main limitation | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept this metadata repair | Observed Git identity/failure and retained file hashes; 95 tests pass | No regression or changed accepted-phase evidence | HEAD excludes uncommitted work; file hashes remain necessary | Bind supervisor review to current controls and refresh the next plan | Accounting/forecast validity or whole-mission completion |

This finding corrects future controller manifests. Historical records retain
their original, stale Git message; the completion and Git checkpoint notes
provide the dated correction. The strongest alternative explanation for a
successful probe is that it identifies a commit while relevant files are dirty;
retaining the existing content hashes addresses that limitation.
