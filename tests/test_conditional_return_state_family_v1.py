"""Conditional event quantities must respect complete native next-state checks."""
from copy import deepcopy
from pathlib import Path
from fractions import Fraction as Q
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import conditional_return_state_family_v1 as family
from test_typed_return_transition_v1 import fixtures,raw_args
from test_conditional_history_family_v1 import domain
from test_joint_measurement_constraints_v1 import premise
from test_piecewise_method_family_v1 import BUDGET


def fixture(kind='settle',variable=True):
    _,s,e=next(x for x in fixtures.selected_cases() if x[2]['kind']==kind)
    s,e=deepcopy(s),deepcopy(e);domains={}
    if variable:
        fields={'actual_units':('0/1','12/1'),'inventory_nrv':('5/1','30/1')} if kind=='settle' else {'proceeds':('0/1','100/1')}
        for field in fields:e[field]='unknown'
        for field,(lo,hi) in fields.items():
            domains[field]=domain(lo,hi);domains[field]['source_ref']=family.source_ref(family.core.digest(e),'/'+field)
    return {'profile':family.PROFILE,'state':s,'event':e,'event_domains':domains,
            'premise':premise('conditional_native_state'),'obligations':[],'branch_limit':16}


def refresh_sources(d):
    for field,item in d['event_domains'].items():item['source_ref']=family.source_ref(family.core.digest(d['event']),'/'+field)


