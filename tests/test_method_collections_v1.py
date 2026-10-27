"""Independent expectations for finite collections and guarded row checks."""
from copy import deepcopy
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import method_requirements_v1 as core
import method_collections_v1 as collections


def known(value): return {'status':'known','value':value}
def unknown(reason='not supplied'): return {'status':'unknown','reason':reason}
def declaration(kind='text'):
    return {'type':{'kind':kind,'context':{'entity':'Example'}},'role':'state','source_ref':'constructed:field'}
def fixture():
    d={'profile':collections.PROFILE,'method_id':'independent.collections','version':'1','inputs':{},
       'collections':{'rows':{'fields':{'id':declaration(),'date':declaration('date')}},
                      'targets':{'fields':{'id':declaration()}}},
       'constraints':[{'id':'unique','op':'unique','collection':'rows','field':'id'},
                      {'id':'dates','op':'ordered','collection':'rows','field':'date'},
                      {'id':'refs','op':'references','source':'rows','field':'id',
                       'target':'targets','target_field':'id'}],
       'residual_prerequisites':['Ordered lifecycle and accounting effects remain separate.']}
    v={'globals':{},'collections':{
        'rows':{'status':'complete','rows':[{'id':known('a'),'date':known('2025-01-01')},
                                          {'id':known('b'),'date':known('2025-02-01')}]},
        'targets':{'status':'complete','rows':[{'id':known('a')},{'id':known('b')}]}}}
    return d,v


def each_fixture():
    boolean={'type':deepcopy(core.BOOL),'role':'state','source_ref':'constructed:boolean'}
    template={'profile':'MethodRequirements/3','method_id':'row.guard','version':'3',
        'inputs':{'active':deepcopy(boolean),'body':deepcopy(boolean)},
        'requirements':[{'id':'row','guard':{'op':'ref','id':'active'},'guard_requires':['active'],
            'predicate':{'op':'ref','id':'body'},'requires':['body'],'admission_refs':[],
            'on_false':'invalid','on_unknown':'unresolved'}],
        'required_known':[],'capabilities':[],'residual_prerequisites':['Method effects remain separate.']}
    d={'profile':collections.PROFILE,'method_id':'each.guarded','version':'1','inputs':{'active':boolean},
       'collections':{'rows':{'fields':{'body':deepcopy(boolean)}}},
       'constraints':[{'id':'each','op':'each','collection':'rows','definition':template,
          'bindings':{'active':{'scope':'global','field':'active'},'body':{'scope':'row','field':'body'}}}],
       'residual_prerequisites':['No execution follows.']}
    v={'globals':{'active':known(True)},'collections':{'rows':{'status':'complete','rows':[{'body':known(True)}]}}}
    return d,v


def run(d,v): return collections.assess(d,v,[])


