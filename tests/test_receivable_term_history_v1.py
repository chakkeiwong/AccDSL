from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import receivable_term_history_v1 as terms
spec=importlib.util.spec_from_file_location('term_history_examples',ROOT/'data/accounting-master/receivable-term-history-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)

class ReceivableTermHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.migration,cls.body,cls.roles=ex.migration_fixture();cls.migrated=terms.migrate(cls.migration)
        assert cls.migrated['status']=='migrated_provisional',cls.migrated
        cls.base=cls.migrated['state']
    def state(self):return deepcopy(self.base)
    def checked(self,state,request,status='proposed',reason=None):
        before=deepcopy(state);r=terms.step(state,request);self.assertEqual(state,before);self.assertEqual(r['status'],status,r)
        if reason:self.assertEqual(r['reason'],reason)
        for key in terms.FLAGS:self.assertIs(r[key],False)
        return r
    def test_two_charts_full_history_receipts_and_carry(self):
        cases=ex.cases();self.assertEqual(len(cases),2)
        for row in cases.values():
            claim=row['final']['book']['memory']['claims']['invoice/a~1']
            self.assertEqual(claim['assessments']['imported']['overdue'],'20/1')
            self.assertEqual(claim['assessments']['assess.mar']['overdue'],'0/1')
            self.assertEqual(claim['assessments']['assess.next']['remaining'],'0/1')
    def test_migration_preserves_original_scalar_state(self):
        old=self.migration['book'];new=self.base['book'];self.assertEqual(self.migrated['source_book'],old)
        for key in ['balances','flows','seen','context','date','period']:self.assertEqual(new[key],old[key])
        for key,value in old['memory']['claims']['invoice/a~1'].items():self.assertEqual(new['memory']['claims']['invoice/a~1'][key],value)
        self.assertEqual(new['memory']['claims']['invoice/a~1']['assessments']['imported']['event_id'],'unknown')
    def test_stale_migration_and_missing_premise(self):
        request=deepcopy(self.migration);request['expected_book_sha256']='0'*64
        self.assertEqual(terms.migrate(request)['reason'],'stale_migration_book')
        request=deepcopy(self.migration);request['premise']='';self.assertEqual(terms.migrate(request)['status'],'invalid')
    def test_stale_state_term_unknown_claim_and_customer(self):
        for field,value,reason in [('prior_term','absent','stale_current_term'),('claim_id','missing','unknown_claim'),('customer','Other','claim_customer_mismatch')]:
            state=self.state();request=ex.amend(state);request['event']['inputs'][field]['value']['value']=value
            self.checked(state,request,'invalid',reason)
        state=self.state();request=ex.amend(state);request['expected_state_sha256']='0'*64;self.checked(state,request,'invalid','stale_term_state')
    def test_unknown_and_false_approval_do_not_mutate(self):
        state=self.state();request=ex.amend(state);request['event']['inputs']['approved']['value']={'status':'unknown','reason':'Not selected'}
        self.checked(state,request,'unresolved')
        request=ex.amend(state);request['event']['inputs']['approved']['value']['value']=False
        self.checked(state,request,'unsupported','applicability_not_selected')
    def test_backdate_sealed_day_due_and_duplicate_event(self):
        state=self.state();request=ex.amend(state,day='2027-02-27');self.checked(state,request,'invalid','event_chronology')
        request=ex.amend(state,day='2027-02-28');self.checked(state,request,'invalid','assessment_day_sealed')
        request=ex.amend(state,due='2027-03-09');self.checked(state,request,'invalid','due_before_effective')
        request=ex.amend(state,identity=state['book']['seen'][0]);self.checked(state,request,'invalid','duplicate_event')
    def test_same_day_order_and_second_term_ambiguity(self):
        state=self.state();state=self.checked(state,ex.amend(state,day='2027-03-31'))['after']
        request=ex.amend(state,'same.day','2027-03-31','another','2027-05-31');self.checked(state,request,'invalid','ambiguous_term_effective_date')
        assessment=ex.event(state,'assess','assess.same','2027-03-31',start='2027-03-01',end_exclusive='2027-04-01')
        after=self.checked(state,assessment)['after'];self.assertEqual(after['book']['memory']['claims']['invoice/a~1']['overdue'],'0/1')
        self.checked(after,ex.amend(after,'late.same','2027-03-31','later','2027-05-31'),'invalid','assessment_day_sealed')
    def test_duplicate_term_principal_change_and_extra_inputs(self):
        state=self.state();self.checked(state,ex.amend(state,term_id='initial'),'invalid','duplicate_term_id')
        request=ex.amend(state);request['event']['inputs']['principal']=deepcopy(request['event']['inputs']['due'])
        self.checked(state,request,'invalid','exact_event_inputs')
    def test_historical_term_basis_cannot_be_relabelled(self):
        state=self.state();after=self.checked(state,ex.amend(state))['after']
        claim=after['book']['memory']['claims']['invoice/a~1'];claim['assessments']['imported']['term_id']='extension1'
        with self.assertRaisesRegex(Exception,'assessment_term_basis'):terms.validate(after)
        after=self.checked(state,ex.amend(state))['after'];claim=after['book']['memory']['claims']['invoice/a~1'];claim['overdue']='0/1'
        with self.assertRaisesRegex(Exception,'assessment_summary'):terms.validate(after)
    def test_receipt_overpayment_and_schema_drift_refuse(self):
        state=self.state();request=ex.event(state,'collect','too.much','2027-03-10',claim_id='invoice/a~1',customer='Customer A',amount='21/1')
        self.checked(state,request,'invalid','typed_transition:preconditions')
        state=self.state();state['memory_definition']['root']['fields']['claims']['values']['fields']['terms']['max_items']=1
        with self.assertRaisesRegex(Exception,'term_claim_type'):terms.validate(state)
    def test_replay_rejects_changed_history_and_flags(self):
        state=self.state();request=ex.amend(state);r=self.checked(state,request);self.assertTrue(terms.verify(state,request,r))
        for key,value in [('after',{}),('term_history_complete',True),('executed',0)]:
            altered=deepcopy(r);altered[key]=value;self.assertFalse(terms.verify(state,request,altered))
    def test_structure_and_dependency_limits(self):
        from unittest.mock import patch
        state=self.state();request=ex.amend(state);request['event']['inputs']['cycle']=request
        self.assertEqual(terms.step(state,request)['reason'],'record_structure_limit')
        with patch.dict(terms.PINS,{'declared_receivable_lifecycle_v1.py':'0'*64}):
            self.assertEqual(terms.migrate(self.migration)['reason'],'term_dependency:declared_receivable_lifecycle_v1.py')

    def test_postcondition_checks_actual_written_date(self):
        from unittest.mock import patch
        original=terms.state_request
        def altered(state,event,operations):
            request=original(state,event,operations)
            predicate=request['method']['postconditions']['manifest']['requirements'][0]['predicate']
            predicate['right']['value']='2099-01-01'
            request['expected_method_sha256']=terms.core.digest(request['method'])
            return request
        state=self.state()
        with patch.object(terms,'state_request',side_effect=altered):
            self.checked(state,ex.amend(state),'invalid','typed_transition:postconditions')

    def test_empty_premise_missing_history_and_unassessed_migration(self):
        state=self.state();request=ex.amend(state);request['event']['inputs']['premise']['value']['value']=''
        self.checked(state,request,'invalid','text:text')
        state=self.state();state['book']['memory']['claims']['invoice/a~1']['terms']['initial']['predecessor']='missing'
        with self.assertRaisesRegex(Exception,'term_chain'):terms.validate(state)
        body,_,_=ex.legacy.lifecycle_fixture();body['commands']=body['commands'][:2]
        result=terms.life.run(body);request=deepcopy(self.migration);request['book']=result['current'];request['expected_book_sha256']=terms.core.digest(request['book'])
        migrated=terms.migrate(request);self.assertEqual(migrated['status'],'migrated_provisional',migrated)
        claim=migrated['state']['book']['memory']['claims']['invoice/a~1']
        self.assertFalse(claim['assessed']);self.assertEqual(claim['assessments'],{});self.assertEqual(claim['latest_assessment'],'none')

if __name__=='__main__':unittest.main()
