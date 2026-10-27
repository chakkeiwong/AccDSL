from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json,sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import lease_allocation_family_v1 as family

def domain(a=0,b=120,lc=True,uc=True):
    return {'lower':family.fmt(a),'upper':family.fmt(b),'lower_inclusive':lc,'upper_inclusive':uc}

def request(a=0,b=120,lc=True,uc=True,cells=3):
    return {'profile':family.PROFILE,'source_lock_sha256':family.SOURCE_LOCK_SHA256,
            'allocation_domain':domain(a,b,lc,uc),'allocation_premise':'Supplied exact two-right synthetic allocation family',
            'source_ref':'synthetic:retained-total120-liabilities100-50',
            'collection_complete':True,'max_cells':cells}

def query(*constraints):
    return {'profile':family.QUERY,'conditional_on':'complete_execution','constraints':list(constraints),
            'premise':'Supplied hypothetical final observation','source_ref':'synthetic:outcome-condition','max_replays':1}

class LeaseAllocationFamilyTests(unittest.TestCase):
    def test_full_domain_keeps_all_three_regions(self):
        req=request();before=deepcopy(req);r=family.assess(req)
        self.assertEqual(r['status'],'exact_conditional_partition')
        self.assertEqual([x['id'] for x in r['cells']],['complete','rejected_depreciation','unsupported_reduction'])
        self.assertFalse(r['all_allocations_complete']);self.assertTrue(r['coverage']['complete'])
        self.assertEqual(r['complete_execution_bounds']['profit'],domain(-69,-39))
        self.assertEqual(req,before)
        for k in family.FLAGS:self.assertIs(r[k],False)

    def test_every_boundary_and_failure_prefix(self):
        for x,kind,n in [(0,'complete',4),(30,'complete',4),(111,'rejected_depreciation',3),(120,'unsupported_reduction',1)]:
            r=family.assess(request(x,x));self.assertEqual(len(r['cells']),1)
            c=r['cells'][0];self.assertEqual(c['id'],kind);self.assertEqual(c['prefix_length'],n)
            self.assertEqual(len(c['native_replay']['result']['proposals']),n)
            self.assertEqual(c['allocation_domain'],domain(x,x))

    def test_open_boundaries_do_not_leak_to_adjacent_cells(self):
        r=family.assess(request(30,111,False,False))
        self.assertEqual([c['id'] for c in r['cells']],['rejected_depreciation'])
        self.assertEqual(r['cells'][0]['allocation_domain'],domain(30,111,False,False))
        self.assertIsNone(r['complete_execution_bounds'])
        r=family.assess(request(111,120,False,True))
        self.assertEqual([c['id'] for c in r['cells']],['unsupported_reduction'])

    def test_fractional_complete_interval_preserves_attainment(self):
        r=family.assess(request(Q(1,3),Q(59,2),False,True))
        self.assertTrue(r['all_allocations_complete'])
        self.assertEqual(r['complete_execution_bounds']['final_rou'],domain(Q(1,2),Q(89,3),True,False))
        self.assertEqual(r['complete_execution_bounds']['cash'],domain(101,101))

    def test_budget_zero_and_one_preserve_unvisited_regions(self):
        for budget in [0,1]:
            r=family.assess(request(cells=budget));self.assertEqual(r['status'],'partial_search')
            self.assertEqual(len(r['cells']),3);self.assertEqual(r['coverage']['checked_cells'],budget)
            self.assertIsNone(r['complete_execution_bounds']);self.assertIsNone(r['all_allocations_complete'])
            for c in r['cells'][budget:]:self.assertFalse(c['checked']);self.assertIsNone(c['native_replay'])
            q=family.query(request(cells=budget),query());self.assertEqual(q['status'],'partial_search');self.assertIsNone(q['outcome_bounds'])

    def test_original_native_inputs_and_successful_prefix_are_complete(self):
        r=family.assess(request())
        for c in r['cells']:
            w=c['native_replay'];again=family.native.run_prefix(w['opening'],w['events'])
            self.assertEqual(again,w['result'])
            for i,p in enumerate(again['proposals']):
                before=w['opening'] if i==0 else again['proposals'][i-1]['after']
                self.assertEqual(family.native.apply(before,w['events'][i],p),p['after'])

    def test_same_aggregate_opening_different_joint_outcomes(self):
        a=family.native_replay(Q(20));b=family.native_replay(Q(30))
        self.assertEqual(a['opening']['balances'],b['opening']['balances'])
        self.assertNotEqual(a['result']['state']['balances'],b['result']['state']['balances'])

    def test_joint_marginal_endpoints_cannot_be_combined(self):
        cond=query({'target':'final_rou','domain':domain(30,30)}, {'target':'profit','domain':domain(-69,-69)})
        r=family.query(request(),cond);self.assertEqual(r['status'],'infeasible_conditional_selection')
        self.assertIsNone(r['outcome_bounds']);self.assertEqual(len(r['family']['cells']),3)

    def test_final_asset_observation_retains_unconditioned_family(self):
        cond=query({'target':'final_rou','domain':domain(10,10)})
        r=family.query(request(),cond);self.assertEqual(r['selection'],domain(20,20))
        self.assertEqual(r['outcome_bounds']['profit'],domain(-59,-59));self.assertEqual(len(r['family']['cells']),3)
        self.assertEqual(r['native_replay']['result']['state']['balances']['rou'],'10/1')

    def test_empty_complete_region_and_constant_outcome(self):
        r=family.query(request(31,120),query());self.assertEqual(r['status'],'infeasible_conditional_selection')
        r=family.query(request(),query({'target':'cash','domain':domain(100,100)}))
        self.assertEqual(r['status'],'infeasible_conditional_selection')
        r=family.query(request(),query({'target':'cash','domain':domain(100,102,False,False)}))
        self.assertEqual(r['selection'],domain(0,30))

    def test_unknown_membership_and_premise_remain_unresolved(self):
        for value in [False,None,'unknown']:
            r=request();r['collection_complete']=value
            self.assertEqual(family.assess(r)['status'],'unresolved')
        r=request();r['allocation_premise']=None
        self.assertEqual(family.assess(r)['status'],'unresolved')
        q=query();q['premise']=None
        self.assertEqual(family.query(request(),q)['status'],'unresolved')

    def test_invalid_and_unsupported_fields_do_not_become_unknown(self):
        for field,value,status in [('max_cells',True,'invalid'),('max_cells',4,'invalid'),('collection_complete',0,'invalid'),
            ('source_lock_sha256','0'*64,'unsupported'),('profile','AnyLease','unsupported'),('source_ref','', 'invalid')]:
            r=request();r[field]=value;self.assertEqual(family.assess(r)['status'],status)
        r=request();r['callback']='any';self.assertEqual(family.assess(r)['status'],'invalid')
        for value in [0,True,1.5,'2/2','unknown']:
            r=request();r['allocation_domain']['lower']=value
            self.assertEqual(family.assess(r)['status'],'invalid')
        for d in [domain(-1,30),domain(0,121),domain(30,30,False,True),domain(40,30)]:
            r=request();r['allocation_domain']=d;self.assertEqual(family.assess(r)['status'],'invalid')

    def test_query_requires_declared_complete_condition(self):
        q=query();q['conditional_on']='all_actual_histories'
        self.assertEqual(family.query(request(),q)['status'],'unsupported')

    def test_query_replay_budget_is_explicit(self):
        q=query({'target':'final_rou','domain':domain(10,10)});q['max_replays']=0
        r=family.query(request(),q)
        self.assertEqual(r['status'],'partial_search');self.assertIsNone(r['selection'])
        self.assertIsNone(r['outcome_bounds']);self.assertIsNone(r['native_replay'])
        self.assertEqual(r['unverified_candidate_selection'],domain(20,20))
        q['max_replays']=True
        self.assertEqual(family.query(request(),q)['status'],'invalid')
        q=query({'target':'revenue','domain':domain(0,1)})
        self.assertEqual(family.query(request(),q)['status'],'unsupported')

    def test_roundtrip_and_forged_result(self):
        req=request();result=family.assess(req)
        self.assertTrue(family.verify_result(req,json.loads(json.dumps(result))))
        result['cells'][1]['native_status']='hypothetical_sequence_complete'
        with self.assertRaises(family.Refused):family.verify_result(req,result)

    def test_source_corruption_refuses_without_editing_protected_files(self):
        original=Path.read_bytes
        def changed(path):
            content=original(path)
            return content+b' ' if path==family.HERE/'source-lock.json' else content
        with patch.object(Path,'read_bytes',changed):
            r=family.assess(request());self.assertEqual(r['status'],'unsupported');self.assertEqual(r['reason'],'source lock changed')

if __name__=='__main__':unittest.main()
