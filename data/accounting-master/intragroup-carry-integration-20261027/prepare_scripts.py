from pathlib import Path
H=Path(__file__).resolve().parent;out=H/'integrate.py';assert not out.exists()
text=(H.parent/'intragroup-integration-20261027/integrate.py').read_text()
changes=[
 ('manuscript-acquisition-worked-v530-20261027','manuscript-observation-frontier-v532-20261027'),
 ('manuscript-intragroup-v531-20261027','manuscript-intragroup-carry-v533-20261027'),
 ('201608f8891939d9be2737feb963348e9c26d3201089932b30ead08d767910dc','fd7f72fda3a4a848f1b9a090961a91037aedf76a79904d57cf0d62782f201a75'),
 ('f05f94176ad582b6fa2b0536db343b627816e1d783f3e165d387b8956d7b201f','3b7fce8cabe7b9eb7529d1316e054ae831a4c87e5e41f9e2519b89400762e7dd'),
 ('intragroup.tex','carry.tex'),('simulation/intragroup','simulation/carry'),
 ("Version 5.30","Version 5.32"),("Version 5.31","Version 5.33"),("startswith('5.30;')","startswith('5.32;')"),
 ("['acquisition-intragroup-20261027','acquisition-intragroup-realisation-20261027']","['acquisition-intragroup-carry-20261027']"),
 ("[('acquisition-intragroup-20261027','attempt-01'),('acquisition-intragroup-realisation-20261027','attempt-01')]","[('acquisition-intragroup-carry-20261027','attempt-01')]"),
 ('accounting-intragroup-integration-20261027.md','accounting-intragroup-carry-integration-20261027.md'),
 ('That requires a separate two-year comparison.','check which profit adjustments then belong to NCI.'),
 ('The acquisition worksheet now has a second task:','Suppose the first year ends with the entire lot still inside the group.'),
 ("['pre-control','unrealised','outside','inventory','tax','journals']","['retained','opening','equipment','inventory','tax','journals']")]
for old,new in changes:assert old in text,old;text=text.replace(old,new)
out.write_text(text);print('Created protected5.32-to5.33 integration driver.')
