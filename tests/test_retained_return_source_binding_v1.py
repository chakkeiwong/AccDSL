"""Exact finite source projection and prefix recomputation rejection tests."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import retained_return_source_binding_v1 as binding
spec=importlib.util.spec_from_file_location('source_binding_monetary_cases',ROOT/'data/accounting-master/typed-monetary-effects-20261024/examples.py')
cases=importlib.util.module_from_spec(spec);spec.loader.exec_module(cases)
core=binding.core


def run(packet,state,event):
    s,e=core.canonical(state),core.canonical(event)
    return binding.bind_and_propose(packet,s,sha256(s).hexdigest(),e,sha256(e).hexdigest())


class RetainedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(ROOT/binding.PACKET).read_bytes()

    def test_both_retained_events_bind_and_recompute_prefix(self):
        for (name,state,event),prefix_count in zip(cases.selected_cases()[:2],[1,10]):
            old=deepcopy((state,event));result=run(self.raw,state,event)
            self.assertEqual(result['status'],'source_bound_proposal',result)
            self.assertEqual(len(result['prefix']),prefix_count)
            self.assertEqual(result['recomputed_before_sha256'],core.digest(state))
            native_after,_,_=binding.typed.structure.native.transition(state,event)
            self.assertEqual(result['result']['proposal']['after'],native_after)
            self.assertEqual((state,event),old)
            for key in binding.BOUNDARY:
                if key!='scope':self.assertFalse(result[key])

    def test_changed_event_value_and_pointer_are_not_original_source(self):
        _,state,event=cases.selected_cases()[0]
        for edit in [{'inventory_nrv':'5/1'}, {'date':'2025-02-02'},
                     {'source_pointer':'/record_registry/'+'0'*64+'/body'},
                     {'component_id':'different'}]:
            candidate=deepcopy(event);candidate.update(edit)
            self.assertEqual(run(self.raw,state,candidate)['reason'],'source_event_correspondence')

    def test_balanced_wrong_before_state_rejects(self):
        _,state,event=cases.selected_cases()[0]
        state['balances']['cash']=binding.typed.monetary.fmt(binding.typed.monetary.rational(state['balances']['cash'])+1)
        state['balances']['capital']=binding.typed.monetary.fmt(binding.typed.monetary.rational(state['balances']['capital'])-1)
        self.assertEqual(binding.typed.propose(*self.args(state,event))['status'],'proposed')
        self.assertEqual(run(self.raw,state,event)['reason'],'source_prefix_state_correspondence')

    @staticmethod
    def args(state,event):
        s,e=core.canonical(state),core.canonical(event)
        return s,sha256(s).hexdigest(),e,sha256(e).hexdigest()

    def test_changed_packet_hash_rejects_before_interpretation(self):
        _,state,event=cases.selected_cases()[0]
        for raw in [self.raw+b' ',b'{}',self.raw.replace(b'build_wall_seconds',b'build_Wall_seconds',1)]:
            self.assertEqual(run(raw,state,event)['reason'],'retained_packet_digest_mismatch')

    def test_unknown_event_identity_unsupported(self):
        _,state,event=cases.selected_cases()[0];event['id']='not_in_packet'
        self.assertEqual(run(self.raw,state,event)['status'],'unsupported')

    def test_duplicate_and_financial_float_rules(self):
        for raw in [b'{"x":1,"x":2}',b'{"financial":1.5}',b'{"build_wall_seconds":NaN}',
                    b'{"build_wall_seconds":-1.0}',b'{"build_wall_seconds":1.0,"record":{"n":2.0}}']:
            with self.assertRaises(ValueError):binding.strict_packet(raw)
        self.assertEqual(binding.strict_packet(b'{"build_wall_seconds":1.5}')['build_wall_seconds'],1.5)
        packet=binding.strict_packet(self.raw)
        self.assertEqual(len(packet['record_registry']),232)

    def test_packet_size_and_raw_input_identity(self):
        _,state,event=cases.selected_cases()[0]
        self.assertEqual(run(b'x'*(binding.MAX_PACKET_BYTES+1),state,event)['reason'],'packet_size_limit')
        s,h,e,eh=self.args(state,event)
        self.assertEqual(binding.bind_and_propose(self.raw,s,'0'*64,e,eh)['reason'],'raw_digest_mismatch')


if __name__=='__main__':unittest.main()
