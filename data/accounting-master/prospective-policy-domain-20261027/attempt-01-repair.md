# Attempt01 import failure

The first bounded run stopped before domain construction because a predecessor
adds its directory to sys.path and bare import fixtures resolved its fixture
module rather than this unit's fixtures.py. No scientific result was produced.
The failed source snapshots,checks and manifest remain unchanged. The verifier
now loads its exact fixture path under a unique module name. Candidate domain
logic is unchanged. This is an environment/import repair,not research rejection;
no continuation veto. Attempt02 is the next fresh bounded run.
