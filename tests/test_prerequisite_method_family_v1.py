"""Shared input constraints versus exact unchanged native prerequisites."""
from copy import deepcopy
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import prerequisite_method_family_v1 as joined
from test_typed_return_transition_v1 import fixtures
from test_conditional_history_family_v1 import domain
from test_joint_measurement_constraints_v1 import premise
from test_piecewise_method_family_v1 import BUDGET
AUDIT=ROOT/'data/accounting-master/method-family-prerequisites-audit-20261024/audit.json'


def fixture(kind='settle',variable=True,over=False):
    audit=json.loads(AUDIT.read_text())
    row=next(x for x in audit['selected'] if x['kind']==kind)
    capture=deepcopy(row['capture']);method=deepcopy(row['method'])
    _,state,event=next(x for x in fixtures.selected_cases() if x[2]['kind']==kind)
    values=fixtures.project(state,event)
    family={'profile':joined.parent.PROFILE,'method':method,
        'selected_method_digest':joined.core.digest(method),
        'domains':{k:domain(v['value']) for k,v in values.items()},
        'measurements':[],'obligations':[],'branch_limit':16}
    if variable and kind=='settle':
        family['domains']['n']=domain('0/1','12/1');family['domains']['nrv']=domain('5/1','30/1')
    if over:
        capture=deepcopy(audit['counterexample']['prerequisites'])
        family=deepcopy(audit['counterexample']['request']);method=family['method']
    manifest=capture['manifest'];bindings={}
    for key,item in manifest['inputs'].items():
        if key in row['mapped']:
            bindings[key]={'kind':'method_input','input':key,'premise':premise('mapping:'+key),
                          'requirement_source_ref':item['source_ref'],
                          'method_source_ref':method['inputs'][key]['source_ref']}
        else:
            bindings[key]={'kind':'external','binding':deepcopy(capture['values'][key]),
                          'premise':premise('external:'+key),'source_ref':item['source_ref']}
    return {'profile':joined.PROFILE,'family':family,'requirements':manifest,
        'selected_requirements_digest':joined.core.digest(manifest),'bindings':bindings,
        'available_capabilities':capture['available'],'obligations':[]}


def redigest(d):d['selected_requirements_digest']=joined.core.digest(d['requirements'])


