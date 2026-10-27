"""Record actual pages295–300; exact local arithmetic is supporting evidence."""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import json,fitz
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0289-0294.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
for n,a,b in [
 ('commitment net movement',Q(53)-Q('39.8'),Q('13.2')),('no new orders',Q(53)-Q('13.2'),Q('39.8')),
 ('five new orders',Q(53)+5-Q('18.2'),Q('39.8')),('cash settlement net assets',Q('13.2')-Q('13.2'),Q(0)),
 ('credit delivery balance',Q('13.2')-Q('13.2'),Q(0)),
 ('2023 resource fair value',29965+31590+100544,162099),('2024 resource fair value',29943+35228+91479,156650),
 ('2024 December resource fair value',30299+23476+87593,141368),('2023 cost plus loss',173752-11653,162099),
 ('2024 cost plus loss',160600-3950,156650),('December cost plus loss',147088-5720,141368),
 ('September restrictions subtraction',156650-2600-13200,140850),('December restrictions subtraction',141368-3300-126,137942),
 ('December cash/current securities',30299+23476,53775),('December current less escrow',53775-3300-126,50349),
 ('annual security cash released',51211+11135-48656,13690),('quarter security cash released',15967+3492-6124,13335),
 ('opening marketable securities',31590+100544,132134),('annual closing securities',35228+91479,126707),
 ('quarter closing securities',23476+87593,111069),('annual securities movement',126707-132134,-5427),
 ('quarter securities movement',111069-126707,-15638),('annual residual',-5427+13690,8263),('quarter residual',-15638+13335,-2303),
 ('annual valuation cost change',160600-173752,-13152),('annual unrealized change',-3950+11653,7703),
 ('annual fair value change',-13152+7703,-5449),('quarter valuation cost change',147088-160600,-13512),
 ('quarter unrealized change',-5720+3950,-1770),('quarter fair value change',-13512-1770,-15282),
 ('cash-population difference',30737-29965,772),('annual cash-flow change',29943-30737,-794),('annual BS cash change',29943-29965,-22),
 ('quarter cash change',30299-29943,356),('trade annual residual',3902-3788,114),('trade quarter residual',-3771+3597,-174),
 ('vendor annual residual',1356-1356,0),('vendor quarter residual',-3166+3166,0),
 ('two customers share',18+11,29),('overlap both carriers',29+33-29,33),('overlap no carriers',29+33,62),
 ('only18 customer carrier',29+33-18,44),('only11 customer carrier',29+33-11,51),
 ('customer population sum',sum([18,11,9,9,8,7,4,9,9,8,8]),100),('first carrier set',18+11+4,33),('second carrier set',9+9+8+7,33),
 ('vendor September share',44+23,67),('vendor December share',43+24,67),
 ('annual segment bridge',162044-31370-7458,123216),('quarter segment bridge',53174-8268-2074,42832),
 ('annual common cost',31370+7458,38828),('allocation1',sum([14000,10000,5000,4000,5828]),38828),
 ('allocation2',sum([13000,10000,6000,4000,5828]),38828),('China hypothetical1',27082-5000,22082),('China hypothetical2',27082-6000,21082)]:c(n,Q(a),Q(b))
