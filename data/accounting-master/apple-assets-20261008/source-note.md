# Inventory and PP&E source reading

8 October 2026. The full annual and interim Note 5 spans are partitioned into
seven units, covering twenty-four monetary cells. Ten dependency spans preserve
FIFO/straight-line policy, fiscal/basis context, statement tables and two
previously inspected lease passages. Only selected rows within statement
context spans are formalised; this is not a complete reading of every statement
transaction or complete Apple semantics. Eight query examples state the
supported answers and unresolved inputs.

Original annual PDF pages 34, 36, 37, 42 and 45 were visually inspected at
readable resolution (printed pages 31, 33, 34, 39 and 42). The retained interim
HTML inventory/PP&E, balance and cash-flow tables were inspected in a three-page
derived print view, including both date headers, signs and relevant totals.
Inline-XBRL namespace unwrapping preserved text. The print layout is not an
original browser screenshot and contains some harmless background-decoration
spill. Source HTML/PDF and extraction hashes remain pinned; no network ran.

The annual and interim September values agree across statements and notes.
Gross PP&E classes sum, gross less accumulated depreciation equals net, and
both inventory components sum at each interim date. Annual/interim operating
reconciliation rows sum to the displayed cash-generated totals in all five
period columns. This is arithmetic/context evidence, not source correctness
or a model of each underlying cash transaction.

Annual inventories rise 955 million while the indirect cash-flow adjustment is
−1,046, leaving −91 relative to minus the balance change. Quarter inventories
fall 375 while the adjustment is +215, leaving −160. Components fall 835 and
finished goods rise 460 in the quarter. The residuals identify a mismatch
between the shortcut and disclosed quantities, not its cause, a journal entry,
gross purchases or total supplier cash. No FX, acquisition, write-down or
reclassification amount is inferred.

Annual gross PP&E increases 4,529, accumulated depreciation increases 2,564
and net PP&E increases 1,965. PP&E-specific depreciation expense is reported as
8.2 billion; total cash-flow depreciation/amortisation is 11,445 million.
Quarter gross/contra/net changes are 1,487/1,098/389, capital payments 2,940,
and broad depreciation/amortisation 3,080. No separate quarter PP&E depreciation
expense is supplied by the inspected Note 5. Its absence is not zero, and the
later quarter is not part of fiscal 2024.

The first annual asset model deliberately assumes that cash capital payments
9,447 equal gross additions, all depreciation charges are expensed at the
displayed PP&E-specific 8,200, and only additions, depreciation and retirements
change the book. It requires gross retirements 4,918 but removed accumulated
depreciation 5,636, violating nonnegative retired carrying amount by 718.
Under an explicitly hypothetical nearest-rounding model, the outer gap interval
using net PPE endpoints is [666.5,769.5] million, still positive. This rejects
the combined model assumptions, not the source, and does not locate a unique
missing movement. Full ASC authority is not claimed.

Two repair histories assume gross retirements 6,000/7,000, removed accumulated
depreciation 5,636, zero disposal proceeds and year-end additions 10,529/11,529.
Both preserve the selected endpoints, PP&E expense and cash payments; the
unpaid portions are 1,082/2,082. Their loss on retirement is 364/1,364. Journals
balance and incremental assets −7,482 equal liabilities plus equity in each:
1,082−8,564 and 2,082−9,564. Gross additions can also be allocated to match the
three reported gross classes. These are feasible books under the aggregate
model, not reconstructed actual cohorts or a fit to all Apple statements.
No weights or preferred history are inferred.

The lease dependency reinforces the missing-classification problem: finance
ROU is in PP&E, operating ROU is in other noncurrent assets, while the 1.0
billion noncash ROU acquisition disclosure covers both classes. It neither
identifies the missing PP&E addition nor becomes an investing cash payment.
Future queries still require lot/asset ages, life/residual values, production
and consumption flows, write-downs, ownership and settlement facts.

## Reader transition

Baseline PDF pages 27 and 68–69 were inspected. Chapter 3 explains what FIFO
and straight-line policy readings leave unknown. Chapter 9 teaches explicit
lot and depreciation operations before its lease/tax example. The new source-
backed asset section is inserted between those methods and lease/tax, with a
short forward reference in Chapter 3. The opening Apple case chapter remains
intact. This connects sources to operation inputs without accumulating another
unrelated opening-case subsection.

The intended reader must distinguish indirect adjustment from cash paid,
stock change from additions, and broad D&A from PP&E-specific expense; then
explain the failed joint model and why unpaid additions are only one possible
repair. Provisional author review will test those questions on the actual PDF.
