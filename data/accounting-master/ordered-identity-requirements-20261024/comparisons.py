"""Apply explicit lifecycle declarations to the frozen snapshot counterexamples."""
from copy import deepcopy
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_identity_lifecycle_v1 as identity
import method_requirements_v1 as core
NATIVE=HERE.parent/'company-return-schema-20261023/return_schema.py'
spec=importlib.util.spec_from_file_location('identity_native_return_schema',NATIVE)
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


def build(row):
    body=row['body'];snapshot=deepcopy(row['definition']);values=deepcopy(row['values'])
    core.need(body['component']['settled'] is False,'retained adapter requires explicit unsettled opening')
    lot_type=deepcopy(snapshot['collections']['lots']['fields']['id'])
    component_type=deepcopy(snapshot['collections']['components']['fields']['id'])
    lot_type['source_ref']='derived-sha256:'+core.digest(body)+'#/events/*/lot_id'
    snapshot['collections']['events']['fields']['lot_id']=lot_type
    for event,value in zip(body['events'],values['collections']['events']['rows']):
        value['lot_id']={'status':'known','value':event['lot_id']}
    for name,declaration in [('retired_lots',lot_type),('retired_components',component_type)]:
        snapshot['collections'][name]={'fields':{'id':deepcopy(declaration)}}
        values['collections'][name]={'status':'complete','rows':[]}
    def op(name,pool,key):return {'op':name,'pool':pool,'key':{'scope':'row','field':key}}
    definition={'profile':identity.PROFILE,'method_id':'retained.return.identity_sequence','version':'1',
        'snapshot':snapshot,'events':'events','action_field':'kind',
        'pools':{'lots':{'live':{'collection':'lots','field':'id'},
                         'retired':{'collection':'retired_lots','field':'id'}},
                 'components':{'live':{'collection':'components','field':'id'},
                               'retired':{'collection':'retired_components','field':'id'}}},
        'actions':[{'tag':'settle','operations':[op('consume','components','component_id'),op('create','lots','lot_id')]},
                   {'tag':'sell','operations':[op('consume','lots','lot_id')]}],
        'residual_prerequisites':['Monetary invariants, source authority, journal effects and reporting remain separate.',
            'Explicit empty retired pools belong to this retained synthetic opening only.']}
    return definition,values


def comparisons():
    prior=json.loads((HERE.parent/'collection-reference-requirements-20261024/cases.json').read_text())
    rows=[]
    for old in prior:
        try:native.validate(old['body']);native_status='valid'
        except Exception:native_status='invalid'
        d,v=build(old);result=identity.assess(d,v,[])
        expected='identity_requirements_satisfied' if native_status=='valid' else 'invalid'
        repaired=(not old['boundary_counterexample'] or
                  result.get('reason')=='identity_not_live' and bool(result.get('details',{}).get('pool')))
        rows.append({'case':old['case'],'prior_snapshot_status':old['result']['status'],
                     'was_counterexample':old['boundary_counterexample'],'native_status':native_status,
                     'definition':d,'values':v,'result':result,'expected':expected,
                     'passed':result['status']==expected and native_status==old['native']['status'] and repaired})
    return rows
