"""Complete shape checks precede selected state projections."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import native_return_state_structure_v1 as structure
core=structure.core
SAVED=ROOT/'data/accounting-master/company-return-execution-20261024/trace.json'


def states():
    data=json.loads(SAVED.read_text())
    return {**{row['id']:row['proposal']['after'] for row in data['trace']},'next_opening':data['next_opening']}


def inspect(value):
    raw=core.canonical(value)
    return structure.inspect(raw,sha256(raw).hexdigest(),core.digest(structure.schema()))


def fixed_objects():
    """Find an actual saved representative for every fixed schema-object path."""
    found={}
    def walk(value,shape,path=(),pattern=()):
        if type(value) is dict:
            if 'properties' in shape:found.setdefault(pattern,(path,deepcopy(value),shape))
            for key,item in value.items():
                if key in shape.get('properties',{}):
                    rule=shape['properties'][key];next_pattern=pattern+(key,)
                else:rule=shape['additionalProperties'];next_pattern=pattern+('*',)
                walk(item,rule,path+(key,),next_pattern)
        elif type(value) is list:
            for i,item in enumerate(value):walk(item,shape['items'],path+(i,),pattern+('*',))
    for name,state in states().items():
        before=set(found);walk(state,structure.schema())
        for key in set(found)-before:
            path,item,shape=found[key];found[key]=(name,path,item,shape)
    return found


class NativeStructureTests(unittest.TestCase):
    def test_all_saved_states_roundtrip_without_admission(self):
        for name,value in states().items():
            with self.subTest(name=name):
                before=deepcopy(value);result=inspect(value)
                self.assertEqual(result['status'],'structure_valid',result)
                self.assertEqual(result['value'],value);self.assertEqual(value,before)
                for flag in ['executed','method_eligible','source_admission','accounting_admission']:
                    self.assertFalse(result[flag])

    def test_missing_and_extra_fields_at_every_fixed_object(self):
        found=fixed_objects();saved=states()
        self.assertGreaterEqual(len(found),12)
        for pattern,(name,path,item,shape) in found.items():
            for key in shape['required']:
                value=deepcopy(saved[name]);node=value
                for token in path:node=node[token]
                node.pop(key)
                with self.subTest(path=pattern,missing=key):self.assertEqual(inspect(value)['status'],'invalid')
            value=deepcopy(saved[name]);node=value
            for token in path:node=node[token]
            node['unexpected_field']='extra'
            with self.subTest(path=pattern,extra=True):self.assertEqual(inspect(value)['status'],'invalid')

    def test_hashes_and_strict_raw_decoding(self):
        value=next(iter(states().values()));raw=core.canonical(value);h=sha256(raw).hexdigest();schema=core.digest(structure.schema())
        self.assertEqual(structure.inspect(raw,h,'0'*64)['reason'],'schema_digest_mismatch')
        self.assertEqual(structure.inspect(raw+b' ',h,schema)['reason'],'raw_digest_mismatch')
        for malformed in [b'{"x":1,"x":2}',b'{"x":1.0}',b'{"x":NaN}',b'\xff',b'[] []']:
            self.assertEqual(structure.inspect(malformed,sha256(malformed).hexdigest(),schema)['status'],'invalid')

    def test_exact_scalars_dates_booleans_and_pointers(self):
        saved=states();base=next(v for v in saved.values() if v['lots'])
        edits=[lambda s:s['balances'].update(cash='2/2'),lambda s:s['balances'].update(cash=True),
               lambda s:s['balances'].update(cash=1.5),lambda s:s.update(date='2025-02-30'),
               lambda s:s['component'].update(settled=1),lambda s:s.update(conditional=1),
               lambda s:next(iter(s['lots'].values())).update(disposed='unknown'),
               lambda s:s['source'].update(packet_sha256='not-a-hash'),
               lambda s:s['component'].update(source_pointer='/record_registry/absent/body'),
               lambda s:s['component'].update(source_pointer=s['component']['source_pointer']+'/bad~2'),
               lambda s:s['context'].update(entity='two\nlines')]
        for edit in edits:
            value=deepcopy(base);edit(value);self.assertEqual(inspect(value)['status'],'invalid')

    def test_declared_legacy_unknowns_and_concrete_runtime_memory(self):
        base=next(iter(states().values()))
        for key in ['sold_units','expected_units','unit_refund','unit_cost','estimated_handling','estimated_deterioration']:
            value=deepcopy(base);value['component'][key]='unknown'
            self.assertEqual(inspect(value)['status'],'structure_valid')
        for key in ['rate','refund_tax_base','recovery_tax_base',*structure.author.FINDINGS]:
            value=deepcopy(base);value['tax_premises'][key]='unknown'
            self.assertEqual(inspect(value)['status'],'structure_valid')
        for parent,key in [('component','refund'),('component','recovery'),('component','settled'),
                           ('tax_premises','opening_dta'),('tax_premises','opening_dtl'),('balances','cash')]:
            value=deepcopy(base);value[parent][key]='unknown';self.assertEqual(inspect(value)['status'],'invalid')

    def test_structure_does_not_claim_semantic_feasibility(self):
        value=next(iter(states().values()));value['balances']['cash']='-1/1'
        self.assertEqual(inspect(value)['status'],'structure_valid')
        value['seen']+=value['seen']
        self.assertEqual(inspect(value)['status'],'structure_valid')
        value['period']['end_exclusive']=value['period']['start']
        self.assertEqual(inspect(value)['status'],'structure_valid')

    def test_carry_keeps_prior_year_memory_and_unicode_values(self):
        value=states()['next_opening'];self.assertTrue(value['prior_years'])
        value['context']['entity']='公司 Café'
        result=inspect(value);self.assertEqual(result['status'],'structure_valid')
        self.assertEqual(result['value']['tax_adjustments'],value['tax_adjustments'])
        self.assertEqual(result['value']['prior_years'],value['prior_years'])
        value['context']['entity']='公司 Café'
        self.assertNotEqual(result['decoded_sha256'],inspect(value)['decoded_sha256'])


if __name__=='__main__':unittest.main()
