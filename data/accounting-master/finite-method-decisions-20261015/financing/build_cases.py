"""Author finite historical-rule financing cases, not a product engine."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import hashlib,json,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rat(n):q=Q(n);return str(q)
def save(name,x):(OUT/name).write_text(json.dumps(x,indent=2)+'\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 source_specs={
 'aasb132':('docs/design/research/standards/aasb132','5c8ce25447c6186ec49f751bc9e7ad48563caaff542b0e0287f3f7783a480501',[('classification','21          A contract','28      The issuer'),('components','28      The issuer','33      If an entity'),('conversion','AG30      Paragraph','AG36      An entity'),('repurchase-inducement','IE39    The following','IE50    The incremental')]),
 'aasb9':('docs/design/research/p08-v1/aasb9','8f5a87c67a76c193bedeee8ea7f3f21556b3886eee4184a62c7045256b3f84f0',[('eligibility','6.2.1   A derivative','6.5.2   There are'),('hedge-accounting','6.5.5   If a hedging','6.5.15   When an entity'),('effectiveness','B6.4.1    Hedge effectiveness','B6.5.7   Rebalancing'),('benchmark-measurement','5.4.5   An entity','5.5 Impairment\n'),('benchmark-designation','6.9.1    As and when','Chapter 7 Effective date and transition\n')]),
 'aasb107':('docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb107-compiled-jun2023',None,[('cash-classification','16      The separate','18        An entity'),('interest-election','31      Cash flows','34      Dividends'),('noncash','43      Investing','44A')])}
 authorities=[]
 for sid,(base,expected,spans) in source_specs.items():
  pdf=ROOT/(base+'.pdf');txt=ROOT/(base+'.txt');s=txt.read_text();assert expected is None or sha(pdf)==expected
  items=[]
  for name,start,end in spans:
   a=s.index(start);b=s.index(end,a+len(start))
   if name=='repurchase-inducement':b=s.index('\n',b)+1
   items.append({'id':name,'start':a,'end':b,'text':s[a:b],'sha256':hashlib.sha256(s[a:b].encode()).hexdigest(),'offset_unit':'Unicode code points'})
  authorities.append({'id':sid,'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),'text':str(txt.relative_to(ROOT)),'text_sha256':sha(txt),'cover':s[:s.index('\f')],'spans':items,'scope':'historical AU for-profit Tier1 calendar2024/25; no optional later amendments','current_authority_claim':False})
 save('source-support.json',{'authorities':authorities,'inspection':'Technical paragraphs and relevant examples inspected from retained primary text; no new current-source admission'})
 cases=[]
 def case(key,opening,assumptions):
  c={'id':key,'opening':{k:rat(v) for k,v in opening.items()},'assumptions':assumptions,'events':[],'pretax_only':True,'tax_status':'uncomputed','runtime_executed':False};cases.append(c);return c
 def event(c,key,postings,oci=0,owner=0,basis=0,cash=None,state=None):
  c['events'].append({'id':key,'postings':[{'account':k,'debit_signed':rat(v)} for k,v in postings.items() if v],'oci':rat(oci),'owner_equity_change':rat(owner),'direct_basis_equity_change':rat(basis),'cash_flows':{k:rat((cash or {}).get(k,0)) for k in ['operating','investing','financing']},'state':state or {}})
 # Source-rounded example is separate from the exact cash-flow valuation.
 c=case('repurchase-rounded',{'cash':2000,'debt':-962,'capital':-1038},['AASB132 IE39-46 rounded illustration; original rights unchanged; equity includes original component60; zero fees.'])
 event(c,'repurchase',{'debt':962,'expense':119,'capital':619,'cash':-1700},owner=-619,cash={'financing':-1700},state={'old_equity_component_retained_within_total':'60','rights_changed':False})
 def pv(r):return sum(Q(50)/(1+r)**k for k in range(1,11))+Q(1000)/(1+r)**10
 old=pv(Q(11,200));fv=pv(Q(1,25));loss=fv-old;equity=1700-fv
 c=case('repurchase-exact',{'cash':2000,'debt':-old,'capital':old-2000},['Cash-flow-derived exact fractions; source presentation rounds to962/1081; zero fees, unchanged privileges.'])
 event(c,'repurchase',{'debt':old,'expense':loss,'capital':equity,'cash':-1700},owner=-equity,cash={'financing':-1700})
 c['valuation']={'face':'1000','coupon':'50','remaining_half_years':10,'old_period_rate':'11/200','market_period_rate':'1/25','old_pv':rat(old),'current_pv':rat(fv),'equity_allocation':rat(equity)}
 c=case('immediate-inducement',{'cash':2000,'debt':-960,'capital':-1040},['Immediate unconditional share-only conversion; supplied debt960 is local, not IE49 carrying debt; equity includes original60; zero fees.'])
 c['terms']={'face':'1000','old_conversion_price':'25','new_conversion_price':'20','share_price_at_amendment':'40','share_price_later':'50','original_equity':'60','carrying_debt':'960'}
 event(c,'amend-and-convert',{'debt':960,'expense':400,'capital':-1360},owner=1360,state={'shares_issued':50,'loss_measurement_date':'amendment','original_equity_preserved':'60'})
 # Shared documentary cash-flow hedge with two cumulative measurements.
 for branch in ['inventory','interest','discontinued-expected','cancelled','unrecoverable-loss']:
  c=case('cash-flow-'+branch,{'cash':200,'capital':-200},['Supplied eligible external whole derivative and reliably measured item; documented inception designation; no excluded components; independent economic/credit/ratio findings; no intermediate release before listed measurement.'])
  if branch=='inventory':
   event(c,'measure-1',{'derivative':12,'reserve':-10,'income':-2},oci=10,state={'cumulative_D':'12','cumulative_H':'-10','effective':'10','ineffective':'2'})
   event(c,'measure-2',{'derivative':3,'reserve':-4,'expense':1},oci=4,state={'cumulative_D':'15','cumulative_H':'-14','effective':'14','ineffective':'1'})
   event(c,'buy-inventory',{'inventory':114,'cash':-114},cash={'operating':-114})
   event(c,'settle-derivative',{'cash':15,'derivative':-15},cash={'operating':15})
   event(c,'basis-adjust',{'reserve':14,'inventory':-14},basis=-14,state={'nonfinancial_basis_transfer':'14','reclassification':False})
   event(c,'sell-inventory',{'cash':130,'income':-130},cash={'operating':130})
   event(c,'cost-of-sales',{'expense':100,'inventory':-100})
  elif branch=='interest':
   event(c,'measure',{'derivative':8,'reserve':-8},oci=8,state={'cumulative_D':'8','cumulative_H':'-8','effective':'8','ineffective':'0'})
   event(c,'settle',{'cash':8,'derivative':-8},cash={'operating':8})
   event(c,'pay-interest',{'expense':18,'cash':-18},cash={'operating':-18})
   event(c,'release-to-interest',{'reserve':8,'income':-8},oci=-8,state={'reclassification':True})
  elif branch in ['discontinued-expected','cancelled']:
   event(c,'measure',{'derivative':10,'reserve':-10},oci=10,state={'cumulative_D':'10','cumulative_H':'-10','effective':'10','ineffective':'0'})
   event(c,'discontinue',{},state={'active':False,'highly_probable':False,'still_expected':branch=='discontinued-expected'})
   if branch=='cancelled':event(c,'release-cancelled',{'reserve':10,'income':-10},oci=-10,state={'reclassification':True})
  else:
   event(c,'measure-loss',{'derivative':-10,'reserve':10},oci=-10,state={'cumulative_D':'-10','cumulative_H':'10','effective':'-10','ineffective':'0'})
   event(c,'release-unrecoverable',{'expense':4,'reserve':-4},oci=4,state={'unrecoverable_portion':'4','reclassification':True})
 c=case('fair-value-debt',{'cash':200,'debt':-100,'capital':-100},['Supplied qualifying fair-value hedge, derivative gain8, debt risk-value increase10; contractual principal100 plus coupon21 due in one year; revised EIR starts on discontinuation; interest cash is operating under the explicit historical election.'])
 event(c,'measure-derivative',{'derivative':8,'income':-8})
 event(c,'measure-item',{'expense':10,'debt':-10})
 event(c,'discontinue',{},state={'active':False,'recalculated_eir':'1/10','remaining_payment':'121','years':'1'})
 event(c,'accrete',{'expense':11,'debt':-11})
 event(c,'pay-debt',{'debt':121,'cash':-121},cash={'financing':-100,'operating':-21})
 # Produce expected reports; verifier independently recomputes events and facts.
 for c in cases:
  ledger={k:Q(v) for k,v in c['opening'].items()};oci=owner=basis=Q(0);flows={k:Q(0) for k in ['operating','investing','financing']};initial_equity=-sum(ledger.get(k,0) for k in ['capital','reserve'])
  for e in c['events']:
   for p in e['postings']:ledger[p['account']]=ledger.get(p['account'],0)+Q(p['debit_signed'])
   oci+=Q(e['oci']);owner+=Q(e['owner_equity_change']);basis+=Q(e['direct_basis_equity_change'])
   for k in flows:flows[k]+=Q(e['cash_flows'][k])
   profit=-ledger.get('expense',0)-ledger.get('income',0);assets=sum(ledger.get(k,0) for k in ['cash','inventory'])+max(ledger.get('derivative',0),0);liabilities=-ledger.get('debt',0)+max(-ledger.get('derivative',0),0);equity_now=-ledger.get('capital',0)-ledger.get('reserve',0)+profit
   e['expected_report']={k:rat(v) for k,v in {'cash':ledger.get('cash',0),'inventory':ledger.get('inventory',0),'derivative_net':ledger.get('derivative',0),'debt':-ledger.get('debt',0),'reserve':-ledger.get('reserve',0),'pretax_profit':profit,'oci':oci,'comprehensive_pretax':profit+oci,'owner_equity_change':owner,'direct_basis_equity_change':basis,'assets':assets,'liabilities':liabilities,'pretax_equity':equity_now,'equity_bridge':initial_equity+profit+oci+owner+basis,**flows}.items()}
 adverse=[
 {'id':'wrong-repurchase-full-loss','candidate':'expense738/equity0','rejection':'AG33-34 require separate equity allocation619'},
 {'id':'wrong-inducement-later-price','candidate':'loss500','rejection':'AG35 amendment-date loss400'},
 {'id':'wrong-inducement-face-transfer','candidate':'debit debt1000','rejection':'carrying debt960 controls derecognition'},
 {'id':'cash-alternative-equity','candidate':'all equity because issuer may choose shares','rejection':'132.26 tests every settlement alternative'},
 {'id':'missing-designation','candidate':'OCI10','rejection':'6.4.1 inception documentation missing'},
 {'id':'credit-dominance','candidate':'qualifies because underlying prices correlate','rejection':'6.4.1/B6.4.6-8 require independent economic/credit findings'},
 {'id':'incremental-lower-of','candidate':'second effective increment3','rejection':'cumulative target14 minus previous10 is4'},
 {'id':'basis-as-reclassification','candidate':'OCI-14 and expense credit14','rejection':'6.5.11(d)(i) direct inventory basis transfer'},
 {'id':'release-on-settlement','candidate':'reserve becomes0 when derivative cash15 arrives','rejection':'settlement alone does not release reserve'},
 {'id':'expected-is-cancelled','candidate':'release10 because no longer highly probable','rejection':'6.5.12 distinguishes still expected'},
 {'id':'old-rate-after-discontinuation','candidate':'interest23.1 on110','rejection':'6.5.10 recalculated EIR10%, interest11'},
 {'id':'reform-name-only','candidate':'automatic exception','rejection':'5.4.7 direct consequence and economic equivalence required'},
 {'id':'unknown-measurement-zero','candidate':'missing derivative fair value becomes0','rejection':'measurement unresolved'},
 {'id':'double-basis-transfer','candidate':'apply14 twice under same event','rejection':'event replay and reserve state reject duplicate'}]
 save('cases.json',{'scope':'historical conditional pretax documentary methods','cases':cases,'adverse_cases':adverse,'not_concluded':['current compliance','actual instrument valuation','runtime execution','R03 completion']})
 print(json.dumps({'cases':len(cases),'events':sum(len(c['events']) for c in cases),'adverse':len(adverse),'authorities':len(authorities)}))
if __name__=='__main__':main()
