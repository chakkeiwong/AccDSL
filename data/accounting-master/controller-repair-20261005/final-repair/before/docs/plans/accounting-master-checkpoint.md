# Accounting master checkpoint

Updated 5 October 2026 after the follow-up controller repair. The active task
is to finish the governing proposal; product implementation remains disabled.

P15 is accepted internally. **P16 is incomplete:** four proposed contracts
exist; five contracts, the initial profile and fourteen decisions remain open.
The saved independent uncertainty review is valid. P17–P19 are pending.

## Current execution

The master is stopped immediately before a reviewed restart. Run
`20261005T083051-60af77f3` passed 210 current tests, then independent controller
review identified six additional defects. It stopped cleanly without attempting
P16. Those defects are now repaired: prepared worker evidence and runtime
records are checked, configuration queries use bounded registered processes,
current readiness is revalidated, test injection is isolated, and built-in
primary deliverables are verified. The updated suites passed **198 controller
and 20 proposal tests**. Fresh independent startup review is still required.

Use the [audited repair plan](accounting-master-controller-repair-20261005.md),
[follow-up result](../../data/accounting-master/controller-repair-20261005/followup/result.md)
and `data/accounting-master/controller-repair-20261005/followup/resume-record.json`.
The recorded supervisor recovery preserves both controller-only failures and
the prior no-progress count; it admits review of the changed, tested controller.
No accepted phase evidence or frozen source was rewritten.

Next run the exact existing approved command; inspect startup review and repair
any actionable findings. After acceptance, resume the saved P16 uncertainty
review read-only, then plan accounting/state-transition specifications and the
remaining architecture contracts/profile/decisions.

```text
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py campaign --max-seconds 172800
```

The original allowance ends at `2026-10-06T16:29:46.450619+00:00` (7 October
00:29 Hong Kong). Monotonic deadline `1940875.230219879` on boot
`ffea3b13-9fd0-447f-87a1-8f419eed8a63` is authoritative. It has not been reset.
Ordinary runs have a 7,200-second ceiling; one initial editable attempt plus
five retries per phase execution remains the cap. Current process ownership,
review, phase and budget state are recorded in `active-process.json`,
`controller-review.json`, `state.json`, `next-plan.json` and `campaign.json`
under `data/accounting-master`. Do not start a second master.

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
