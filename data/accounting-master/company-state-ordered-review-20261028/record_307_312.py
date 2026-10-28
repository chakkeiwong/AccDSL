"""Record actual rendered reading307–312; retained sources stay unchanged."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0301-0306.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
c('Americas later disclosed costs',89587+9802,99389)
c('Americas same operating profit',167045-89587-9802,67656)
c('original residual cost',167045-67656,99389)
c('corporate costs',31370+7458,38828)
c('consolidated operating income',162044-31370-7458,123216)
c('other segment selling marketing',18639-9802,8837)
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf'])
for n in range(307,313):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
with (D/'arithmetic-0307-0312.json').open('x') as f:json.dump(dict(count=len(checks),checks=checks,scope='Exact displayed example arithmetic only; no new source/rule certification'),f,indent=2)
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0307-0312',pages=list(range(307,313)),entry_state=prior['exit_state'],
 exit_state='Later segment expense detail can answer an earlier-period disclosure question without changing the economic transactions or original as-of information. Third-party indemnities, defense costs, settlements and insurance recoveries require separate contract and timing facts. Regulation can restrict feasible operations without a damages payment. Demand weakness and supply interruption may share causes but neither the reports nor regional labels determine their joint law, supplier-to-customer mapping or management response. Continue the disruption and recovery paths from the unfinished trade-restriction discussion.',
 observations=[
 dict(pages=[307],finding='A remedy against a search partner may affect licensing revenue without an Apple fine; reported proposal is not an imposed remedy. Source disclosures identify channels but lack terms, dates and behavior needed for a numeric forecast. Later disclosure is introduced as added information about unchanged earlier transactions.',disposition='The distinctions prevent applying one loss percentage across Services or double-counting tax escrow as DMA loss. The move from legal effects to historical information follows the reader’s unresolved need for dated contract facts; sources are not newly certified.'),
 dict(pages=[308],finding='The adoption table labels issuer plans and fiscal timing. The2025 comparative expense disclosure fills some2024 segment detail without retroactive access or a new transaction. Equal7458 amounts under changed captions do not prove equal scopes.',disposition='167045-89587-9802=67656 and162044-31370-7458=123216 check. Later selling-marketing total18639 leaves8837 outside Americas. Table hyphenation is readable; no clipping. No current standard adoption opinion is asserted.'),
 dict(pages=[309],finding='January clarification can appear in a report covering a December period without having occurred in that period. No material change in estimates is not constant estimates or balances. Indemnification reverses the tempting intuition that every third-party claim produces a receivable for Apple.',disposition='Prose preserves availability/event/report-period clocks and direction of the potential obligation. The last sentence is continued on310; no missing mathematical prerequisite or new local typo confirmed.'),
 dict(pages=[310],finding='Indemnity existence does not supply coverage, payment or recognized liability. Defense expense can occur even when allegations fail; settlements can change ongoing operations. Insurance needs distinct terms and recognition premises before any recovery is netted.',disposition='The mechanism keeps damage outcome, defense services, operating restriction and recovery separate. Business interruption, data and credit insurance populations are not conflated. Dense paragraphs are legible and each adds a different dependency.'),
 dict(pages=[311],finding='Insurance qualifications do not yield a common insured proportion or convert purchased coverage into an insurer-issued contract. A regulation may restrict imports or product design; new subject headings and repeated wording do not identify new events or unchanged laws.',disposition='Interim incorporation preserves annual dependency and exception language. Policy existence is kept separate from compliance, allegation and mitigation. No source probability or causal coefficient is invented.'),
 dict(pages=[312],finding='The operating scenario needs an effective measure, affected entity/product/route, timing and response before translating a disclosed risk into delivery or cost. Demand and supply can fail independently; common macro causes permit dependence but do not determine a joint law.',disposition='The geographic customer/supplier mismatch is recalled with a new operational consequence. No tariff rate or universal sales haircut is inferred. Page ends within the trade-restriction mechanism, explicitly carried in the exit state; layout remains readable.')],
 equations_reviewed=['28.17 displayed Americas expense bridge'],equation_judgments=[dict(labels=['28.17 displayed Americas expense bridge'],role='displayed comparative segment identity',verdict='correct local arithmetic; unchanged profit plus added cost categories does not establish historical availability or identical caption scope')],
 arithmetic_artifact='arithmetic-0307-0312.json',source_claims_reviewed=[],render_binding='render-bindings-0307-0312.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0307-0312.json').open('x') as f:json.dump(packet,f,indent=2);f.write(chr(10))
with (H/'inventory-before-0312.json').open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks))))