class ConditionalReturnStateFamilyTests(unittest.TestCase):
    def test_known_settlement_and_sale_match_complete_originals(self):
        for kind in ['settle','sell']:
            d=fixture(kind,False);before=deepcopy(d);r=family.assess(d,BUDGET)
            self.assertEqual(r['status'],'conditional_state_family_witness',r)
            b=next(x for x in r['branches'] if x['status']=='feasible')
            p=family.native.propose(*raw_args(d['state'],d['event']))['proposal']
            self.assertEqual(b['replay']['after'],p['after']);self.assertEqual(d,before)
            self.assertTrue(b['replay']['both_original_transitions_checked']);self.assertFalse(r['executed'])
            self.assertTrue(family.verify_result(d,BUDGET,r))

    def test_unknown_quantity_and_recoverable_value_preserve_next_states(self):
        d=fixture();r=family.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_state_family_witness',r)
        self.assertEqual(r['coverage']['feasible'],2)
        carrying=set()
        for b in r['branches']:
            self.assertEqual(b['witness']['n'],'2/1')
            replay=b['replay'];carrying.add(replay['after']['lots'][d['event']['lot_id']]['carrying'])
            self.assertTrue(replay['after']['component']['settled'])
            self.assertEqual(replay['after']['component']['refund'],'0/1')
        self.assertEqual(len(carrying),2);self.assertEqual(d['event']['actual_units'],'unknown')

    def test_low_cash_empty_family_without_balancing_financing(self):
        d=fixture();s=d['state'];cash=Q(s['balances']['cash'])
        s['balances']['cash']='1/1';s['balances']['original_equity']=family.native.monetary.fmt(Q(s['balances']['original_equity'])+cash-1)
        joined,_=family.prepare(d,BUDGET)
        self.assertEqual(family.parent.assess(joined,BUDGET)['status'],'conditional_family_witness')
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible',r)
        self.assertTrue(family.verify_result(d,BUDGET,r))
        self.assertTrue(any('native:closing_cash_nonnegative' in b['conflict']['labels'] for b in r['branches']))

    def test_zero_quantity_excluded_despite_consistent_cash(self):
        d=fixture(variable=False);d['event'].update(actual_units='0/1',refund_cash='0/1',handling_cash='0/1')
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible',r)

    def test_lot_order_duplicate_event_and_disposed_lot(self):
        d=fixture('sell',False);settle=fixture(variable=False)
        d['state']=deepcopy(settle['state']);d['event']['date']=settle['event']['date']
        self.assertEqual(family.assess(d,BUDGET)['reason'],'unknown_lot')
        after=family.native.propose(*raw_args(settle['state'],settle['event']))['proposal']['after']
        d['state']=after;self.assertEqual(family.assess(d,BUDGET)['status'],'conditional_state_family_witness')
        settle['state']=after;self.assertEqual(family.assess(settle,BUDGET)['reason'],'duplicate_event')
        sold=family.native.propose(*raw_args(d['state'],d['event']))['proposal']['after']
        d['state']=sold;d['event']['id']='new-sale'
        self.assertEqual(family.assess(d,BUDGET)['reason'],'lot_already_disposed')

    def test_unknown_rights_and_unknown_state_are_not_filled(self):
        d=fixture();d['event']['all_rights_closed']='unknown';refresh_sources(d)
        self.assertEqual(family.assess(d,BUDGET)['status'],'unresolved')
        d=fixture();d['state']['component']['unit_cost']='unknown'
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'unresolved',r)
        self.assertNotIn('branches',r)

    def test_false_external_findings_and_wrong_identity_retain_status(self):
        d=fixture();d['event']['all_rights_closed']=False;refresh_sources(d)
        self.assertEqual(family.assess(d,BUDGET)['status'],'unsupported')
        d=fixture();d['event']['component_id']='another-component';refresh_sources(d)
        self.assertEqual(family.assess(d,BUDGET)['status'],'invalid')

    def test_domains_cannot_replace_known_facts_or_structural_fields(self):
        d=fixture(variable=False);d['event_domains']['actual_units']=domain('0/1','12/1');refresh_sources(d)
        self.assertEqual(family.assess(d,BUDGET)['reason'],'domain_cannot_replace_known_fact')
        d=fixture();d['event_domains']['refund_cash']=domain('0/1','100/1');refresh_sources(d)
        self.assertEqual(family.assess(d,BUDGET)['reason'],'event_domain_allowlist')
        d=fixture();d['event_domains']['actual_units']['source_ref']='guessed'
        self.assertEqual(family.assess(d,BUDGET)['reason'],'event_domain_source_mismatch')

    def test_missing_premise_and_unknown_cash_prevent_solving(self):
        for mutate in [lambda d:d.update(premise=None),
                       lambda d:d['event_domains']['actual_units'].update(premise=None),
                       lambda d:d['event'].update(refund_cash='unknown')]:
            d=fixture();mutate(d);refresh_sources(d);r=family.assess(d,BUDGET)
            self.assertEqual(r['status'],'unresolved',r);self.assertNotIn('branches',r)

    def test_non_affine_unknown_inputs_remain_unsupported(self):
        d=fixture();d['event']['unit_handling']='unknown';d['event_domains']['unit_handling']=domain('0/1','10/1');refresh_sources(d)
        self.assertEqual(family.assess(d,BUDGET)['status'],'unsupported')

    def test_partial_and_zero_budgets_preserve_unknown_branches(self):
        d=fixture();r=family.assess(d,{**BUDGET,'max_cells':1})
        self.assertEqual(r['status'],'conditional_state_family_witness',r)
        self.assertEqual(r['branches'][1]['status'],'unvisited');self.assertFalse(r['coverage']['complete'])
        for key in ['max_cells','elapsed_ms','solver_timeout_ms','solver_rlimit']:
            self.assertEqual(family.assess(d,{**BUDGET,key:0})['status'],'unknown')
        d['branch_limit']=1;self.assertEqual(family.assess(d,BUDGET)['status'],'unknown')

    def test_target_obligations_prevent_actual_state_claim(self):
        d=fixture();d['obligations']=[{'id':'actual','meaning':'No admitted actual opening','affects':['history']}]
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'candidate_state_with_unresolved_obligations',r)
        self.assertEqual(r['target_existence'],'unknown');self.assertFalse(r['source_admission'])

    def test_forged_state_replay_and_alternate_candidate(self):
        d=fixture();r=family.assess(d,BUDGET);self.assertTrue(family.verify_result(d,BUDGET,r))
        for mutate in [lambda x:x.update(committed=True),
                       lambda x:x['branches'][0]['replay']['after']['component'].update(settled=False),
                       lambda x:x['native_compilation']['joined_definition']['bindings'].pop('n')]:
            bad=deepcopy(r);mutate(bad);self.assertFalse(family.verify_result(d,BUDGET,bad))
        b=r['branches'][0];b['witness']['nrv']='25/1';b['replay']=family.replay_witness(d,BUDGET,0,b['witness'])
        self.assertTrue(family.verify_result(d,BUDGET,r))

    def test_original_context_regenerated_without_dropping_event_date(self):
        d=fixture();d['state']['context']['entity']='Q';d['event']['date']='2025-02-02';refresh_sources(d)
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_state_family_witness',r)
        context=r['native_compilation']['joined_definition']['family']['method']['inputs']['n']['type']['context']
        self.assertEqual(context,{'entity':'Q','book_role':'legal','at':'2025-02-02'})
        self.assertEqual(r['branches'][0]['replay']['flows'][0]['entity'],'Q')

    def test_malformed_and_conflicting_domain_inputs_reject(self):
        for mutate in [lambda x:x['interval'].update(lower='13/1',upper='12/1'),
                       lambda x:x['interval'].update(lower='1.5'),
                       lambda x:x.update(extra='unexpected')]:
            d=fixture();mutate(d['event_domains']['actual_units']);self.assertEqual(family.assess(d,BUDGET)['status'],'invalid')
        d=fixture();p=deepcopy(d['premise']);p['meaning']='conflicting meaning'
        d['event_domains']['actual_units']['premise']=p
        self.assertEqual(family.assess(d,BUDGET)['status'],'invalid')

    def test_invalid_opening_and_unresolved_numeric_event_remain_distinct(self):
        d=fixture();s=d['state'];cash=Q(s['balances']['cash'])
        s['balances']['cash']='-1/1';s['balances']['original_equity']=family.native.monetary.fmt(Q(s['balances']['original_equity'])+cash+1)
        self.assertEqual(family.assess(d,BUDGET)['status'],'funding_failure')
        d=fixture();d['event_domains'].pop('actual_units')
        self.assertEqual(family.assess(d,BUDGET)['status'],'unresolved')

    def test_forged_witness_cannot_bypass_original_quantity_or_cash(self):
        d=fixture();r=family.assess(d,BUDGET);w=deepcopy(r['branches'][0]['witness']);w['n']='11/1'
        with self.assertRaises(ValueError):family.replay_witness(d,BUDGET,0,w)
        d=fixture(variable=False);d['event']['refund_cash']='41/1'
        self.assertEqual(family.assess(d,BUDGET)['status'],'conditionally_infeasible')


if __name__=='__main__':unittest.main()
