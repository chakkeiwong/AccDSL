"""Independent closed-schema and atomic-update behavior."""
from copy import deepcopy
from pathlib import Path
import sys, unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import method_memory_effects_v1 as memory
core=memory.core
TEXT={'type':'string','minLength':1,'maxLength':4096}
RATIONAL={'type':'string','x-exact-kind':'rational'}


def record(fields):
    return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}


def literal(value):
    return {'kind':'literal','value':value}


def read(source,pointer):
    return {'kind':'read','source':source,'pointer':pointer}


def operation(name,kind,path,value):
    return {'id':name,'op':kind,'path':path,'value':value}


def fixture():
    state=record({'left':RATIONAL,'right':RATIONAL,
                  'rows':{'type':'object','propertyNames':TEXT,'additionalProperties':record({'amount':RATIONAL})},
                  'seen':{'type':'array','items':TEXT}})
    input_shape=record({'amount':RATIONAL,'id':TEXT})
    h,k=core.digest(state),core.digest(input_shape)
    definition={'profile':memory.PROFILE,'state_schema':h,'input_schema':k,'operations':[
        operation('change','replace',['left'],read('inputs','/amount')),
        operation('read_old','replace',['right'],read('before','/left')),
        operation('new_row','insert',['rows',{'input_pointer':'/id'}],
                  {'kind':'object','fields':{'amount':read('inputs','/amount')}}),
        operation('seen','append',['seen'],read('inputs','/id'))]}
    return definition,{h:state,k:input_shape},{'left':'1/1','right':'2/1','rows':{},'seen':[]},{'amount':'3/1','id':'new'}


def run(definition,schemas,before,inputs):
    h=core.digest(definition)
    return memory.stage({h:definition},h,schemas,before,inputs)


