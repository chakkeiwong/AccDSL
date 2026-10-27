from pathlib import Path
HERE=Path(__file__).resolve().parent;target=HERE/'integrate.py';assert not target.exists()
text=(HERE.parent/'authored-program-integration-20261026/integrate.py').read_text()
changes={
 "SOURCE=ROOT/'docs/design/proposal/manuscript-method-authoring-20261026'":"SOURCE=ROOT/'docs/design/proposal/manuscript-authored-program-20261026'",
 "TARGET=ROOT/'docs/design/proposal/manuscript-authored-program-20261026'":"TARGET=ROOT/'docs/design/proposal/manuscript-state-invariants-20261026'",
 "BASE='3cdfb69adfa669a75cb8902fc7ee45d25ed939a988f571b8204350cb784e576e'":"BASE='3940039f83325f0ab3763f208b708ae08f307d0759f28403241ae6ac13c21571'",
 "ADDED=['authored-program-composition']":"ADDED=['authored-state-invariants']",
 'Version 4.45':'Version TEMP','Version 4.46':'Version 4.47','Version TEMP':'Version 4.46',
 "name=='sections/complete-method-authoring.tex'":"name=='sections/authored-program-composition.tex'",
 'len(sources)==180':'len(sources)==181',
 "['authored-method-registry-20261026','authored-program-composition-20261026']":"['authored-program-invariant-audit-20261026','authored-state-invariants-20261026']",
 "['result.md','checks.json','run-manifest.json','verify.py','registry.py' if unit.startswith('authored-method') else 'runner.py']":"(['result.md','checks.json','run-manifest.json','probe.py'] if unit.endswith('audit-20261026') else ['result.md','checks.json','run-manifest.json','verify.py','guards.py','guarded_runner.py'])",
 'accdsl-authored-program-20261026-tex-cache':'accdsl-state-invariants-20261026-tex-cache',
 'From an authored method to a sequence of company statements':'A typed claim can still disagree with the book',
 'not production capacity claims.':'The state-control repair therefore preserves',
 "'version':'4.46'":"'version':'4.47'",
}
for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
target.write_text(text);print('Prepared guarded-state manuscript integrator')
