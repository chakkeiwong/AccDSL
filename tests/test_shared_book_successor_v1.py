from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import shared_book_successor_v1 as m
spec=importlib.util.spec_from_file_location('successor_examples',ROOT/'data/accounting-master/shared-book-successor-20261024/examples.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)

class SharedBookTests(unittest.TestCase):
    def test_saved_refusal_cases(self):
        for row in e.cases():
            r=m.run_prefix(row['opening'],row['events'])
            self.assertEqual(r['status'],row['expected_status'],row['case'])
            self.assertEqual(r.get('stop_status'),row['expected_stop'],row['case'])
            self.assertTrue(all(r[k] is False for k in m.FLAGS))

    def test_mixed_prefix_conserves_cash_and_component_memory(self):
        opening=e.opening();before=deepcopy(opening);events=e.events();r=m.run_prefix(opening,events)
        self.assertEqual(opening,before);self.assertEqual(r['status'],'complete',r.get('stop_status'))
        self.assertEqual(len(r['trace']),5);after=r['after']
        self.assertEqual(after['balances']['cash'],'361/1');self.assertEqual(after['balances']['rou'],'90/1')
        self.assertEqual(after['balances']['lease_liability'],'0/1');self.assertEqual(after['balances']['inventory'],'60/1')
        self.assertEqual(len(after['flows']),5);self.assertEqual(len(after['seen']),5)
        for t in r['trace']:
            p=t['result']['proposal'];self.assertEqual(sum(Q(x) for x in p['journal'].values()),0)
            self.assertEqual(Q(p['journal']['cash']),sum(Q(f['amount']) for f in p['flows']))
            old=before;new=p['after']
            for k,v in old['balances'].items():self.assertEqual(Q(new['balances'][k])-Q(v),Q(p['journal'][k]))
            if t['event']['module']=='return':self.assertEqual(old['leases'],new['leases'])
            else:
                for k in ['component','lots','tax_adjustments','tax_premises','other_inventory','prior_years']:self.assertEqual(old[k],new[k])
            before=new

    def test_original_component_comparators(self):
        source=e.sources();s=e.opening()
        for module,index,key in [('return',1,'typed_return'),('lease',0,'shared_lease')]:
            r=m.propose(s,e.events()[index]);self.assertEqual(r['status'],'proposed',r.get('reason'))
            actual=r['proposal'];original=source[key]['native_result']['proposal']
            for account,value in original['journal'].items():
                if account in actual['journal']:self.assertEqual(actual['journal'][account],value,account)
                else:self.assertEqual(Q(value),0,account)
            self.assertEqual([(f['activity'],f['amount']) for f in actual['flows']],[(f['activity'],f['amount']) for f in original['flows']])
            if module=='return':
                self.assertEqual(actual['after']['component'],original['after']['component'])
                lots=deepcopy(actual['after']['lots']);original_lots=deepcopy(original['after']['lots'])
                for lot in lots.values():lot.pop('acquired')
                for lot in original_lots.values():lot.pop('acquired')
                self.assertEqual(lots,original_lots)
            else:self.assertEqual(actual['after']['leases'][0]['component'],original['after']['leases'][0]['component'])

    def test_all_five_original_native_method_comparators(self):
        for row in e.native_comparators():
            a=row['successor_result']['proposal'];b=row['original_result']['proposal']
            for key in set(a['journal'])|set(b['journal']):self.assertEqual(Q(a['journal'].get(key,'0/1')),Q(b['journal'].get(key,'0/1')),key)
            self.assertEqual([(f['activity'],f['amount']) for f in a['flows']],[(f['activity'],f['amount']) for f in b['flows']])
            if row['module']=='lease':self.assertEqual([x['component'] for x in a['after']['leases']],[x['component'] for x in b['after']['leases']])
            else:
                self.assertEqual(a['after']['component'],b['after']['component'])
                for key in a['after']['lots']:
                    self.assertEqual({k:v for k,v in a['after']['lots'][key].items() if k!='acquired'}, {k:v for k,v in b['after']['lots'][key].items() if k!='acquired'})

    def test_stale_forged_and_duplicate_apply(self):
        s=e.opening();event=e.events()[0];r=m.propose(s,event);p=r['proposal']
        self.assertEqual(m.apply(s,event,p)['status'],'applied_diagnostic')
        for part in ['journal','memory','flow','admission']:
            bad=deepcopy(p)
            if part=='journal':bad['journal']['cash']='1/1'
            elif part=='memory':bad['after']['component']['refund']='0/1'
            elif part=='flow':bad['flows']=[{'amount':'1/1'}]
            else:bad['committed']=True
            self.assertEqual(m.apply(s,event,bad)['status'],'invalid')
        changed=deepcopy(s);changed['balances']['cash']='501/1';changed['balances']['original_equity']='19/1'
        self.assertEqual(m.apply(changed,event,p)['status'],'invalid')
        self.assertEqual(m.propose(p['after'],event)['status'],'invalid')
        bad=deepcopy(p);bad['committed']=0
        self.assertEqual(m.apply(s,event,bad)['status'],'invalid')

    def test_shared_cash_competition_preserves_completed_prefix(self):
        s=e.opening();s['balances']['cash']='130/1';s['balances']['original_equity']='390/1'
        events=e.events();r=m.run_prefix(s,[events[0],events[1],events[3]])
        self.assertEqual(r['status'],'stopped');self.assertEqual(r['stop_status'],'funding_failure')
        self.assertEqual(r['after']['balances']['cash'],'82/1');self.assertEqual(len(r['after']['seen']),2)
        lease_only=m.run_prefix(s,[events[0],events[3]]);self.assertEqual(lease_only['status'],'complete')
        self.assertEqual(lease_only['after']['balances']['cash'],'9/1')

    def test_unknown_premises_and_membership(self):
        s=e.opening();event=e.events()[1];event['event']['inventory_nrv']='unknown'
        self.assertEqual(m.propose(s,event)['status'],'unresolved')
        s['lease_membership']='unknown';self.assertEqual(m.propose(s,e.events()[0])['status'],'unresolved')
        s=e.opening();event=e.events()[4];event['event']['parameters']['systematic_allocation_supported']=None
        self.assertEqual(m.propose(s,event)['status'],'unresolved')

    def test_unsupported_context_methods_and_invalid_allocations(self):
        s=e.opening();s['context']['currency']='EUR';self.assertEqual(m.propose(s,e.events()[0])['status'],'unsupported')
        s=e.opening();event=e.events()[0];event['module']='tax';self.assertEqual(m.propose(s,event)['status'],'unsupported')
        s['balances']['rou']='121/1';s['balances']['original_equity']='19/1'
        self.assertEqual(m.propose(s,e.events()[0])['status'],'invalid')

    def test_empty_prefix_still_validates_opening(self):
        s=e.opening();self.assertEqual(m.run_prefix(s,[])['status'],'complete')
        s['balances']['cash']='1/1'
        self.assertEqual(m.run_prefix(s,[])['stop_status'],'invalid')

if __name__=='__main__':unittest.main()
