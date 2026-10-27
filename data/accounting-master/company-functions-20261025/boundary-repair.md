# Boundary fixture correction

The initial 20 focused tests passed. An added alias-only expansion test expected
120 calls of a 16-function chain to fit the 2,048-scope budget. It failed with
Invalid:expansion_scope_limit. This was a fixture arithmetic error: validation
of all 16 templates consumes 1+2+...+16 = 136 visits, and the main scope adds
one. Therefore 119 calls consume 136+1+119*16 = 2,041 visits; 120 consume 2,057.
The test now checks 119 succeeds and 120 refuses. The compiler did not change.
The design now states the scope-visit bound explicitly alongside emitted nodes.
This is a harness repair, not evidence against pure-function semantics.
