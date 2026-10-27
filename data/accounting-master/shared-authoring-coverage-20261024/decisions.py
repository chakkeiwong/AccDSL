EVIDENCE = {'authoring': 'shared-book-authoring-20261024', 'manuscript': 'shared-authoring-integration-20261024'}
UPDATES = {}
def add(ids, evidence, advance, residual, next_action):
    for key in ids.split():
        UPDATES[key] = {'evidence': evidence, 'advance': advance, 'residual': residual,
            'next_action': next_action, 'full_requirement_closed': False, 'acceptance': 'not_promoted'}
add('MC05', ['authoring'],
    'Authored opening dates, period bounds and ordered event records preserve exact native timing and stopped-prefix outcomes.',
    'Actual source clocks, fiscal completeness and tax-close versus exclusive-period timing remain unresolved.',
    'Audit close-time compatibility before attempting annual tax or carry.')
add('MC11 MC13', ['authoring'],
    'Complete authored mixed programs reproduce all native memory, event traces and refusals for 16 original requests.',
    'General histories, arbitrary methods, endogenous behaviour and durable native execution remain open.',
    'Audit complete tax-state compatibility without dropping nonselected lease or return memory.')
add('MC16 G4', ['authoring', 'manuscript'],
    'Explicit report selection preserves the complete recorded statements, gross origins and unresolved annual coverage.',
    'Tax assessment, fiscal completion and period carry remain separate missing capabilities.',
    'Determine the exact original-tax compatibility and missing-fact boundaries.')
add('MC24 G2', ['authoring', 'manuscript'],
    'A bounded grammar authors the complete shared opening and ordered events; full text/typed/native equality and explicit compiler refusals are checked.',
    'Other modules, reusable functions, source admission, independent implementations and human authoring usability remain incomplete.',
    'Specify explicit tax prerequisites and timing before extending the finite grammar.')
add('MC26', ['authoring'],
    'Exact rationals, false/unknown values and all nonselected memory survive text round trips; malformed scalar types fail.',
    'No general nonlinear/integer solver or numerical-method comparison is added.',
    'Use exact arithmetic to expose omitted-income or timing differences in native tax reuse.')
add('MC28', ['authoring', 'manuscript'],
    'The complete synthetic return/lease program is now authorable and reproduces recorded financial results and failed prefixes.',
    'Actual company source-to-state admission and complete annual cases remain open.',
    'Retain original source and synthetic assumptions while auditing tax readiness.')
add('MC32', ['manuscript'],
    'Version 3.77 preserves 172 sources and 276 displays; actual new pages and transitions are reviewed.',
    'Dense navigation, whole-document and independent/domain/human acceptance remain pending.',
    'Explain any demonstrated tax boundary in a protected successor when substantive evidence is ready.')
add('MC33 MC34 MC35', ['authoring', 'manuscript'],
    '289 checks and 28 test methods distinguish 16 exact execution matches from three compiler refusals; internal execution continues.',
    'No whole phase or requirement closure; professional and human acceptance remain unclaimed.',
    'Continue audited simulator work, preserving all broader queues and the no-forecast priority.')
add('I05', ['authoring'],
    'Text lowering retains complete results rather than summaries, including memory, gross origins, failed events and coverage.',
    'General adapters and arbitrary module composition remain unsupported.',
    'Require complete state and income coverage before admitting a tax adapter.')
add('P17-04.10', ['authoring'],
    'Tax remains explicitly unresolved through authored report selection; unsupported tax module is a compiler refusal.',
    'The mixed state has no applicable tax-close method, lease tax bases or loss/refund policy.',
    'Audit the original return tax method and design explicit successor prerequisites.')
add('P17-04.11', ['authoring', 'manuscript'],
    'Recorded statements are completely authorable and preserve the original annual-completion limits.',
    'Annual close, tax adjustments and cross-period shared-book carry remain missing.',
    'Check exclusive close dates and state dates before extending period transitions.')
