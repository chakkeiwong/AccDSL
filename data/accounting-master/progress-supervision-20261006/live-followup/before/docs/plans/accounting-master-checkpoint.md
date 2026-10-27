# Accounting master checkpoint

Updated 6 October 2026 after progress-supervision repair. The active task
is to finish the governing proposal; product implementation remains disabled.

P15 is accepted internally. **P16 is incomplete:** five proposed contracts exist
(evidence, time, history families, uncertainty and accounting); language/IR,
persistence, interfaces and failure semantics remain unfinished, along with the
initial profile and fourteen decisions. P17–P19 remain pending. The latest P16
work on malformed input, stale versions, request-binding disagreement and digest
corruption has completed editing and checks; its saved bounded review is pending.

## Current execution

The prior campaign stopped cleanly at the supervisor's request before changing
controller files. Invocation `20261005T164323-68702696` preserved the P16 review at
`P16/execution-0/pending-review.json`; its SHA-256 is
`980cead72d0c289f0682566311b2cb94e14d0f1eed2e64e17205ce6d20bc7417`.
The worker group is finished with no survivors.

The [progress-supervision repair](accounting-progress-supervision-20261006.md)
replaces ordinary worker cutoffs with verified milestone monitoring, checkpoint
requests and bounded finishing extensions. A validated unchanged PARTIAL
checkpoint can reach fresh checks and independent review after a timeout without
another editing attempt. The actual process failure remains recorded. Read-only
findings count without edits; repeated reports, logs and clock polls do not.

Review and validation are recorded in
`data/accounting-master/progress-supervision-20261006/`. The new controller receipt
uses the existing supervisor finding-adjudication mechanism and preserves prior
review findings. Startup reruns both required controller/proposal suites. The
932 protected files and pending review were revalidated before restart. These
engineering checks do not accept any proposal phase.

Resume with the exact existing approved command:

```text
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py campaign --max-seconds 172800
```

The original allowance ends at `2026-10-06T16:29:46.450619+00:00` (7 October
00:29 Hong Kong). Monotonic deadline `1940875.230219879` on boot
`ffea3b13-9fd0-447f-87a1-8f419eed8a63` is authoritative and has not been reset.
Ordinary invocations retain their 7,200-second ceiling. Each phase execution
retains one initial editable attempt plus five retries. Extensions are capped by
the invocation/campaign deadline and preserve the editable verification reserve.

Current status and process ownership are in `campaign.json`, `active-process.json`,
`state.json` and `next-plan.json` under `data/accounting-master`. Do not launch a
second copy. The restart receipt identifies exactly which stop request was
archived; any other operator stop remains authoritative. The progress channel is
cooperative, so a provider call that never returns still ends at a bounded stop.

## Prepared candidate inputs

The four authorized isolated packets are complete and imported as candidate
P16/P17 inputs: lease/tax methods, matched accounting authority, filing-adapter
source audit and 31 provisional located annotations across four reports. Use
the [packet index](../design/proposal/methods/preparation-20261005-v1/supervisor/README.md)
and [requirement supplement](accounting-independent-preparation-20261005.md).
The import receipt is `data/accounting-master/independent-preparation-20261005-v1/receipt.json`.
These packets did not accept any phase or close the full requirements.

Current ASC/official ASBE authority, actual contract/tax-law support, full method
coverage, adapter runtime evaluation and adjudicated annotation remain open.
Claude adoption requirements remain in
`docs/design/proposal/architecture/claude-adoption-v1.md`. All MC01–MC35 and
G1–G18 obligations survive staging. Human/domain acceptance and empirical
forecast validity remain unestablished. No paid engagement or publication is
authorized. Frozen corpus/product checkpoints remain unchanged; prior master
checkpoint versions are preserved under the controller-repair baseline folders.
