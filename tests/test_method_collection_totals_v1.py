"""Independent signed arithmetic and completeness obligations for totals."""
from copy import deepcopy
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import method_requirements_v1 as core
import method_collection_totals_v1 as totals
import method_collections_v1 as collections


def known(value):return {'status':'known','value':value}
def fixture():
    money={'kind':'rational','context':{'entity':'Example','book_role':'legal'},'dimensions':{'USD':1},'scale':'1/1'}
    amount={'type':money,'role':'state','source_ref':'constructed:money'}
    key={'type':{'kind':'text','context':{'entity':'Example'}},'role':'state','source_ref':'constructed:id'}
    snap={'profile':collections.PROFILE,'method_id':'sum.snapshot','version':'1','inputs':{'expected':deepcopy(amount)},
          'collections':{'rows':{'fields':{'id':key,'amount':deepcopy(amount)}}},
          'constraints':[{'id':'unique','op':'unique','collection':'rows','field':'id'}],
          'residual_prerequisites':['Full account coverage remains separate.']}
    req={'id':'total','guard':{'op':'const','type':core.BOOL,'value':True},'guard_requires':[],
         'predicate':{'op':'eq','left':{'op':'ref','id':'sum'},'right':{'op':'ref','id':'expected'}},
         'requires':['sum','expected'],'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'}
    assessment={'profile':'MethodRequirements/3','method_id':'sum.equality','version':'3',
        'inputs':{'sum':deepcopy(amount),'expected':deepcopy(amount)},'requirements':[req],
        'required_known':[],'capabilities':[],'residual_prerequisites':['No accounting authority follows.']}
    d={'profile':totals.PROFILE,'method_id':'totals.example','version':'1','snapshot':snap,'assessment':assessment,
       'bindings':{'sum':{'kind':'sum','collection':'rows','field':'amount'},'expected':{'kind':'global','input':'expected'}},
       'residual_prerequisites':['No journal execution.']}
    v={'globals':{'expected':known('3/2')},'collections':{'rows':{'status':'complete','rows':[
        {'id':known('a'),'amount':known('7/3')},{'id':known('b'),'amount':known('-5/6')}]}}}
    return d,v


def run(d,v):return totals.assess(d,v,[])


class TotalTests(unittest.TestCase):
    def test_exact_signed_sum_and_immutable_lineage(self):
        d,v=fixture();before=deepcopy((d,v));r=run(d,v)
        self.assertEqual(r['status'],'collection_total_requirements_satisfied')
        self.assertEqual(r['bound_values']['sum'],known('3/2'))
        self.assertEqual([c['row'] for c in r['lineage']['sum']['contributors']],[0,1])
        self.assertEqual(before,(d,v))
        for flag in ['executed','method_eligible','source_admission','accounting_admission']:self.assertFalse(r[flag])

    def test_empty_complete_zero_and_partial_empty_unknown(self):
        d,v=fixture();v['collections']['rows']['rows']=[];v['globals']['expected']=known('0/1')
        self.assertEqual(run(d,v)['bound_values']['sum'],known('0/1'))
        self.assertEqual(run(d,v)['status'],'collection_total_requirements_satisfied')
        v['collections']['rows'].update(status='partial',reason='unreported accounts')
        r=run(d,v);self.assertEqual(r['status'],'unresolved')
        self.assertEqual(r['bound_values']['sum']['status'],'unknown')
        self.assertEqual(r['lineage']['sum']['observed_subtotal'],'0/1')

    def test_unknown_cannot_be_canceled_or_replaced_by_subtotal(self):
        d,v=fixture();v['collections']['rows']['rows'][1]['amount']={'status':'unknown','reason':'unmeasured'}
        r=run(d,v);self.assertEqual(r['status'],'unresolved')
        self.assertEqual(r['lineage']['sum']['unresolved_inputs'],{'rows/1/amount':'unmeasured'})
        self.assertEqual(r['lineage']['sum']['observed_subtotal'],'7/3')
        v['globals']['expected']=known('7/3')
        self.assertEqual(run(d,v)['status'],'unresolved')
        del v['collections']['rows']['rows'][1]['amount']
        self.assertEqual(run(d,v)['lineage']['sum']['unresolved_inputs']['rows/1/amount'],'missing_row_field')

    def test_known_mismatch_and_duplicate_account_remain_invalid(self):
        d,v=fixture();v['globals']['expected']=known('2/1')
        self.assertEqual(run(d,v)['status'],'invalid')
        d,v=fixture();v['collections']['rows']['rows'][1]['id']=known('a')
        v['globals']['expected']={'status':'unknown','reason':'unknown total'}
        r=run(d,v);self.assertEqual(r['status'],'invalid')
        self.assertEqual(r['assessment']['status'],'unresolved')

    def test_dimensions_scale_context_and_role_are_exact(self):
        edits=[lambda d:d['assessment']['inputs']['sum']['type'].update(scale='1000/1'),
               lambda d:d['assessment']['inputs']['sum']['type'].update(dimensions={'EUR':1}),
               lambda d:d['assessment']['inputs']['sum']['type']['context'].update(book_role='consolidated'),
               lambda d:d['snapshot']['collections']['rows']['fields']['amount'].update(role='assumption'),
               lambda d:d['bindings']['sum'].update(field='id')]
        for edit in edits:
            d,v=fixture();edit(d);self.assertEqual(run(d,v)['status'],'invalid')

    def test_exact_mapping_and_missing_inputs(self):
        d,v=fixture();d['bindings'].pop('sum');self.assertEqual(run(d,v)['status'],'invalid')
        d,v=fixture();v['globals'].clear();self.assertEqual(run(d,v)['status'],'unresolved')
        d,v=fixture();v['collections'].clear();r=run(d,v)
        self.assertEqual(r['status'],'unresolved');self.assertEqual(r['lineage']['sum']['unresolved_inputs'],{'rows':'missing_collection'})

    def test_work_budget_counts_repeated_sum_visits(self):
        d,v=fixture();v['collections']['rows']['rows']=[{'id':known(str(i)),'amount':known('0/1')} for i in range(256)]
        v['globals']['expected']=known('0/1')
        req=d['assessment']['requirements'][0];amount=deepcopy(d['assessment']['inputs']['sum'])
        for i in range(31):
            name='sum'+str(i);d['assessment']['inputs'][name]=deepcopy(amount)
            d['assessment']['required_known'].append(name);d['bindings'][name]=deepcopy(d['bindings']['sum'])
        r=run(d,v);self.assertEqual(r['sum_visits'],8192);self.assertEqual(r['status'],'collection_total_requirements_satisfied')
        d['assessment']['inputs']['extra']=deepcopy(amount);d['assessment']['required_known'].append('extra')
        d['bindings']['extra']=deepcopy(d['bindings']['sum'])
        self.assertEqual(run(d,v)['reason'],'sum_work_limit')


if __name__=='__main__':unittest.main()
