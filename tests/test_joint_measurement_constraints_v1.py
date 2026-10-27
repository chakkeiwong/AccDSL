"""Hand-solvable systems and independent Fraction witness verification."""
from copy import deepcopy
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import joint_measurement_constraints_v1 as joint
TYPE={'kind':'rational','context':{'entity':'example','at':'2024-09-28','perimeter':'consolidated'},
      'dimensions':{'currency:USD':1},'scale':'1000000/1'}
BUDGET={'max_slots':0,'max_formula_nodes':10000,'max_integer_assignments':1,'max_cells':1,
        'elapsed_ms':5000,'solver_timeout_ms':1000,'solver_rlimit':1000000}


def premise(key):return {'id':key,'status':'proposed','meaning':'explicit constructed test assumption'}
def obs(low='0/1',high='1/1',lower=True,upper=True):
    return {'type':deepcopy(TYPE),'source_ref':'constructed:measurement',
            'interval':{'lower':low,'upper':high,'lower_inclusive':lower,'upper_inclusive':upper},
            'interval_premise':premise('test_interval')}
def equation(key,terms,rhs='0/1'):
    return {'id':key,'type':deepcopy(TYPE),'terms':[{'observation':k,'coefficient':a} for k,a in terms],
            'rhs':rhs,'identity_premise':premise('identity.'+key)}
def definition(observations=None,equations=None):
    return {'profile':joint.PROFILE,'observations':{'x':obs()} if observations is None else observations,
            'equations':[equation('x0',[('x','1/1')])] if equations is None else equations}


class JointMeasurementTests(unittest.TestCase):
    def test_local_compatibility_is_not_joint_consistency(self):
        x0=equation('x0',[('x','1/1')]);x1=equation('x1',[('x','1/1')],'1/1')
        for row in [x0,x1]:
            result=joint.assess(definition(equations=[row]),BUDGET)
            self.assertEqual(result['status'],'conditionally_feasible',result)
            self.assertTrue(result['witness_checked_exactly'])
        result=joint.assess(definition(equations=[x0,x1]),BUDGET)
        self.assertEqual(result['status'],'conditionally_infeasible',result)
        self.assertTrue(all(c['rechecked']=='unsat' for c in result['conflicts']))

    def test_strict_endpoints_preserved(self):
        for low,high,li,ui,rhs,expected in [
            ('0/1','1/1',False,True,'0/1','conditionally_infeasible'),
            ('0/1','1/1',True,False,'1/1','conditionally_infeasible'),
            ('-3/2','-1/2',False,True,'-1/2','conditionally_feasible'),
            ('-3/2','-1/2',False,True,'-3/2','conditionally_infeasible'),
            ('-1/2','1/2',False,False,'0/1','conditionally_feasible')]:
            d=definition({'x':obs(low,high,li,ui)},[equation('at',[('x','1/1')],rhs)])
            self.assertEqual(joint.assess(d,BUDGET)['status'],expected)

    def test_exact_fractional_shared_witness_and_cancellation(self):
        d=definition({'x':obs(),'y':obs()},[
            equation('sum',[('x','1/1'),('y','1/1')],'1/1'),
            equation('ratio',[('x','2/1'),('y','-1/1')])])
        old=deepcopy(d);result=joint.assess(d,BUDGET)
        self.assertEqual(result['witness'],{'x':'1/3','y':'2/3'});self.assertEqual(d,old)
        d=definition(equations=[equation('cancel',[('x','1/1'),('x','-1/1')])])
        result=joint.assess(d,BUDGET);self.assertEqual(result['status'],'conditionally_feasible')
        self.assertTrue(joint.check_witness(d,result['witness']))

    def test_witness_verifier_rejects_tampering(self):
        d=definition()
        for witness in [{},{'x':'2/1'},{'x':'1/2'},{'x':'0/1','extra':'0/1'},{'x':'0/2'}]:
            with self.assertRaises(ValueError):joint.check_witness(d,witness)

    def test_missing_assumptions_and_intervals_remain_unresolved(self):
        for edit in [lambda d:d['observations']['x'].update(interval=None),
                     lambda d:d['observations']['x'].update(interval_premise=None),
                     lambda d:d['equations'][0].update(identity_premise=None)]:
            d=definition();edit(d);result=joint.assess(d,BUDGET)
            self.assertEqual(result['status'],'unresolved');self.assertNotIn('solver_status',result)
            self.assertTrue(result['missing'])

    def test_validation_precedes_unknown_outcome(self):
        d=definition();d['observations']['x']['interval']=None;d['equations'][0]['rhs']='1.5'
        self.assertEqual(joint.assess(d,BUDGET)['status'],'invalid')

    def test_context_units_and_scale_are_exact(self):
        for key,value in [('context',{**TYPE['context'],'perimeter':'legal'}),
                          ('dimensions',{'currency:EUR':1}),('scale','1/1')]:
            d=definition();d['observations']['x']['type'][key]=value
            self.assertEqual(joint.assess(d,BUDGET)['reason'],'equation_context_type_mismatch')

    def test_zero_and_small_budgets_never_imply_infeasibility(self):
        for field in ['max_cells','max_integer_assignments','elapsed_ms','solver_timeout_ms','solver_rlimit','max_formula_nodes']:
            budget={**BUDGET,field:0};result=joint.assess(definition(),budget)
            self.assertEqual(result['status'],'unknown',(field,result))
            self.assertNotIn('witness',result)

    def test_closed_inputs_duplicates_and_conflicting_premises(self):
        edits=[lambda d:d.update(callback='anything'),
               lambda d:d['equations'].append(deepcopy(d['equations'][0])),
               lambda d:d['observations'].update(unused=obs()),
               lambda d:d['equations'][0]['terms'][0].update(observation='missing'),
               lambda d:d['observations']['x']['interval_premise'].update(status='accepted'),
               lambda d:d['equations'][0].update(identity_premise={**premise('test_interval'),'meaning':'conflicting text'})]
        for edit in edits:
            d=definition();edit(d);self.assertEqual(joint.assess(d,BUDGET)['status'],'invalid')

    def test_rational_forms_and_empty_interval_reject(self):
        for bad in [True,1,1.5,'1','2/2','1/0']:
            d=definition();d['equations'][0]['rhs']=bad
            self.assertEqual(joint.assess(d,BUDGET)['status'],'invalid')
        d=definition({'x':obs('0/1','0/1',True,False)})
        self.assertEqual(joint.assess(d,BUDGET)['reason'],'empty_observation_interval')

    def test_limits_and_no_admission(self):
        d=definition();d['equations'][0]['rhs']=str(2**4096)+'/1'
        self.assertEqual(joint.assess(d,BUDGET)['reason'],'rational_bit_limit')
        d=definition();d['equations']*=257
        self.assertEqual(joint.assess(d,BUDGET)['reason'],'equation_limit')
        d=definition();d['equations'][0]['terms']*=4097
        self.assertEqual(joint.assess(d,BUDGET)['reason'],'term_limit')
        for field,value in [('elapsed_ms',60001),('max_cells',2),('max_slots',1)]:
            self.assertEqual(joint.assess(definition(),{**BUDGET,field:value})['status'],'invalid')
        result=joint.assess(definition(),BUDGET)
        self.assertFalse(result['executed']);self.assertFalse(result['accounting_admission'])
        self.assertEqual(result['actual_history'],'unknown');self.assertIsNone(result['executable_opening'])


if __name__=='__main__':unittest.main()
