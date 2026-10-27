"""Exact retained-source bindings. No downloads or predecessor execution."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
MANIFEST='data/accounting-master/p17-completion-20261014/P17-06/prudential-connection/source-manifest.json'
REVIEW='data/accounting-master/p17-completion-20261014/P17-06/prudential-connection/source-review.md'
CAPITAL_METHOD='docs/design/proposal/methods/bank-prudential-connection-20261014.md'
LOSS_METHOD='docs/design/proposal/methods/bank-methods-v1.md'
ANCHORS={
 '3.1':['3.1(a),(c),(d): ordinary national-bank scope and supervisory limits'],
 '3.2':['3.2: AACL, carrying value, exposure amount(1), standardized-total-RWA(2)'],
 '3.10':['3.10(b)(1)-(4): risk-based and average-assets leverage denominators'],
 '3.20':['3.20(b)(1)(i)-(xiii),(b)(2): stock and retained earnings','3.20(d)(3): allowance cap'],
 '3.22':['3.22(a)(1),(e),(g): goodwill, DTL and deducted-asset exclusion'],
 '3.31':['3.31(a)-(b): standardized exposure weighting'],
 '3.32':['3.32(a)(1)(i)(A),(f)(1),(k),(l): central bank, corporate and excluded alternatives'],
 'fdic1':['FFIEC051 Part I item42; physical39-40; printed RC-R-27-28'],
 'fdic2':['FFIEC051 Part II items26,28-31; physical89-90; printed RC-R-109-110']}

def sources():
 out=[]
 for row in json.loads((ROOT/MANIFEST).read_text())['sources']:
  key=row.get('section','fdic'+str(row.get('part','')))
  out.append(dict(key=key,path=row['path'],sha256=row['sha256'],
    text_path=row.get('text_path'),text_sha256=row.get('text_sha256'),
    anchors=ANCHORS[key],role='historical_rule' if 'section' in row else 'older_ordering_crosscheck',
    snapshot='2026-01-01' if 'section' in row else None,method=CAPITAL_METHOD))
 out.append(dict(key='bank-methods',path=LOSS_METHOD,sha256=None,text_path=None,text_sha256=None,
   anchors=['B1: information before decisions and events','B2-B3: joint shortfalls, disjoint defaults, conditioning versus new law','B4: funding, policy and capital distinctions'],
   role='method_semantics',snapshot=None,method=LOSS_METHOD))
 return out
