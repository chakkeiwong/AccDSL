"""Record actual individual rendered reading301–306 and exact supporting math."""
from datetime import date
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0295-0300.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
c('country sales sum',142196+66952+181887,391035)
c('country assets sum',35664+4797+5219,45680)
c('Americas less US',167045-142196,24849)
c('non-iPhone total',391035-201183,189852)
c('other regions total',391035-66952,324083)
c('other region non-iPhone offset',189852-66952,122900)
for z in [Q(36000),Q(38000)]:
 cells=[z,Q(66952)-z,Q(201183)-z,Q(122900)+z]
 c(str(z)+' all cells nonnegative',min(cells)>=0,True)
 c(str(z)+' China row',cells[0]+cells[1],Q(66952))
 c(str(z)+' other region row',cells[2]+cells[3],Q(324083))
 c(str(z)+' iPhone column',cells[0]+cells[2],Q(201183))
 c(str(z)+' non-iPhone column',cells[1]+cells[3],Q(189852))
 c(str(z)+' all sales',sum(cells),Q(391035))
 c(str(z)+' China share higher',z/Q(66952)>(Q(201183)-z)/Q(324083),True)
 c(str(z)+' other region proportional share feasible',0<=(Q(201183)-z)/Q(324083)<=1,True)
 c(str(z)+' conditional loss',z/Q(10),Q(3600) if z==36000 else Q(3800))
c('conditional loss difference',Q(3800)-Q(3600),Q(200))
c('channel shares',38+62,100)
c('post period motion', (date(2024,9,30)-date(2024,9,28)).days,2)
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf'])
for n in range(301,307):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
with (D/'arithmetic-0301-0306.json').open('x') as f:json.dump(dict(count=len(checks),checks=checks,scope='Exact manuscript illustration only; source authority not newly checked'),f,indent=2)
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0301-0306',pages=list(range(301,307)),entry_state=prior['exit_state'],
 exit_state='Geographic and product sales margins do not identify joint product-region exposure or legal sellers. Incorporation, ownership, production custody, tax residence and functional currency require different evidence. Litigation adds operating remedies as well as potential payments; allegations, issuer positions, reported orders, dates and jurisdictions must stay separate. A September30 motion lies after the September28 period end, and repeated interim wording is not proof that intervening legal facts were unchanged. Continue from these unresolved legal-event, remedy and historical-availability distinctions.',
 observations=[
 dict(pages=[301],finding='Country flows and asset stocks have separate denominators; the China/Greater China equality is a reported comparison, not a legal-entity map. Equation28.24 turns product/region margins into a joint-table unknown with four cells.',disposition='Country sales/assets totals and the201183/189852 product split check. Date/stock/flow distinctions precede the equation; no source authority is newly certified. Table and display are legible.'),
 dict(pages=[302],finding='Two explicit z values preserve all disclosed numerical margins and yield different conditional shock losses. The prose qualifies the unquantified generally/moderately language, so these witnesses are not certified as complete interpretations. Geography then motivates the missing seller/owner/obligor layer.',disposition='Both tables, higher China share and3600/3800 losses check exactly. The source’s then-planned adoption is separated from a later2025 disclosure. The transition states why legal entities matter; no new current-rule claim is imported.'),
 dict(pages=[303],finding='Eighteen named subsidiary rows are expressly nonexhaustive. A Singapore risk discussion is evidence of unnamed subsidiaries, not permission to invent Apple Singapore. Ultimate wholly-owned membership permits different immediate ownership paths.',disposition='All18 rows visually inspected; footnote qualifications remain adjacent to the table. Named incorporation states/countries do not become control links or a historical ownership roster. No unsupported group graph is inferred.'),
 dict(pages=[304],finding='Apple India incorporation, Europe segment attribution, sales channels and outsourced-equipment custody describe distinct relationships. Functional currency and tax residence cannot be filled from jurisdiction alone; four Ireland rows do not identify the two unnamed historic tax branches.',disposition='38/62 channel shares sum100. Legal seller, asset owner, control, tax and currency dependencies are stated before the proposed query meaning. Dense prose remains legible without clipping; source and legal applicability are not re-certified.'),
 dict(pages=[305],finding='The legal discussion distinguishes a payment exposure from operating restrictions. Management’s incurred-loss assessment does not supply total accrual, case allocation, likelihood or zero exposure. Annual and interim settlement assertions describe different periods.',disposition='The source assessment is clearly attributed and qualified. No numeric probability or accounting threshold is inferred. The transition from entity scope to operating/legal consequences is coherent; final sentence correctly continues on306.'),
 dict(pages=[306],finding='DMA, DOJ and Epic retain different allegations, remedies, jurisdictions and procedural stages. The conditional10percent cap is not multiplied into a fine estimate; a reported disputed plan is not judicial acceptance. Event dates and reporting availability remain separate.',disposition='September30 is two days after September28. Historical source statements are not treated as present legal guidance. Page layout and quotations remain readable; no confirmed substantive manuscript defect in this segment.')],
 equations_reviewed=['28.24'],equation_judgments=[dict(labels=['28.24'],role='local exact cross-classification witness from reported margins',verdict='correct algebra under nonnegative displayed cells; both proposed z witnesses preserve every row/column and conditional10percent loss differs200. Qualitative mix constraints remain unquantified.')],
 arithmetic_artifact='arithmetic-0301-0306.json',source_claims_reviewed=[],render_binding='render-bindings-0301-0306.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0301-0306.json').open('x') as f:json.dump(packet,f,indent=2);f.write(chr(10))
with (H/'inventory-before-0306.json').open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks))))

