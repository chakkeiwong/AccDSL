EVIDENCE={'compatibility':'shared-tax-compatibility-20261024',
          'information':'shared-tax-readiness-20261024','manuscript':'tax-readiness-integration-20261024'}
UPDATES={}
def add(ids,evidence,advance,residual,next_action):
    for key in ids.split():UPDATES[key]={'evidence':evidence,'advance':advance,'residual':residual,
        'next_action':next_action,'full_requirement_closed':False,'acceptance':'not_promoted'}
add('MC05',['compatibility','information'],
    'Exclusive tax endpoints, last included days and state dates are distinct; the731-day window is not treated as one annual period.',
    'Actual source clocks, fiscal coverage and executable shared-book close/carry remain open.',
    'Bind conditional calculations to the explicitly assessed interval without altering original state dates.')
add('MC11 MC13',['compatibility','information'],
    'Unchanged mixed execution is replayed inside information assessment; two original tax controls still match exactly.',
    'General execution methods, loss/refund and durable cross-period tax state remain unspecified.',
    'Require full state/report preservation while adding a separate conditional arithmetic result.')
add('MC16 G4',['compatibility','information','manuscript'],
    'Omitted gain, incompatible close timing and absent tax facts are demonstrated;61 explicit declarations preserve unresolved annual tax.',
    'Information completeness is not a consistent executable tax method, and no annual statements or cash-tax postings are added.',
    'Reconcile native adjustment origins and right/account bases before computing conditional gross tax.')
add('MC24 G2',['information','manuscript'],
    'Closed tax-information requests preserve exact known/unknown provenance, account/right populations and interval semantics.',
    'Textual treatment declarations do not specify executable rules; general DSL, independent implementations and usability remain open.',
    'Specify a separate finite uniform-rate assumption and explicit adjustment-allocation contract.')
add('MC26',['compatibility','information'],
    'Exact pretax comparison exposes omitted20 gain; dimensional rational inputs and explicit unknowns are checked.',
    'No admitted tax law, nonlinear/integer solver expansion or numerical-method ranking follows.',
    'Check exact allocation sums and independent current-tax arithmetic under labelled hypothetical assumptions.')
add('MC28',['compatibility','information','manuscript'],
    'The mixed worked example now shows tax reuse failure and concrete missing-information outcomes without manufactured tax facts.',
    'Complete actual-company tax, source admission and annual close remain unresolved.',
    'Add conditional arithmetic examples while retaining original factual unknowns and controls.')
add('MC32',['manuscript'],
    'Version3.78 preserves173 sources,276 displays and all references; two new interpreted displays and seven rendered pages checked.',
    'Dense language navigation and whole-document/independent/domain/human acceptance remain pending.',
    'Integrate further calculations only with exact evidence and bounded rendered review.')
add('MC33 MC34 MC35',['compatibility','information','manuscript'],
    '92 compatibility checks and203 information checks distinguish failed reuse from continuing design;29 tests pass.',
    'No whole requirement/phase closure or professional acceptance;S6 held,S7 deferred.',
    'Continue internally audited reconciliation work and preserve all other queues.')
add('I05',['information'],
    'Complete report, terminated zero-valued right, unknowns and failed prefixes remain in the assessment result.',
    'Generic module composition and cross-field tax consistency remain unimplemented.',
    'Retain exact native return adjustments once, not both in allocations and a second hidden sum.')
add('P17-04.10',['compatibility','information','manuscript'],
    'Direct tax reuse is rejected for concrete reasons; all61 declarations and explicit false/unknown outcomes are represented.',
    'No current/deferred calculation, tax loss rule, settlement or legal admission.',
    'Implement exact conditional current-tax reconciliation, basis checks and explicit loss_route_required.')
add('P17-04.11',['compatibility','information'],
    'Tax-information and report intervals are distinguished; information_supplied keeps annual_close_ready false.',
    'Actual annual completeness, tax postings and shared-period carry remain missing.',
    'Keep gross tax arithmetic separate from posting and annual authorization.')
