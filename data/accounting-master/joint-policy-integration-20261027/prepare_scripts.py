from pathlib import Path
H=Path(__file__).resolve().parent;assert not (H/'integrate.py').exists()
s=(H.parent/'policy-refinement-integration-20261027/integrate.py').read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("S=R/'docs/design/proposal/manuscript-prospective-policy-v538-20261027'","S=R/'docs/design/proposal/manuscript-policy-refinement-v539-20261027'")
rep("T=R/'docs/design/proposal/manuscript-policy-refinement-v539-20261027'","T=R/'docs/design/proposal/manuscript-joint-policy-v540-20261027'")
rep('3afcbd9a22548aeffd9c88f1e2016be176d65fb9bab27ea09302d5bf8fc70770','26b999910aeda9f934ffe75f8ec5d96b2c64cb1956655e2483c3c87971015318')
rep('5ef46b46034f10d867e285869b48a12fc38eb99813ae30a2f9bfc6590fa23f64','5f5a5fb6b1a6711e0b8e9582fee3a5b303ce4f897d4a19d321c6c1ed2ddb4d55')
rep('Version 5.39','__NEW__');rep('Version 5.38','Version 5.39');rep('__NEW__','Version 5.40');rep("startswith('5.38;')","startswith('5.39;')")
rep('policy-refinement.tex','joint-stage.tex');rep('input{simulation/policy-refinement}','input{simulation/joint-stage}')
rep("['policy-domain-transport-20261027','policy-observation-refinement-20261027']","['two-decision-source-views-20261027','joint-stage-policy-20261027']")
rep("[('policy-domain-transport-20261027','attempt-01'),('policy-observation-refinement-20261027','attempt-01')]","[('two-decision-source-views-20261027','attempt-01'),('joint-stage-policy-20261027','attempt-01')]")
rep('accounting-policy-refinement-integration-20261027.md','accounting-joint-policy-integration-20261027.md')
rep("('refinement','A manager may receive a differently worded notice','before earlier policy work can be reused.',['fiber','erasure','512','2,048','refined','unresolved'])","('joint','A manager can make the first payment before receiving a correction','admitting actual actor information remain separate tasks.',['Cartesian','15','12','unresolved','correction','second'])")
(H/'integrate.py').write_text(s);print('Created guarded5.40 writer.')

