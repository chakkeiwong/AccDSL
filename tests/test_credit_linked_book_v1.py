"""Exact journal mapping, dependent observations and atomic refusals."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import credit_linked_book_v1 as bridge
spec=importlib.util.spec_from_file_location('credit_linked_book_examples',ROOT/'data/accounting-master/credit-linked-book-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)


class LinkedBookTests(unittest.TestCase):
    def result(self,req,status='proposed_exact_read_only'):
        before=deepcopy(req);result=bridge.propose(req)
        self.assertEqual(result['status'],status,result)
        self.assertEqual(req,before);self.assertEqual(result['mutations'],[])
        for flag in bridge.FLAGS:self.assertFalse(result[flag])
        if status!='proposed_exact_read_only':self.assertNotIn('trace',result)
        return result

    def test_all_nine_cases_two_charts_with_and_without_complement(self):
        for case in bridge.linked.retained():
            for chart in ['named','numbered']:
                for complement in [False,True]:
                    row=ex.checked_case(case['id'],chart,complement)
                    self.assertEqual(row['result']['status'],'proposed_exact_read_only')

    def test_exact_replay_and_forged_balanced_result(self):
        req=ex.fixture();result=self.result(req)
        self.assertTrue(bridge.verify(req,result))
        forged=deepcopy(result);cash=req['roles']['cash'];gross=req['roles']['gross']
        root=bridge.algebra.Root.create(result['root']['context'],result['root']['rate'])
        balances=forged['trace'][0]['after']['balances']
        balances[cash]=(bridge.algebra.Expr.from_wire(root,balances[cash])+1).wire()
        balances[gross]=(bridge.algebra.Expr.from_wire(root,balances[gross])-1).wire()
        forged['trace'][0]['after_sha256']=bridge.digest(forged['trace'][0]['after'])
        self.assertFalse(bridge.verify(req,forged))

    def test_zero_entries_cannot_disappear(self):
        req=ex.fixture();result=self.result(req)
        first=next(t for t in result['trace'] if t['native_journal_id']=='july_accrual')
        zero=next(p for p in first['gross_postings'] if p['role']=='allowance')
        self.assertEqual(zero['amount']['terms'],[])
        first['gross_postings'].remove(zero)
        self.assertFalse(bridge.verify(req,result))

    def test_same_date_observations_keep_distinct_journal_prefixes(self):
        result=self.result(ex.fixture())
        selected=[r for r in result['observations'] if r['date']=='2026-01-01']
        self.assertEqual([r['native_stage_id'] for r in selected],['first_accrual','first','improvement_accrual','improvement'])
        self.assertEqual([r['journal_prefix'] for r in selected],[5,6,7,8])
        for row in selected:
            self.assertEqual(row['state_sha256'],result['trace'][row['journal_prefix']-1]['after_sha256'])

    def test_allowance_is_signed_contra_asset_and_zero_cash_writeoff(self):
        req=ex.fixture('adverse-without-no-recovery-finding');result=self.result(req)
        self.assertEqual(req['opening']['accounts'][req['roles']['allowance']]['classification'],'asset')
        root=bridge.algebra.Root.create(result['root']['context'],result['root']['rate'])
        first=next(o for o in result['observations'] if o['native_stage_id']=='first')
        book=result['trace'][first['journal_prefix']-1]['after']
        self.assertEqual(bridge.algebra.Expr.from_wire(root,book['balances'][req['roles']['allowance']]).rational_projection(),-22)
        result=self.result(ex.fixture())
        writeoff=next(t for t in result['trace'] if t['native_journal_id']=='july_writeoff')
        self.assertEqual(writeoff['journal'][ex.fixture()['roles']['cash']]['terms'],[])

    def test_cash_origins_keep_price_cost_fee_without_classification(self):
        req=ex.fixture('performing-prepayment');result=self.result(req)
        origins=result['closing']['unclassified_cash_origins']
        self.assertEqual([r['kind'] for r in origins[:3]],['price','integral_cost','integral_fee'])
        self.assertEqual(origins,result['native_result']['cash_flows'])
        self.assertTrue(all('activity' not in r for r in origins))
        self.assertEqual(result['unclassified_report_probe']['result']['reason'],'statement_reconciliation')

    def test_complete_native_state_and_complement_preserved(self):
        req=ex.fixture();req['opening']['memory']['tag']='User "state" Ω with spaces'
        result=self.result(req)
        native=next(r['result'] for r in bridge.linked.retained() if r['id']=='partial-early-writeoff')
        self.assertEqual(result['native_result'],native)
        self.assertEqual(result['schemas'],req['schemas'])
        for step in result['trace']:self.assertEqual(step['after']['memory'],req['opening']['memory'])

    def test_stale_linked_hash_and_native_refusal(self):
        req=ex.fixture();req['expected_linked_result_sha256']='0'*64
        self.assertEqual(self.result(req,'rejected')['reason'],'linked_result_binding')
        req=ex.fixture();q=req['linked_request']['native_request'];q['acquisition']['findings']['amortised_cost']=None
        req['linked_request']['native_request_sha256']=bridge.digest(q)
        result=self.result(req,'unresolved')
        self.assertEqual(result['reason'],'linked_refusal')
        self.assertEqual(result['linked_refusal']['native_refusal']['reason'],'missing_amortised_cost')

    def test_rehashed_unretained_request(self):
        req=ex.fixture();q=req['linked_request']['native_request'];q['opening_cash']='301'
        req['linked_request']['native_request_sha256']=bridge.digest(q)
        result=self.result(req,'rejected')
        self.assertEqual(result['linked_refusal']['reason'],'outside_retained_native_request')

    def test_role_population_alias_and_classification(self):
        for change in ['missing','extra','alias','class']:
            req=ex.fixture()
            if change=='missing':req['roles'].pop('allowance')
            elif change=='extra':req['roles']['capital']='owner.capital'
            elif change=='alias':req['roles']['gross']=req['roles']['cash']
            else:req['opening']['accounts'][req['roles']['allowance']]['classification']='liability'
            self.result(req,'rejected')

    def test_unit_alias_and_context_binding(self):
        for change in ['scale','native','host','currency','entity','premise']:
            req=ex.fixture()
            if change=='scale':req['context_adapter']['unit_scale']='1000/1'
            elif change in ['native','host']:req['context_adapter'][change+'_context_sha256']='0'*64
            elif change=='currency':req['opening']['context']['currency']='USD'
            elif change=='entity':req['opening']['context']['entity']='Another Bank'
            else:req['context_adapter']['premise']=' '
            self.result(req,'rejected')

    def test_balanced_wrong_opening_is_not_accepted(self):
        for role in ['cash','gross','allowance']:
            req=ex.fixture();account=req['roles'][role]
            req['opening']['balances'][account]=bridge.fmt(Q(req['opening']['balances'][account])+1)
            req['opening']['balances']['owner.capital']=bridge.fmt(Q(req['opening']['balances']['owner.capital'])-1)
            self.assertEqual(self.result(req,'rejected')['reason'],'native_opening_balance:'+role)

    def test_unrelated_temporary_balance_is_not_hidden(self):
        req=ex.fixture();book=req['opening'];book['accounts']['other.income']={'classification':'income'}
        book['balances']['other.income']='-1/1';book['balances']['owner.capital']=bridge.fmt(Q(book['balances']['owner.capital'])+1)
        self.assertEqual(self.result(req,'rejected')['reason'],'opening_temporary_balance')

    def test_dates_and_event_identity(self):
        req=ex.fixture();req['opening']['period']['end_exclusive']='2027-01-01'
        self.assertEqual(self.result(req,'rejected')['reason'],'native_dates_within_period')
        req=ex.fixture();req['opening']['date']='2025-01-02'
        self.assertEqual(self.result(req,'rejected')['reason'],'opening_date')
        req=ex.fixture();req['opening']['seen']=['credit.partial-early-writeoff.acquisition']
        self.assertEqual(self.result(req,'rejected')['reason'],'duplicate_event_identity')

    def test_order_skip_and_duplicate_journal_rejected(self):
        req=ex.fixture();exact=bridge.linked.calculate(req['linked_request'])
        for change in ['skip','order','duplicate']:
            schedule=deepcopy(exact['schedule'])
            if change=='skip':schedule['journals'].pop(1)
            elif change=='order':schedule['journals'][1:3]=list(reversed(schedule['journals'][1:3]))
            else:schedule['journals'].insert(1,deepcopy(schedule['journals'][0]))
            with self.assertRaises(bridge.algebra.Refusal):bridge.timeline(req['linked_request']['native_request'],schedule)

    def test_unsupported_operations_and_budgets(self):
        for operation in ['post','order','merge_roots']:
            req=ex.fixture();req['operation']=operation
            self.assertEqual(self.result(req,'unsupported')['reason'],'operation_unsupported')
        req=ex.fixture()
        for constant,reason in [('MAX_REQUEST_BYTES','request_budget'),('MAX_RESULT_BYTES','result_budget'),('MAX_JOURNALS','sequence_budget')]:
            with patch.object(bridge,constant,1):self.assertEqual(self.result(req,'unsupported')['reason'],reason)

    def test_dependency_hash_and_extra_fields(self):
        req=ex.fixture()
        with patch.dict(bridge.PINS,{'credit_linked_algebra_v1.py':'0'*64}):
            self.assertEqual(self.result(req,'rejected')['reason'],'dependency_hash:credit_linked_algebra_v1.py')
        req=ex.fixture();req['extra_root']={}
        self.assertEqual(self.result(req,'rejected')['reason'],'credit_linked_book_shape')
        self.result(None,'rejected')
        req=ex.fixture();req['cycle']=req
        self.assertEqual(bridge.propose(req)['status'],'invalid')

if __name__=='__main__':unittest.main()
