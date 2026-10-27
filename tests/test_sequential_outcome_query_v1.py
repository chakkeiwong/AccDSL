"""Whole-family outcomes cannot be inferred from selected witness values."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import sequential_outcome_query_v1 as query
from test_sequential_return_state_family_v1 import fixture as family_fixture,observation
from test_piecewise_method_family_v1 import BUDGET

def fixture(prefix=2,account='inventory',threshold='60/1',operator='eq'):
    family=family_fixture();typ=observation(family,prefix,account,threshold)['type']
    return {'profile':query.PROFILE,'family':family,'prefix':prefix,'type':typ,
            'terms':[{'account':account,'coefficient':'1/1'}],'operator':operator,'threshold':threshold}

def profit(prefix=2):
    d=fixture(prefix,threshold='16/1')
    d['terms']=[{'account':k,'coefficient':'-1/1'} for k in ['revenue','cogs','selling_expense']]
    return d

class SequentialOutcomeQueryTests(unittest.TestCase):
    def answer(self,d,budget=BUDGET):
        r=query.assess(d,budget);self.assertIn(r['status'],['conditional_outcome_query','candidate_outcome_query'],r)
        return r

    def test_terminal_constant_requires_all_regions(self):
        d=fixture();before=deepcopy(d);r=self.answer(d)
        self.assertEqual(r['decision']['conclusion'],'necessary');self.assertEqual(d,before)
        self.assertEqual(r['coverage'],{'total':6,'attempted':6,'decided':6,'unresolved':0,'complete':True})
        self.assertTrue(query.verify_result(d,BUDGET,json.loads(json.dumps(r))))

    def test_intermediate_value_has_witness_and_counterexample(self):
        d=fixture(1,threshold='65/1');r=self.answer(d)
        self.assertEqual(r['decision']['conclusion'],'contingent')
        self.assertEqual(r['decision']['possible'],'yes');self.assertEqual(r['decision']['necessary'],'no')
        for x in r['regions']:
            if x['status']=='feasible':
                self.assertTrue(x['replay']['original_complete_replay']['complete_prefix_states_checked'])

    def test_impossible_outcome_needs_nonempty_family(self):
        r=self.answer(fixture(1,threshold='64/1'))
        self.assertEqual(r['decision']['conclusion'],'impossible');self.assertTrue(r['decision']['counterexample_witness'])

    def test_intermediate_observation_selects_necessary_outcome(self):
        d=fixture(1,threshold='65/1');d['family']['observations']=[observation(d['family'],1,'inventory','65/1')]
        self.assertEqual(self.answer(d)['decision']['conclusion'],'necessary')

    def test_profit_paths_and_cancellation_share_original_state(self):
        self.assertEqual(self.answer(profit())['decision']['conclusion'],'necessary')
        d=profit(1);d['threshold']='-4/1'
        self.assertEqual(self.answer(d)['decision']['conclusion'],'contingent')

    def test_empty_unfunded_family_has_no_necessary_outcome(self):
        d=fixture();s=d['family']['first_family']['state'];cash=Q(s['balances']['cash']);s['balances']['cash']='1/1'
        s['balances']['original_equity']=query.native.monetary.fmt(Q(s['balances']['original_equity'])+cash-1)
        d['family']['sale_event']['proceeds']='1000/1';r=self.answer(d)
        self.assertEqual(r['decision']['conclusion'],'empty_family')
        self.assertEqual(r['decision']['necessary'],'not_applicable_empty_family');self.assertFalse(r['decision']['satisfying_witness'])

    def test_every_comparator_preserves_strictness(self):
        for op,conclusion in [('eq','necessary'),('lt','impossible'),('le','necessary'),('gt','impossible'),('ge','necessary')]:
            self.assertEqual(self.answer(fixture(operator=op))['decision']['conclusion'],conclusion,op)

    def test_open_upper_endpoint_is_impossible(self):
        d=fixture(1,threshold='80/1');dom=d['family']['first_family']['event_domains']['inventory_nrv']['interval']
        dom.update(upper='20/1',upper_inclusive=False)
        self.assertEqual(self.answer(d)['decision']['conclusion'],'impossible')
        dom['upper_inclusive']=True
        self.assertEqual(self.answer(d)['decision']['conclusion'],'contingent')

    def test_known_witness_under_partial_search_is_not_necessity(self):
        r=self.answer(fixture(),{**BUDGET,'max_cells':1})
        self.assertTrue(r['decision']['satisfying_witness']);self.assertEqual(r['decision']['conclusion'],'unknown')
        self.assertEqual(r['decision']['necessary'],'unknown');self.assertEqual(r['coverage']['attempted'],1)

    def test_counterexample_refutes_necessity_before_complete_search(self):
        r=self.answer(fixture(1,threshold='65/1'),{**BUDGET,'max_cells':3})
        self.assertFalse(r['coverage']['complete']);self.assertTrue(r['decision']['counterexample_witness'])
        self.assertEqual(r['decision']['necessary'],'no');self.assertEqual(r['decision']['possible'],'unknown')

    def test_zero_resources_preserve_unknown(self):
        for field in ['max_cells','elapsed_ms','max_integer_assignments','solver_timeout_ms','solver_rlimit','max_formula_nodes']:
            r=self.answer(fixture(),{**BUDGET,field:0})
            self.assertEqual(r['decision']['conclusion'],'unknown',field)

    def test_branch_limit_is_unknown_not_empty(self):
        d=fixture();d['family']['first_family']['branch_limit']=1;r=query.assess(d,BUDGET)
        self.assertEqual(r['status'],'unknown');self.assertFalse(r['branch_partition_complete'])

    def test_missing_premises_remain_unresolved(self):
        d=fixture();d['family']['premise']=None;r=query.assess(d,BUDGET)
        self.assertEqual(r['status'],'unresolved');self.assertFalse(r['formulation_complete'])
        self.assertNotIn('decision',r)

    def test_target_obligation_keeps_answer_candidate_only(self):
        d=fixture();d['family']['obligations']=[{'id':'actual','meaning':'actual opening unknown','affects':['history']}]
        r=self.answer(d);self.assertEqual(r['status'],'candidate_outcome_query')
        self.assertEqual(r['decision']['conclusion'],'necessary');self.assertFalse(r['formulation_complete'])
        self.assertEqual(r['actual_outcome'],'unknown')

    def test_false_and_unknown_native_findings_are_preserved(self):
        for value,status in [(False,'unsupported'),('unknown','unresolved')]:
            d=fixture();d['family']['sale_event']['performance_complete']=value
            self.assertEqual(query.assess(d,BUDGET)['status'],status)

    def test_types_dates_terms_and_threshold_reject(self):
        edits=[lambda d:d.update(prefix=True),lambda d:d.update(prefix=0),lambda d:d.update(operator='ne'),
          lambda d:d['type']['context'].update(at='2025-02-02'),lambda d:d['type'].update(scale='1000/1'),
          lambda d:d['type'].update(dimensions={'units:widget':1}),lambda d:d.update(terms=[]),
          lambda d:d['terms'].append(deepcopy(d['terms'][0])),lambda d:d['terms'][0].update(account='absent'),
          lambda d:d['terms'][0].update(coefficient='1.0'),lambda d:d.update(threshold=1),
          lambda d:d.update(threshold='2/2'),lambda d:d.update(callback='ignored')]
        for edit in edits:
            d=fixture();edit(d);self.assertEqual(query.assess(d,BUDGET)['status'],'invalid',d)

    def test_later_date_uses_original_sale_type(self):
        d=fixture();d['family']['sale_event']['date']='2025-03-01'
        self.assertEqual(query.assess(d,BUDGET)['status'],'invalid')
        d['type']['context']['at']='2025-03-01'
        self.assertEqual(self.answer(d)['decision']['conclusion'],'necessary')

    def test_alternative_witness_and_serialization(self):
        d=fixture();r=self.answer(d);row=next(x for x in r['regions'] if x['status']=='feasible')
        row['witness']['nrv']='25/1'
        row['replay']=query.replay_witness(d,BUDGET,row['branch'],row['region'],row['witness'])
        self.assertTrue(query.verify_result(d,BUDGET,json.loads(json.dumps(r))))

    def test_forged_value_decision_state_and_conflict_reject(self):
        d=fixture();r=self.answer(d)
        for field in ['value','state','decision','conflict']:
            bad=deepcopy(r)
            if field=='decision':bad['decision']['conclusion']='contingent'
            elif field=='conflict':
                x=next(x for x in bad['regions'] if x['status']=='infeasible');x['conflict']['labels']=['sale:proceeds_nonnegative']
            else:
                x=next(x for x in bad['regions'] if x['status']=='feasible')
                if field=='value':x['replay']['value']='61/1'
                else:x['replay']['original_complete_replay']['after']['balances']['cash']='0/1'
            self.assertFalse(query.verify_result(d,BUDGET,bad),field)

    def test_bad_witness_cannot_move_between_predicate_regions(self):
        d=fixture(1,threshold='65/1');r=self.answer(d)
        yes=next(x for x in r['regions'] if x['status']=='feasible' and x['predicate_holds'])
        with self.assertRaises(ValueError):query.replay_witness(d,BUDGET,yes['branch'],1,yes['witness'])

if __name__=='__main__':unittest.main()
