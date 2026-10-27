# Retained context boundaries and concept period forms

All 193 retained contexts support the selected date-only boundary
interpretation, and all 1,127 facts use a context form compatible with their
exact concept declaration. The 98 duration contexts and 95 instant contexts
join 218 duration concepts and 164 instant concepts. They contain 592 duration
facts and 535 instant facts. This is source-level period consistency; full
schema/XBRL validation and financial-time admission remain not_run/Unknown.

The XBRL 2.1 period rule gives a date-only start the boundary at the start of
that day, and a date-only end or instant the boundary at the start of the
following day. Context c-1 therefore runs from 2023-10-01T00:00:00 to
2024-09-29T00:00:00. Both boundaries are untimezoned. Their calendar-day
difference is 364; neither a timezone nor an elapsed UTC interval is inferred.

Context c-114 is a consequential actual witness. Its startDate and endDate
both say 2016-08-30, and f-685, IncomeTaxContingencyNumberOfSubsidiaries, uses
that duration context. The implied boundaries are 2016-08-30T00:00:00 and
2016-08-31T00:00:00. Their strict ordering passes. A rule demanding that the
literal end-date token be greater than the literal start-date token would be
wrong relative to the retained XBRL rule. This witness shows a defect in that
proposed shortcut; it does not assert a defect in the frozen translator, which
preserves the tokens without applying that shortcut.

The context inventory has thirteen distinct source-period signatures. Duration
lengths are one context of one day, four of 91 days, 65 of 364 days and 28 of
371 days. These are descriptive calendar differences, not financial year
fractions or elapsed UTC durations. Equal period signatures do not identify
equal contexts: identifiers, dimensions and other context content remain
separate. Every context and fact occurrence remains preserved.

All observed date tokens are positive four-digit calendar dates without a
timezone. The checker uses XML whitespace normalization and explicitly admits
only that subset. A Gregorian leap/month/ordinal/rollover implementation is
checked against Python date arithmetic for every observed boundary and the
fixtures. DateTime, timezone-bearing, negative-year and long-year forms return
outside_scope rather than a general invalidity verdict. Forever is exercised
as an authored structural fixture; no actual retained context uses it.

The retained XBRL section's explanation says XML Schema prohibits hour 24.
Its own bibliography names XML Schema Datatypes Second Edition, whose section
3.2.7.1 permits lexical 24 when minutes and seconds are zero, while section
3.2.7.2 excludes it from canonical representation. The blanket lexical
prohibition is wrong relative to that cited text. This discrepancy does not
change the explicit date-only boundary rule used here. Its historical cause
has not been checked; the plan's “older” description is not an established
origin claim. No generic 24-hour acceptance or rejection was implemented.

## Evidence and decision

No new acquisition was needed. Nine technical/dependency anchors and seventeen
input bindings retain the XBRL/XSD sources, exact instance, prior inventory,
packet, portable records and declaration sources. The one-time check reports
1,224 counted assertions, thirty fixtures, three rejected source corruptions,
four altered period controls and 1,127 rejected opposite-periodType mutations.
Every actual context byte slice and every fact/declaration join is also checked
inside construction/replay guards. The mutation count is not independent
scientific replication.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept finite period account | 193 exact context records and 1,127 compatible joins | Calendar, source and period-form guards pass | General dateTime/timezone handling remains outside scope | Retain separate interpretations with unchanged source/portable records | Complete XBRL validity |
| Reject literal strict-date shortcut | Actual c-114 maps to a positive one-day interval | Literal equality does not veto implied-boundary ordering | No claim about a particular installed processor | Preserve explicit role-aware boundary requirement | Current frozen translator defect |
| Keep financial time Unknown | All frozen time/calendar fields remain Unknown | No inferred zone or reporting semantics | Actual reporting calendar/timezone and downstream financial mapping | Continue source-supported context/unit/dimension preparation | Historical availability or economic event time |
| Continue program | Protected state preserved; no global continuation veto | Missing runtime acceptance blocks promotion only | Other source/method and independent/domain/human gaps remain | Next inspect four typed-domain values against their exact declarations | Whole-row closure or program completion |

The local target is role-specific, untimezoned XBRL period boundaries and
declared form compatibility. The computed objects equal that target within
the stated finite profile, supported by source anchors and exact retained
joins. They are not the proposed system's admitted financial Context.time.
That mapping remains explicitly unevaluated.

Executed with standard-library CPU Python and GPU devices intentionally hidden:

    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-context-periods-20261020/build_records.py
    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-context-periods-20261020/verify.py --check

No stochastic comparison, upstream execution, dependency installation or
financial default change occurred. The manifest binds the commit, lifecycle
commands, environment, elapsed wall time and outputs.

Post-run challenge: a different effective declaration/DTS or an installed
processor's behavior could differ from the retained-source account. Full
context dimensional validity is the weakest unexamined dependency for broader
admission. An altered source declaration, missing context or contradictory
boundary would overturn its corresponding local record. The explicit subset
and unchanged Unknown fields prevent these checks from quietly establishing a
larger claim.

Version 3.44 remains 396 pages and not_ready. All 53 obligations, six
interactions and 46 operations remain; the additive R08 supplement closes no
whole row. No result invalidated the harness, target, data or research direction.
