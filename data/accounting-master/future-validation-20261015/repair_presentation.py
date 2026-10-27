from pathlib import Path
import json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
p=ROOT/'docs/design/proposal/manuscript-future-validation-20261015/sections/future-validation.tex'
s=p.read_text()
rep={
 r'Gneiting and Raftery \citep[sec.~4.2, eqs.~20--21]{gneiting2007proper}, section 4.2, equations (20)--(21),': r'\citet[sec.~4.2, eqs.~20--21]{gneiting2007proper}',
 'Start with rational enumeration and the normal-normal target already derived in the normal model in the conditional-inference discussion:': 'Start with rational enumeration and the normal conditional model derived earlier:',
 'Cash 100+10z': r'Cash \(100+10z\)',
 'Under U Bernoulli(1/2), X=U and Y=2X+U, conditioning on X=1 gives Y=3; intervening to set X=1 gives Y in': r'Under \(U\sim\mathrm{Bernoulli}(1/2)\), \(X=U\) and \(Y=2X+U\), conditioning on \(X=1\) gives \(Y=3\); intervening to set \(X=1\) gives \(Y\) in',
}
applied=[]
for a,b in rep.items():
 assert a in s,a;s=s.replace(a,b);applied.append(a)
p.write_text(s)
(OUT/'presentation-repair.json').write_text(json.dumps({'findings':['Duplicate author/section citation','Redundant normal-model introduction','Plain-text mathematical expressions'],'replacements':applied,'prior_render':'render-v1','requires_new_build_and_render':True},indent=2)+'\n')
print(json.dumps({'replacements':len(applied)}))
