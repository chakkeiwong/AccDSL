from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import compatible_book_composition_v1 as c
spec=importlib.util.spec_from_file_location('composition_examples',ROOT/'data/accounting-master/compatible-book-composition-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)

class CompatibleCompositionTests(unittest.TestCase):
    def checked(self,body,reason=None):
        before=deepcopy(body);r=c.compose(body);self.assertEqual(body,before)
        self.assertEqual(r['status'],'invalid' if reason else 'worksheet_composed',r)
        if reason:self.assertEqual(r['reason'],reason)
        for flag in c.FLAGS:self.assertIs(r[flag],False)
        return r

    def test_exact_two_charts_and_original_books(self):
        cases=ex.cases();self.assertEqual(len(cases),2)
        for row in cases.values():
            self.assertEqual(row['result']['books'],row['request']['books'])
            self.assertEqual(row['result']['world'],row['request']['world'])
            self.assertEqual(row['result']['adjusted_balances'],ex.EXPECTED_ADJUSTED)

    def test_no_eliminations_returns_unadjusted_worksheet(self):
        body=ex.fixture();body['eliminations']=[];r=self.checked(body)
        self.assertEqual(r['raw_balances'],r['adjusted_balances']);self.assertFalse(r['consolidation_complete'])

    def test_stale_books_and_elimination_amounts(self):
        body=ex.fixture();body['books']['P']['memory']['origin']='S-state'
        self.checked(body,'book_state_binding')
        body=ex.fixture();body['eliminations'][0]['positive']['expected_balance']='10/1'
        self.checked(body,'stale_elimination_balance')

    def test_context_and_period_mismatches(self):
        for field in ['case_id','date','period']:
            body=ex.fixture();book=body['books']['S']
            if field=='case_id':book['context']['case_id']='other'
            elif field=='date':book['date']='2025-12-30'
            else:book['period']['start']='2025-02-01'
            ex.rehash(body);self.checked(body,'book_case_binding' if field=='case_id' else 'book_time_compatibility')

    def test_map_must_be_complete_and_preserve_classification(self):
        body=ex.fixture();del body['account_maps']['P']['P.cash'];self.checked(body,'complete_account_map')
        body=ex.fixture();body['account_maps']['P']['P.cash']='capital';self.checked(body,'account_classification_compatibility')
        body=ex.fixture();body['chart']['unused']={'classification':'asset'};self.checked(body,'unused_common_accounts')

    def test_unresolved_world_or_component_refuses(self):
        body=ex.fixture();body['world']['obligations']=[{'id':'unresolved','meaning':'Unknown policy','affects':['composition']}]
        self.checked(body,'unresolved_world_obligations')
        body=ex.fixture();body['world']['components']['P']['obligation_ids']=['missing']
        self.checked(body,'unknown_component_obligation')

    def test_control_and_ownership_are_supplied_not_inferred(self):
        body=ex.fixture();body['world']['control_edges'][0]['ownership_fraction']='4/5';self.checked(body,'full_ownership_only')
        body=ex.fixture();body['world']['control_edges'][0]['end_exclusive']='2025-12-31';self.checked(body,'control_at_snapshot')
        body=ex.fixture();body['compatibility']['full_ownership_premise']='different';self.checked(body,'supplied_control_premise')

    def test_duplicate_eliminations_and_reused_source_accounts(self):
        body=ex.fixture();body['eliminations'].append(deepcopy(body['eliminations'][0]));self.checked(body,'duplicate_elimination_id')
        body=ex.fixture();row=deepcopy(body['eliminations'][0]);row['id']='again';body['eliminations'].append(row)
        self.checked(body,'reused_elimination_account')

    def test_unmatched_full_balances_are_not_plugged(self):
        body=ex.fixture();body['books']['S']['balances'].update({'S.payable':'-19/1','S.cash':'69/1'})
        body['eliminations'][0]['negative']['expected_balance']='-19/1';ex.rehash(body)
        self.checked(body,'opposite_full_balances_required')

    def test_cash_and_wrong_role_eliminations_refuse(self):
        body=ex.fixture();body['eliminations'][1]['kind']='receivable_payable';self.checked(body,'elimination_classification')
        body=ex.fixture();body['books']['P']['balances'].update({'P.cash':'20/1','P.receivable':'80/1'});ex.rehash(body)
        body['eliminations']=body['eliminations'][:1]
        body['eliminations'][0]['positive'].update(account='P.cash',expected_balance='20/1')
        self.checked(body,'cash_elimination_unsupported')

    def test_wrong_control_direction_refuses_investment_pair(self):
        body=ex.fixture();body['world']['control_edges'][0].update(parent='S',child='P')
        self.checked(body,'investment_control_direction')

    def test_unsupported_sector_and_schema_bytes_refuse(self):
        body=ex.fixture();body['world']['books']['S']['sector']='bank'
        body['world']['components']['S'].update(sector='bank',profile='BankAssessment/1')
        self.checked(body,'corporate_books_only')
        body=ex.fixture();next(iter(body['schemas'].values()))['required']=[];self.checked(body,'schema_digest')

    def test_replay_rejects_changed_flags_books_and_balances(self):
        body=ex.fixture();r=self.checked(body);self.assertTrue(c.verify(body,r))
        for key,value in [('adjusted_balances',{}),('books',{}),('consolidation_complete',True),('executed',0)]:
            changed=deepcopy(r);changed[key]=value;self.assertFalse(c.verify(body,changed))

    def test_resource_and_dependency_refusals(self):
        body=ex.fixture();body['compatibility']['measurement_basis']='x'*4097;self.checked(body,'text:compatibility_measurement_basis')
        with patch.dict(c.PINS,{'company_book_transition_v1.py':'0'*64}):self.checked(ex.fixture(),'dependency_hash:company_book_transition_v1.py')
        body=ex.fixture();body['eliminations'].append(body)
        self.assertEqual(c.compose(body)['reason'],'record_structure_limit')

    def test_same_book_zero_and_unknown_pairs_refuse(self):
        body=ex.fixture();body['books']['P']['balances'].update({'P.capital':'-20/1','P.cash':'-100/1'});ex.rehash(body)
        body['eliminations']=body['eliminations'][:1]
        body['eliminations'][0]['negative'].update(owner='P',account='P.capital',expected_balance='-20/1')
        self.checked(body,'cross_book_elimination_required')
        body=ex.fixture()
        body['books']['P']['balances'].update({'P.receivable':'0/1','P.cash':'100/1'})
        body['books']['S']['balances'].update({'S.payable':'0/1','S.cash':'50/1'})
        for side in ['positive','negative']:body['eliminations'][0][side]['expected_balance']='0/1'
        ex.rehash(body);self.checked(body,'opposite_full_balances_required')
        body=ex.fixture();body['eliminations'][0]['kind']='intragroup_profit';self.checked(body,'elimination_kind')

    def test_currency_identity_and_unbalanced_books_refuse(self):
        body=ex.fixture();body['books']['S']['context']['currency']='EUR';ex.rehash(body)
        self.checked(body,'book_identity_binding')
        body=ex.fixture();body['books']['S']['balances']['S.cash']='71/1';ex.rehash(body)
        self.checked(body,'book_unbalanced')
        body=ex.fixture();body['books']['S']['context']['book']='other';ex.rehash(body)
        self.checked(body,'book_identity_binding')

if __name__=='__main__':unittest.main()
