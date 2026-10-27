"""Create this successor's bounded build script without running predecessor writers."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
target=HERE/'integrate.py';assert not target.exists()
text=(HERE.parent/'method-timing-integration-20261026/integrate.py').read_text()
changes={
 "SOURCE=ROOT/'docs/design/proposal/manuscript-exact-time-20261026'":"SOURCE=ROOT/'docs/design/proposal/manuscript-method-authoring-20261026'",
 "TARGET=ROOT/'docs/design/proposal/manuscript-method-authoring-20261026'":"TARGET=ROOT/'docs/design/proposal/manuscript-authored-program-20261026'",
 "BASE='46d96f2bbb80561b31ca94919c6fbb6cd822d042eff39d5f50502c1769016802'":"BASE='3cdfb69adfa669a75cb8902fc7ee45d25ed939a988f571b8204350cb784e576e'",
 "ADDED=['exact-native-information','complete-method-authoring']":"ADDED=['authored-program-composition']",
 "Version 4.44":"Version TEMP", "Version 4.45":"Version 4.46", "Version TEMP":"Version 4.45",
 "name=='sections/exact-information-time.tex'":"name=='sections/complete-method-authoring.tex'",
 "len(sources)==178":"len(sources)==180",
 "['complete-method-authoring-20261026','exact-native-timing-20261026']":"['authored-method-registry-20261026','authored-program-composition-20261026']",
 "'frontend.py' if unit.startswith('complete') else 'checker.py'":"'registry.py' if unit.startswith('authored-method') else 'runner.py'",
 "accdsl-method-authoring-20261026-tex-cache":"accdsl-authored-program-20261026-tex-cache",
 "Exact timing must retain the whole evidence dependency":"From an authored method to a sequence of company statements",
 "every accounting treatment implemented by that engine.":"not production capacity claims.",
 "'version':'4.45'":"'version':'4.46'",
}
for old,new in changes.items():
    assert old in text,old;text=text.replace(old,new)
target.write_text(text)
print('Prepared successor integrator; predecessor unchanged')
