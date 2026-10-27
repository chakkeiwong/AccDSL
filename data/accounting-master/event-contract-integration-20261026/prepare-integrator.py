from pathlib import Path
HERE=Path(__file__).resolve().parent;target=HERE/'integrate.py';assert not target.exists()
text=(HERE.parent/'state-invariant-integration-20261026/integrate.py').read_text()
changes={
 "SOURCE=ROOT/'docs/design/proposal/manuscript-authored-program-20261026'":"SOURCE=ROOT/'docs/design/proposal/manuscript-state-invariants-20261026'",
 "TARGET=ROOT/'docs/design/proposal/manuscript-state-invariants-20261026'":"TARGET=ROOT/'docs/design/proposal/manuscript-event-contract-20261026'",
 "BASE='3940039f83325f0ab3763f208b708ae08f307d0759f28403241ae6ac13c21571'":"BASE='ccc3ffbb83303dcbeb892decd3bd9f36cd112d54148ab15fe24167f9bd34c38e'",
 "ADDED=['authored-state-invariants']":"ADDED=['authored-event-contract']",
 'Version 4.46':'Version TEMP','Version 4.47':'Version 4.48','Version TEMP':'Version 4.47',
 "name=='sections/authored-program-composition.tex'":"name=='sections/authored-state-invariants.tex'",
 'len(sources)==181':'len(sources)==182',
 "['authored-program-invariant-audit-20261026','authored-state-invariants-20261026']":"['authored-event-prerequisite-audit-20261026','authored-event-contract-20261026']",
 "'guards.py','guarded_runner.py'":"'contract.py','contract_runner.py'",
 'accdsl-state-invariants-20261026-tex-cache':'accdsl-event-contract-20261026-tex-cache',
 'A typed claim can still disagree with the book':"Keep the event’s intent when a method is specialized",
 'The state-control repair therefore preserves':'These comparisons extend the checked refusal scope',
 "'version':'4.47'":"'version':'4.48'",
}
for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
target.write_text(text);print('Prepared selected-contract manuscript integrator')