class PrerequisiteMethodFamilyTests(unittest.TestCase):
    def test_valid_retained_comparators_replay_both_originals(self):
        for kind in ['settle','sell']:
            d=fixture(kind,False);before=deepcopy(d);r=joined.assess(d,BUDGET)
            self.assertEqual(r['status'],'conditional_family_witness',r)
            self.assertEqual(d,before);self.assertTrue(joined.verify_result(d,BUDGET,r))
            b=next(x for x in r['branches'] if x['status']=='feasible')
            self.assertEqual(b['replay']['prerequisites']['status'],'requirements_satisfied')
            self.assertTrue(b['replay']['both_original_evaluators_checked'])
            self.assertFalse(r['method_eligible']);self.assertFalse(r['executed'])

    def test_quantity_over_sold_is_empty_despite_balanced_parent(self):
        d=fixture(over=True)
        self.assertEqual(joined.parent.assess(d['family'],BUDGET)['status'],'conditional_family_witness')
        r=joined.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditionally_infeasible',r)
        self.assertEqual(r['target_existence'],'conditionally_empty')
        self.assertTrue(joined.verify_result(d,BUDGET,r))

    def test_shared_quantity_narrowed_by_exact_cash_fact_keeps_minimum_arms(self):
        d=fixture();r=joined.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(r['coverage']['total'],2);self.assertEqual(r['coverage']['feasible'],2)
        expected=d['bindings']['refund_cash']['binding']['value']
        price=d['family']['domains']['p']['interval']['lower']
        for branch in r['branches']:
            self.assertEqual(joined.Q(branch['witness']['n'])*joined.Q(price),joined.Q(expected))
            self.assertTrue(branch['replay']['both_original_evaluators_checked'])
        self.assertEqual(r['definition']['family'],d['family'])

    def test_false_unknown_and_conflicting_external_facts_preserve_precedence(self):
        for value,status in [(False,'unsupported'),('unknown','unresolved')]:
            d=fixture();b=d['bindings']['all_rights_closed']
            b['binding']=({'status':'unknown','reason':'not verified'} if value=='unknown' else
                          {'status':'known','value':value})
            self.assertEqual(joined.assess(d,BUDGET)['status'],status)
        d=fixture();d['bindings']['all_rights_closed']['binding']={'status':'known','value':False}
        d['bindings']['event_date']['binding']={'status':'known','value':'1900-01-01'}
        r=joined.assess(d,BUDGET);self.assertEqual(r['status'],'invalid',r)
        self.assertIn('unsupported',{x['consequence'] for x in r['prerequisite_compilation']['fixed_findings']})

    def test_unknown_external_cash_does_not_become_solver_choice(self):
        d=fixture();d['bindings']['refund_cash']['binding']={'status':'unknown','reason':'cash fact absent'}
        r=joined.assess(d,BUDGET);self.assertEqual(r['status'],'unresolved',r)
        self.assertNotIn('branches',r)

    def test_mapping_digest_type_and_provenance_are_checked(self):
        for mutate in [lambda d:d['bindings'].pop('n'),
            lambda d:d['bindings']['n'].update(input='p'),
            lambda d:d['bindings']['n'].update(method_source_ref='guessed'),
            lambda d:d['bindings']['n'].update(requirement_source_ref='guessed'),
            lambda d:d['bindings']['sold'].update(source_ref='guessed'),
            lambda d:d.update(selected_requirements_digest='0'*64)]:
            d=fixture();mutate(d);self.assertEqual(joined.assess(d,BUDGET)['status'],'invalid')

    def test_missing_mapping_and_parent_premises_prevent_solving(self):
        for mutate in [lambda d:d['bindings']['n'].update(premise=None),
                       lambda d:d['family']['domains']['n'].update(premise=None)]:
            d=fixture();mutate(d);r=joined.assess(d,BUDGET)
            self.assertEqual(r['status'],'unresolved');self.assertNotIn('branches',r)

    def test_parent_and_join_obligations_keep_target_unknown(self):
        d=fixture();d['family']['obligations']=[{'id':'memory','meaning':'Unspecified state','affects':['execution']}]
        d['obligations']=[{'id':'source','meaning':'Unadmitted facts','affects':['membership']}]
        r=joined.assess(d,BUDGET)
        self.assertEqual(r['status'],'candidate_with_unresolved_obligations')
        self.assertEqual(r['target_existence'],'unknown');self.assertEqual(len(r['target_obligations']),2)

    def test_inactive_rule_and_required_known_remain_separate(self):
        d=fixture();req=next(r for r in d['requirements']['requirements'] if r['id']=='all_rights_closed')
        req['guard']['value']=False;redigest(d)
        d['bindings']['all_rights_closed']['binding']={'status':'known','value':False}
        r=joined.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_family_witness',r)
        findings=r['branches'][0]['replay']['prerequisites']['findings']
        self.assertEqual(next(x for x in findings if x['id']=='all_rights_closed')['activation'],'inactive')
        d['bindings']['all_rights_closed']['binding']={'status':'unknown','reason':'not known'}
        self.assertEqual(joined.assess(d,BUDGET)['status'],'unresolved')

    def test_unknown_or_symbolic_guard_is_not_assumed_true(self):
        d=fixture();req=d['requirements']['requirements'][0]
        req['guard']={'op':'ref','id':'all_rights_closed'};req['guard_requires']=['all_rights_closed'];redigest(d)
        d['bindings']['all_rights_closed']['binding']={'status':'unknown','reason':'not inspected'}
        self.assertEqual(joined.assess(d,BUDGET)['status'],'unresolved')
        d=fixture();req=d['requirements']['requirements'][0]
        req['guard']={'op':'lt','left':{'op':'const','value':'0/1','type':d['requirements']['inputs']['n']['type']},
                      'right':{'op':'ref','id':'n'}};req['guard_requires']=['n'];redigest(d)
        self.assertEqual(joined.assess(d,BUDGET)['status'],'unsupported')

    def test_capability_unknown_product_and_symbolic_disjunction_reject(self):
        d=fixture();d['requirements']['capabilities']=['named_capability'];redigest(d)
        self.assertEqual(joined.assess(d,BUDGET)['status'],'unsupported')
        d['available_capabilities']=['named_capability']
        self.assertEqual(joined.assess(d,BUDGET)['status'],'conditional_family_witness')
        d=fixture();d['family']['domains']['p']=domain('10/1','20/1')
        self.assertEqual(joined.assess(d,BUDGET)['status'],'unsupported')
        d=fixture();req=next(x for x in d['requirements']['requirements'] if x['id']=='quantities')
        req['predicate']['op']='any';redigest(d)
        self.assertEqual(joined.assess(d,BUDGET)['status'],'unsupported')

    def test_global_cells_and_zero_budget_preserve_unvisited_arm(self):
        d=fixture();r=joined.assess(d,{**BUDGET,'max_cells':1})
        self.assertEqual(r['coverage']['attempted'],1);self.assertEqual(r['branches'][1]['status'],'unvisited')
        self.assertEqual(r['declared_search'],'partial')
        for key in ['max_cells','elapsed_ms','solver_timeout_ms','solver_rlimit','max_formula_nodes']:
            self.assertEqual(joined.assess(d,{**BUDGET,key:0})['status'],'unknown',key)

    def test_forged_candidate_and_constraints_reject(self):
        d=fixture();r=joined.assess(d,BUDGET);self.assertTrue(joined.verify_result(d,BUDGET,r))
        b=next(x for x in r['branches'] if x['status']=='feasible')
        bad=deepcopy(b['witness']);bad['n']='11/1'
        with self.assertRaises(ValueError):joined.replay_witness(d,BUDGET,b['index'],bad)
        for mutate in [lambda x:x.update(accounting_admission=True),
                       lambda x:x['branches'][0]['replay']['prerequisites'].update(status='invalid'),
                       lambda x:x['branch_manifest'][0].update(parent_sha256='0'*64),
                       lambda x:x['prerequisite_compilation']['mapped_inputs'].update(n='p')]:
            forged=deepcopy(r);mutate(forged);self.assertFalse(joined.verify_result(d,BUDGET,forged))

    def test_alternate_valid_witness_and_conflict_replay(self):
        d=fixture();r=joined.assess(d,BUDGET)
        b=r['branches'][0];b['witness']['nrv']='25/1'
        b['replay']=joined.replay_witness(d,BUDGET,0,b['witness'])
        self.assertTrue(joined.verify_result(d,BUDGET,r))
        d=fixture(over=True);r=joined.assess(d,BUDGET)
        r['branches'][0]['conflict']['labels']=['invented'];self.assertFalse(joined.verify_result(d,BUDGET,r))

    def test_all_inactive_predicates_keep_no_active_status(self):
        d=fixture(variable=False)
        for req in d['requirements']['requirements']:req['guard']['value']=False
        redigest(d);r=joined.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(r['branches'][0]['replay']['prerequisites']['status'],'no_active_requirements')

    def test_conflicting_shared_mapping_premise_rejects(self):
        d=fixture();d['bindings']['n']['premise']=deepcopy(d['family']['domains']['n']['premise'])
        d['bindings']['n']['premise']['meaning']='changed meaning for existing identity'
        self.assertEqual(joined.assess(d,BUDGET)['status'],'invalid')

    def test_finite_branch_cap_stays_unknown_with_original_parents(self):
        d=fixture();d['family']['branch_limit']=1;r=joined.assess(d,BUDGET)
        self.assertEqual(r['status'],'unknown',r)
        self.assertFalse(r['branch_partition_complete']);self.assertEqual(r['definition'],d)

    def test_unknown_inactive_optional_fact_is_preserved(self):
        d=fixture(variable=False);key='all_rights_closed'
        req=next(r for r in d['requirements']['requirements'] if r['id']==key)
        req['guard']['value']=False;d['requirements']['required_known'].remove(key);redigest(d)
        d['bindings'][key]['binding']={'status':'unknown','reason':'unused inactive finding'}
        r=joined.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(r['branches'][0]['replay']['candidate_bindings'][key]['status'],'unknown')


if __name__=='__main__':unittest.main()
