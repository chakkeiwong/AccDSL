"""Exact composition, immutable failures, and declared company isolation."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import company_book_transition_v1 as engine
spec=importlib.util.spec_from_file_location('company_book_examples',ROOT/'data/accounting-master/company-book-transition-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)


class CompanyBookTests(unittest.TestCase):
    def result(self,book,request,status):
        before=deepcopy((book,request));result=engine.propose(book,request)
        self.assertEqual(result['status'],status,result)
        self.assertEqual((book,request),before)
        for flag in engine.FLAGS:self.assertFalse(result[flag])
        if status!='proposed':self.assertNotIn('after',result)
        return result

    def test_two_owners_charts_and_memory_layouts(self):
        for owner,path in [('alpha',['loan']),('beta',['contracts','obligation'])]:
            book,request=ex.fixture(owner);result=self.result(book,request,'proposed')
            cash=book['cash_account'];liability=request['method']['account_map']['liability']
            self.assertEqual(result['after']['balances'][cash],'193/2')
            self.assertEqual(result['after']['balances'][liability],'-53/2')
            memory=result['after']['memory']
            for key in path:memory=memory[key]
            self.assertEqual(memory,{'outstanding':'53/2','paid':'7/2','last_date':'2027-01-02','last_event':'payment.1'})
            self.assertEqual(result['after']['memory']['untouched'],book['memory']['untouched'])
            for key in book['accounts']:
                if key not in [cash,liability]:self.assertEqual(result['after']['balances'][key],book['balances'][key])
            self.assertEqual([f['amount'] for f in result['flows']],['-7/2'])
            self.assertEqual(sum(Q(v) for v in result['journal'].values()),0)
            self.assertEqual(engine.apply(book,request,result)['status'],'applied_provisional')

    def test_repeated_payment_and_full_extinguishment(self):
        book,request=ex.fixture();first=self.result(book,request,'proposed')
        book=first['after'];request['event'].update(id='payment.2',date='2027-01-03')
        request['event']['inputs']['amount']['value']=engine.known('53/2');ex.rehash(book,request)
        second=self.result(book,request,'proposed')['after']
        self.assertEqual(second['balances']['bank.alpha'],'70/1')
        self.assertEqual(second['balances']['note.alpha'],'0/1')
        self.assertEqual(second['memory']['loan']['paid'],'30/1')
        self.assertEqual(second['seen'],['payment.1','payment.2'])
        self.assertEqual(second['flows'][:1],book['flows'])

    def test_unknown_and_false_findings_are_distinct(self):
        for key in ['amount','approved']:
            book,request=ex.fixture();request['event']['inputs'][key]['value']={'status':'unknown','reason':'unobserved'}
            self.result(book,request,'unresolved')
        book,request=ex.fixture();request['event']['inputs']['approved']['value']=engine.known(False)
        self.result(book,request,'unsupported')

    def test_nonpositive_excess_and_cash_shortfall(self):
        for amount in ['0/1','-1/1','31/1']:
            self.result(*ex.fixture(amount=amount),'invalid')
        book,request=ex.fixture();book['balances'].update({'bank.alpha':'1/1','capital.alpha':'19/1'});ex.rehash(book,request)
        self.result(book,request,'invalid')

    def test_foreign_owner_currency_units_and_scales(self):
        for field,value in [('context',{'entity':'foreign'}),('dimensions',{'currency:EUR':1}),
                            ('dimensions',{'goods:unit':1}),('scale','1000/1')]:
            book,request=ex.fixture();request['event']['inputs']['amount']['type'][field]=value
            self.result(book,request,'invalid')
        book,request=ex.fixture();request['method']['context']['entity']='foreign';ex.rehash(book,request)
        self.result(book,request,'invalid')

    def test_account_map_and_cash_role(self):
        for role,target in [('cash','missing'),('liability','bank.alpha'),('cash','machine.alpha')]:
            book,request=ex.fixture();request['method']['account_map'][role]=target;ex.rehash(book,request)
            self.result(book,request,'invalid')

    def test_schema_registry_and_digest_pins(self):
        book,request=ex.fixture();request['schemas'][book['memory_schema']]['required'].pop()
        self.result(book,request,'invalid')
        book,request=ex.fixture();request['schemas'].pop(book['memory_schema'])
        self.result(book,request,'invalid')

    def test_memory_money_to_quantity_is_rejected_statically(self):
        book,request=ex.fixture();request['method']['memory']['definition']['operations'][0]['path']=['untouched','quantity']
        request['event']['inputs']['approved']['value']=engine.known(False);ex.rehash(book,request)
        result=self.result(book,request,'invalid');self.assertEqual(result['reason'],'memory_write_type_mismatch')

    def test_memory_write_escape_container_and_dynamic_paths(self):
        for path in [['balances','bank.alpha'],['loan'],['loan',{'input_pointer':'/event_id'}]]:
            book,request=ex.fixture();request['method']['memory']['definition']['operations'][0]['path']=path;ex.rehash(book,request)
            self.result(book,request,'invalid')
        book,request=ex.fixture();request['method']['memory']['definition']['operations'][0]['op']='insert';ex.rehash(book,request)
        self.result(book,request,'invalid')

    def test_memory_types_cover_exact_leaf_population(self):
        for action in ['missing','extra']:
            book,request=ex.fixture()
            if action=='missing':book['memory_types'].pop('/loan/paid')
            else:book['memory_types']['/missing']=engine.money_type(book)
            ex.rehash(book,request);self.result(book,request,'invalid')

    def test_postcondition_failure_returns_no_applied_state(self):
        book,request=ex.fixture();request['method']['memory']['definition']['operations'][0]['value']={'kind':'literal','value':'29/1'}
        ex.rehash(book,request);result=self.result(book,request,'invalid')
        self.assertEqual(result['reason'],'postconditions')
        self.assertNotIn('after',engine.apply(book,request,result))

    def test_stale_state_method_and_nested_identity(self):
        book,request=ex.fixture();book['date']='2027-01-02';self.result(book,request,'invalid')
        book,request=ex.fixture();request['method']['version']='2';self.result(book,request,'invalid')
        for part in ['preconditions','postconditions','monetary']:
            book,request=ex.fixture();key='definition' if part=='monetary' else 'manifest'
            request['method'][part][key]['method_id']='different';ex.rehash(book,request)
            self.assertEqual(self.result(book,request,'invalid')['reason'],'nested_method_identity')

    def test_rehashed_proposal_and_request_tampering(self):
        for key in ['after','journal','flows','memory']:
            book,request=ex.fixture();proposal=self.result(book,request,'proposed')
            if key=='after':proposal['after']['memory']['untouched']['tag']='changed';proposal['after_sha256']=engine.digest(proposal['after'])
            elif key=='journal':proposal[key]['bank.alpha']='-1/1'
            elif key=='flows':proposal[key][0]['amount']='-1/1'
            else:proposal[key]['after']['loan']['paid']='999/1'
            self.assertEqual(engine.apply(book,request,proposal)['status'],'invalid')
        book,request=ex.fixture();proposal=self.result(book,request,'proposed');request['event']['inputs']['amount']['value']=engine.known('2/1')
        self.assertEqual(engine.apply(book,request,proposal)['status'],'invalid')

    def test_event_chronology_and_duplicates(self):
        for day in ['2026-12-31','2028-01-01','2027-02-30']:
            book,request=ex.fixture();request['event']['date']=day;self.result(book,request,'invalid')
        book,request=ex.fixture();book['seen']=['payment.1'];ex.rehash(book,request);self.result(book,request,'invalid')

    def test_balanced_book_and_existing_flow_integrity(self):
        book,request=ex.fixture();book['balances']['bank.alpha']='99/1';ex.rehash(book,request);self.result(book,request,'invalid')
        book,request=ex.fixture();book=self.result(book,request,'proposed')['after']
        request['event']['id']='next';book['flows'][0]['currency']='EUR';ex.rehash(book,request);self.result(book,request,'invalid')

    def test_unbalanced_postings_and_gross_cash_refused(self):
        for key in ['postings','flows']:
            book,request=ex.fixture();request['method']['monetary']['definition'][key].pop();ex.rehash(book,request)
            self.result(book,request,'invalid')

    def test_noncanonical_and_oversized_values(self):
        for amount in [True,1,'1','2/2','1/0',str(2**4096)+'/1']:
            self.result(*ex.fixture(amount=amount),'invalid')
        book,request=ex.fixture();request['event']['inputs']['amount']['provenance']='x'*4097;self.result(book,request,'invalid')
        book,request=ex.fixture();request['method']['id']='x'*1_000_001;ex.rehash(book,request);self.result(book,request,'invalid')

    def test_all_false_guards_are_vacuous_not_no_action(self):
        book,request=ex.fixture()
        for row in request['method']['preconditions']['manifest']['requirements']:row['guard']['value']=False
        ex.rehash(book,request);result=self.result(book,request,'proposed')
        self.assertEqual(result['preconditions']['status'],'no_active_requirements')
        self.assertEqual(result['journal']['bank.alpha'],'-7/2')

    def test_static_memory_input_schema_mismatch(self):
        book,request=ex.fixture();part=request['method']['memory'];old=part['definition']['input_schema']
        shape=deepcopy(request['schemas'][old]);shape['properties']['remaining']=ex.scalar('text')
        h=engine.digest(shape);request['schemas'][h]=shape;part['definition']['input_schema']=h;ex.rehash(book,request)
        self.assertEqual(self.result(book,request,'invalid')['reason'],'memory_input_scalar_kind')

    def test_memory_overlap_and_unknown_binding(self):
        book,request=ex.fixture();operations=request['method']['memory']['definition']['operations'];duplicate=deepcopy(operations[0]);duplicate['id']='duplicate';operations.append(duplicate);ex.rehash(book,request)
        self.result(book,request,'invalid')
        book,request=ex.fixture();request['method']['monetary']['bindings']['amount']=ex.event('missing');ex.rehash(book,request);self.result(book,request,'invalid')

    def test_json_type_substitution_cannot_pass_replay(self):
        book,request=ex.fixture();proposal=self.result(book,request,'proposed');proposal['committed']=0
        self.assertEqual(engine.apply(book,request,proposal)['status'],'invalid')

    def test_transitive_native_comparisons(self):
        spec=importlib.util.spec_from_file_location('book_native_tests',ROOT/'data/accounting-master/company-book-transition-20261025/native_comparisons.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        rows=module.comparisons();self.assertEqual(len(rows),5)
        for row in rows:
            for name,passed in row['checks'].items():self.assertTrue(passed,(row['case'],name))

    def test_dependency_hash_refusal(self):
        from unittest.mock import patch
        book,request=ex.fixture()
        with patch.dict(engine.PINS,{'method_requirements_v1.py':'0'*64}):
            self.assertTrue(self.result(book,request,'invalid')['reason'].startswith('dependency_hash:'))

    def test_memory_resource_boundaries(self):
        book,request=ex.fixture()
        for i in range(253):book['accounts']['extra.'+str(i)]={'classification':'asset'};book['balances']['extra.'+str(i)]='0/1'
        ex.rehash(book,request);self.assertEqual(self.result(book,request,'invalid')['reason'],'account_limit')
        book,request=ex.fixture();node={'kind':'literal','value':'0/1'}
        for i in range(49):node={'kind':'object','fields':{'child':node}}
        request['method']['memory']['definition']['operations'][0]['value']=node;ex.rehash(book,request)
        self.result(book,request,'invalid')


if __name__=='__main__':unittest.main()
