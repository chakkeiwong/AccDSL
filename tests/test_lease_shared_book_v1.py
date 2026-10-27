from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json,sys,unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import lease_shared_book_v1 as lease
spec=importlib.util.spec_from_file_location('shared_lease_authored',lease.SOURCE/'authored_cases.py')
authored=importlib.util.module_from_spec(spec);spec.loader.exec_module(authored)
ORIGINAL=next(c for c in authored.CASES if c['id']=='heterogeneous-rights')

def fixture():
    values={k:lease.fmt(ORIGINAL['opening_balances'].get(k,0)) for k in lease.types.ACCOUNTS}
    state={'profile':lease.PROFILE,'context':deepcopy(lease.SCOPE['context']),
      'original_scope_sha256':lease.SCOPE_HASH,'period':{'start':'2024-01-01','end_exclusive':'2026-01-01'},
      'date':'2024-01-01','balances':values,'leases':[{'component':lease.encode(ORIGINAL['opening_component']),
      'instantiation_premise':'Retained heterogeneous-rights synthetic fixture'}],
      'collection_complete':True,'membership_premise':'Supplied complete synthetic lease inventory',
      'funding_policy':'no_overdraft','seen':[],'flows':[],'conditional':True}
    events=[{'profile':lease.EVENT,'id':'event-'+str(i),'kind':'lease','method':s['method'],'lease_id':'lease1',
      'date':s['event_date'],'parameters':lease.encode(s['parameters']),'original_scope_sha256':lease.SCOPE_HASH}
      for i,s in enumerate(ORIGINAL['steps'],1)]
    return state,events

def cash(state,value):
    before=lease.amount(state['balances']['cash']);state['balances']['cash']=lease.fmt(value)
    state['balances']['original_equity']=lease.fmt(lease.amount(state['balances']['original_equity'])+before-value)

def two_leases():
    state,events=fixture();other=deepcopy(state['leases'][0]);other['component']['lease_id']='lease2'
    other['instantiation_premise']='Separately supplied synthetic second lease with same finite method inputs'
    state['leases'].append(other)
    state['balances']['rou']='240/1';state['balances']['lease_liability']='-300/1'
    state['balances']['original_equity']=lease.fmt(lease.amount(state['balances']['original_equity'])+30)
    return state,events


