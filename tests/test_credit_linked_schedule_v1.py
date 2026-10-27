"""Exact dependence, independent targets and refusal boundaries."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import credit_linked_algebra_v1 as algebra
import credit_linked_schedule_v1 as schedule


class AlgebraTests(unittest.TestCase):
    def setUp(self):
        self.context=deepcopy(schedule.retained()[0]['request']['context'])
        self.root=algebra.Root.create(self.context,'1/10')

    def rejects(self, reason, fn):
        with self.assertRaises(algebra.Refusal) as caught: fn()
        self.assertEqual(caught.exception.reason,reason)

    def test_positive_and_negative_power_reduction(self):
        self.assertEqual(self.root.power(365).rational_projection(),Q(11,10))
        self.assertEqual(self.root.power(-365).rational_projection(),Q(10,11))
        self.assertTrue((self.root.power(-181)*self.root.power(181)-1).zero)
        self.assertEqual(self.root.power(-1).terms,((364,Q(10,11)),))

    def test_associativity_distributivity_and_inverse_day_shift(self):
        a=self.root.power(181)*100-100; b=self.root.power(364)+3; c=self.root.power(2)-4
        self.assertTrue(((a+b)*c-a*c-b*c).zero)
        self.assertTrue(((a*b)*c-a*(b*c)).zero)
        self.assertTrue((a.shift(-181).shift(181)-a).zero)
        self.assertTrue((a/7*7-a).zero)

    def test_zero_rate_collapses_even_irregular_powers(self):
        root=algebra.Root.create(self.context,'0')
        self.assertEqual(root.power(7305).rational_projection(),1)
        self.assertEqual(root.power(-7305).rational_projection(),1)
        self.assertEqual(algebra.Expr.normalized(root,{181:Q(2),-19:Q(3)}).rational_projection(),5)

    def test_negative_rate_root(self):
        root=algebra.Root.create(self.context,'-1/10')
        self.assertEqual(root.power(365).rational_projection(),Q(9,10))
        self.assertTrue((root.power(181)*root.power(184)-Q(9,10)).zero)

    def test_context_and_rate_mix_refused_even_for_zero(self):
        context={**self.context,'entity':'Another Bank'}
        roots=[algebra.Root.create(context,'1/10'),algebra.Root.create(self.context,'1/20')]
        for root in roots:
            self.rejects('mixed_root_context_or_rate',lambda:self.root.value(0)+root.value(0))
            self.rejects('mixed_root_context_or_rate',lambda:self.root.value(0)*root.value(0))

    def test_canonical_roundtrip_and_foreign_root(self):
        x=self.root.power(181)*80-100
        self.assertEqual(algebra.Expr.from_wire(self.root,x.wire()),x)
        wire=x.wire(); wire['root_sha256']='0'*64
        self.rejects('expression_root_binding',lambda:algebra.Expr.from_wire(self.root,wire))

    def test_malformed_and_noncanonical_wire(self):
        base=self.root.power(1).wire()
        cases=[([{'power':True,'coefficient':'1'}],'canonical_power_order'),
               ([{'power':365,'coefficient':'1'}],'canonical_power_order'),
               ([{'power':1,'coefficient':'0'}],'canonical_coefficient'),
               ([{'power':1,'coefficient':'1/1'}],'rational_encoding'),
               ([{'power':1,'coefficient':1}],'coefficient_wire_encoding'),
               ([{'power':1,'coefficient':'1'},{'power':1,'coefficient':'2'}],'canonical_power_order'),
               ([{'power':2,'coefficient':'1'},{'power':1,'coefficient':'2'}],'canonical_power_order')]
        for terms,reason in cases:
            self.rejects(reason,lambda:algebra.Expr.from_wire(self.root,{**base,'terms':terms}))

    def test_coefficient_boundary_and_operation_overflow(self):
        large=Q(2**1023); x=self.root.value(large)
        self.assertEqual(x.rational_projection(),large)
        self.rejects('coefficient_budget',lambda:x*2)
        self.rejects('coefficient_budget',lambda:self.root.value(Q(1,2**1024)))
        self.rejects('coefficient_budget',lambda:self.root.value('9'*641))

    def test_term_and_power_boundaries(self):
        x=algebra.Expr.normalized(self.root,{p:Q(1) for p in range(365)})
        self.assertEqual(len(x.terms),365)
        self.rejects('term_budget',lambda:algebra.Expr.normalized(self.root,{p:Q(1) for p in range(366)}))
        self.assertTrue((self.root.power(7305)*self.root.power(-7305)-1).zero)
        for p in [-7306,7306]: self.rejects('power_budget',lambda:self.root.power(p))

    def test_no_general_inverse_order_or_point_substitution(self):
        x=self.root.power(181)
        self.rejects('polynomial_division_unsupported',lambda:x/(x+1))
        self.rejects('division_by_zero',lambda:x/0)
        self.rejects('rational_projection_not_certified',x.rational_projection)
        with self.assertRaises(TypeError): x < 1

    def test_reducible_polynomial_nonzero_does_not_prove_inequality(self):
        # z**365=32 implies (z**73)**5=32=2**5, hence z**73=2 for positive z.
        root=algebra.Root.create(self.context,'31'); remainder=root.power(73)-2
        self.assertFalse(remainder.zero)
        self.assertEqual(remainder.equality_certificate(0),'not_certified')
        self.assertTrue((root.power(365)-32).zero)

    def test_invalid_root_domain(self):
        for rate in ['-1','-2']: self.rejects('positive_root_domain',lambda:algebra.Root.create(self.context,rate))
        self.rejects('rational_encoding',lambda:algebra.Root.create(self.context,True))


class ScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=schedule.retained()
        cls.results={r['id']:schedule.calculate(schedule.request(r['id'])) for r in cls.rows}

    def test_all_nine_complete_inputs_and_metadata_preserved(self):
        self.assertEqual(len(self.results),9)
        for row in self.rows:
            req=schedule.request(row['id']); before=deepcopy(req); result=schedule.calculate(req)
            self.assertEqual(req,before); self.assertEqual(result,self.results[row['id']])
            self.assertEqual(result['status'],'certified_read_only')
            self.assertEqual(result['native_result_sha256'],schedule.digest(row['result']))
            for key in ['cash_flows','uncollected_contract','writeoff_contract','context','financial_derecognized']:
                self.assertEqual(result['schedule'][key],row['result'][key])
            self.assertFalse(result['posts']); self.assertEqual(result['mutations'],[])
            for key in ['native_accounting_admission','source_complete','host_book_admission']: self.assertFalse(result[key])

    def test_every_identity_target_and_containment_certificate(self):
        for result in self.results.values():
            cert=result['certificates']
            self.assertTrue(all(r['status']=='certified_equal' and not r['remainder']['terms'] for r in cert['identities']))
            self.assertTrue(all(r['certified_equal'] and r['actual']==r['expected'] for r in cert['authored_targets']))
            for c in cert['containment']:
                self.assertTrue(c['contained'])
                self.assertLessEqual(Q(c['native_enclosure']['lower']),Q(c['enclosure']['lower']))
                self.assertLessEqual(Q(c['enclosure']['upper']),Q(c['native_enclosure']['upper']))

    def test_shared_july_factor_cancels_exactly(self):
        result=self.results['partial-early-writeoff']; root=algebra.Root.create(result['root']['context'],result['root']['rate'])
        j=next(r for r in result['schedule']['journals'] if r['id']=='july_accrual')
        entries={k:algebra.Expr.from_wire(root,v) for k,v in j['entries'].items()}
        self.assertEqual(entries['gross'],root.power(181)*100-100)
        self.assertEqual(entries['interest'],-entries['gross'])
        self.assertTrue(sum(entries.values(),root.value(0)).zero)

    def test_three_exact_cases_project_to_native_rationals(self):
        ids=['unchanged-annual','zero-rate','three-irregular-receipts']
        for identity in ids:
            result=self.results[identity]; root=algebra.Root.create(result['root']['context'],result['root']['rate'])
            for c in result['certificates']['containment']:
                q=algebra.Expr.from_wire(root,c['exact_expression']).rational_projection()
                self.assertEqual(str(q),c['native_enclosure']['lower'])
                self.assertEqual(c['native_enclosure']['lower'],c['native_enclosure']['upper'])

    def test_rehashed_unretained_request_refused(self):
        req=schedule.request('partial-early-writeoff'); req['native_request']['opening_cash']='301'
        req['native_request_sha256']=schedule.digest(req['native_request'])
        native,_=schedule.load_native(); req['expected_native_result_sha256']=schedule.digest(native.calculate(req['native_request']))
        result=schedule.calculate(req)
        self.assertEqual(result['reason'],'outside_retained_native_request'); self.assertNotIn('schedule',result)

    def test_forged_result_hash_and_stale_request_refused(self):
        req=schedule.request('partial-early-writeoff'); req['expected_native_result_sha256']='0'*64
        self.assertEqual(schedule.calculate(req)['reason'],'native_result_binding')
        req=schedule.request('partial-early-writeoff'); req['native_request']['opening_cash']='301'
        self.assertEqual(schedule.calculate(req)['reason'],'native_request_hash')

    def test_native_refusal_preserved_before_retention_check(self):
        req=schedule.request('partial-early-writeoff')
        req['native_request']['acquisition']['findings']['amortised_cost']=None
        req['native_request_sha256']=schedule.digest(req['native_request'])
        result=schedule.calculate(req)
        self.assertEqual(result['status'],'unresolved'); self.assertEqual(result['reason'],'native_refusal')
        self.assertEqual(result['native_refusal']['reason'],'missing_amortised_cost')
        self.assertNotIn('schedule',result)

    def test_protected_source_change_refused(self):
        req=schedule.request('partial-early-writeoff')
        with patch.dict(schedule.PINS,{'reference.py':'0'*64}):
            self.assertEqual(schedule.calculate(req)['reason'],'dependency_hash:reference.py')

    def test_containment_is_not_weakened_to_overlap(self):
        root=algebra.Root.create(self.rows[0]['request']['context'],'1/10'); _,bounds=schedule.load_native()
        interval=bounds.factor(root.rate,181,24)
        # A point at the lower endpoint overlaps the computed enclosure but does not contain it.
        native=bounds.I.point(interval.lo).wire()
        with self.assertRaises(algebra.Refusal) as caught: schedule.crosscheck(root.power(181),native,bounds)
        self.assertEqual(caught.exception.reason,'enclosure_not_contained:')

    def test_structure_and_metadata_changes_refused(self):
        _,bounds=schedule.load_native()
        for x,y in [({'id':'a'},{'id':'b'}),([1],[1,2]),({'a':1},{'b':1})]:
            with self.assertRaises(algebra.Refusal): schedule.crosscheck(x,y,bounds)

    def test_malformed_and_extra_request_fields_refused(self):
        for req in [None,{}, {'profile':schedule.PROFILE}]:
            self.assertEqual(schedule.calculate(req)['status'],'rejected')
        req=schedule.request('zero-rate'); req['native_result']={}
        self.assertEqual(schedule.calculate(req)['reason'],'request_shape')


if __name__=='__main__': unittest.main()