class MemoryEffectsTests(unittest.TestCase):
    def test_atomic_success_and_original_read_semantics(self):
        args=fixture();old=deepcopy(args)
        result=run(*args)
        self.assertEqual(result['status'],'staged',result)
        self.assertEqual(result['after'],{'left':'3/1','right':'1/1','rows':{'new':{'amount':'3/1'}},'seen':['new']})
        self.assertEqual(args,old)
        for key in memory.BOUNDARY:
            if key!='scope':self.assertFalse(result[key])
        result['after']['rows']['new']['amount']='9/1'
        self.assertEqual(args,old)

    def test_late_failure_returns_no_partial_state(self):
        definition,schemas,before,inputs=fixture()
        definition['operations'].append(operation('bad','replace',['absent'],literal('4/1')))
        old=deepcopy((before,inputs));result=run(definition,schemas,before,inputs)
        self.assertEqual(result['status'],'invalid');self.assertNotIn('after',result)
        self.assertEqual((before,inputs),old)

    def test_failed_output_schema_is_atomic(self):
        definition,schemas,before,inputs=fixture()
        definition['operations'][-1]['value']=literal(False)
        old=deepcopy(before);result=run(definition,schemas,before,inputs)
        self.assertEqual(result['status'],'invalid');self.assertNotIn('after',result)
        self.assertEqual(before,old)

    def test_insert_collision_and_replace_absence(self):
        for collide in [True,False]:
            args=list(fixture())
            if collide:args[2]['rows']['new']={'amount':'8/1'}
            else:args[0]['operations'][0]['path']=['absent']
            result=run(*args)
            self.assertEqual(result['reason'],'insert_target_exists' if collide else 'replace_target_absent')

    def test_overlap_conflicts_and_repeated_appends(self):
        for path in [['left'],['rows'],['rows',{'input_pointer':'/id'},'amount']]:
            definition,schemas,before,inputs=fixture()
            definition['operations'].append(operation('conflict','replace',path,literal('7/1')))
            self.assertEqual(run(definition,schemas,before,inputs)['reason'],'conflicting_memory_paths')
        definition,schemas,before,inputs=fixture()
        definition['operations'].append(operation('again','append',['seen'],literal('second')))
        self.assertEqual(run(definition,schemas,before,inputs)['after']['seen'],['new','second'])

    def test_dynamic_keys_do_not_escape_map(self):
        definition,schemas,before,inputs=fixture();inputs['id']='a/b~c'
        result=run(definition,schemas,before,inputs)
        self.assertEqual(result['status'],'staged',result)
        self.assertEqual(list(result['after']['rows']),['a/b~c'])
        self.assertEqual(result['operations'][2]['resolved_path'],['rows','a/b~c'])

    def test_strict_reads_missing_paths_and_arrays(self):
        for pointer in ['/missing','/left/child','/seen/00','/seen/-','/bad~2']:
            definition,schemas,before,inputs=fixture()
            definition['operations'][0]['value']=read('before',pointer)
            self.assertEqual(run(definition,schemas,before,inputs)['status'],'invalid')
        definition,schemas,before,inputs=fixture();before['seen']=['old']
        definition['operations'][-1]['value']=read('before','/seen/0')
        self.assertEqual(run(definition,schemas,before,inputs)['after']['seen'],['old','old'])

    def test_no_root_or_array_index_writes(self):
        for path in [[],['seen','0']]:
            definition,schemas,before,inputs=fixture();before['seen']=['old']
            definition['operations']=[operation('bad','replace',path,literal('new'))]
            self.assertEqual(run(definition,schemas,before,inputs)['status'],'invalid')

    def test_schema_and_definition_identities(self):
        definition,schemas,before,inputs=fixture();h=core.digest(definition)
        self.assertEqual(memory.stage({},h,schemas,before,inputs)['status'],'unsupported')
        self.assertEqual(memory.stage({'0'*64:definition},'0'*64,schemas,before,inputs)['status'],'invalid')
        schemas[definition['state_schema']]['required'].pop()
        self.assertEqual(run(definition,schemas,before,inputs)['status'],'invalid')

    def test_remote_schema_and_open_or_unknown_keywords_rejected(self):
        for bad in [{'$ref':'https://example.invalid/schema'}, {'type':'object','additionalProperties':True},
                    {'type':'string','pattern':'(a+)+$'}, {'type':'string','x-arbitrary':True},
                    {'type':'number'}, {'type':'boolean','const':1}, {'type':'string','format':'uri'}]:
            with self.subTest(schema=bad):
                with self.assertRaises((ValueError,TypeError)):
                    memory.check_schema(bad)

    def test_input_schema_and_exact_scalar_validation(self):
        for value in ['2/2','1.0',True,1,None]:
            definition,schemas,before,inputs=fixture();inputs['amount']=value
            self.assertEqual(run(definition,schemas,before,inputs)['status'],'invalid')
        definition,schemas,before,inputs=fixture();before['extra']='unexpected'
        self.assertEqual(run(definition,schemas,before,inputs)['status'],'invalid')

    def test_closed_operations_and_templates(self):
        edits=[lambda d:d.update(callback='x'),lambda d:d['operations'][0].update(op='delete'),
               lambda d:d['operations'][0].update(id='new_row'),
               lambda d:d['operations'][0]['value'].update(source='staged'),
               lambda d:d['operations'][0].update(value={'kind':'call','function':'x'}),
               lambda d:d['operations'][0].update(path=[{'input_pointer':'/id','extra':'x'}])]
        for edit in edits:
            definition,schemas,before,inputs=fixture();edit(definition)
            self.assertEqual(run(definition,schemas,before,inputs)['status'],'invalid')

    def test_bounds_and_whole_native_schema(self):
        definition,schemas,before,inputs=fixture();definition['operations']*=65
        self.assertEqual(run(definition,schemas,before,inputs)['reason'],'operation_limit')
        definition,schemas,before,inputs=fixture();inputs['id']='x'*1_000_001
        self.assertEqual(run(definition,schemas,before,inputs)['reason'],'record_size_limit')
        import native_return_state_structure_v1 as structure
        memory.check_schema(structure.schema())

    def test_recomputed_retained_memory(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('typed_memory_comparisons',ROOT/'data/accounting-master/typed-memory-effects-20261024/examples.py')
        example=importlib.util.module_from_spec(spec);spec.loader.exec_module(example)
        rows=example.comparisons()
        self.assertEqual(len(rows),10)
        self.assertEqual(sum(row['staged'] for row in rows),9)
        for row in rows:self.assertTrue(row['passed'],row['case'])


if __name__=='__main__':unittest.main()
