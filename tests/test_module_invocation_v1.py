from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import importlib.util,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import module_invocation_v1 as m
spec=importlib.util.spec_from_file_location('module_invocation_examples',ROOT/'data/accounting-master/module-invocation-20261024/examples.py')
examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)

class ModuleInvocationTests(unittest.TestCase):
    def test_four_capabilities_preserve_complete_native_results(self):
        import typed_return_transition_v1 as r
        import lease_shared_book_v1 as l
        import henkel_lease_measurements_v1 as h
        p=examples.payloads()
        originals={'typed_return':r.propose(p['typed_return']['state_text'].encode(),p['typed_return']['state_raw_sha256'],p['typed_return']['event_text'].encode(),p['typed_return']['event_raw_sha256']),
                   'shared_lease':l.propose(p['shared_lease']['state'],p['shared_lease']['event']),
                   'henkel_measurements':h.assess(p['henkel_measurements']['request'],p['henkel_measurements']['budget'])}
        original_sector=json.loads((ROOT/'data/accounting-master/module-composition-audit-20261024/probe-results.json').read_text())['sector']['report_response']
        originals['sector_report']=original_sector
        for key,payload in p.items():
            b=m.request(key,payload);before=deepcopy(b);result=m.invoke(b)
            self.assertEqual(result['status'],'returned');self.assertEqual(result['native_result'],originals[key],key)
            self.assertEqual(before,b);self.assertTrue(m.verify_result(b,result))
            self.assertTrue(all(result[k] is False for k in m.FLAGS))

    def test_preserved_native_failures_and_capability_refusals(self):
        for row in examples.cases():
            r=m.invoke(row['request']);self.assertEqual(r['status'],row['expected_status'],row['case'])
            if row['expected_native_status'] is not None:self.assertEqual(r['native_status'],row['expected_native_status'],row['case'])
            self.assertTrue(m.verify_result(row['request'],r),row['case'])

    def test_capability_mismatch_never_calls_native(self):
        p=examples.payloads()['sector_report'];b=m.request('sector_report',p,'propose')
        with patch.object(m,'native_call',side_effect=AssertionError('must not invoke')):
            r=m.invoke(b);self.assertEqual(r['status'],'unsupported');self.assertIsNone(r['native_result'])

    def test_hashes_and_closed_fields_reject_before_native(self):
        b=m.request('shared_lease',examples.payloads()['shared_lease'])
        changes=[{'registry_sha256':'0'*64},{'descriptor_sha256':'0'*64},{'payload_sha256':'0'*64},{'module_id':'arbitrary'},{'path':'/tmp/code.py'},{'callback':'execute'},{'profile':'Wrong/1'}]
        for change in changes:
            x=deepcopy(b);x.update(change)
            with patch.object(m,'native_call',side_effect=AssertionError('must not invoke')):self.assertEqual(m.invoke(x)['status'],'invalid')
        x=deepcopy(b);x['payload']['unexpected']=True;x['payload_sha256']=m.digest(x['payload'])
        self.assertEqual(m.invoke(x)['status'],'invalid')

    def test_raw_digest_and_duplicate_json_are_native_invalid(self):
        p=examples.payloads()['typed_return'];p['event_text']+=' '
        r=m.invoke(m.request('typed_return',p));self.assertEqual(r['native_status'],'invalid');self.assertEqual(r['native_result']['reason'],'raw_digest_mismatch')
        p=examples.payloads()['typed_return'];p['event_text']='{"kind":"sell","kind":"settle"}'
        p['event_raw_sha256']=sha256(p['event_text'].encode()).hexdigest()
        self.assertEqual(m.invoke(m.request('typed_return',p))['native_status'],'invalid')

    def test_dependency_and_caller_identity_are_bound(self):
        b=m.request('shared_lease',examples.payloads()['shared_lease'])
        with patch.object(m,'LOCK_SHA256','0'*64):self.assertEqual(m.invoke(b)['status'],'invalid')
        r=m.registry();self.assertEqual(r['caller_sha256'],sha256(Path(m.__file__).read_bytes()).hexdigest())
        with patch.object(m,'registry',return_value={**r,'caller_sha256':'0'*64}):self.assertEqual(m.invoke(b)['reason'],'registry_hash')

    def test_forged_output_rejected_even_with_rehashed_native_result(self):
        b=m.request('shared_lease',examples.payloads()['shared_lease']);r=m.invoke(b)
        for change in ['cash','memory','flows','admission','extra','native_status']:
            x=deepcopy(r)
            if change=='cash':x['native_result']['proposal']['journal']['cash']='999/1'
            elif change=='memory':x['native_result']['proposal']['after']['leases']=[]
            elif change=='flows':x['native_result']['proposal']['flows']=[{'invented':True}]
            elif change=='admission':x['committed']=True
            elif change=='extra':x['extra']=True
            else:x['native_status']='committed'
            x['native_result_sha256']=m.digest(x['native_result']);self.assertFalse(m.verify_result(b,x),change)

    def test_measurement_replay_checks_witness_not_runtime_identity(self):
        import henkel_lease_measurements_v1 as h
        b=m.request('henkel_measurements',{'request':h.fixture(assume=True),'budget':h.BUDGET});r=m.invoke(b)
        x=deepcopy(r);j=x['native_result']['temporal_assessment']['joint_assessment'];j['solver_wall_seconds']=0.123
        x['native_result_sha256']=m.digest(x['native_result']);self.assertTrue(m.verify_result(b,x))
        j['witness']['2024.rou_net.total']='0/1';x['native_result_sha256']=m.digest(x['native_result'])
        self.assertFalse(m.verify_result(b,x))

    def test_portable_input_limits_are_fail_closed(self):
        for bad in [None,[],{}, {'x':float('nan')},{'x':lambda:None}]:self.assertEqual(m.invoke(bad)['status'],'invalid')
        b=m.request('shared_lease',examples.payloads()['shared_lease'])
        with patch.object(m,'MAX_NODES',2):self.assertEqual(m.invoke(b)['status'],'invalid')

if __name__=='__main__':unittest.main()
