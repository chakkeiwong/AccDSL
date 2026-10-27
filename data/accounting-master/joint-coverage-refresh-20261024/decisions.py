"""Scoped updates after joint source measurements; no whole closure."""
EVIDENCE = {'joint':'joint-measurement-constraints-20261024',
            'source':'joint-source-relation-binding-20261024',
            'manuscript':'joint-measurements-integration-20261024'}
UPDATES = {}
for key in ['MC04','MC08','MC09','MC10','MC13','MC16','MC24','MC26','MC28',
            'P17-08.01','P17-08.02','P17-08.06']:
    UPDATES[key] = {
        'evidence':['joint','source','manuscript'],
        'advance':'Closed exact joint measurement assessment and exact retained source binding preserve 256 observations/143 dispositions; 18 selected same-date balance equations use 54 shared quantities under explicit proposed hypotheses, with independent rational witness checks.',
        'residual':'Selected measurement feasibility is not admissible history, executable state, uniqueness, probability or full statement consistency. Temporal equations require explicit role/context compatibility rather than erasing dates or measurement kinds.',
        'next_action':'Audit and specify reusable temporal measurement contexts, starting with opening-plus-period-movement-to-closing relations and exact source lineage.',
        'full_requirement_closed':False, 'acceptance':'not_promoted'}
