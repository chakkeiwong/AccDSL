from pathlib import Path
HERE=Path(__file__).resolve().parent
target=HERE/'advance.py';assert not target.exists()
text=(HERE.parent/'method-timing-integration-20261026/advance.py').read_text()
changes={
 'accounting-authored-method-registry-20261026.md':'accounting-authored-program-invariant-audit-20261026.md',
 'data/accounting-master/method-timing-integration-20261026/':'data/accounting-master/authored-program-integration-20261026/',
 'accounting-method-timing-integration-20261026.md':'accounting-authored-program-integration-20261026.md',
 'Version 4.45, 541 pages':'Version 4.46, 542 pages',
 'Version 4.45 is 541 pages':'Version 4.46 is 542 pages',
 'Version 4.45, 541 pages':'Version 4.46, 542 pages',
 '4.45;541 pages;not_ready':'4.46;542 pages;not_ready',
 'Version4.45:541 pages;178 predecessor sources preserved;complete method and exact native timing integrated':'Version4.46:542 pages;180 predecessor sources preserved;authored registry/program composition integrated',
 'Version 4.45 integrates this result and the exact native information checker.':'Version 4.46 integrates full methods, explicit registries and finite authored programs.',
 'Complete method authoring integrated':'Authored program composition integrated',
 'Version 4.46 is 542 pages, not_ready. A.54.7–8 explain native exact timing':'Version 4.46 is 542 pages, not_ready. A.54.9 explains authored registry',
 'closure and complete bounded method authoring. All 178 predecessor sources':'dispatch and complete finite program composition. All 180 predecessor sources',
 'remain; no new warnings. Cover and physical pages 505–508 inspected.':'remain; no new warnings. Cover and physical pages 507–510 inspected.',
 'The next dependency is explicit v1/v2 registry composition. All 53 obligations,':'Next: audit outer lifecycle invariants and refusal scope. All 53 obligations,',
 'Current question: how can complete methods be authored while retaining existing semantics?':'Current question: how can authored methods compose through explicit transition versions?',
 'Current question: how can authored methods compose through explicit transition versions?':'Current question: which native cross-record invariants remain outside authored programs?',
 'docs/plans/accounting-complete-method-authoring-audit-20261026.md':'docs/plans/accounting-authored-method-registry-20261026.md',
 'data/accounting-master/post-binding-program-refresh-20261026/remaining-work.md':'data/accounting-master/method-timing-integration-20261026/remaining-work.md',
 'docs/design/proposal/manuscript-exact-time-20261026/accounting-product-proposal.pdf':'docs/design/proposal/manuscript-method-authoring-20261026/accounting-product-proposal.pdf',
 '46d96f2bbb80561b31ca94919c6fbb6cd822d042eff39d5f50502c1769016802':'3cdfb69adfa669a75cb8902fc7ee45d25ed939a988f571b8204350cb784e576e',
 'Compose authored methods through explicit v1/v2 registry entries':'Audit outer lifecycle invariants against authored programs',
 'Check complete sequential state/results before program-level adoption':'Bind explicit cross-record requirements using existing evaluators',
 'Next: implement and verify explicit v1/v2 authored registry composition.':'Next: audit cross-record invariants and refusal scope in authored programs.',
 'Method/timing integration and ten-control refresh completed.':'Authored-program integration and ten-control refresh completed.'
}
for old,new in changes.items():text=text.replace(old,new)
# Replace the queue paragraph with the actual next dependency.
start=text.index("tail=NL.join(");end=text.index("(ROOT/remaining).write_text",start)
text=text[:start]+'''tail=NL.join(['## Next dependency: cross-record invariant coverage','',
 'Complete method authoring, explicit v1/v2 registry calls and two eleven-command',
 'programs now have full retained-state/report/carry comparisons. Unknown and',
 'refused later commands preserve successful prefixes. Outer lifecycle controls',
 'still need a separate audit: claim totals versus receivables, event membership,',
 'dates and assessment snapshots. Equal happy paths do not establish equal',
 'refusal scope. Audit these checks before wider dynamic language expansion.',
 '', 'Execute '+plan+'. Broader sources, fiscal/sector methods and acceptance remain.',
 'No whole obligation closes. S6 held; E3 deferred.', ''])
'''+text[end:]
target.write_text(text)
print('Prepared scoped control successor')
