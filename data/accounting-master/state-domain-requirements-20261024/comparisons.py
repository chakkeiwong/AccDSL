"""Selected native state domains, preserving complete original findings."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_state_assessment_v1 as state_check
import method_requirements_v1 as core
spec=importlib.util.spec_from_file_location('state_prior_total_comparisons',HERE.parent/'shared-book-requirements-20261024/comparisons.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
native=prior.native
known=prior.known;ref=prior.ref;binary=prior.binary;fmt=prior.fmt


def project(state):
    total,values=prior.project(state);snap=total['snapshot'];assessment=total['assessment']
    h=core.digest(state)
    money=deepcopy(assessment['inputs']['inventory']['type'])
    text={'kind':'text','context':deepcopy(money['context'])}
    units={**deepcopy(money),'dimensions':{'goods:return_unit':1}}
    def declaration(t,path):return {'type':deepcopy(t),'role':'state','source_ref':'derived-sha256:'+h+'#'+path}
    def constant(value,t):return {'op':'const','type':deepcopy(t),'value':value}
    def requirement(name,predicate,deps,guard=None,gdeps=None):
        return {'id':name,'guard':guard or constant(True,core.BOOL),'guard_requires':gdeps or [],
                'predicate':predicate,'requires':deps,'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'}
    added={'cash':(money,state['balances']['cash']),
           'settled':(core.BOOL,state['component']['settled']),
           'component':(text,state['component']['id'])}
    for key,(t,value) in added.items():
        snap['inputs'][key]=declaration(t,'/selected/'+key)
        values['globals'][key]=({'status':'unknown','reason':'explicit_native_unknown'} if value=='unknown' else known(value))
        if key!='component':
            assessment['inputs'][key]=deepcopy(snap['inputs'][key]);total['bindings'][key]={'kind':'global','input':key}
    zero=constant('0/1',money)
    assessment['requirements'].extend([
        requirement('cash.nonnegative',binary('le',zero,ref('cash')),['cash']),
        requirement('other_inventory.nonnegative',binary('le',zero,ref('other_inventory')),['other_inventory']),
        requirement('settled.rights',{'op':'all','args':[binary('eq',ref('refund'),zero),binary('eq',ref('recovery'),zero)]},
                    ['refund','recovery'],ref('settled'),['settled'])])
    assessment['required_known'].append('settled')
    fields=snap['collections']['lots']['fields']
    for key,t in [('stored_id',text),('component_id',text),('units',units),('disposed',core.BOOL)]:
        fields[key]=declaration(t,'/lots/*/'+key)
    for (key,lot),row in zip(state['lots'].items(),values['collections']['lots']['rows']):
        for name,value in [('stored_id',lot['id']),('component_id',lot['component_id']),
                           ('units',lot['units']),('disposed',lot['disposed'])]:
            row[name]=({'status':'unknown','reason':'explicit_native_unknown'} if value=='unknown' else known(value))
    declared={k:deepcopy(v) for k,v in fields.items()}
    declared['component']=deepcopy(snap['inputs']['component'])
    uzero=constant('0/1',units)
    row_rules=[
        requirement('lot.identity',{'op':'all','args':[binary('eq',ref('id'),ref('stored_id')),
                    binary('eq',ref('component_id'),ref('component'))]},['id','stored_id','component_id','component']),
        requirement('lot.amounts',{'op':'all','args':[binary('le',uzero,ref('units')),binary('le',zero,ref('carrying'))]},['units','carrying']),
        requirement('lot.disposed',{'op':'all','args':[binary('eq',ref('units'),uzero),binary('eq',ref('carrying'),zero),
                    binary('eq',ref('tax_base'),zero)]},['units','carrying','tax_base'],ref('disposed'),['disposed']),
        requirement('lot.live',binary('lt',uzero,ref('units')),['units'],{'op':'not','arg':ref('disposed')},['disposed'])]
    template={'profile':'MethodRequirements/3','method_id':'native.lot.domains','version':'3','inputs':declared,
              'requirements':row_rules,'required_known':['disposed'],'capabilities':[],
              'residual_prerequisites':['Full record structure and source meaning remain separate.']}
    mapping={k:{'scope':'row','field':k} for k in fields};mapping['component']={'scope':'global','field':'component'}
    snap['constraints'].append({'id':'lots.domains','op':'each','collection':'lots','definition':template,'bindings':mapping})
    for name,rows in [('seen',[{'id':known(key)} for key in state['seen']]),
                      ('tax_ids',[{'id':known(row['event_id'])} for row in state['tax_adjustments']])]:
        snap['collections'][name]={'fields':{'id':declaration(text,'/'+name+'/*')}}
        values['collections'][name]={'status':'complete','rows':rows}
        snap['constraints'].append({'id':name+'.unique','op':'unique','collection':name,'field':'id'})
    snap['constraints'].append({'id':'tax.seen','op':'references','source':'tax_ids','field':'id','target':'seen','target_field':'id'})
    definition={'profile':state_check.PROFILE,'method_id':'retained.state.domains','version':'1','totals':total,
                'false_categories':{'cash.nonnegative':'funding_failure'},
                'residual_prerequisites':['Full outer/nested record shape, source authority, typed effects and replay remain separate.']}
    return definition,values


def comparisons():
    old=json.loads((HERE.parent/'shared-book-requirements-20261024/cases.json').read_text())
    rows=[]
    def trial(name,state,expected_native,expected_common,difference=None):
        try:native.invariant(deepcopy(state));n={'status':'valid'}
        except native.Rejected as exc:n={'status':exc.status,'reason':exc.reason}
        d,v=project(state);r=state_check.assess(d,v,[])
        rows.append({'case':name,'native':n,'definition':d,'values':v,'state':state,'result':r,
                     'expected_native':expected_native,'expected_common':expected_common,
                     'intentional_difference':difference,'passed':n['status']==expected_native and r['status']==expected_common})
    for item in old:
        expected='state_requirements_satisfied' if item['native']['status']=='valid' else item['native']['status']
        trial(item['case'],item['state'],item['native']['status'],expected)
    source=next(r['state'] for r in old if any(not lot['disposed'] for lot in r['state']['lots'].values()))
    unsettled=next(r['state'] for r in old if not r['state']['component']['settled'])
    def mutate(name,base,edit,n='invalid',c=None,difference=None):
        s=deepcopy(base);edit(s);trial(name,s,n,c or n,difference)
    mutate('lot_stored_identity',source,lambda s:next(iter(s['lots'].values())).update(id='wrong'))
    mutate('lot_component_identity',source,lambda s:next(iter(s['lots'].values())).update(component_id='wrong'))
    mutate('negative_units',source,lambda s:next(iter(s['lots'].values())).update(units='-1/1'))
    mutate('empty_live_lot',source,lambda s:next(iter(s['lots'].values())).update(units='0/1'))
    mutate('settled_outstanding_rights',unsettled,lambda s:s['component'].update(settled=True))
    mutate('unknown_settlement',unsettled,lambda s:s['component'].update(settled='unknown'),'unresolved')
    mutate('unknown_disposition',source,lambda s:next(iter(s['lots'].values())).update(disposed='unknown'),
           'invalid','unresolved','Explicit unknown extension; native requires concrete Boolean disposition.')
    mutate('duplicate_seen',source,lambda s:s['seen'].append(s['seen'][0]))
    mutate('duplicate_adjustment',source,lambda s:s['tax_adjustments'].append(deepcopy(s['tax_adjustments'][0])))
    mutate('adjustment_unseen',source,lambda s:s['tax_adjustments'][0].update(event_id='unseen'))
    def negative_other(s):
        delta=-1-Fraction(s['other_inventory']);s['other_inventory']='-1/1'
        s['balances']['inventory']=fmt(Fraction(s['balances']['inventory'])+delta)
        s['balances']['capital']=fmt(Fraction(s['balances']['capital'])-delta)
    mutate('negative_other_inventory',source,negative_other)
    def negative_carrying(s):
        lot=next(iter(s['lots'].values()));delta=-1-Fraction(lot['carrying'])
        lot.update(carrying='-1/1',tax_base='-1/1')
        s['balances']['inventory']=fmt(Fraction(s['balances']['inventory'])+delta)
        s['balances']['capital']=fmt(Fraction(s['balances']['capital'])-delta)
    mutate('negative_lot_carrying',source,negative_carrying)
    mixed=deepcopy(next(r['state'] for r in old if r['case']=='balanced_cash_shortfall'))
    mixed['seen'].append(mixed['seen'][0])
    trial('funding_and_duplicate_seen',mixed,'funding_failure','invalid',
          'Native first-failure is funding; complete summary is invalid and retains the funding finding.')
    return rows