class CollectionTests(unittest.TestCase):
    def test_complete_and_immutable(self):
        d,v=fixture();before=deepcopy((d,v));result=run(d,v)
        self.assertEqual(result['status'],'collection_requirements_satisfied')
        self.assertEqual(result['definition_sha256'],core.digest(d))
        self.assertEqual(result['values_sha256'],core.digest(v))
        self.assertEqual(before,(d,v))
        for key in ['executed','method_eligible','source_admission','accounting_admission']:
            self.assertFalse(result[key])

    def test_duplicate_survives_unknown_and_partial_coverage(self):
        d,v=fixture()
        v['collections']['rows']['rows'][1]['id']=known('a')
        v['collections']['rows']['rows'].append({'id':unknown(),'date':unknown()})
        v['collections']['rows'].update(status='partial',reason='remaining records unavailable')
        result=run(d,v)
        self.assertEqual(result['status'],'invalid')
        self.assertEqual(result['findings'][0]['details'][0]['rows'],[0,1])
        self.assertIn('rows/2/id',result['findings'][0]['unresolved_inputs'])

    def test_complete_empty_differs_from_missing_or_partial(self):
        d,v=fixture()
        v['collections']['rows']['rows']=[]
        v['collections'].pop('targets')
        self.assertEqual(run(d,v)['status'],'collection_requirements_satisfied')
        v['collections']['rows'].update(status='partial',reason='incomplete coverage')
        self.assertEqual(run(d,v)['status'],'unresolved')
        v['collections'].pop('rows')
        self.assertEqual(run(d,v)['status'],'unresolved')

    def test_known_subsequence_order_detects_reversal(self):
        d,v=fixture();rows=v['collections']['rows']['rows']
        rows[0]['date']=known('2025-03-01')
        rows.insert(1,{'id':known('c'),'date':unknown()})
        result=run(d,v)
        self.assertEqual(result['findings'][1]['consequence'],'invalid')
        self.assertEqual(result['findings'][1]['details'][0]['rows'],[0,2])
        rows[0]['date']=known('2025-01-01')
        self.assertEqual(run(d,v)['findings'][1]['consequence'],'unresolved')
        rows[1]['date']=known('2025-01-01')
        self.assertEqual(run(d,v)['findings'][1]['consequence'],'satisfied')

    def test_reference_requires_exactly_one_known_complete_match(self):
        d,v=fixture();target=v['collections']['targets']
        target['rows'].pop()
        self.assertEqual(run(d,v)['findings'][2]['consequence'],'invalid')
        target.update(status='partial',reason='more targets possible')
        self.assertEqual(run(d,v)['findings'][2]['consequence'],'unresolved')
        target['rows'].append({'id':known('a')})
        self.assertEqual(run(d,v)['findings'][2]['consequence'],'invalid')
        d,v=fixture();v['collections']['targets']['rows'].append({'id':unknown()})
        self.assertEqual(run(d,v)['findings'][2]['consequence'],'unresolved')

    def test_type_context_and_structural_refusals(self):
        for edit in [lambda d:d['collections']['targets']['fields']['id']['type']['context'].update(entity='Other'),
                     lambda d:d['constraints'][1].update(field='id'),
                     lambda d:d['constraints'][0].update(op='callback'),
                     lambda d:d['constraints'].append(deepcopy(d['constraints'][0]))]:
            d,v=fixture();edit(d);self.assertEqual(run(d,v)['status'],'invalid')
        for edit in [lambda v:v['collections']['rows'].pop('status'),
                     lambda v:v['collections']['rows'].update(status='partial'),
                     lambda v:v['collections']['rows']['rows'][0].update(extra=known('x')),
                     lambda v:v['collections']['rows']['rows'][0].update(date=known('2025-02-30')),
                     lambda v:v['collections'].update(extra={'status':'complete','rows':[]})]:
            d,v=fixture();edit(v);self.assertEqual(run(d,v)['status'],'invalid')

    def test_guarded_rows_preserve_inactive_and_required_known(self):
        d,v=each_fixture();v['globals']['active']=known(False)
        v['collections']['rows']['rows'][0]['body']=unknown('body not observed')
        result=run(d,v)
        self.assertEqual(result['status'],'collection_requirements_satisfied')
        row=result['findings'][0]['details'][0]
        self.assertEqual(row['assessment']['status'],'no_active_requirements')
        self.assertEqual(row['bindings']['body'],{'scope':'row','field':'body','collection':'rows','row':0})
        d['constraints'][0]['definition']['required_known']=['body']
        self.assertEqual(run(d,v)['status'],'unresolved')

    def test_invalid_row_survives_unknown_membership(self):
        d,v=each_fixture();v['collections']['rows'].update(status='partial',reason='incomplete')
        v['collections']['rows']['rows']=[{'body':known(False)},{'body':unknown()}]
        result=run(d,v)
        self.assertEqual(result['status'],'invalid')
        self.assertEqual(len(result['findings'][0]['details']),2)

    def test_each_validates_empty_templates_and_complete_mapping(self):
        d,v=each_fixture();v['collections']['rows']['rows']=[]
        self.assertEqual(run(d,v)['status'],'collection_requirements_satisfied')
        d['constraints'][0]['definition']['requirements'][0]['predicate']={'op':'call','name':'arbitrary'}
        self.assertEqual(run(d,v)['status'],'invalid')
        d,v=each_fixture();d['constraints'][0]['bindings'].pop('body')
        self.assertEqual(run(d,v)['status'],'invalid')
        d,v=each_fixture();d['collections']['rows']['fields']['body']['role']='assumption'
        self.assertEqual(run(d,v)['status'],'invalid')

    def test_explicit_row_constraint_and_expansion_limits(self):
        d,v=fixture();d['constraints']=d['constraints'][:1]
        v['collections']['targets']['rows']=[]
        v['collections']['rows']['rows']=[{'id':known(str(i))} for i in range(collections.MAX_ROWS)]
        self.assertEqual(run(d,v)['status'],'collection_requirements_satisfied')
        v['collections']['rows']['rows'].append({'id':known('extra')})
        self.assertEqual(run(d,v)['reason'],'row_limit')
        d,v=each_fixture()
        base=deepcopy(d['constraints'][0]);d['constraints']=[]
        for i in range(collections.MAX_CONSTRAINTS):
            item=deepcopy(base);item['id']=str(i);d['constraints'].append(item)
        v['collections']['rows']['rows']=[]
        self.assertEqual(run(d,v)['status'],'collection_requirements_satisfied')
        d['constraints'].append({**deepcopy(base),'id':'extra'})
        self.assertEqual(run(d,v)['reason'],'constraint_limit')
        d['constraints'].pop();v['collections']['rows']['rows']=[{'body':known(True)}]*collections.MAX_ROWS
        self.assertEqual(run(d,v)['reason'],'expanded_work_limit')


if __name__=='__main__': unittest.main()
