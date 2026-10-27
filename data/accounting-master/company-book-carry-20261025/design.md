# Explicit provisional recorded-balance carry

CompanyBookCarry/1 fields:profile,report_request,expected_report_sha256,close_id,
retained_account,next_end_exclusive,memory_policies. Recompute CompanyBookReport/1
and require its exact digest and reported status. Closing date must be the last
included calendar day before period.end_exclusive. The next period starts at that
endpoint and ends at the supplied later date. This is provisional and does not
assert the prior fiscal event population or notes are complete.

Retained_account is explicitly named and classified equity. Close_id is nonempty
and absent from lifetime seen IDs. Every income/expense balance b produces -b in
the closing journal;the retained-account entry is sum(b). All other journal entries
are zero. Journal sum and cash change are zero. This transfers recorded profit
to the named retained-equity account without guessing its identity.

Memory_policies is a closed mapping with exactly one policy for each memory_types
pointer. preserve fields:kind,provenance. next_period_start fields:kind,provenance,
allowed only for date leaves. reset fields:kind,type,value,provenance;type must equal
the leaf's complete declared type and the literal must validate. No implicit resets
or deleted fields. The existing memory stage performs fixed scalar replacements;
the book validator checks the result. Policies state authored assumptions,not
business or tax correctness. Dynamic collection schemas remain unchanged.

Output contains the unchanged report,the complete closing journal,closed_book,
next_opening,memory_stage and an external archive record binding prior state/report,
close identity and policies. closed_book keeps the old memory/date/period and adds
the close ID;next_opening applies declared memory policies,sets new period/date and
clears prior-period flows. Both retain lifetime event IDs and unchanged permanent
accounts. Archive is a returned value;no database write or durable history claim.
All admission/commit/fiscal-complete flags remain false. Apply recomputes the full
proposal with canonical JSON equality. Native comparison is balance-only unless
every separate native clock/memory/archive policy is explicitly matched.
