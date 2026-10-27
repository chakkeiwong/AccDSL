"""Explicit selected-field projection; full native validation remains separate."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_collections_v1 as common
NATIVE=HERE.parent/'company-return-schema-20261023/return_schema.py'
spec=importlib.util.spec_from_file_location('collection_native_return_schema',NATIVE)
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


def known(value): return {'status':'known','value':value}
def ref(key): return {'op':'ref','id':key}
def binary(op,left,right): return {'op':op,'left':left,'right':right}


def project(body):
    """Author a new selected structural projection, never infer complete state."""
    h=core.digest(body)
    context={'entity':body['context']['entity'],'book_role':body['context']['book_role'],
             'case_id':body['context']['case_id']}
    def declaration(kind,pointer):
        return {'type':{'kind':kind,'context':deepcopy(context)},'role':'state',
                'source_ref':'derived-sha256:'+h+'#'+pointer}
    inputs={'component':declaration('text','/component/id'),
            'start':declaration('date','/period/start'),'end':declaration('date','/period/end_exclusive')}
    fields={
        'components':{'id':deepcopy(inputs['component'])},
        'lots':{k:declaration('date' if k=='acquired' else 'text','/lots/*/'+k)
                for k in ['id','component_id','acquired']},
        'events':{k:declaration('date' if k=='date' else 'text','/events/*/'+k)
                  for k in ['id','date','kind','component_id']}}
    d={'profile':common.PROFILE,'method_id':'retained.return.snapshot','version':'1',
       'inputs':inputs,'collections':{name:{'fields':f} for name,f in fields.items()},
       'constraints':[{'id':'lot.ids','op':'unique','collection':'lots','field':'id'},
                      {'id':'event.ids','op':'unique','collection':'events','field':'id'},
                      {'id':'event.order','op':'ordered','collection':'events','field':'date'},
                      {'id':'lot.component','op':'references','source':'lots','field':'component_id',
                       'target':'components','target_field':'id'}],
       'residual_prerequisites':['Ordered lot creation/disposal, settlement count and monetary effects remain separate.',
                                'Complete native record schema and source authority are not checked here.']}
    def each(name,collection,mapping,predicate,requires,guard=None,guard_requires=None):
        declared={key:deepcopy(inputs[field] if scope=='global' else fields[collection][field])
                  for key,(scope,field) in mapping.items()}
        template={'profile':'MethodRequirements/3','method_id':name,'version':'3','inputs':declared,
                  'requirements':[{'id':name,'guard':guard or {'op':'const','type':core.BOOL,'value':True},
                      'guard_requires':guard_requires or [],'predicate':predicate,'requires':requires,
                      'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'}],
                  'required_known':[],'capabilities':[],'residual_prerequisites':['Selected row condition only.']}
        d['constraints'].append({'id':name,'op':'each','collection':collection,'definition':template,
            'bindings':{key:{'scope':scope,'field':field} for key,(scope,field) in mapping.items()}})
    each('opening.acquired','lots',{'acquired':('row','acquired'),'start':('global','start')},
         binary('le',ref('acquired'),ref('start')),['acquired','start'])
    each('event.period','events',{'day':('row','date'),'start':('global','start'),'end':('global','end')},
         {'op':'all','args':[binary('le',ref('start'),ref('day')),binary('lt',ref('day'),ref('end'))]},
         ['day','start','end'])
    kind=fields['events']['kind']['type']
    each('settlement.component','events',{'kind':('row','kind'),'component':('row','component_id'),
                                        'expected':('global','component')},
         binary('eq',ref('component'),ref('expected')),['component','expected'],
         binary('eq',ref('kind'),{'op':'const','type':kind,'value':'settle'}),['kind'])
    values={'globals':{'component':known(body['component']['id']),'start':known(body['period']['start']),
                       'end':known(body['period']['end_exclusive'])},'collections':{}}
    selected={'components':[{'id':body['component']['id']}],'lots':body['lots'],'events':body['events']}
    for name,rows in selected.items():
        values['collections'][name]={'status':'complete','rows':[
            {key:known(row[key]) for key in fields[name] if key in row} for row in rows]}
    return d,values


def comparisons():
    base=json.loads((HERE.parent/'company-return-schema-20261023/fixture.json').read_text())
    opening={'id':'opening_lot','component_id':base['component']['id'],'units':'1/1',
             'carrying':'8/1','tax_base':'8/1','acquired':base['period']['start']}
    rows=[]
    def trial(name,edit,expected_native,expected_common,boundary=False):
        b=deepcopy(base);edit(b)
        try:
            native.validate(b);old={'status':'valid'}
        except Exception as exc:
            old={'status':'invalid','reason':str(exc).splitlines()[0][:180]}
        d,values=project(b);result=common.assess(d,values,[])
        rows.append({'case':name,'boundary_counterexample':boundary,'body':b,'definition':d,'values':values,
                     'native':old,'result':result,'expected_native':expected_native,
                     'expected_common':expected_common,
                     'passed':old['status']==expected_native and result['status']==expected_common})
    ok='collection_requirements_satisfied'
    trial('baseline',lambda b:None,'valid',ok)
    trial('opening_lot',lambda b:b['lots'].append(deepcopy(opening)),'valid',ok)
    trial('duplicate_lot',lambda b:b['lots'].extend([deepcopy(opening),deepcopy(opening)]),'invalid','invalid')
    trial('lot_component',lambda b:b['lots'].append({**opening,'component_id':'absent'}),'invalid','invalid')
    trial('late_acquisition',lambda b:b['lots'].append({**opening,'acquired':'2025-01-02'}),'invalid','invalid')
    trial('duplicate_event',lambda b:b['events'][1].update(id=b['events'][0]['id']),'invalid','invalid')
    trial('reversed_dates',lambda b:b['events'].reverse(),'invalid','invalid')
    trial('before_period',lambda b:b['events'][0].update(date='2024-12-31'),'invalid','invalid')
    trial('end_excluded',lambda b:b['events'][1].update(date=b['period']['end_exclusive']),'invalid','invalid')
    trial('settlement_component',lambda b:b['events'][0].update(component_id='absent'),'invalid','invalid')
    trial('equal_dates',lambda b:b['events'][1].update(date=b['events'][0]['date']),'valid',ok)
    def reverse_equal(b):
        b['events'][1]['date']=b['events'][0]['date'];b['events'].reverse()
    trial('equal_date_sale_before_creation',reverse_equal,'invalid',ok,True)
    trial('missing_sale_lot',lambda b:b['events'][1].update(lot_id='absent'),'invalid',ok,True)
    trial('whole_lot_sold_twice',lambda b:b['events'].append({**b['events'][1],'id':'second_sale'}),'invalid',ok,True)
    def twice(b):
        b['events'].insert(1,{**b['events'][0],'id':'second_settlement','lot_id':'another_lot'})
    trial('two_complete_settlements',twice,'invalid',ok,True)
    return rows
