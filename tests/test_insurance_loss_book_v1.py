from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import insurance_loss_book_v1 as bridge
spec=importlib.util.spec_from_file_location('insurance_loss_examples',ROOT/'data/accounting-master/insurance-loss-book-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)


class InsuranceLossBookTests(unittest.TestCase):
    def result(self,q,status='proposed_provisional'):
        before=deepcopy(q);r=bridge.propose(q)
        self.assertEqual(r['status'],status,r);self.assertEqual(q,before)
        self.assertTrue(all(r[k] is False for k in bridge.FLAGS))
        if status!='proposed_provisional':self.assertNotIn('execution',r)
        return r

    def test_two_charts_two_loss_components_and_complement(self):
        for chart in ['named','numbered']:
            for case in bridge.CASES:
                row=ex.checked_case(chart,case)
                r=row['result'];self.assertEqual(len(r['expected_steps']),6)
                self.assertEqual(r['native_result']['report']['total_profit'],'5')
                self.assertEqual(r['native_result']['mutations'],[])
                self.assertFalse(r['native_result']['posts'])
                for e in r['execution']['trace']:
                    if e['command']['kind']=='event':
                        actual=e['result']['transition']['monetary']['diagnostics']['postings']
                        self.assertEqual(len(actual),len(next(s for s in r['expected_steps'] if s['id']==e['command']['event']['id'])['native_journal']))

    def test_no_complement_and_exact_replay(self):
        q=ex.fixture(complement=False);r=self.result(q)
        self.assertTrue(bridge.verify(q,r))
        self.assertEqual(r['execution']['trace'][-1]['result']['equity']['closing'],'105/1')
        r['execution']['current']['balances'][q['roles']['cash']]='106/1'
        self.assertFalse(bridge.verify(q,r))

    def test_zero_loss_keeps_zero_gross_reversal_posting(self):
        q=ex.fixture(case='zero-loss-boundary');r=self.result(q)
        step=r['execution']['trace'][1]
        gross=step['result']['transition']['monetary']['diagnostics']['postings']
        p=next(x for x in gross if x['account']=='loss_reversal')
        self.assertEqual(p['binding']['value'],'0/1')
        self.assertEqual(step['result']['transition']['after']['memory']['insurance']['loss_component'],'0/1')

    def test_unknown_and_false_native_findings_preserved(self):
        for finding,status in [(None,'unresolved'),(False,'unsupported')]:
            q=ex.fixture();q['native_request']['findings']['source_profile_applicable']=finding
            q['native_request_sha256']=bridge.core.digest(q['native_request'])
            r=self.result(q,status);self.assertIn('source_profile_applicable',r['reason'])

    def test_forged_rehashed_native_result_refused(self):
        q=ex.fixture();q['native_result']['report']['journals'][0]['finance_expense']='9'
        q['native_result_sha256']=bridge.core.digest(q['native_result'])
        self.assertEqual(self.result(q,'invalid')['reason'],'native_result_recomputation')

    def test_unsupported_valid_native_variation_refused(self):
        q=ex.fixture();q['native_request']['data']['cash']='201'
        q['native_request_sha256']=bridge.core.digest(q['native_request'])
        q['native_result']=bridge.native_result(q['native_request']);q['native_result_sha256']=bridge.core.digest(q['native_result'])
        self.assertEqual(self.result(q,'invalid')['reason'],'outside_retained_native_request')

    def test_stale_native_hashes(self):
        for field in ['native_request_sha256','native_result_sha256']:
            q=ex.fixture();q[field]='0'*64
            self.assertEqual(self.result(q,'invalid')['reason'],'stale_native_input')

    def test_role_alias_missing_extra_wrong_class(self):
        for kind in ['alias','missing','extra','class']:
            q=ex.fixture()
            if kind=='alias':q['roles']['liability']=q['roles']['cash']
            elif kind=='missing':q['roles'].pop('loss_reversal')
            elif kind=='extra':q['roles']['loss_component']=q['roles']['liability']
            else:q['roles']['loss_reversal']=q['roles']['claims_expense'];q['roles']['claims_expense']=ex.fixture()['roles']['loss_reversal']
            self.result(q,'invalid')

    def test_owner_currency_context_or_unit_mismatch(self):
        for kind in ['owner','currency','context','scale']:
            q=ex.fixture()
            if kind=='owner':q['opening']['context']['entity']='Foreign Insurer'
            elif kind=='currency':q['opening']['context']['currency']='USD'
            elif kind=='context':q['context_adapter']['host_context_sha256']='0'*64
            else:q['context_adapter']['unit_scale']='1000/1'
            self.result(q,'invalid')

    def test_balanced_wrong_opening_refused(self):
        q=ex.fixture();q['opening']['balances'][q['roles']['cash']]='201/1'
        capital=next(a for a,x in q['opening']['accounts'].items() if x['classification']=='equity')
        q['opening']['balances'][capital]=bridge.fmt(int(q['opening']['balances'][capital].split('/')[0])-1)
        self.assertEqual(self.result(q,'invalid')['reason'],'native_opening_balance:cash')

    def test_wrong_loss_memory_progress_and_case_identity(self):
        for field,value in [('loss_component','21/1'),('next_step','1/1'),('case_ref','wrong')]:
            q=ex.fixture();q['opening']['memory']['insurance'][field]=value
            self.assertEqual(self.result(q,'invalid')['reason'],'insurance_memory_value:'+field)

    def test_memory_pointer_and_type_mismatch(self):
        q=ex.fixture();q['memory_map']['next_step']=q['memory_map']['loss_component'];self.result(q,'invalid')
        q=ex.fixture();q['opening']['memory_types']['/insurance/loss_component']=deepcopy(q['opening']['memory_types']['/insurance/next_step'])
        self.assertEqual(self.result(q,'invalid')['reason'],'insurance_memory_type:loss_component')

    def test_native_dates_not_shifted_or_truncated(self):
        q=ex.fixture();q['opening']['period']['end_exclusive']='2027-01-01'
        self.assertEqual(self.result(q,'invalid')['reason'],'native_dates_within_host_period')
        q=ex.fixture();compiled,_,_=bridge.build(q)
        compiled['commands'][0]['event']['date']='2025-12-31'
        result=bridge.program.run(compiled)
        self.assertEqual(result['status'],'stopped_provisional')
        self.assertEqual(result['trace'],[])
        self.assertEqual(result['current'],q['opening'])

    def test_progress_prevents_skipped_and_repeated_journals(self):
        q=ex.fixture();compiled,_,_=bridge.build(q)
        skipped=deepcopy(compiled);skipped['commands'].pop(0)
        r=bridge.program.run(skipped);self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(r['trace'],[])
        repeated=deepcopy(compiled);extra=deepcopy(repeated['commands'][0]);extra['event']['id']='repeat.first'
        repeated['commands'].insert(1,extra)
        r=bridge.program.run(repeated);self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(len(r['trace']),1)
        self.assertEqual(r['current']['memory']['insurance']['next_step'],'1/1')

    def test_unsupported_cash_policy_and_bad_map(self):
        q=ex.fixture();q['cash_policy']['claims_activity']='financing'
        self.assertEqual(self.result(q,'invalid')['reason'],'supported_claim_cash_activity')
        q=ex.fixture();q['mapping']['lines'].pop();self.result(q,'invalid')

    def test_closed_shape_recursive_input_and_dependency_change(self):
        q=ex.fixture();q['extra']=True;self.result(q,'invalid')
        q=ex.fixture();q['schemas']['cycle']=q
        with patch.object(bridge,'native_result') as native:
            self.assertEqual(bridge.propose(q)['status'],'invalid');native.assert_not_called()
        q=ex.fixture()
        with patch.dict(bridge.PINS,{'scripts/declared_company_program_v2.py':'0'*64}):
            self.assertEqual(self.result(q,'invalid')['reason'],'dependency_hash:scripts/declared_company_program_v2.py')


if __name__=='__main__':unittest.main()
