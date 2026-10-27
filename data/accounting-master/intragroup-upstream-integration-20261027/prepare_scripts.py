from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'integrate.py';assert not p.exists()
s=(H.parent/'intragroup-carry-integration-20261027/integrate.py').read_text()
replacements=[
('manuscript-observation-frontier-v532-20261027','BASE_SOURCE'),
('manuscript-intragroup-carry-v533-20261027','manuscript-intragroup-upstream-v534-20261027'),
('BASE_SOURCE','manuscript-intragroup-carry-v533-20261027'),
('fd7f72fda3a4a848f1b9a090961a91037aedf76a79904d57cf0d62782f201a75','2c470216543a01dfda5e1b7f84f029f4b744de31402f1309a5e7d4ae081819d7'),
('3b7fce8cabe7b9eb7529d1316e054ae831a4c87e5e41f9e2519b89400762e7dd','64a65ca8029744ae9d47b12bee520113a452316050a4a7033288d12dd2f0b25d'),
('Version 5.33','Version 5.34'),('Version 5.32','Version 5.33'),("'5.32;'","'5.33;'"),
('carry.tex','upstream.tex'),('simulation/carry','simulation/upstream'),
('acquisition-intragroup-carry-20261027','acquisition-intragroup-upstream-20261027'),
('accounting-intragroup-carry-integration-20261027','accounting-intragroup-upstream-integration-20261027'),
('Suppose the first year ends with the entire lot still inside the group.','Now let the subsidiary sell the inventory to the parent.'),
('check which profit adjustments then belong to NCI.','through retained profit when the outside sale occurs in a later year.'),
("['retained','opening','equipment','inventory','tax','journals']","['subsidiary','vendor','inventory','tax','NCI','journals']")]
for old,new in replacements:assert old in s,old;s=s.replace(old,new)
compile(s,str(p),'exec');p.write_text(s);print('Prepared upstream integration writer.')
