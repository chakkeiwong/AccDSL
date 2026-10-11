# Author review

The SEC body identifies HSBC Holdings plc and one original 2023 Form 20-F
within the stated recent-array scope. The issuer-hosted cover was visually
read at normal resolution and agrees on issuer, form, fiscal period and
filing date. The selected annual-report cover was also visually read; it
shows Accounts 2023. Both final PNGs are copied by the same render settings
from the checked PDFs and retained with hashes in event.json.

The initial check assumed the annual-report title would be one contiguous
extracted phrase. It failed before writing outputs because extraction
returned “Annual Report and Accounts 2024 Accounts 2023.” The rendered
cover shows the 2023 label; 2024 is not visible. The repaired check preserves
both raw anchors and requires this visual review. No source bytes were
edited, and no wrong-report or E05 conflict claim follows from the extra
extracted year. The successful rerun passes all 22 checks.

Engineering checks support the bounded parsing and preservation. Source
review supports the filing event and visibly different document covers.
Full document equivalence, original filed bytes and selected annual-PDF
availability remain not checked. This is author source review, not
independent acceptance, manuscript readability certification or accounting
approval.
