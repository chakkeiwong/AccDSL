# Source-span recorder repair

The first recorder call stopped at writeoff_derecognition before creating
source-audit.json or a manifest. Python splitlines counted PDF form-feed page
separators as line boundaries, while the inspected sed/rg anchors count newline
characters. Replaced splitlines with split('\n') for the original PDF text.
This repairs extraction coordinates, not the source or interpretation. Retained
the failure and command here. No successful evidence writer is being rerun.

The second call stopped at allowance_rule before writing evidence. Three later
anchors had originally been obtained with Python splitlines; re-established
them with newline-based rg: IFRS 9 5.5.8 at 35353, 5.5.13-14 at 35411-35421,
and IAS 7 20 at 2928. Updated the source map and recorder consistently.
