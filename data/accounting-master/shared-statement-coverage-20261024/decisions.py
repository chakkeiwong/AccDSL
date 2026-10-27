EVIDENCE={'statements':'shared-book-statements-20261024','manuscript':'shared-statement-integration-20261024'}
UPDATES={}
def add(ids,evidence,advance,residual,next_action):
    for key in ids.split():UPDATES[key]={'evidence':evidence,'advance':advance,'residual':residual,'next_action':next_action,'full_requirement_closed':False,'acceptance':'not_promoted'}
add('MC05',['statements'],
    'Recorded views retain declared fiscal bounds, last completed date and attempted failed event instead of treating requested dates as completed.',
    'Actual source/publication clocks and complete fiscal coverage remain unresolved.',
    'Preserve exact dates and event order in matched text and typed declarations.')
add('MC11 MC13',['statements'],
    'Financial views replay complete event prefixes and retain full execution/memory, including funding-failure prefixes.',
    'General histories, arbitrary methods and durable execution remain outside this finite reference.',
    'Require full result equality when adding authored text, including failed-event coverage and memory.')
add('MC16 G4',['statements','manuscript'],
    'All25 accounts feed recorded balance-sheet, income, equity and direct/indirect cash views; four exact identities reconcile; unknown tax remains visible.',
    'These recorded views do not assess tax, complete fiscal events or constitute full annual financial statements.',
    'Expose recorded-report selection in language authoring without inventing annual readiness.')
add('MC24 G2',['statements'],
    'Closed replay-based report requests refuse caller-supplied closing states and preserve all execution and coverage fields.',
    'The mixed book still requires typed/Python construction; general language and independent implementations remain incomplete.',
    'Implement a bounded complete authoring grammar and test exact text/typed equivalence.')
add('MC26',['statements'],
    'Exact rational reconciliations, signed working-capital terms and lease-gain removal are checked independently of saved totals.',
    'No solver expansion, numerical superiority or nonlinear/integer evidence is added.',
    'Keep rational types and unknown values unchanged through the frontend.')
add('MC28',['statements','manuscript'],
    'The synthetic mixed sequence now connects events to recorded financial views and failed-prefix reports in Version3.76.',
    'Actual source-to-state admission and complete real-company cases remain open.',
    'Make the complete synthetic program authorable while retaining actual-source limits.')
add('MC32',['manuscript'],
    'Version3.76 preserves171 sources and272 displays and adds four interpreted reconciliation displays; new pages and transitions inspected.',
    'Dense chapter navigation, full-document and independent/domain/human review remain pending.',
    'Integrate checked authoring semantics with a concrete example; do not claim whole-document acceptance.')
add('MC33 MC34 MC35',['statements','manuscript'],
    '309 recorded checks,19 cases and bounded author review separate arithmetic from tax and annual acceptance; work remains internally prepared.',
    'No whole requirement/phase closure or professional acceptance; S6 held and S7 deferred.',
    'Continue audited language work and preserve all broader queues.')
add('I05',['statements'],
    'Complete replay preserves all prefix memory, gross origins and failure fields instead of deriving statements from lossy summaries.',
    'General aggregation and arbitrary adapters remain unsupported.',
    'Demand canonical full-result equality after text lowering.')
add('P17-04.10',['statements'],
    'Recorded zero tax is explicitly separate from unresolved tax assessment; the original annual report still refuses incomplete tax.',
    'No new tax method or annual close is supplied.',
    'Carry the unresolved tax boundary through every authored result.')
add('P17-04.11',['statements','manuscript'],
    'Recorded equity, balance-sheet and gross/indirect cash reconciliation now derive from the shared event prefix, including stopped execution.',
    'Complete annual accounting adjustments, period carry and full statements remain missing.',
    'Specify a recorded-report language request distinct from annual-close authorization.')
