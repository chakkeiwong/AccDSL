EVIDENCE={'reconciliation':'shared-tax-reconciliation-20261024','manuscript':'tax-reconciliation-integration-20261024'}
UPDATES={}
def add(ids,evidence,advance,residual,next_action):
    for key in ids.split():UPDATES[key]={'evidence':evidence,'advance':advance,'residual':residual,
        'next_action':next_action,'full_requirement_closed':False,'acceptance':'not_promoted'}
add('MC05',['reconciliation'],
    'Conditional arithmetic retains the exact assessed interval and original native dates without claiming a close.',
    'Native cross-period carry,actual fiscal completion and source clocks remain open.',
    'Require explicit contiguous loss-ledger intervals without claiming native financial-state continuity.')
add('MC11 MC13',['reconciliation'],
    'Complete native statements and unknown/stopped outcomes survive numerical rejection and accepted conditional arithmetic.',
    'General module execution,durable commits and native tax-period state remain incomplete.',
    'Use pure recomputed loss proposals with complete input and native-result preservation.')
add('MC16 G4',['reconciliation','manuscript'],
    'Complete income,identified native adjustments and right/account tax bases reconcile before gross conditional tax arithmetic.',
    'Loss treatment,credits,deferred recognition,payable,cash settlement and annual completion remain separate.',
    'Specify loss generation and explicit utilization without automatic refund or deferred asset.')
add('MC24 G2',['reconciliation'],
    'Closed selected-model and allocation records refuse forged origins,duplicate native adjustments and basis inconsistencies.',
    'General tax rules,broader DSL,human authoring and independent implementation remain incomplete.',
    'Define loss-state types,provenance,expiry policy,allocation and apply semantics explicitly.')
add('MC26',['reconciliation'],
    'Exact negative,zero,positive and fractional arithmetic checked; native adjustment counted once and four basis equalities enforced.',
    'No numerical-method superiority,general solver extension or admitted tax treatment.',
    'Check exact loss conservation and caps with boundary and tamper cases.')
add('MC28',['reconciliation','manuscript'],
    'The synthetic worked case preserves -19 loss boundary and explicit hypothetical positive/zero controls.',
    'Actual source-to-tax admission and complete annual-company examples remain open.',
    'Connect an explicit loss ledger to these exact conditional results,using distinct hypothetical periods.')
add('MC32',['manuscript'],
    'Version3.79 preserves174 source files and278 displays; prior tax prose is verbatim and one interpreted equation is appended.',
    'Dense navigation,whole-document,independent/domain/human acceptance remain pending.',
    'Keep later numerical exposition with the relevant tax section and inspect actual rendering.')
add('MC33 MC34 MC35',['reconciliation','manuscript'],
    '240 checks,24 cases,26 tests and repaired bounded rendered review preserve explicit limits and continued internal work.',
    'No whole requirement/phase or professional acceptance;S6 held,S7 deferred.',
    'Continue audited loss work and all other preserved queues.')
add('I05',['reconciliation'],
    'Identified native adjustments cannot silently be duplicated or omitted; rejected arithmetic retains the complete report.',
    'Generic composition and cross-period state continuity remain unimplemented.',
    'Bind loss uses to exact conditional results and preserve whole native outputs.')
add('P17-04.10',['reconciliation','manuscript'],
    'An explicitly selected uniform-rate/no-credit profile checks allocations,bases and exact conditional gross tax.',
    'No admitted jurisdiction,loss law,refund,deferred tax or settlement method.',
    'Implement a separate explicit conditional loss-lot model with conservation and unknown eligibility.')
add('P17-04.11',['reconciliation'],
    'No conditional tax result modifies the recorded accounts,cash,close date or annual readiness.',
    'Tax postings,annual completeness and native period carry remain missing.',
    'Distinguish loss-ledger carry from financial-statement carry in the next design.')
