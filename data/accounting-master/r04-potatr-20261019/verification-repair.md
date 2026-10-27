# First-check repair

The first --check attempt failed before writing checks.json. The numerical
comparison incorrectly required canonical reduced-fraction strings; the
recorded ratio2450000/52031 is exactly350000/7433, but the strings differ.
This is a local checker defect, not a paper or arithmetic failure. Compare
Fraction values rather than representation strings. The input record remains
unchanged and all five deliberately altered numerical controls must still fail.
No completed one-time stage is rerun; the unsuccessful check has no completion
record. Retry the repaired, still-incomplete check, then record once.
