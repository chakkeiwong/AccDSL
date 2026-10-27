# FundedYearInputsDraft/1 documentary grammar

Every nonblank line is one declaration ending in a semicolon. Tokens use POSIX
shell-style quote/escape lexical rules through Python shlex, without comments,
expansion, command execution or multiline strings. Quoted tokens carry spaces.
This is a deliberately explicit lexical choice for a documentary subset, not
the production AccDSL grammar. Unsupported keywords and extra arguments reject.

Each singleton below is required exactly once. Claims and events may repeat
their declaration keyword, but their IDs/event kinds must be unique. Claim
array order is preserved; event array order supplies explicit predecessor order
and must agree with its dates. Exact numbers use reduced n/d with positive d;
decimals, noncanonical fractions and floats reject. Empty/missing declarations
reject. An event instant may be the literal unknown, yielding unresolved timing.

    profile FundedYearInputsDraft/1;
    name IDENTIFIER;
    projection ALIAS SHA256;
    context ENTITY BOOK CURRENCY;
    share RATIONAL;
    source PATH SHA256;
    assumption QUOTED_TEXT;
    claim ID receivable|payable opening|delivery|purchase RECOGNISED SETTLEMENT;
    facility ID LIMIT DRAWN RESERVED;
    loan FACILITY_ID PRINCIPAL ANNUAL_RATE ACT365_calendar FEE operating;
    tax RATE immediate_deductible;
    event KIND UTC_INSTANT|unknown;

The body fields are direct lowerings of those tokens, using the published
closed JSON schema. No rate, amount, date, source identifier or policy is added
by the parser. The imported projection supplies the other previously specified
operating events, amounts and accounting methods; this is an extension of that
example, not whole-company authoring. The example's zero fee and eligibility
assumption remain explicit restrictions. This input subset does not replace
SettlementDecisionDraft/1's fuller draw-window and evidence-admission design.

Conformance requires a typed body equal to the lowered text, source/projection
closure, consistent units, exact claim/control allocations, valid dates and
ordering, and reconciliation with the retained funded-year trace. Known invalid
records reject; unknown required dates remain unresolved. Syntax acceptance
does not grant accounting posting permission or commit a state.
