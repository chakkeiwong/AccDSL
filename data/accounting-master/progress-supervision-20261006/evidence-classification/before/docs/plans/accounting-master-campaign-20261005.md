# Forty-eight-hour proposal campaign

The user grants 48 additional hours for the full campaign on 5 October 2026
(Hong Kong). Finish the governing proposal through P16–P19, continuing from
the checked MA02a comparison. Product implementation, professional engagement,
publication and spending on new services remain outside this campaign. Existing
authorized model workers continue under their standing grant.

## Intent and evidence

Question: can the existing proposal sequence produce a substantively reviewed,
internally ready governing proposal, preserving MC01–MC35 and G1–G18? The
baseline is P15 accepted and P16 partial at next-plan generation 223. Three full
architecture contracts and the current uncertainty examples are saved; six
contracts, initial profile, integration, P17 methods, P18 manuscript and P19
readiness remain unfinished. Existing versions are retained, including frozen
corpus, accepted evidence and the 79-page manuscript baseline.

Promotion requires all proposal phases' original criteria, checks and completed
independent substantive result reviews, then the existing derived readiness
decision. Structural check counts, source counts, file changes and timely worker
responses cannot substitute for those criteria. Human acceptance stays pending.
File progress and clock use explain execution behavior; they are not design
quality metrics. Missing contracts trigger drafting, missing authority triggers
legitimate source investigation, and review rejection triggers actual repairs.
Integrity loss, ambiguous child ownership, a stop request and the deadline stop
continuation. Repeated no-progress or inaccessible model service requires
supervisor investigation, not an unchanged automatic restart loop.

## Campaign mechanism and skeptical audit

Keep normal two-hour invocations, full worker admission and one initial attempt
plus five retries per phase execution. Add a `campaign` action to the exact
approved master entrypoint. It runs the existing supervisor sequentially and
continues after budget or repair limits only when saved progress and current
eligibility justify another invocation. It uses the current next-plan and
original check/review rules; it does not accept phases or change their scope.

The campaign has one durable state record, a separate exclusive campaign lock,
the existing per-invocation writer lock, and one fixed monotonic deadline with
the host boot identity. Resume preserves that deadline; it never resets another
48 hours. A different host boot requires explicit supervisor recovery because
its monotonic values cannot be compared. UTC records provide human-readable
provenance, not worker time budgets. Current preparation time consumes the
campaign allowance. The nominal deadline is 7 October around 00:30 Hong Kong;
the stored monotonic deadline is authoritative on this boot.

An automatic continuation must honor stop requests between invocations rather
than treating them as explicit user resumes. Stop immediately on controller
veto or interrupted ownership. Permit at most one automatic retry of an
invocation with no substantive file/acceptance progress; existing phase-level
no-progress deferrals remain untouched. A missing eligible phase is a recorded
supervisor-repair stop. Review-only progress may need another bounded attempt,
but cannot justify an infinite empty loop. Preserve every previous run outcome.

Audit findings:

- Simply increasing one run's time leaves a partially completed phase unscheduled
  after its retry cap. A bounded outer campaign loop is necessary for sustained
  execution; no unlimited worker or reset retry counter within an execution.
- Existing `run` archives stop requests because it means explicit user resume.
  Automatic calls need a separate flag that leaves requests intact, including
  one arriving at the next run boundary. Test this race explicitly.
- New invocations must reserve startup plus a complete useful cycle. Stop when
  the fixed campaign remainder cannot admit one; never use a fresh invocation
  to enlarge the campaign deadline.
- Saved files can be only reporting changes. Treat progress as permission to
  inspect the next task, not acceptance; original plan/result review and
  substantive criteria remain decisive. Do not create more completion reports
  as substitutes for unresolved proposal content.
- Provider errors are not mathematical or proposal failures. Retain their actual
  process classification; investigate repeated failure without silently changing
  models, gateways or grants.
- The 48 hours is a work allowance, not a promise of readiness. Source gaps and
  unresolved consequential design choices may survive. Complete feasible
  internal work under MC35 before attributing tasks to future paid review.

Audit decision: implement and verify the small campaign supervisor extension,
then execute. No material direction or permission question remains. The existing
monotonic worker repair, full suites, review receipt, protected hashes and exact
command match must pass before live launch. Verify campaign deadline persistence,
stop propagation, bounded no-progress retry, progression after saved partial
work, readiness stop and veto stop with deterministic injected runs.

## Work order and records

P16 next: MA03a overlap and MA04b projection, then remaining attachment failures,
conditioning, duplicate-evidence protection, likelihood updates and conditional
outcomes. Finish the six full contracts, proposed initial profile and integrated
dependency/acceptance order. P17 completes domain methods and primary-source
support; P18 integrates and inspects the governing manuscript; P19 tests actual
readiness against every original requirement. Advance only when dependencies
are accepted. Review and repair feedback changes the next task, not the mission.

Use `data/accounting-master/campaign.json` for the live budget, invocations and
stop state. Store this controller extension's before-files, review and tests
under `data/accounting-master/campaign-20261005/`. Existing run directories
preserve exact commands, environment, phase evidence and outcomes. Update the
mutable master checkpoint after meaningful state changes. No worker may edit
the campaign state, controller or its review records.

Exact authorized command:

```text
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py campaign --max-seconds 172800
```

The campaign ends on reviewed proposal readiness, a genuine unrepaired
continuation veto, a user stop or its time limit. Per-invocation budget exhaustion
does not end an otherwise viable campaign with sufficient remaining allowance.
