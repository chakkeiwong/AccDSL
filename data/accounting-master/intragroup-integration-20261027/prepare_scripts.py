"""Create a separate bounded integration driver from the inspected predecessor."""
from pathlib import Path
H=Path(__file__).resolve().parent;S=H.parent/'acquisition-worked-integration-20261027/integrate.py'
out=H/'integrate.py';assert not out.exists()
text=S.read_text()
changes=[
 ('manuscript-acquisition-design-v529-20261027','manuscript-acquisition-worked-v530-20261027'),
 ('manuscript-acquisition-worked-v530-20261027\'\nPDFS','manuscript-intragroup-v531-20261027\'\nPDFS'),
 ('df51ceccf52ea02dcf8320cd071b7338d61e8fe549a157090d0a5177786f950d','201608f8891939d9be2737feb963348e9c26d3201089932b30ead08d767910dc'),
 ('d51391a22e2665beb85c1e580b9ab9852568e87d0ac88284da856f8c95d72817','f05f94176ad582b6fa2b0536db343b627816e1d783f3e165d387b8956d7b201f'),
 ('acquisition-worked.tex','intragroup.tex'),('simulation/acquisition-worked','simulation/intragroup'),
 ("assert t.count('Version 5.29')==1;return t.replace('Version 5.29','Version 5.30')","assert t.count('Version 5.30')==1;return t.replace('Version 5.30','Version 5.31')"),
 ("startswith('5.29;')","startswith('5.30;')"),
 ("['acquisition-worksheet-20261027','acquisition-consideration-20261027','acquisition-revision-prefix-repair-20261027']","['acquisition-intragroup-20261027','acquisition-intragroup-realisation-20261027']"),
 ("[('acquisition-worksheet-20261027','attempt-01'),('acquisition-consideration-20261027','attempt-01'),('acquisition-revision-prefix-repair-20261027','attempt-01')]","[('acquisition-intragroup-20261027','attempt-01'),('acquisition-intragroup-realisation-20261027','attempt-01')]"),
 ('accounting-acquisition-worked-integration-20261027.md','accounting-intragroup-integration-20261027.md'),
 ("'Version 5.30' in texts[0]","'Version 5.31' in texts[0]"),
 ("ending='without leaking pre-control activity or losing the acquired measurement basis.'","ending='That requires a separate two-year comparison.'"),
 ('The unknown amounts in the preceding section protect the real financing question from invented measurements.','The acquisition worksheet now has a second task:'),
 ("['pre-control','discovery','noncash','negative','original','tax']","['pre-control','unrealised','outside','inventory','tax','journals']")]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
assert "T=R/'docs/design/proposal/manuscript-intragroup-v531-20261027'" in text
assert "S=R/'docs/design/proposal/manuscript-acquisition-worked-v530-20261027'" in text
out.write_text(text)
print('Created separate intragroup integration driver; no preparation/build writer rerun.')
