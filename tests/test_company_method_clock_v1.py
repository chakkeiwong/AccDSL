from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import company_method_clock_v1 as binder
spec=importlib.util.spec_from_file_location('company_clock_examples',ROOT/'data/accounting-master/company-method-clock-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)


class CompanyClockTests(unittest.TestCase):
    def result(self,book,call,status):
        before=deepcopy((book,call));result=binder.propose(book,call)
        self.assertEqual(result['status'],status,result);self.assertEqual((book,call),before)
        for flag in binder.FLAGS:self.assertFalse(result[flag])
        return result

    def test_two_owner_payment_requests_and_complete_results(self):
        for owner in ['alpha','beta']:
            book,call,request=ex.payment(owner);result=self.result(book,call,'proposed')
            self.assertEqual(result['materialized_request'],request)
            self.assertEqual(result['transition'],binder.transition.propose(book,request))
            self.assertEqual(binder.apply(book,call,result)['transition'],binder.transition.apply(book,request,result['transition']))

    def test_sale_date_is_actual_event_metadata(self):
        book,call,expected=ex.sale();result=self.result(book,call,'proposed')
        self.assertEqual(result['materialized_request'],expected)
        self.assertEqual(result['transition'],binder.transition.propose(book,expected))
        call['event']['date']='2025-10-01';result=self.result(book,call,'proposed')
        self.assertEqual(result['materialized_request']['event']['inputs']['event_date']['value']['value'],'2025-10-01')

    def test_duplicate_date_input_refused(self):
        book,call,expected=ex.sale();call['event']['inputs']['event_date']=expected['event']['inputs']['event_date']
        self.assertEqual(self.result(book,call,'invalid')['reason'],'supplied_input_population')

    def test_closed_period_cannot_be_bypassed_by_supplied_date(self):
        book,call,expected=ex.sale();book['date']='2025-06-01'
        # Keep every historical flow within the new diagnostic starting date.
        book['flows']=[];call['event']['date']='2025-06-15';ex.rehash(book,call)
        result=self.result(book,call,'invalid');self.assertEqual(result['transition']['reason'],'preconditions')
        self.assertNotIn('after',result['transition'])

    def test_current_state_is_rebound_between_calls(self):
        book,call,_=ex.payment();first=self.result(book,call,'proposed')
        book=first['transition']['after'];call['event'].update(id='second',date='2027-01-03');ex.rehash(book,call)
        second=self.result(book,call,'proposed')
        self.assertEqual(second['transition']['after']['balances']['bank.alpha'],'93/1')
        self.assertEqual(second['transition']['after']['memory']['loan']['paid'],'7/1')

    def test_unknown_false_and_invalid_fact_status_preserved(self):
        for value,status in [({'status':'unknown','reason':'not observed'},'unresolved'),
                             ({'status':'known','value':False},'unsupported'),
                             ({'status':'known','value':0},'invalid')]:
            book,call,_=ex.payment();call['event']['inputs']['approved']['value']=value
            self.result(book,call,status)

    def test_account_role_classification_checked(self):
        book,call,_=ex.payment();call['registry']['entries']['pay']['account_classes']['liability']='asset';ex.rehash(book,call)
        self.assertEqual(self.result(book,call,'invalid')['reason'],'role_class_mismatch')

    def test_unknown_method_and_unsupported_clock(self):
        book,call,_=ex.payment();call['method_key']='other';self.result(book,call,'unsupported')
        for kind in ['assessment_interval','period_carry','measurement_date']:
            book,call,_=ex.payment();call['registry']['entries']['pay']['clock']['kind']=kind;ex.rehash(book,call)
            self.assertEqual(self.result(book,call,'unsupported')['reason'],'clock_family:'+kind)

    def test_registry_and_method_hash_binding(self):
        book,call,_=ex.payment();call['registry']['entries']['pay']['clock']['kind']='changed';self.result(book,call,'invalid')
        book,call,_=ex.payment();call['registry']['entries']['pay']['method']['version']='changed'
        call['expected_registry_sha256']=binder.digest(call['registry']);self.result(book,call,'invalid')

    def test_stale_state_context_and_metadata_type(self):
        book,call,_=ex.payment();book['date']='2027-01-02';self.result(book,call,'invalid')
        book,call,_=ex.payment();call['registry']['context']['entity']='other';ex.rehash(book,call);self.result(book,call,'invalid')
        book,call,_=ex.sale();call['registry']['entries']['sell']['metadata_bindings']['event_date']='id';ex.rehash(book,call)
        self.assertEqual(self.result(book,call,'invalid')['reason'],'metadata_type')

    def test_all_registry_entries_validated_before_execution(self):
        book,call,_=ex.payment();entry=deepcopy(call['registry']['entries']['pay']);entry['method']['memory']['definition']['operations'][0]['path']=['balances','cash']
        call['registry']['entries']['unused']=entry;ex.rehash(book,call)
        self.assertEqual(self.result(book,call,'invalid')['reason'],'memory_write_scope')

    def test_supplied_input_population_and_types(self):
        for kind in ['missing','extra','wrong_type']:
            book,call,_=ex.payment()
            if kind=='missing':call['event']['inputs'].pop('approved')
            elif kind=='extra':call['event']['inputs']['extra']=deepcopy(call['event']['inputs']['amount'])
            else:call['event']['inputs']['amount']['type']['scale']='1000/1'
            self.result(book,call,'invalid')

    def test_metadata_population_overlap(self):
        book,call,_=ex.sale();entry=call['registry']['entries']['sell'];entry['event_inputs']['event_date']={'kind':'date','context':{}};ex.rehash(book,call)
        self.assertEqual(self.result(book,call,'invalid')['reason'],'metadata_input_overlap')

    def test_canonical_replay_tampering(self):
        for kind in ['flag','method_key','amount']:
            book,call,_=ex.payment();result=self.result(book,call,'proposed')
            if kind=='flag':result['committed']=0
            elif kind=='method_key':result['method_key']='other'
            else:result['transition']['after']['balances']['bank.alpha']='999/1'
            self.assertEqual(binder.apply(book,call,result)['status'],'invalid')

    def test_entry_count_resource_bound(self):
        book,call,_=ex.payment();entry=call['registry']['entries']['pay']
        call['registry']['entries']={str(i):deepcopy(entry) for i in range(33)};ex.rehash(book,call)
        # Global structure budget may veto before the explicit entry bound.
        self.result(book,call,'invalid')

    def test_no_executable_callback_fields(self):
        book,call,_=ex.payment();call['registry']['entries']['pay']['callback']='arbitrary';ex.rehash(book,call)
        self.result(book,call,'invalid')

    def test_event_identity_binding_and_type_conflict(self):
        book,call,_=ex.payment();entry=call['registry']['entries']['pay'];part=entry['method']['preconditions'];m=part['manifest']
        typ={'kind':'text','context':{}}
        m['inputs']['actual_id']=ex.book_examples.decl(typ,'actual_id')
        m['requirements'].append({'id':'id_is_present','guard':ex.book_examples.const(binder.core.BOOL,True),
            'guard_requires':[],'predicate':ex.book_examples.binary('eq',ex.book_examples.ref('actual_id'),ex.book_examples.const(typ,'payment.1')),
            'requires':['actual_id'],'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'})
        part['bindings']['actual_id']={'kind':'event','name':'actual_id'};entry['metadata_bindings']['actual_id']='id';ex.rehash(book,call)
        result=self.result(book,call,'proposed')
        self.assertEqual(result['materialized_request']['event']['inputs']['actual_id']['value']['value'],'payment.1')
        call['event']['id']='changed';result=self.result(book,call,'invalid')
        self.assertEqual(result['transition']['reason'],'preconditions')

    def test_dependency_integrity_and_missing_schema(self):
        from unittest.mock import patch
        book,call,_=ex.payment()
        with patch.object(binder,'TRANSITION_SHA256','0'*64):
            self.assertEqual(self.result(book,call,'invalid')['reason'],'transition_dependency_hash')
        book,call,_=ex.payment();call['registry']['entries']['pay']['schemas']={};ex.rehash(book,call)
        self.result(book,call,'invalid')


if __name__=='__main__':unittest.main()
