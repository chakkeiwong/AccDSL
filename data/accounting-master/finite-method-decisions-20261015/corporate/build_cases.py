"""Author finite documentary cases; never call the product runtime."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,subprocess,datetime
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(event,period,debit,credit):
    return dict(event=event,period=period,debit={k:str(v) for k,v in debit.items()},credit={k:str(v) for k,v in credit.items()})
def case(key,source,opening,inputs,events,expected,adverse):
    return dict(id=key,source=source,opening={k:str(v) for k,v in opening.items()},inputs=inputs,
                events=events,expected=expected,adverse=adverse,
                tax="uncomputed; these are pretax contributions, not after-tax equity")
def e(cash,assets,liabilities,equity,profit,oci=0):
    return dict(cash=str(cash),other_assets={k:str(v) for k,v in assets.items()},
                liabilities={k:str(v) for k,v in liabilities.items()},equity=str(equity),
                cumulative_profit=str(profit),cumulative_oci=str(oci))
C=[]
C.append(case('restoration-cost-increase','EU2023 IFRIC1.5/7; IAS36',
 {'cash':100,'ppe':80,'provision':-20,'capital':-160},
 {'revised_provision':'50','recoverable':'90','remaining_years':'4','residual':'0',
  'discount':'separate flat-zero supplied rate hypothesis; no passage-of-time accretion in this branch'},[
 j('estimate-change','P1',{'ppe':30},{'provision':30}),
 j('impairment','P1',{'expense.impairment':20},{'ppe':20}),
 j('next-year-depreciation','P2',{'expense.depreciation':'45/2'},{'ppe':'45/2'})],
 {'P1':e(100,{'ppe':90},{'provision':50},140,-20),
  'P2':e(100,{'ppe':'135/2'},{'provision':50},'235/2','-85/2')},
 ['Carrying110 without the admitted impairment test is wrong.','Depreciation over original life ignores the revised remaining life.']))
C.append(case('restoration-cost-decrease','EU2023 IFRIC1.5(b)',
 {'cash':100,'ppe':30,'provision':-80,'capital':-50},
 {'revised_provision':'30'},[
 j('estimate-change','P1',{'provision':50},{'ppe':30,'income.restoration':20})],
 {'P1':e(100,{'ppe':0},{'provision':30},70,20)},
 ['A negative PPE balance of20 is rejected.','Crediting all50 to income ignores the remaining asset cost.']))
C.append(case('restoration-revaluation-increase','EU2023 IFRIC1.6(a)(ii)/6(c)',
 {'cash':100,'ppe':150,'provision':-50,'capital':-180,'surplus':-20},
 {'revised_provision':'85','same_asset_surplus':'20','current_fair_value':'150',
  'revaluation_review':'same-asset and whole-class review establishes no further adjustment'},[
 j('estimate-change','P1',{'oci.restoration':20,'expense.restoration':15},{'provision':35})],
 {'P1':e(100,{'ppe':150},{'provision':85},165,-15,-20)},
 ['An unrelated asset surplus cannot absorb the loss.','A missing whole-class review returns unresolved.']))
C.append(case('restoration-revaluation-decrease','EU2023 IFRIC1.6(a)(i)/6(b)/6(c)',
 {'cash':100,'ppe':25,'provision':-80,'capital':-60,'retained_prior_loss':15},
 {'revised_provision':'30','hypothetical_cost_carrying':'40','same_asset_prior_profit_deficit':'15',
  'current_fair_value':'25','revaluation_review':'no additional revaluation required'},[
 j('estimate-change','P1',{'provision':50},{'income.restoration':25,'oci.restoration':25})],
 {'P1':e(100,{'ppe':25},{'provision':30},95,25,25)},
 ['Using revalued25 instead of hypothetical cost40 as the paragraph6(b) floor is wrong.',
  'Routing the full50 through OCI ignores both excess10 and prior profit deficit15.']))
C.append(case('restoration-lifetime','EU2023 IFRIC1.5/7/8; IAS37',
 {'cash':100,'ppe':120,'provision':-20,'capital':-200},
 {'initial_remaining_years':'2','residual':'0','discount_rate':'1/10',
  'year1_revised_provision':'33','cashflow_classification':'unresolved; total cash bridge only'},[
 j('first-depreciation','P1',{'expense.depreciation':60},{'ppe':60}),
 j('first-unwind','P1',{'expense.finance':2},{'provision':2}),
 j('revised-estimate','P1',{'ppe':11},{'provision':11}),
 j('final-depreciation','P2',{'expense.depreciation':71},{'ppe':71}),
 j('final-unwind','P2',{'expense.finance':'33/10'},{'provision':'33/10'}),
 j('actual-settlement','P2',{'provision':'363/10'},{'cash':'363/10'})],
 {'P1':e(100,{'ppe':71},{'provision':33},138,-62),
  'P2':e('637/10',{'ppe':0},{'provision':0},'637/10','-1363/10')},
 ['Capitalising unwind2 or3.3 violates paragraph8.','An estimate change is not a cash payment.']))
C.append(case('restoration-exhausted-life','EU2023 IFRIC1.7',
 {'cash':100,'provision':-20,'capital':-80},
 {'revised_provision':'25','remaining_life':'0','applies_to':'both asset models'},[
 j('late-change','P1',{'expense.restoration':5},{'provision':5})],
 {'P1':e(100,{}, {'provision':25},75,-5)},
 ['Recreating an asset or using old revaluation surplus after useful life is wrong.']))
C.append(case('assurance-population','AASB15.B28-B33; AASB137.14/24/36-62',
 {'cash':1000,'inventory':600,'capital':-1600},
 {'population':100,'costs':['0','10','40'],'weights':['3/4','1/5','1/20'],
  'price':'2000','cost_of_goods':'600','initial_reimbursement':'100',
  'reimbursement_fraction':'1/4','reimbursement_condition':'virtually certain on settlement',
  'paid_claims':'100','revised_remaining_best_estimate':'250',
  'discount':'immaterial short horizon; explicit finding','recognition':'present duty and probable population outflow admitted'},[
 j('sale','P1',{'cash':2000},{'income.sales':2000}),
 j('goods-transfer','P1',{'expense.goods':600},{'inventory':600}),
 j('warranty-recognition','P1',{'expense.warranty':400},{'provision':400}),
 j('reimbursement-recognition','P1',{'reimbursement':100},{'income.reimbursement':100}),
 j('claim-payment','P1',{'provision':100},{'cash':100}),
 j('claim-reimbursement','P1',{'cash':25},{'reimbursement':25}),
 j('remaining-claims-review','P1',{'provision':50},{'income.warranty_release':50}),
 j('reimbursement-review','P1',{'expense.reimbursement':'25/2'},{'reimbursement':'25/2'}),
 j('final-claims','P2',{'provision':250},{'cash':250}),
 j('final-reimbursement','P2',{'cash':'125/2'},{'reimbursement':'125/2'})],
 {'P1':e(2925,{'inventory':0,'reimbursement':'125/2'},{'provision':250},'5475/2','2275/2'),
  'P2':e('5475/2',{'inventory':0,'reimbursement':0},{'provision':0},'5475/2','2275/2')},
 ['A25% individual claim probability does not permit zero for the whole population.',
  'Merely probable reimbursement is unrecognised, not an automatic100 asset.',
  'Netting the reimbursement against the liability conceals the gross obligation.',
  'Using400 again after100 paid and a new250 remaining estimate double counts.']))
C.append(case('mixed-contract-modification','AASB15.18-21(c)/39-45/63/73-90',
 {'cash':100,'capital':-100},
 {'construction_price':'100','visits':4,'visit_price':'5','original_construction_cost':'80',
  'construction_cost_incurred':'40','addition_construction':'40','addition_visits':2,
  'revised_construction_cost':'100','visit_cost':'2',
  'allocation':'independently supported equal standalone prices; no discount or variable consideration',
  'progress':'faithful cost-to-cost; no inefficient or uninstalled input in40',
  'construction':'new work integrated into same partially satisfied obligation',
  'visits_scope':'distinct inspections on an existing unrelated operating line',
  'financing':'one-year-or-less paragraph63 practical expedient elected'},[
 j('initial-prepayment','P1',{'cash':120},{'contract_liability':120}),
 j('initial-construction-cost','P1',{'expense.construction':40},{'cash':40}),
 j('initial-construction-performance','P1',{'contract_liability':50},{'income.construction':50}),
 j('first-visit-cost','P1',{'expense.visits':2},{'cash':2}),
 j('first-visit-performance','P1',{'contract_liability':5},{'income.visits':5}),
 j('amendment-prepayment','P1',{'cash':50},{'contract_liability':50}),
 j('construction-catch-up','P1',{'contract_liability':6},{'income.construction':6}),
 j('two-visits-cost','P1',{'expense.visits':4},{'cash':4}),
 j('two-visits-performance','P1',{'contract_liability':10},{'income.visits':10}),
 j('construction-completion-cost','P2',{'expense.construction':60},{'cash':60}),
 j('construction-completion','P2',{'contract_liability':84},{'income.construction':84}),
 j('three-visits-cost','P2',{'expense.visits':6},{'cash':6}),
 j('three-visits-performance','P2',{'contract_liability':15},{'income.visits':15})],
 {'P1':e(224,{}, {'contract_liability':99},125,25),
  'P2':e(158,{}, {'contract_liability':0},158,58)},
 ['Using old50% on revised140 gives70 rather than56.',
  'A prospective-only treatment loses catch-up6.',
  'Applying40% to all170 wrongly recognizes future distinct visits.',
  'Unknown allocation, approval, progress or enforceability returns unresolved.']))

# Production cases use the retained EU source, not an undated AU scope transfer.
C.append(case('production-wip','EU2023 IAS2.10-18/28-33',
 {'cash':3000,'capital':-3000},
 {'started':100,'completed':80,'ending_wip':20,'conversion_fraction':'1/2',
  'material_cost':'1000','variable_conversion':'450','fixed_cost':'600',
  'normal_equivalent_units':'120','sold':50,'sale_price':'30',
  'policy':'material at start; homogeneous conversion; no opening WIP/waste; separate component equivalent units',
  'next_month_normal_equivalent_units':'10','next_month_fixed_cost':'50','next_month_variable_cost':'50',
  'nrv':'independently supported not below assigned cost'},[
 j('material-use','P1',{'wip':1000},{'cash':1000}),
 j('variable-conversion','P1',{'wip':450},{'cash':450}),
 j('fixed-conversion','P1',{'wip':450,'expense.idle':150},{'cash':600}),
 j('completed-transfer','P1',{'finished':1600},{'wip':1600}),
 j('goods-sale','P1',{'cash':1500},{'income.sales':1500}),
 j('goods-cost','P1',{'expense.goods':1000},{'finished':1000}),
 j('final-conversion','P2',{'wip':100},{'cash':100}),
 j('final-transfer','P2',{'finished':400},{'wip':400}),
 j('remaining-sale','P2',{'cash':1500},{'income.sales':1500}),
 j('remaining-cost','P2',{'expense.goods':1000},{'finished':1000})],
 {'P1':e(2450,{'wip':300,'finished':600},{},3350,350),
  'P2':e(3850,{'wip':0,'finished':0},{},3850,850)},
 ['Treating20 half-converted units as fully converted misallocates conversion.',
  'Assigning all600 fixed overhead to90 units capitalises150 idle expense.',
  'Unknown physical progress or normal capacity returns unresolved.']))
C.append(case('joint-products','EU2023 IAS2.14',
 {'cash':500,'capital':-500},
 {'joint_cost':'300','quantities':{'A':60,'B':40},'splitoff_prices':{'A':'4','B':'9'},
  'sold':{'A':30,'B':10},'basis':'observable split-off relative sales values; inseparable costs; no subsequent costs',
  'nrv':'each unsold product independently passes lower-of-cost/NRV'},[
 j('joint-production','P1',{'product_A':120,'product_B':180},{'cash':300}),
 j('sale-A','P1',{'cash':120},{'income.sales':120}),
 j('sale-B','P1',{'cash':90},{'income.sales':90}),
 j('cost-A','P1',{'expense.goods':60},{'product_A':60}),
 j('cost-B','P1',{'expense.goods':45},{'product_B':45})],
 {'P1':e(410,{'product_A':60,'product_B':135},{},605,105)},
 ['Mass allocation180/120 is not the admitted relative-sales policy.',
  'Missing split-off values cannot be replaced by equal weights.']))
C.append(case('immaterial-byproduct','EU2023 IAS2.14',
 {'cash':500,'capital':-500},
 {'production_cost':'300','byproduct_nrv':'20','immateriality':'separately established for the entity; no numeric shortcut'},[
 j('production','P1',{'main_product':280,'byproduct':20},{'cash':300}),
 j('byproduct-sale','P1',{'cash':20},{'income.sales':20}),
 j('byproduct-cost','P1',{'expense.goods':20},{'byproduct':20})],
 {'P1':e(220,{'main_product':280,'byproduct':0},{},500,0)},
 ['Deducting20 from main cost without retaining the byproduct loses inventory.',
  'A material co-product cannot use the immaterial shortcut.']))
C.append(case('deferred-supplier','EU2023 IAS2.18; IFRS9 amortised cost; IAS7 policy',
 {'cash':100,'capital':-100},
 {'normal_price':'100','due':'121','years':2,'eir':'1/10','sale':'150',
  'classification':'ordinary original supplier payable; no finance provider or qualifying asset',
  'cashflow_policy':'supplier principal operating; interest paid operating under historical IAS7 election'},[
 j('goods-receipt','P1',{'inventory':100},{'supplier':100}),
 j('sale','P1',{'cash':150},{'income.sales':150}),
 j('sale-cost','P1',{'expense.goods':100},{'inventory':100}),
 j('first-interest','P1',{'expense.finance':10},{'supplier':10}),
 j('second-interest','P2',{'expense.finance':11},{'supplier':11}),
 j('payment','P2',{'supplier':121},{'cash':121})],
 {'P1':e(250,{'inventory':0},{'supplier':110},140,40),
  'P2':e(129,{'inventory':0},{'supplier':0},129,29)},
 ['Inventory121 capitalises21 financing improperly in this case.',
  'Interest10.5 in each year ignores the admitted effective-interest method.',
  'An actual altered creditor or financing arrangement needs fresh cashflow analysis.']))

if __name__=='__main__':
    assert not (OUT/'cases.json').exists(), 'Preserve completed evidence; do not rerun builder.'
    paths=['docs/design/research/p08-v3-preparation/eu-2023-1803-original.pdf',
           'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
           'docs/design/proposal/methods/sources/aasb15-compiled-dec2022.pdf',
           'docs/design/proposal/methods/sources/aasb15-compiled-dec2022.txt']
    paths += [str(p.relative_to(ROOT)) for p in sorted((OUT/'sources').iterdir()) if p.is_file()]
    dump('source-manifest.json',{'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'aasb137_url':'https://www.aasb.gov.au/admin/file/content105/c9/AASB137_08-15_COMPdec22_01-23.pdf',
      'files':[{'path':p,'sha256':sha(ROOT/p)} for p in paths],
      'scope':'historical synthetic cases; operative-date discrepancy retained in source-reading.md'})
    dump('cases.json',{'kind':'author-entered documentary arithmetic; not product execution',
                       'version':'R03-E/1','cases':C})
    print(json.dumps({'cases':len(C),'events':sum(len(c['events']) for c in C),
                      'adverse_targets':sum(len(c['adverse']) for c in C)}))
