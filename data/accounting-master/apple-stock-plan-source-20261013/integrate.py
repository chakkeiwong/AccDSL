"""Create an additive, source-only manuscript candidate; preserve its baseline."""
import hashlib
import json
import shutil
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
BASE = ROOT / 'docs/design/proposal/manuscript-apple-settlement-paths-20261013'
CAND = ROOT / 'docs/design/proposal/manuscript-apple-stock-plan-20261013'
if CAND.exists():
    raise SystemExit('Candidate exists; inspect instead of overwriting.')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sources = {}
for p in sorted(BASE.rglob('*')):
    if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}:
        rel = p.relative_to(BASE)
        sources[str(rel)] = sha(p)
        dest = CAND / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
p = CAND / 'accounting-product-proposal.tex'
p.write_text(p.read_text().replace('Version 2.64', 'Version 2.65'))
p = CAND / 'chapters/14-financing-groups.tex'
p.write_text(p.read_text().replace(r'\input{sections/apple-eps-ownership}',
    r'\input{sections/apple-eps-ownership}'+'\n'+r'\input{sections/apple-stock-plan}'))
p = CAND / 'sections/apple-eps-ownership.tex'
old = 'The 2022 employee plan permits several award types. Its RSUs generally vest'
new = ('The annual report describes several award types under the 2022 employee\n'
       'plan and the usual terms of its RSUs. In that reported practice, RSUs generally vest')
assert old in p.read_text()
p.write_text(p.read_text().replace(old, new))
shutil.copy2(UNIT/'apple-stock-plan.tex', CAND/'sections/apple-stock-plan.tex')
bib = r'''
@misc{apple2022plan,
  author = {{Apple Inc.}},
  title = {Form 8-K, 4 March 2022: 2022 Employee Stock Plan and Award Forms},
  year = {2022},
  note = {Items 5.02 and 5.07; Exhibits 10.1--10.3. Retained 31-page filing counterpart; selected operative clauses inspected},
  url = {https://d18rn0p25nwr6d.cloudfront.net/CIK-0000320193/1e8cf761-1736-43bb-81b0-4e8fe94bd0c8.pdf}
}
@misc{apple2025proxy,
  author = {{Apple Inc.}},
  title = {2025 Proxy Statement},
  year = {2025},
  note = {Retained issuer-associated HTML; selected printed pages 51, 53--54 and 97},
  url = {https://d18rn0p25nwr6d.cloudfront.net/CIK-0000320193/62c3eec4-b7bc-4f7b-b132-3a03f5c10bdf.html}
}
'''
p = CAND/'references.bib'; p.write_text(p.read_text()+bib)
(UNIT/'bibliography-additions.bib').write_text(bib)
(UNIT/'candidate.json').write_text(json.dumps({'baseline':str(BASE.relative_to(ROOT)),
    'candidate':str(CAND.relative_to(ROOT)), 'source_hashes':sources,
    'edits':{'root':'Version increment only','chapter14':'Add stock-plan section after EPS',
    'apple-eps':'Scope general terms to reported issuer practice','bibliography':'Two entries appended'}},indent=2)+'\n')
print(json.dumps({'candidate':str(CAND.relative_to(ROOT)),'baseline_sources':len(sources)}))
