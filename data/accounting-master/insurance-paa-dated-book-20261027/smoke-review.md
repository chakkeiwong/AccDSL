# First smoke: complete native run; journal-shape check repaired

The copied native engine completed all eight events and the interim report.
The verifier then failed because it expected a list of journal posting records;
CompanyBookTransition/1 returns a full account-to-change map, including explicit
zeros for unaffected accounts. The complete saved native result is retained in
smoke-01/current-result.json, with its exact original verifier.

Correct the verifier to compare that complete map against independently authored
postings plus explicit zero changes for every other opening account. No financial
calculation, expected amount, native engine or profile has changed. This is a
harness shape error and a repair trigger, not a failure of the financial method.
