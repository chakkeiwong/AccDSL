from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('reassessment_examples',ROOT/'data/accounting-master/shared-tax-reassessment-20261024/examples.py')
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);m=x.m


class ReassessmentTests(unittest.TestCase):
    def test_incremental_tax_preserves_actual_cash(self):
        q=x.scenario();r=m.propose(q);self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['calculation']['pretax_income'],'5/1')
        self.assertEqual(r['financial_calculation'],{'previous_expense':'1/2','replacement_expense':'21/4',
            'actual_paid':'1/2','incremental_expense':'19/4','replacement_payable':'19/4'})
        self.assertEqual(r['journal']['current_tax'],'19/4');self.assertEqual(r['journal']['income_tax_payable'],'-19/4')
        self.assertEqual(r['after']['balances']['cash'],'721/2')
        self.assertEqual(r['recorded_statements']['recorded_profit'],'-1/4')
        self.assertEqual(r['recorded_statements']['balance_sheet'],{'total_assets':'1401/2',
            'total_liabilities':'435/4','equity_including_profit':'2367/4'})
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'-59/2')
        self.assertEqual(r['assessed_until'],'2026-01-01')

    def test_unpaid_reversal_and_refund_boundary(self):
        r=m.propose(x.scenario('1/1',False));self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['journal']['current_tax'],'-1/4');self.assertEqual(r['journal']['income_tax_payable'],'1/4')
        self.assertEqual(r['after']['balances']['cash'],'361/1')
        self.assertEqual(r['after']['balances']['income_tax_payable'],'-1/4')
        r=m.propose(x.scenario('1/1',True));self.assertEqual(r['status'],'unsupported')
        self.assertEqual(r['reason'],'tax_receivable_or_refund_route_required');self.assertNotIn('after',r)
        self.assertEqual(r['continuation_result']['after']['balances']['cash'],'721/2')
        self.assertEqual(r['financial_calculation']['replacement_payable'],'-1/4')

    def test_zero_and_negative_taxable(self):
        zero=m.propose(x.scenario('0/1',False));self.assertEqual(zero['status'],'proposed')
        self.assertEqual(zero['after']['balances']['current_tax'],'0/1')
        loss=m.propose(x.scenario('-19/1',False));self.assertEqual(loss['status'],'proposed')
        self.assertEqual(loss['loss_state']['lots'][0]['remaining'],'19/1')
        self.assertEqual(loss['loss_state']['cursor'],'2026-01-01')
        self.assertEqual(loss['after']['balances']['dta'],'10/1')
        self.assertEqual(loss['after']['balances']['dtl'],'-4/1')
        self.assertEqual(loss['recorded_statements']['recorded_profit'],'5/1')

    def test_provisional_loss_is_replaced_not_added(self):
        origin=x.previous.origin('-19/1');q=x.scenario('-7/1',False,origin=origin)
        r=m.propose(q);self.assertEqual(r['status'],'proposed')
        self.assertEqual(sum(Q(l['remaining']) for l in r['loss_state']['lots']),Q(7))
        self.assertEqual(len(r['loss_state']['lots']),1)
        self.assertEqual(r['continuation_result']['loss_state']['lots'][0]['remaining'],'19/1')
        self.assertEqual(r['superseded']['loss_state_sha256'],m.book.digest(origin['loss_state']))
        q['loss_policy']['generation']['id']=origin['loss_state']['lots'][0]['id']
        self.assertEqual(m.propose(q)['status'],'invalid')

    def test_original_loss_usage_is_recomputed(self):
        origin=x.origin_with_opening_loss(use='1/1')
        q=x.scenario('21/1',False,origin=origin,uses=[{'lot_id':'original-loss','amount':'19/1'}],cap='19/1')
        r=m.propose(q);self.assertEqual(r['status'],'proposed')
        self.assertEqual(origin['loss_state']['lots'][0]['used'],'1/1')
        self.assertEqual(r['loss_state']['lots'][0]['used'],'19/1')
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'0/1')
        self.assertEqual(r['financial_calculation']['replacement_expense'],'1/2')
        self.assertEqual(r['financial_calculation']['incremental_expense'],'1/4')
        q['original_loss_opening_sha256']=m.book.digest(origin['loss_state'])
        self.assertEqual(m.propose(q)['status'],'invalid')

    def test_loss_kernel_matches_original_for_selected_controls(self):
        rows=json.loads((ROOT/'data/accounting-master/conditional-tax-losses-20261024/cases.json').read_text())
        names=['consume_19_from_21','partial_use_7','expiry_at_endpoint_allows_use_then_expires','generate_19']
        for row in rows:
            if row['case'] not in names:continue
            q=row['request'];r=row['result'];calc=r['reconciliation_result']['calculation']
            policy={k:deepcopy(q[k]) for k in ['model','utilization_cap','uses','generation']}
            actual=m.replacement_losses(q['state'],q['reconciliation_request']['information_request']['interval'],
                calc,policy,q['step_id'],q['reconciliation_sha256'],q['state'])
            for key in ['movements','totals','taxable_profit_before_losses','taxable_profit_after_losses','conditional_gross_current_tax']:
                self.assertEqual(actual[key],r['proposal'][key],(row['case'],key))
            if row['case']!='generate_19':self.assertEqual(actual['after'],r['proposal']['after'])
            else:
                a=deepcopy(actual['after']);b=deepcopy(r['proposal']['after'])
                a['lots'][0].pop('origin_reference');b['lots'][0].pop('origin_reference');self.assertEqual(a,b)

    def test_unknown_false_extra_and_scope_information(self):
        original=x.scenario()
        for mutate,status in [
            (lambda q:q['information'].pop('basis/income_tax_payable/closing'),'unresolved'),
            (lambda q:q['information'].update(rate={'status':'unknown','reason':'No rate'}),'unresolved'),
            (lambda q:q['information'].update(interval_coverage=x.known(False)),'unsupported'),
            (lambda q:q['information'].update(invented=x.known('0/1')),'invalid'),
            (lambda q:q['information'].update(regime=x.known('changed')),'invalid'),
            (lambda q:q['information'].update(rate=x.known('-1/4')),'invalid'),
            (lambda q:q['information'].update(loss_route=x.known('unknown')),'invalid')]:
            q=deepcopy(original);mutate(q);r=m.propose(q);self.assertEqual(r['status'],status,r.get('reason'))
            self.assertIn('continuation_result',r)

    def test_native_adjustments_and_basis_must_reconcile(self):
        original=x.scenario()
        for mutation in [lambda q:q['allocations'].pop(0),
            lambda q:q['allocations'].append(deepcopy(q['allocations'][0])),
            lambda q:q['allocations'][0].update(amount='-23/1'),
            lambda q:q['information'].update({'basis/rou/closing':x.known('1/1')}),
            lambda q:q['information'].update({'income/other_gains/current_adjustment':x.known('41/1')})]:
            q=deepcopy(original);mutation(q);self.assertEqual(m.propose(q)['status'],'invalid')

    def test_interval_identity_and_incomplete_prefix(self):
        original=x.scenario()
        for mutation in [lambda q:q.update(continuation_sha256='0'*64),
            lambda q:q['interval'].update(start='2024-02-01'),
            lambda q:q['interval'].update(end_exclusive='2025-01-01',activity_through='2024-12-31'),
            lambda q:q['interval'].update(end_exclusive='2027-01-01',activity_through='2026-12-31'),
            lambda q:q['interval'].update(activity_through='2026-01-01'),
            lambda q:q.update(id='tax-payment')]:
            q=deepcopy(original);mutation(q);self.assertEqual(m.propose(q)['status'],'invalid')
        q=deepcopy(original);q['continuation_request']['operations'].append(x.previous.payment())
        q['continuation_sha256']=m.book.digest(q['continuation_request'])
        r=m.propose(q);self.assertEqual(r['status'],'unresolved');self.assertEqual(r['continuation_result']['status'],'stopped')

    def test_model_selection_and_full_apply(self):
        q=x.scenario();r=m.propose(q);self.assertEqual(m.apply(q,r)['status'],'applied')
        for key,value in [('committed',0),('loss_state',{}),('journal',{}),('assessed_until','2027-01-01')]:
            altered=deepcopy(r);altered[key]=value;self.assertEqual(m.apply(q,altered)['status'],'invalid')
        for value,status in [({'status':'unknown','reason':'Not selected'},'unresolved'),(x.known(False),'unsupported')]:
            body=deepcopy(q);body['model']['selected']=value;self.assertEqual(m.propose(body)['status'],status)

    def test_complete_financial_state_and_source_preservation(self):
        q=x.scenario();saved=deepcopy(q);r=m.propose(q);self.assertEqual(q,saved)
        before=r['continuation_result']['after'];after=r['after']
        for k,v in before['balances'].items():
            if k not in ['current_tax','income_tax_payable']:self.assertEqual(after['balances'][k],v,k)
        for k,v in before.items():
            if k not in ['balances','seen','date']:self.assertEqual(after[k],v,k)
        self.assertEqual(set(r['recorded_statements']['reconciliations'].values()),{'0/1'})
        self.assertTrue(all(r[k] is False for k in m.FLAGS))

    def test_loss_caps_and_generation_boundaries(self):
        origin=x.origin_with_opening_loss(use='1/1')
        original=x.scenario('21/1',False,origin=origin,uses=[{'lot_id':'original-loss','amount':'19/1'}],cap='19/1')
        for mutate,status in [
            (lambda q:q['loss_policy'].update(utilization_cap=x.known('18/1')),'invalid'),
            (lambda q:q['loss_policy']['uses'][0].update(amount='20/1'),'invalid'),
            (lambda q:q['loss_policy']['uses'].append(deepcopy(q['loss_policy']['uses'][0])),'invalid'),
            (lambda q:q['loss_policy'].update(utilization_cap={'status':'unknown','reason':'Missing cap'}),'unresolved')]:
            q=deepcopy(original);mutate(q);self.assertEqual(m.propose(q)['status'],status)
        q=x.scenario('-19/1',False);q['loss_policy']['generation']['eligible']={'status':'unknown','reason':'No finding'}
        self.assertEqual(m.propose(q)['status'],'unresolved')
        q=x.scenario('-19/1',False);q['loss_policy']['generation']['expiry']={
            'kind':'date','end_exclusive':'2026-01-01','provenance':x.known()['provenance']}
        self.assertEqual(m.propose(q)['status'],'invalid')

    def test_fractional_and_above_one_rate_are_explicit(self):
        q=x.scenario('1/3',False);r=m.propose(q);self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['financial_calculation']['replacement_expense'],'1/12')
        self.assertEqual(r['financial_calculation']['incremental_expense'],'-5/12')
        q['information']['rate']=x.known('5/4');r=m.propose(q)
        self.assertEqual(r['status'],'proposed');self.assertEqual(r['financial_calculation']['replacement_expense'],'5/12')


if __name__=='__main__':unittest.main()
