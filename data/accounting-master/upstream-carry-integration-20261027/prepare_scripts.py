from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'integrate.py';assert not p.exists()
s=(H.parent/'intragroup-upstream-integration-20261027/integrate.py').read_text()
changes=[('manuscript-intragroup-carry-v533-20261027','BASE_SOURCE'),
('manuscript-intragroup-upstream-v534-20261027','manuscript-upstream-carry-v535-20261027'),('BASE_SOURCE','manuscript-intragroup-upstream-v534-20261027'),
('2c470216543a01dfda5e1b7f84f029f4b744de31402f1309a5e7d4ae081819d7','611d83759a0e4d5ba757753613e957aa7364e48cf516ec91fc5b2ee0a52df34d'),
('64a65ca8029744ae9d47b12bee520113a452316050a4a7033288d12dd2f0b25d','5f0352b476ee76236157975f2cc04634ab43408ee7f2184f22771b536464b0dc'),
('Version 5.34','Version 5.35'),('Version 5.33','Version 5.34'),("'5.33;'","'5.34;'"),
('upstream.tex','upstream-carry.tex'),('simulation/upstream','simulation/upstream-carry'),
('acquisition-intragroup-upstream-20261027','acquisition-intragroup-upstream-carry-20261027'),
('accounting-intragroup-upstream-integration-20261027','accounting-upstream-carry-integration-20261027'),
('Now let the subsidiary sell the inventory to the parent.','At the first upstream year end, suppose the parent still holds the whole lot.'),
('through retained profit when the outside sale occurs in a later year.','distinguished before the same consolidation logic can be applied.'),
("['subsidiary','vendor','inventory','tax','NCI','journals']","['subsidiary','retained','inventory','tax','NCI','accounts']")]
for old,new in changes:assert old in s,old;s=s.replace(old,new)
# Avoid compounding the path replacement in the ADDED key.
s=s.replace('simulation/upstream-carry-carry.tex','simulation/upstream-carry.tex')
compile(s,str(p),'exec');p.write_text(s);print('Prepared upstream carry integration writer.')
