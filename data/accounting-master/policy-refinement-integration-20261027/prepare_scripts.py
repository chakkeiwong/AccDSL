from pathlib import Path
H=Path(__file__).resolve().parent;assert not (H/'integrate.py').exists()
s=(H.parent/'prospective-policy-integration-20261027/integrate.py').read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("S=R/'docs/design/proposal/manuscript-debt-exchange-v537-20261027'","S=R/'docs/design/proposal/manuscript-prospective-policy-v538-20261027'")
rep("T=R/'docs/design/proposal/manuscript-prospective-policy-v538-20261027'","T=R/'docs/design/proposal/manuscript-policy-refinement-v539-20261027'")
rep('6ca03da58896b0def9388114460aa1076d1c918342d5982bf253e19a5c281927','3afcbd9a22548aeffd9c88f1e2016be176d65fb9bab27ea09302d5bf8fc70770')
rep('6e1fd02cf3b454fb0cdb3590a8e3df17850d7b57fae467b32c8501a2ffbf11d6','5ef46b46034f10d867e285869b48a12fc38eb99813ae30a2f9bfc6590fa23f64')
rep('Version 5.38','__NEW__');rep('Version 5.37','Version 5.38');rep('__NEW__','Version 5.39');rep("startswith('5.37;')","startswith('5.38;')")
rep("ADDED={'simulation/prospective-policy.tex':'prospective-policy.tex','simulation/conversion-partition.tex':'conversion-partition.tex'}","ADDED={'simulation/policy-refinement.tex':'policy-refinement.tex'}")
rep("'simulation/26-finite-finance.tex','simulation/17-continuous-methods.tex'","'simulation/17-continuous-methods.tex'")
rep("    if n=='simulation/26-finite-finance.tex':return t+'\\n\\\\input{simulation/conversion-partition}\\n'\n",'')
rep('input{simulation/prospective-policy}','input{simulation/policy-refinement}')
rep("['prospective-policy-domain-20261027','prospective-partial-policy-20261027','conversion-control-transaction-20261027']","['policy-domain-transport-20261027','policy-observation-refinement-20261027']")
rep("[('prospective-policy-domain-20261027','attempt-03'),('prospective-partial-policy-20261027','attempt-01'),('conversion-control-transaction-20261027','attempt-01')]","[('policy-domain-transport-20261027','attempt-01'),('policy-observation-refinement-20261027','attempt-01')]")
rep("['prospective-policy.tex','conversion-partition.tex','reader-plan.md']","['policy-refinement.tex','reader-plan.md']")
rep('accounting-prospective-policy-integration-20261027.md','accounting-policy-refinement-integration-20261027.md')
start=s.index("            for label,opening,ending,words in [");end=s.index('                starts=',start)
s=s[:start]+"            for label,opening,ending,words in [('refinement','A manager may receive a differently worded notice','before earlier policy work can be reused.',['fiber','erasure','512','2,048','refined','unresolved'])]:\n"+s[end:]
(H/'integrate.py').write_text(s)
p=H/'policy-refinement.tex';t=p.read_text()
for a,b in [('from32','from 32'),('to2,048','to 2,048'),('are32','are 32'),('and512','and 512'),('/:22','/: 22'),('/:17','/: 17'),('}:22','}: 22'),('}:17','}: 17'),('and12','and 12'),('and10','and 10')]:t=t.replace(a,b)
p.write_text(t)
print('Created5.39 writer;number spacing checked.')