c('September rounding lower',Q('156649.5')-2650-13250,Q('140749.5'))
c('September rounding upper',Q('156650.5')-2550-13150,Q('140950.5'))
c('September stated140.8 lower',Q('140.8')*1000-50,Q(140750))
c('September stated140.8 upper',Q('140.8')*1000+50,Q(140850))
c('rounded intervals intersect',max(Q('140749.5'),Q(140750))<=min(Q('140950.5'),Q(140850)),True)
c('December rounding lower',Q('141367.5')-3350-Q('126.5'),Q(137891))
c('December rounding upper',Q('141368.5')-3250-Q('125.5'),Q(137993))
for name,shares in [('Sept plain',[86,10,4]),('Sept mortgage',[14,9,77]),('Dec plain',[85,11,4]),('Dec mortgage',[13,10,77])]:c(name+' shares',Q(sum(shares)),Q(100))
c('exactly two customers reach10',sum(x>=10 for x in [18,11,9,9,8,7,4,9,9,8,8]),2)
assert all(x['passed'] for x in checks),[x for x in checks if not x['passed']]
doc=fitz.open(ROOT/v['pdf'])
for n in range(295,301):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
with (D/'arithmetic-0295-0300.json').open('x') as f:json.dump(dict(checks=checks,count=len(checks),scope='Exact manuscript-example arithmetic; source authority not newly verified'),f,indent=2);f.write(chr(10))
r=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0295-0300',pages=list(range(295,301)),entry_state=prior['exit_state'],
 exit_state='Commitment declines identify net delivery less new orders only under explicit simplifying assumptions; delivery and payment remain separate. Resource totals, restrictions, valuation, securities turnover, customer overlap and geographic attribution require distinct quantities and dates. Annual and interim segment bridges reconcile, but corporate cost allocations remain nonidentified; two nonnegative allocations give Greater China profits22082 or21082. Continue the geographic and operating-history argument from that unresolved allocation.',
 observations=[
 dict(pages=[295],finding='One weighted-average lease rate cannot recover contract rates or thereafter timing. Fixed/variable expense, cash and noncash additions differ. Note12 term restrictions and MD&A payment horizons describe different populations. Equation28.22 supplies only delivery less new orders.',disposition='13.2 net movement and both synthetic order histories check. Supplied simplifying assumptions prevent an actual purchase/cash estimate. Lease cost and commitment totals are not double-counted.'),
 dict(pages=[296],finding='Cash delivery, credit delivery and later payment have distinct postings. Supply constraints and dated litigation assessment do not provide numerical probabilities or zero exposure. Resource fair-value and adjusted-cost columns are alternative reconciliations, not additive funding.',disposition='Three dated resource totals and valuation reconciliations check. Adjusted cost is not indiscriminately renamed amortized cost. Heading, prose and table are legible.'),
 dict(pages=[297],finding='Restricted escrow affects availability separately from current classification. Conditional rounding intervals reconcile apparently different September totals. December subtraction is indicative; maturity percentages divide separate populations and do not identify liquidation prices or cash dates.',disposition='September/December subtractions, interval endpoints and each separate maturity partition check. Management sufficiency language remains a dated assessment, not a guarantee.'),
 dict(pages=[298],finding='Security cash released differs from stock changes; residuals8263 and-2303 are not identified valuation journals. Total-resource valuation includes cash unlike the securities bridge; OCI has a different population/tax/timing basis. Receivable residuals do not recover gross collections.',disposition='Annual/quarter cash, stock, valuation and receivable arithmetic checks. Rate-shock losses remain issuer scenarios, not cash outflows or loss probabilities; no local model replication is implied.'),
 dict(pages=[299],finding='Customer/carrier shares overlap at the customer level. The11-customer construction supports union shares33/62 and discrete44/51 alternatives. Trade denominator is not silently equated with net BS receivables. Vendor shares use another population; geographic segments are management divisions.',disposition='Customer partition, two large customers, carrier subsets, unions and vendor totals check. Examples preserve unknown identities and loss probabilities; no continuous-overlap assumption is smuggled in.'),
 dict(pages=[300],finding='India falls within the reported Europe segment convention but does not locate seller, factory or cash recipient. Management demand/currency explanations are not estimated response equations. Equation28.23 reconciles company-wide costs while leaving their regional allocation unidentified.',disposition='Annual/interim segment bridges and two nonnegative allocation totals check. China profits22082/21082 are conditional examples, not reported figures. No clipping or new local typographical defect observed.')],
 equations_reviewed=['28.22','28.23','28.13 unnumbered securities residual and inclusion-exclusion'],
 equation_judgments=[dict(labels=['28.22'],role='simplified undelivered-order balance',verdict='correct identity with explicit no-cancellation/price/currency assumptions; does not identify payments'),
 dict(labels=['28.23'],role='segment-to-consolidated operating income bridge',verdict='correct; allocation ambiguity shown by explicit witnesses'),
 dict(labels=['28.13'],role='signed stock/cash residual and exact set union',verdict='correct under stated populations, signs and exact-percentage illustration')],arithmetic_artifact='arithmetic-0295-0300.json',source_claims_reviewed=[],render_binding='render-bindings-0295-0300.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0295-0300.json').open('x') as f:json.dump(r,f,indent=2);f.write(chr(10))
with (HERE/'inventory-before-0300.json').open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
print(json.dumps(dict(segment=r['id'],arithmetic_checks=len(checks))))

