from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('fiscal_timeline_examples',ROOT/'data/accounting-master/fiscal-timeline-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex);api=ex.timeline

class FiscalTimelineTests(unittest.TestCase):
    def run_case(self,state,body,status='complete_mixed_timeline'):
        before=deepcopy((state,body));r=api.run(state,body)
        self.assertEqual(r['status'],status,r.get('reason',r.get('stop')))
        self.assertEqual((state,body),before)
        for key in api.FLAGS:self.assertIs(r[key],False)
        return r

    def test_declared_cases(self):
        for name,(s,b,status) in ex.cases().items():
            with self.subTest(name=name):self.run_case(s,b,status)

    def test_full_native_interleaving_and_reports(self):
        s,b,m=ex.prepared();r=self.run_case(s,b)
        self.assertEqual(r['trace'][0]['request'],m['request'])
        self.assertEqual(r['trace'][0]['result'],m['sale'])
        for row,key in zip(r['trace'][1:],['current','deferred','carry']):
            self.assertEqual(row['result']['transition'],m[key])
        self.assertEqual(r['after'],m['carry']['after'])
        self.assertEqual(r['after']['period_archive'][-1]['report'],m['carry']['details']['report'])
        self.assertEqual(r['timeline_cursor'],r['after']['after']['date'])
        self.assertEqual(r['timeline_cursor'],'2028-01-01')
        self.assertEqual(r['recorded_statements']['recorded_profit'],'0/1')
        self.assertFalse(r['fiscal_complete'])

    def test_independent_nonzero_deferred_and_carry_arithmetic(self):
        s,b,m=ex.prepared();r=self.run_case(s,b)
        close=r['trace'][2]['result']['after']['after']['balances'];final=r['after']['after']['balances']
        self.assertEqual([close[k] for k in ['cash','inventory','current_tax','dta','dtl','deferred_tax']],
                         ['467/1','70/1','5/4','3/1','-5/1','2/1'])
        self.assertEqual(r['trace'][2]['result']['transition']['journal']['dta'],'-2/1')
        self.assertEqual(r['trace'][2]['result']['transition']['flows'],[])
        self.assertEqual(m['carry']['details']['carried_profit'],'7/4')
        self.assertEqual(Q(final['retained']),Q(s['after']['balances']['retained'])-Q(7,4))
        self.assertEqual(final['retained'],'-27/2')
        self.assertEqual(final['income_tax_payable'],'-23/2')
        self.assertTrue(all(final[k]=='0/1' for k in r['after']['account_classes']['income']))
        self.assertEqual(r['after']['historical_vintages'],s['historical_vintages'])
        self.assertEqual(r['after']['recognition_archive'],s['recognition_archive'])
        self.assertEqual(r['after']['after']['flows'],[])
        self.assertEqual(r['after']['current_period_tax'],'unassessed')

    def test_stale_measurement_refuses_without_rebinding(self):
        s,b=ex.payment_variant();original=deepcopy(b['operations'][1]['operation'])
        r=self.run_case(s,b,'stopped_provisional')
        self.assertEqual(len(r['trace']),3)
        self.assertEqual(r['stop']['outcome']['reason'],'measurement_state_digest')
        self.assertEqual(r['stop']['entry']['operation'],original)
        self.assertEqual(r['after']['after']['balances']['cash'],'466/1')
        self.assertEqual(r['after']['deferred_assessments'],[])
        self.assertEqual(len(r['remaining_actions']),2)
        self.assertNotEqual(original['event']['measurement']['state_sha256'],
                            api.runtime.annual.book.digest(r['after']['after']))

    def test_explicit_new_measurement_is_a_different_request(self):
        s,stale=ex.payment_variant();_,fresh=ex.payment_variant(True)
        self.assertNotEqual(api.digest(stale),api.digest(fresh))
        r=self.run_case(s,fresh)
        current=deepcopy(s)
        for row in r['trace']:
            if row['entry']['kind']=='decision':
                req=row['request'];out=api.decision.apply(current,req,api.decision.propose(current,req))
                self.assertEqual(out,row['result']);current=out['after']
            else:
                out=api.runtime.transition(current,row['entry']['operation'])
                self.assertEqual(out,row['result']['transition']);current=out['after']
        self.assertEqual(r['after'],current)
        self.assertEqual(current['after']['balances']['cash'],'466/1')
        self.assertEqual(current['after']['balances']['income_tax_payable'],'-21/2')

    def test_payment_after_deferred_preserves_stale_prefix_and_blocks_carry(self):
        s,b=ex.payment_variant(after_deferred=True);r=self.run_case(s,b,'stopped_provisional')
        self.assertEqual(len(r['trace']),4)
        self.assertEqual(r['after']['current_period_deferred_tax'],'stale')
        self.assertEqual(r['stop']['outcome']['reason'],'assessments_incomplete')
        self.assertEqual(len(r['after']['deferred_assessments']),1)
        self.assertEqual(r['after']['period_archive'],s['period_archive'])

    def test_unknown_and_false_deferred_evidence_keep_native_status(self):
        for kind in ['unknown','false','missing']:
            s,b,m=ex.prepared();key=api.runtime.annual.deferred.FINDINGS[0]
            finding=b['operations'][1]['operation']['event']['findings']
            if kind=='missing':del finding[key]
            else:finding[key]={'status':'unknown','reason':'No finding'} if kind=='unknown' else ex.annual.known(False)
            r=self.run_case(s,b,'stopped_provisional')
            self.assertEqual(r['after'],m['current']['after'])
            expected='unresolved' if kind=='unknown' else 'unsupported' if kind=='false' else 'invalid'
            self.assertEqual(r['stop']['outcome']['status'],expected)

    def test_carry_retains_provisional_finding_statuses(self):
        s,b,_=ex.prepared();findings=b['operations'][2]['operation']['event']['findings']
        key=next(iter(findings));findings[key]=ex.annual.known(False)
        r=self.run_case(s,b)
        self.assertEqual(r['after']['finding_status'][key],'asserted_false')
        self.assertIn('unresolved',r['after']['finding_status'].values())
        self.assertFalse(r['accounting_admission'])

    def test_static_bad_later_clocks_prevent_execution(self):
        mutations=[lambda b:b['operations'][1].update(date='2027-12-30'),
            lambda b:b['operations'][1]['operation']['event'].update(date='2027-12-31'),
            lambda b:b['operations'][2]['operation']['event']['next_period'].update(start='2028-01-02'),
            lambda b:b['operations'][2]['operation']['event']['next_period'].update(end_exclusive='2028-01-01'),
            lambda b:b['operations'][2].update(date='2027-12-31')]
        for mutate in mutations:
            s,b,_=ex.prepared();mutate(b)
            with patch.object(api.runtime,'transition',wraps=api.runtime.transition) as call:
                self.run_case(s,b,'invalid');self.assertEqual(call.call_count,0)

    def test_duplicates_ties_and_stale_initial_state(self):
        s,b,_=ex.prepared();b['operations'][1]['priority']=20;self.run_case(s,b,'unresolved')
        s,b,_=ex.prepared();b['operations'][1]['operation']['event']['id']=b['operations'][0]['operation']['event']['id']
        self.run_case(s,b,'invalid')
        s,b,_=ex.prepared();b['operations'][1]['id']=b['operations'][0]['id'];self.run_case(s,b,'invalid')
        s,b,_=ex.prepared();b['expected_state_sha256']='0'*64;self.run_case(s,b,'invalid')

    def test_carry_is_terminal_and_next_period_needs_new_binding(self):
        s,b,m=ex.prepared();r=self.run_case(s,b)
        later=ex.next_period(r['after']);n=self.run_case(r['after'],later)
        # One unit remains, but the inherited explicit reserve is one half.
        self.assertEqual(n['after']['after']['balances']['cash'],'949/2')
        self.assertEqual(n['after']['after']['balances']['inventory'],'65/1')
        self.assertEqual(n['trace'][0]['result']['decision']['operation']['event']['sold_units'],'1/2')
        self.assertEqual(n['after']['period_archive'],r['after']['period_archive'])
        self.assertEqual(n['after']['historical_vintages'],s['historical_vintages'])
        self.assertEqual(n['after']['current_period_tax'],'unassessed')
        bad=deepcopy(b);bad['schedules'][0]['calendar']['dates'].append('2028-01-02')
        self.run_case(s,bad,'invalid')
        bad=deepcopy(b);bad['operations'].append(deepcopy(bad['operations'][-1]));bad['operations'][-1]['id']='second-carry'
        self.run_case(s,bad,'invalid')

    def test_prior_v2_financial_outcomes_preserved(self):
        for _,(s,b,status) in ex.previous.cases().items():
            old=api.prior.run(s,b);new=deepcopy(b);new['profile']=api.PROFILE;r=self.run_case(s,new,status)
            for key in ['after','calendar','timeline_cursor','remaining_actions']:
                if key in old:self.assertEqual(r[key],old[key])
            if 'reason' in old:self.assertEqual(r['reason'],old['reason'])

    def test_actual_32_native_64_mixed_limits(self):
        _,_,m=ex.prepared();state=m['current']['after'];body=ex.previous.scheduled.root(state,enabled=False)
        body.update(profile=api.PROFILE,operations=[])
        template=body['schedules'][0];template['calendar']={'kind':'explicit_dates','dates':['2027-12-31']}
        body['schedules']=[deepcopy(template) for _ in range(32)]
        for i,schedule in enumerate(body['schedules']):schedule.update(id='idle-'+str(i),priority=100+i)
        current=deepcopy(state)
        for i in range(32):
            op=ex.annual.deferred(current,'measurement-'+str(i),capacity='12/1',recognized='12/1')
            body['operations'].append({'id':'entry-'+str(i),'date':'2027-12-31','priority':i,'operation':op})
            current=api.runtime.transition(current,op)['after']
        r=self.run_case(state,body);self.assertEqual(len(r['trace']),64);self.assertEqual(r['after'],current)
        body['operations'].append(deepcopy(body['operations'][0]));self.run_case(state,body,'invalid')

if __name__=='__main__':unittest.main()
