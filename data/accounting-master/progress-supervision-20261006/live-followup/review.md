# Live follow-up review

The first monitored read-only review completed cleanly and supplied two verified
reports after acknowledging checkpoint/finish instructions. The subsequent
planner had no final response and no verified finding at the grace boundary.
Its clock displayed about 360 ordinary seconds remaining when its actual grace
had only 120 seconds. This is a controller communication defect. The repaired
helper displays the grace limit, marks response due now, and gives a role-neutral
instruction; it does not tell a read-only planner to submit an editable PARTIAL.

The same invocation finished a clean bounded review but campaign accounting
recorded no progress because there was no edit or newly accepted full phase.
The new accounting checks a current-run, phase-bound terminal review and clean
process record. It does not count replayed reviews, output chatter, plans,
provider failures or unsuccessful processes. Historical manifests remain intact.
The recovery receipt records the corrected consecutive-no-progress calculation.

Supervisor audit passes: these two changes correct the evidence actually seen;
they do not weaken phase acceptance, add retry allowance or reset the original
campaign deadline. 232 controller tests and 21 proposal tests passed, with no
skips. The supervisor reviewed the modified helper, scheduling function and
regressions. Independent proposal review remains separate.
