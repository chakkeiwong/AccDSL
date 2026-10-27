# Conditional first tax assessment after carry

FollowingPeriodCurrentTax/1 binds the complete AssessedSharedPeriodCarry/1 request
and digest,unique identity,explicit first_period_accrual_no_credits_v1 selection,
interval,complete information,allocations and loss policy. Require a complete
provisional incoming execution and no new-period current-tax expense or prior
assessment. The interval begins at the financial opening and loss cursor,ends
after that start and no later than the financial endpoint,and includes all
completed events through its final included day.

Before computing new tax,derive opening payable P0 and exact dated carried-tax
payments S from the incoming trace. Each payment consumes only P0,so remaining
payable must equal P0-S with 0<=S<=P0. Every actual payment flow must match those
events. No payment is reclassified as a new-period credit. The carried vintage
records the old assessment identity,interval,result hash,opening amount,
settlements and remaining balance.

Calculate taxable profit from new-period pretax accounts plus explicit complete
adjustments,with each native return adjustment allocated exactly once. Require
known item basis declarations and lease-right/account reconciliation as in the
current-tax information profile;these declarations do not assess deferred tax.
Use the actual carried loss inventory and preserve all prior history. Apply the
selected close-day usage/expiry/generation rule exactly once over the new
interval. No automatic FIFO,refund,credit or DTA arises.

New tax C debits current expense C and credits tax payable C. Aggregate payable
becomes P0-S+C;cash and deferred balances are unchanged. The new vintage records
its interval,request hash,assessment C,no settlements and balance C. Their sum
must equal the actual payable. Keep both histories even when a balance is zero.
Report from the carried financial opening using changes in aggregate payable;
retain full predecessor,loss result and four exact financial ties. The conditional
current assessment endpoint advances externally without claiming a native annual
tax close. Deferred tax in the new period remains unassessed.

Pure apply compares the full recomputed result and retains state,opening,vintages,
losses,information and unresolved findings. Subsequent payments by vintage,
cumulative new-period reassessment,refunds,deferred reassessment and repeated
carry require successor interfaces. No durable journal or annual admission.
