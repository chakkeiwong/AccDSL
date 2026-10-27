"""Selected signed-book equalities against preserved native states and mutations."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_collection_totals_v1 as totals
import method_collections_v1 as collections
NATIVE=HERE.parent/'company-return-execution-20261024/native_returns.py'
spec=importlib.util.spec_from_file_location('totals_native_returns',NATIVE)
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


def known(value):return {'status':'known','value':value}
def ref(key):return {'op':'ref','id':key}
def binary(op,a,b):return {'op':op,'left':a,'right':b}
def fmt(value):
    q=Fraction(value);return f'{q.numerator}/{q.denominator}'


def project(state):
    context={k:state['context'][k] for k in ['entity','book_role']}
    context['date']=state['date']
    money={'kind':'rational','context':context,'dimensions':{'currency:'+state['context']['currency']:1},'scale':'1/1'}
    h=core.digest(state)
    def declaration(kind,path):
        return {'type':deepcopy(money) if kind=='rational' else {'kind':kind,'context':deepcopy(context)},
                'role':'state','source_ref':'derived-sha256:'+h+'#'+path}
    keys=['inventory','other_inventory','refund_liability','refund','recovery_asset','recovery']
    globals={key:declaration('rational','/selected/'+key) for key in keys}
    account={'id':declaration('text','/balances/key'),'amount':declaration('rational','/balances/value')}
    lot={'id':declaration('text','/lots/key'),'carrying':declaration('rational','/lots/*/carrying'),
         'tax_base':declaration('rational','/lots/*/tax_base')}
    snap={'profile':collections.PROFILE,'method_id':'native.book.selected_snapshot','version':'1',
          'inputs':globals,'collections':{'accounts':{'fields':account},
            'registry':{'fields':{'id':deepcopy(account['id'])}},'lots':{'fields':lot}},
          'constraints':[{'id':'accounts.unique','op':'unique','collection':'accounts','field':'id'},
             {'id':'registry.unique','op':'unique','collection':'registry','field':'id'},
             {'id':'lots.unique','op':'unique','collection':'lots','field':'id'},
             {'id':'accounts.declared','op':'references','source':'accounts','field':'id','target':'registry','target_field':'id'},
             {'id':'accounts.complete','op':'references','source':'registry','field':'id','target':'accounts','target_field':'id'}],
          'residual_prerequisites':['Account classification, lot lifecycle, cash feasibility and state effects remain separate.']}
    def requirement(name,predicate,deps,on_false='invalid'):
        return {'id':name,'guard':{'op':'const','type':core.BOOL,'value':True},'guard_requires':[],
                'predicate':predicate,'requires':deps,'admission_refs':[],'on_false':on_false,'on_unknown':'unresolved'}
    tax={'profile':'MethodRequirements/3','method_id':'native.lot.tax','version':'3',
         'inputs':{k:deepcopy(lot[k]) for k in ['carrying','tax_base']},
         'requirements':[requirement('lot.tax_basis',binary('eq',ref('carrying'),ref('tax_base')),['carrying','tax_base'],'unsupported')],
         'required_known':[],'capabilities':[],'residual_prerequisites':['Lot amount domains remain separate.']}
    snap['constraints'].append({'id':'lots.tax','op':'each','collection':'lots','definition':tax,
        'bindings':{k:{'scope':'row','field':k} for k in ['carrying','tax_base']}})
    ins=deepcopy(globals)
    ins['book_total']=deepcopy(account['amount']);ins['lot_total']=deepcopy(lot['carrying'])
    zero={'op':'const','type':money,'value':'0/1'}
    reqs=[requirement('book.balance',binary('eq',ref('book_total'),zero),['book_total']),
          requirement('inventory.allocation',binary('eq',ref('inventory'),binary('add',ref('other_inventory'),ref('lot_total'))),
                      ['inventory','other_inventory','lot_total']),
          requirement('refund.signed',binary('eq',ref('refund_liability'),binary('sub',zero,ref('refund'))),['refund_liability','refund']),
          requirement('recovery.allocation',binary('eq',ref('recovery_asset'),ref('recovery')),['recovery_asset','recovery'])]
    assessment={'profile':'MethodRequirements/3','method_id':'native.book.selected_equalities','version':'3',
        'inputs':ins,'requirements':reqs,'required_known':[],'capabilities':[],
        'residual_prerequisites':['Equalities are necessary only; no full invariant or source authority.']}
    bindings={key:{'kind':'global','input':key} for key in keys}
    bindings.update(book_total={'kind':'sum','collection':'accounts','field':'amount'},
                    lot_total={'kind':'sum','collection':'lots','field':'carrying'})
    definition={'profile':totals.PROFILE,'method_id':'retained.shared_book','version':'1',
        'snapshot':snap,'assessment':assessment,'bindings':bindings,
        'residual_prerequisites':['Cash funding, amount domains, settled/disposed memory and transitions remain separate.']}
    selected={'inventory':state['balances'].get('inventory'),'other_inventory':state['other_inventory'],
              'refund_liability':state['balances'].get('refund_liability'),'refund':state['component']['refund'],
              'recovery_asset':state['balances'].get('recovery_asset'),'recovery':state['component']['recovery']}
    values={'globals':{k:known(v) for k,v in selected.items() if v is not None},'collections':{
        'accounts':{'status':'complete','rows':[{'id':known(k),'amount':known(v)} for k,v in state['balances'].items()]},
        'registry':{'status':'complete','rows':[{'id':known(k)} for k in native.ACCOUNTS]},
        'lots':{'status':'complete','rows':[{'id':known(k),'carrying':known(l['carrying']),'tax_base':known(l['tax_base'])}
                                         for k,l in state['lots'].items()]}}}
    return definition,values


def comparisons():
    saved=json.loads((HERE.parent/'company-return-execution-20261024/trace.json').read_text())
    states={r['id']:r['proposal']['after'] for r in saved['trace']}
    states['next_opening']=saved['next_opening']
    rows=[]
    def trial(name,state,expected_native='valid',expected_common='collection_total_requirements_satisfied',boundary=False):
        try:native.invariant(deepcopy(state));old={'status':'valid'}
        except native.Rejected as exc:old={'status':exc.status,'reason':exc.reason}
        d,v=project(state);result=totals.assess(d,v,[])
        rows.append({'case':name,'boundary_counterexample':boundary,'state':state,'definition':d,'values':v,
                     'native':old,'result':result,'expected_native':expected_native,'expected_common':expected_common,
                     'passed':old['status']==expected_native and result['status']==expected_common})
    for name,state in states.items():trial(name,deepcopy(state))
    opening=next(s for s in states.values() if Fraction(s['component']['refund'])>0)
    live=next(s for s in states.values() if any(not l['disposed'] for l in s['lots'].values()))
    def mutate(name,source,edit,native_status='invalid',common_status='invalid',boundary=False):
        s=deepcopy(source);edit(s);trial(name,s,native_status,common_status,boundary)
    mutate('book_imbalance',opening,lambda s:s['balances'].update(capital=fmt(Fraction(s['balances']['capital'])+1)))
    mutate('inventory_allocation',live,lambda s:s.update(other_inventory=fmt(Fraction(s['other_inventory'])+1)))
    mutate('refund_component',opening,lambda s:s['component'].update(refund=fmt(Fraction(s['component']['refund'])+1)))
    mutate('recovery_component',opening,lambda s:s['component'].update(recovery=fmt(Fraction(s['component']['recovery'])+1)))
    def tax(s):
        lot=next(iter(s['lots'].values()));lot['tax_base']=fmt(Fraction(lot['carrying'])+1)
    mutate('lot_tax_basis',live,tax,'unsupported','unsupported')
    mutate('missing_account',opening,lambda s:s['balances'].pop('capital'))
    mutate('extra_zero_account',opening,lambda s:s['balances'].update(unclassified='0/1'))
    def cash(s):
        # A deliberately balanced adverse fixture isolates the funding constraint.
        old=Fraction(s['balances']['cash']);s['balances']['cash']='-1/1'
        s['balances']['capital']=fmt(Fraction(s['balances']['capital'])+old+1)
    mutate('balanced_cash_shortfall',opening,cash,'funding_failure','collection_total_requirements_satisfied',True)
    mutate('disposed_stock_remains',live,lambda s:next(iter(s['lots'].values())).update(disposed=True),
           'invalid','collection_total_requirements_satisfied',True)
    return rows