class LeaseBookTests(unittest.TestCase):
    def test_original_four_step_lifecycle(self):
        state,events=fixture();before=deepcopy(state)
        for i,event in enumerate(events):
            result=lease.propose(state,event);self.assertEqual(result['status'],'proposed',result)
            proposal=result['proposal'];self.assertEqual(proposal['after']['leases'][0]['component'],lease.encode(ORIGINAL['steps'][i]['after']))
            expected={k:lease.fmt(ORIGINAL['steps'][i]['journal'].get(k,0)) for k in lease.types.ACCOUNTS}
            self.assertEqual(proposal['journal'],expected)
            state=lease.apply(state,event,json.loads(json.dumps(proposal)))
        self.assertEqual(state['balances']['cash'],'101/1')
        self.assertEqual(state['balances']['rou'],'0/1')
        self.assertEqual(state['balances']['lease_liability'],'0/1')
        self.assertEqual(-sum(lease.amount(state['balances'][k]) for k in lease.types.PROFIT),-69)
        self.assertEqual(before,fixture()[0])

    def test_two_lease_components_share_one_cash_pool(self):
        state,events=two_leases();cash(state,Q(400));other=deepcopy(state['leases'][1])
        result=lease.run_prefix(state,events)
        self.assertTrue(result['complete']);self.assertEqual(result['state']['balances']['cash'],'301/1')
        self.assertEqual(result['state']['leases'][1],other)
        self.assertEqual(result['state']['balances']['rou'],'120/1')
        self.assertEqual(result['state']['balances']['lease_liability'],'-150/1')
        self.assertEqual(result['state']['balances']['original_equity'],state['balances']['original_equity'])

    def test_interleaved_lease_events_preserve_local_right_identity(self):
        state,events=two_leases();cash(state,Q(300));joined=[]
        for event in events:
            joined.append(event)
            x=deepcopy(event);x['id']='other-'+event['id'];x['lease_id']='lease2';joined.append(x)
        result=lease.run_prefix(state,joined)
        self.assertTrue(result['complete'],result)
        self.assertEqual(result['state']['balances']['cash'],'102/1')
        self.assertEqual(result['state']['balances']['rou'],'0/1')
        self.assertEqual(result['state']['balances']['lease_liability'],'0/1')
        self.assertEqual(len(result['proposals']),8)

    def test_funding_failure_keeps_complete_successful_prefix(self):
        state,events=fixture();cash(state,Q(50));original=deepcopy(state)
        result=lease.run_prefix(state,events)
        self.assertEqual(result['status'],'funding_failure');self.assertEqual(result['failed_event_index'],2)
        self.assertEqual(len(result['proposals']),2);self.assertEqual(result['state']['balances']['cash'],'50/1')
        self.assertEqual(result['state']['leases'][0]['component']['rights'][0]['liability'],'90/1')
        self.assertEqual(state,original)
        failure=lease.propose(result['state'],events[2]);self.assertIsNone(failure['proposal'])

    def test_exhausted_shared_cash_cannot_be_reused_by_second_lease(self):
        state,events=two_leases();cash(state,Q(150));joined=[]
        for event in events[:3]:
            joined.append(event);x=deepcopy(event);x['id']='other-'+event['id'];x['lease_id']='lease2';joined.append(x)
        result=lease.run_prefix(state,joined)
        self.assertEqual(result['status'],'funding_failure');self.assertEqual(result['failed_event_index'],5)
        self.assertEqual(result['state']['balances']['cash'],'51/1')
        self.assertEqual(result['state']['leases'][0]['component']['rights'][0]['liability'],'0/1')
        self.assertEqual(result['state']['leases'][1]['component']['rights'][0]['liability'],'90/1')

    def test_unknown_complete_membership_amounts_and_premises(self):
        edits=[lambda s:s.update(collection_complete=False),lambda s:s.update(collection_complete='unknown'),
          lambda s:s.update(membership_premise=''),lambda s:s['leases'][0].update(instantiation_premise=''),
          lambda s:s['balances'].update(cash='unknown'),lambda s:s['leases'][0]['component']['rights'][0].update(rou='unknown')]
        for edit in edits:
            state,events=fixture();edit(state);before=deepcopy(state)
            r=lease.propose(state,events[0]);self.assertEqual(r['status'],'unresolved',r);self.assertIsNone(r['proposal']);self.assertEqual(state,before)

    def test_unknown_and_false_original_findings_remain_distinct(self):
        for value,status in [(None,'unresolved'),(False,'rejected'),('yes','invalid')]:
            state,events=fixture();events[0]['parameters']['standalone_allocation_supported']=value
            r=lease.propose(state,events[0]);self.assertEqual(r['status'],status,r)

    def test_original_nonannual_and_partial_termination_refusals(self):
        state,events=fixture();event=deepcopy(events[0]);event['parameters']['annual_end_payments']=False
        self.assertEqual(lease.propose(state,event)['status'],'unsupported')
        event=deepcopy(events[0]);event['parameters']['rights'][1]['removed_rou']='20/1'
        self.assertEqual(lease.propose(state,event)['status'],'rejected')

    def test_closed_registry_allocation_and_component_identity(self):
        edits=[lambda s:s['balances'].update(extra='0/1'),lambda s:s['balances'].pop('rou'),
          lambda s:s['leases'].append(deepcopy(s['leases'][0])),
          lambda s:s['leases'][0]['component']['rights'][1].update(right_id='A'),
          lambda s:s['leases'][0]['component']['rights'][0].update(rou='91/1'),
          lambda s:s.update(collection_complete=0)]
        for edit in edits:
            state,events=fixture();edit(state);r=lease.propose(state,events[0]);self.assertEqual(r['status'],'invalid',r)

    def test_original_context_source_and_policy_not_rebound(self):
        edits=[lambda s:s['context'].update(entity_id='ActualCompany'),lambda s:s['context'].update(currency='EUR'),
          lambda s:s.update(original_scope_sha256='0'*64),lambda s:s.update(funding_policy='free_loan')]
        for edit in edits:
            state,events=fixture();edit(state);r=lease.propose(state,events[0]);self.assertEqual(r['status'],'unsupported',r)

    def test_new_event_identity_dates_and_anniversary(self):
        state,events=fixture();p=lease.propose(state,events[0])['proposal'];after=lease.apply(state,events[0],p)
        self.assertEqual(lease.propose(after,events[0])['status'],'invalid')
        e=deepcopy(events[1]);e['date']='2023-12-31';self.assertEqual(lease.propose(after,e)['status'],'invalid')
        after=lease.run_prefix(state,events[:2])['state'];e=deepcopy(events[2]);e['date']='2024-12-31'
        r=lease.propose(after,e);self.assertEqual(r['reason'],'lease_payment_interval_mismatch')
        e['date']='unknown';self.assertEqual(lease.propose(after,e)['status'],'unresolved')
        e['date']='2026-01-01';self.assertEqual(lease.propose(after,e)['status'],'invalid')

    def test_malformed_rational_and_unknown_method_are_not_guessed(self):
        state,events=fixture()
        for value in ['2/2',1.0,True,{'n':'1','d':'1'}]:
            e=deepcopy(events[0]);e['parameters']['rights'][0]['new_rate']=value
            self.assertEqual(lease.propose(state,e)['status'],'invalid')
        e=deepcopy(events[0]);e['method']='custom.callback';self.assertEqual(lease.propose(state,e)['status'],'unsupported')
        e=deepcopy(events[0]);e['code']='anything';self.assertEqual(lease.propose(state,e)['status'],'invalid')

    def test_forged_balanced_proposal_is_rejected_by_original_replay(self):
        state,events=fixture();proposal=lease.propose(state,events[0])['proposal'];forged=deepcopy(proposal)
        forged['after']['balances']['cash']='201/1';forged['after']['balances']['original_equity']='-171/1'
        lease.invariant(forged['after'])
        with self.assertRaises(lease.Refused):lease.apply(state,events[0],forged)

    def test_unrelated_accounts_and_metadata_are_unchanged(self):
        state,events=fixture();state['balances']['inventory']='70/1';state['balances']['original_equity']='-240/1'
        result=lease.run_prefix(state,events)
        for k in ['inventory','original_equity']:self.assertEqual(result['state']['balances'][k],state['balances'][k])
        for k in ['context','original_scope_sha256','period','membership_premise','funding_policy','conditional']:
            self.assertEqual(result['state'][k],state[k])
        self.assertEqual(sum(lease.amount(f['amount']) for f in result['state']['flows'] if f['activity']=='operating'),-9)
        self.assertEqual(sum(lease.amount(f['amount']) for f in result['state']['flows'] if f['activity']=='financing'),-90)

    def test_empty_sequence_validates_full_opening_and_false_flags(self):
        state,_=fixture();r=lease.run_prefix(state,[]);self.assertTrue(r['complete']);self.assertEqual(r['state'],state)
        for k in lease.FLAGS:self.assertIs(r[k],False)
        state['balances']['cash']='-1/1'
        with self.assertRaises(lease.Refused):lease.run_prefix(state,[])


if __name__=='__main__':unittest.main()
