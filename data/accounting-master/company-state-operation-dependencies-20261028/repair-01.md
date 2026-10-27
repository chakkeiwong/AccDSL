# Preserve the attachment witness namespace

28 October 2026. The first dependency run stopped while preparing its native
comparator: a full attachment witness namespaces history variables separately
from measurement variables. The harness incorrectly requested plain native
history keys. No dependency correctness finding was made from that attempt.

The repair uses the attachment profile's existing key constructor and compares
the complete resulting native history to the retained independent history before
evaluating dependency queries. Old code and the failure are in attempt-01.
Use fresh attempt-02. No native profile or retained witness changes.
