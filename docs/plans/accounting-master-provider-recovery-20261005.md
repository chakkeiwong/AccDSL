# Recover the saved P16 review after provider throttling

The active task remains the governing proposal (MC08–MC14, MC18, MC25,
MC27 and MC33–MC35 for the saved uncertainty review). P16 has no new
acceptance. Run `20261005T103329-d8cd41b3` delivered the focused source packet
correctly. Both independent reviewers exited with code 1 after an upstream
stream interruption and `429 Too Many Requests`; neither returned a final
review. Both process groups finished without surviving children. The campaign
then stopped at its existing two-invocation no-progress boundary.

## Evidence and decision

Question: is the configured worker service available again so that the saved
independent review can resume? Compare a bounded fresh no-tools health request
with the retained failed requests. Use the same configured model and provider,
read-only sandbox, disabled integrations and structured output. A valid reply
shows only current request availability; it cannot establish sustained service
health, a correct proposal, or phase acceptance. A provider error or timeout
blocks this restart and must be recorded, without an unchanged campaign loop.

The exact upstream cause is unknown: the log does not distinguish account
quota, provider capacity, or another gateway limit. No model, provider,
credentials, global configuration, review criteria or review duration will be
changed. Official documentation retrieval returned HTTP 403 from both official
hosts even outside the sandbox; this diagnosis rests on the saved process
and error records rather than an uninspected documentation claim.

## Reviewed recovery procedure

1. Preserve the stopped campaign, state and active-process records. Verify that
   no campaign writer or worker remains, the saved review still validates, and
   the controller review receipt and protected evidence still match.
2. Make one fresh no-tools health request under a 65-second timeout with a
   five-second forced-cleanup allowance. Save exact command, response and log.
   Do not reuse this health response as substantive review evidence.
3. Only on a valid health reply, record a supervisor recovery boundary referring
   to the failed run, health evidence, previous no-progress count and unchanged
   original deadline. Reset the invocation no-progress counter once, preserving
   all invocation history and phase retry usage. This is an explicit recovery
   after external-service investigation, not a report of proposal progress.
4. Resume the exact authorized campaign command:

   `python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py campaign --max-seconds 172800`

   Require the normal fresh startup suites and actual independent uncertainty
   disposition. A valid AGREE advances to the next specification task; REVISE
   requires its material repair. Repeated provider errors return to supervisor
   investigation. No blanket retry allowance or new 48-hour budget is granted.

Artifacts: `data/accounting-master/provider-recovery-20261005/` and the new
master run directory. The original deadline remains monotonic
`1940875.230219879`, UTC `2026-10-06T16:29:46.450619+00:00`, on boot
`ffea3b13-9fd0-447f-87a1-8f419eed8a63`.

Skeptical audit: a successful tiny prompt is a weak service diagnostic and may
not predict a large review. Therefore it permits only the existing bounded
review attempt, never acceptance or unlimited retries. The focused packet was
already delivered; rewriting the proposal or repairing controller source would
not address the observed external error. The campaign's terminal records and
stopping rules stay intact. The baseline, environment, stop conditions and
saved artifacts answer the stated recovery question. Proceed under the user's
repeated continuation instruction and existing campaign authorization.
