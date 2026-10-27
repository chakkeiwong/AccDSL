"""P05 adversarial economic-input execution and independent bridge obligations."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from company_execution_v1 import (Engine,event,execute_period,forecast_period,run_northstar,information,compatible_difference,
                                  stress_record,branch_family,apple_conditional,p03_family,statements,ROOT,INPUT,fingerprint)
from check_accounting_p05 import verify,compare_reference,coverage,REQUIRED_CHECKS

class P05Tests(unittest.TestCase):
    def setUp(self):self.spec=json.loads((ROOT/INPUT).read_text())
    def make(self,op,params,ident='x',**kw):return event(self.spec,ident,op,params,**kw)
    def unchanged(self,engine,e,status='Rejected'):
        before=engine.snapshot();r=engine.apply(e);self.assertEqual(r['status'],status,r);self.assertEqual(before,engine.snapshot());return r

    def test_all_statement_bridges_and_reference_movements(self):
        r=run_northstar(self.spec)
        for p in r['periods'].values():self.assertTrue(verify(p)['passed'])
        self.assertTrue(compare_reference(r['periods'],json.loads((ROOT/'docs/design/fixtures/northstar.json').read_text()))['passed'])

    def test_input_perturbation_changes_delivery_profit_and_tax(self):
        other=deepcopy(self.spec);other['periods'][0]['sales_consideration']='115'
        a=run_northstar(self.spec)['periods']['2024H1'];b=run_northstar(other)['periods']['2024H1']
        self.assertEqual(F(b['statements']['flat']['profit'])-F(a['statements']['flat']['profit']),4)
        self.assertNotEqual(a['journals'],b['journals']);verify(b)

    def test_runtime_never_reads_expected_fixture(self):
        read=Path.read_text
        def guarded(p,*a,**kw):
            if p.name=='northstar.json':raise AssertionError('expected fixture accessed by runtime')
            return read(p,*a,**kw)
        with patch.object(Path,'read_text',guarded):self.assertEqual(run_northstar()['status'],'Complete')

    def test_checker_detects_posting_and_classification_and_bridge_mutations(self):
        r=run_northstar(self.spec)['periods']['2024H1']
        mutations=[]
        a=deepcopy(r);a['journals'][0]['postings'][0]['signed_amount']='71';mutations.append(a)
        a=deepcopy(r);a['journals'][2]['cash_class']='financing';mutations.append(a)
        for section,key in [('income','profit'),('equity','closing'),('plant','depreciation'),('debt','closing')]:
            a=deepcopy(r);a['statements'][section][key]='999';mutations.append(a)
        a=deepcopy(r);a['statements']['cash_flow']['indirect_operating']='999';mutations.append(a)
        for a in mutations:
            with self.assertRaises(AssertionError):verify(a)
        poisoned=json.loads((ROOT/'docs/design/fixtures/northstar.json').read_text());poisoned['expected']['2024H1']['profit']='999'
        with self.assertRaises(AssertionError):compare_reference(run_northstar(self.spec)['periods'],poisoned)

    def test_duplicate_and_conflicting_ids(self):
        en=Engine(self.spec);e=self.make('purchase',{'units':'1'});self.assertEqual(en.apply(e)['status'],'Applied')
        self.unchanged(en,e,'Duplicate');e['params']['units']='2';self.unchanged(en,e)

    def test_invalid_context_dates_and_amounts(self):
        for value in ('NaN','1/0',True,1.2,'-1',None):
            en=Engine(self.spec);self.unchanged(en,self.make('purchase',{'units':value}))
        for key,value in [('date','2024-02-30'),('context',{}),('decision_at','2025-01-01')]:
            e=self.make('purchase',{'units':'1'});e[key]=value;self.unchanged(Engine(self.spec),e)

    def test_insufficient_inventory_excess_settlement_and_unknown_fields(self):
        en=Engine(self.spec)
        for op,p in [('deliver',{'units':'100','consideration':'1'}),('supplier_pay',{'amount':'21'}),('collect',{'amount':'21'})]:self.unchanged(en,self.make(op,p))
        e=self.make('purchase',{'units':'1'});e['postings']=[];self.unchanged(en,e)

    def test_unknown_operation_and_intervention(self):
        en=Engine(self.spec);self.unchanged(en,self.make('lease',{}),'Unsupported')
        self.unchanged(en,self.make('purchase',{'units':'1'},scenario='intervention'),'Unsupported')

    def test_injected_internal_failure_atomic(self):
        def fail(j):raise RuntimeError('injected storage failure')
        en=Engine(self.spec,before_commit=fail)
        self.unchanged(en,self.make('purchase',{'units':'1'}),'InternalFailure')

    def test_balanced_hook_and_provenance_corruption_are_atomic(self):
        def balanced(j):
            for row in j['postings']:row['signed_amount']*=2
        def metadata(j):j['provenance'].append('unauthorised rewrite')
        for hook in (balanced,metadata):
            en=Engine(self.spec,before_commit=hook)
            self.unchanged(en,self.make('purchase',{'units':'1'}),'InternalFailure')
            en.before_commit=None
            self.assertEqual(en.apply(self.make('purchase',{'units':'1'}))['status'],'Applied')
            self.assertEqual(en.balances['inventory'],35)

    def test_dependency_cycle_and_canonical_schedule(self):
        a=self.make('purchase',{'units':'1'},'a',depends=['b']);b=self.make('purchase',{'units':'1'},'b',depends=['a'])
        en=Engine(self.spec);before=en.snapshot();self.assertEqual(en.run([a,b])['status'],'Rejected');self.assertEqual(en.snapshot(),before)
        a['depends']=[];b['depends']=['a'];x=Engine(self.spec);y=Engine(self.spec)
        self.assertEqual(x.run([a,b])['status'],'Complete');self.assertEqual(y.run([b,a])['status'],'Complete');self.assertEqual(x.snapshot(),y.snapshot())

    def test_funding_default_preserves_unpaid_liability_and_last_state(self):
        en=Engine(self.spec);en.apply(self.make('payroll_accrue',{'amount':'1000'},'accrue'))
        r=self.unchanged(en,self.make('payroll_pay',{'amount':'1000'},'pay',depends=['accrue']),'EconomicFundingDefault')
        self.assertEqual(r['cash_shortfall'],'940');self.assertEqual(en.balances['payroll_payable'],-1000)
        self.assertEqual(r['unpaid_obligation'],'1000');self.assertFalse(r['outputs_available'])
        p=deepcopy(self.spec['periods'][0]);p['payroll']='1000';r=execute_period(Engine(self.spec),self.spec,p)
        self.assertEqual(r['status'],'EconomicFundingDefault');self.assertIsNone(r['statements']);self.assertTrue(r['unexecuted'])

    def test_equity_and_par_debt_lifecycles(self):
        en=Engine(self.spec);opening=deepcopy(en.balances)
        for ident,op,p in [('shares','equity_issue',{'shares':'3','price':'4'}),('draw','debt_issue',{'amount':'10'}),
                           ('interest','interest_accrue',{'rate':'0.05','years':'1'}),('pay','interest_pay',{'amount':'5.5'}),
                           ('redeem','debt_redeem',{'amount':'110'}),('close','close',{})]:
            # Cash equity supplies enough for full principal redemption in this bounded case.
            if ident=='redeem':p={'amount':'20'}
            self.assertEqual(en.apply(self.make(op,p,ident))['status'],'Applied')
        r={'status':'Complete','opening':opening,'journals':en.journals,'statements':statements(opening,en.journals)};verify(r)
        self.assertEqual(en.balances['debt'],-90);self.assertEqual(en.balances['capital'],-62)

    def test_full_par_redemption_keeps_financing_bridge(self):
        en=Engine(self.spec);opening=deepcopy(en.balances)
        for ident,op,p in [('raise','equity_issue',{'shares':'50','price':'2'}),
                           ('redeem','debt_redeem',{'amount':'100'}),('close','close',{})]:
            self.assertEqual(en.apply(self.make(op,p,ident))['status'],'Applied')
        s=statements(opening,en.journals)
        verify({'status':'Complete','opening':opening,'journals':en.journals,'statements':s})
        self.assertEqual(s['debt']['closing'],'0');self.assertEqual(s['cash_flow']['direct']['financing'],'0')

    def test_role_date_guard_for_both_consumers(self):
        valid={'value':'0.05','kind':'disclosure','economic_date':'2024-01-01','published':'2024-01-02','ingested':'2024-01-03','roles':['behaviour','measurement']}
        for role in ('behaviour','measurement'):
            self.assertEqual(information(valid,role,'2024-06-30'),F(1,20))
            for key,value in [('economic_date','2025-01-01'),('published','2025-01-01'),('ingested','2025-01-01'),('published',None),('roles',[])]:
                row={**valid,key:value}
                with self.assertRaises(ValueError):information(row,role,'2024-06-30')
        en=Engine(self.spec);bad={**valid,'published':'2025-01-01'}
        self.unchanged(en,self.make('interest_accrue',{'rate':bad,'years':'1'}))
        en.apply(self.make('interest_accrue',{'rate':valid,'years':'1'}));self.assertEqual(en.balances['interest'],5)

    def test_forecast_behaviour_rejects_realized_future_and_accepts_stress(self):
        en=run_northstar(self.spec)['historical_engine'];f=self.spec['forecast']
        records={k:stress_record(v) for k,v in f.items() if k not in ('start','date')}
        self.assertEqual(forecast_period(en,self.spec,'1',records)['sales_consideration'],'300')
        records['demand_units']={'value':'30','roles':['behaviour'],'kind':'realized','economic_date':'2025-12-31','published':'2025-12-31','ingested':'2025-12-31'}
        with self.assertRaises(ValueError):forecast_period(en,self.spec,'1',records)
        with self.assertRaises(ValueError):information(stress_record('7'),'measurement','2025-01-01','historical')

    def test_forecast_does_not_grant_measurement_permission(self):
        en=run_northstar(self.spec)['historical_engine'];before=en.snapshot()
        records={k:stress_record(v) for k,v in self.spec['forecast'].items() if k not in ('start','date')}
        records['fixed_rate']['roles']=['behaviour']
        with self.assertRaisesRegex(ValueError,'role denied'):forecast_period(en,self.spec,'1',records)
        self.assertEqual(en.snapshot(),before)
        with self.assertRaisesRegex(ValueError,'complete explicit'):forecast_period(en,self.spec,'1',{})

    def test_forecast_rejects_future_initial_state(self):
        en=run_northstar(self.spec)['historical_engine'];spec=deepcopy(self.spec)
        spec['forecast']['start']='2024-06-30'
        with self.assertRaisesRegex(ValueError,'future economic state'):forecast_period(en,spec,'1')
        spec['forecast']['start']='2026-01-01'
        with self.assertRaisesRegex(ValueError,'interval reversed'):forecast_period(en,spec,'1')

    def test_forecast_provenance_is_rechecked_at_measurement(self):
        en=run_northstar(self.spec)['historical_engine'];p=forecast_period(en,self.spec,'1')
        p['information_inputs']['fixed_rate']['published']='2026-01-01'
        p['information_inputs']['fixed_rate'].update(kind='disclosure',economic_date='2024-01-01',ingested='2026-01-02')
        before=en.snapshot();r=execute_period(en,self.spec,p)
        self.assertEqual(r['status'],'Rejected');self.assertEqual(en.snapshot(),before)
        self.assertIsNone(r['statements'])

    def test_information_requires_typed_roles_and_kind(self):
        for change in ({'roles':'behaviour measurement'},{'kind':'invented'}):
            with self.assertRaises(ValueError):information({**stress_record('1'),**change},'measurement','2025-01-01','exogenous_stress')

    def test_checker_rejects_identity_cash_endpoints_and_asset_corruption(self):
        base=run_northstar(self.spec)['periods']['2024H1'];bad=[]
        x=deepcopy(base);x['journals'][0]['input_sha256']='0'*64;bad.append(x)
        x=deepcopy(base);x['inputs'][0]['params']['units']='15';bad.append(x)
        x=deepcopy(base);x['journals'][0]['provenance'].append('changed');bad.append(x)
        x=deepcopy(base);x['statements']['cash_flow']['opening']='61';x['statements']['cash_flow']['closing']='61';bad.append(x)
        x=deepcopy(base);x['closing']['assets'][0]['accumulated']='0';bad.append(x)
        x=deepcopy(base);x['closing']['applied'][x['journals'][0]['event_id']]['input_sha256']='bad';bad.append(x)
        for x in bad:
            with self.assertRaises(AssertionError):verify(x)

    def test_checker_requires_named_obligations(self):
        checks=[{'id':i,'passed':True} for i in sorted(REQUIRED_CHECKS)]
        self.assertTrue(coverage(checks)['passed'])
        for i in range(len(checks)):
            report=coverage(checks[:i]+checks[i+1:])
            self.assertFalse(report['passed']);self.assertEqual(report['missing'],[checks[i]['id']])
        self.assertFalse(coverage(checks+[checks[0]])['passed'])

    def test_failed_forecast_prevents_complete_top_level_status(self):
        spec=deepcopy(self.spec);spec['forecast']['payroll']='1000'
        r=run_northstar(spec)
        self.assertEqual(r['status'],'Incomplete')
        self.assertEqual(r['periods']['2025_fixed']['status'],'EconomicFundingDefault')
        self.assertEqual(r['periods']['2025_floating']['status'],'EconomicFundingDefault')
        self.assertTrue(r['periods']['2025_fixed']['unexecuted'])

    def test_revision_views_and_unknown_availability(self):
        old,corrected,annual=self.spec['revision_views']
        self.assertEqual(information({**old,'value':old['revenue']},'behaviour','2024-08-03'),120)
        with self.assertRaises(ValueError):information({**corrected,'value':corrected['revenue']},'behaviour','2024-08-03')
        with self.assertRaises(ValueError):compatible_difference(annual,old,'2025-03-03')
        self.assertEqual(compatible_difference(annual,corrected,'2025-03-03'),150)

    def test_branch_isolation_order_mass_and_conditioning(self):
        en=run_northstar(self.spec)['historical_engine'];before=en.snapshot()
        atoms=[{'id':n,'weight':'1/3','hypothesis':{'fixed_fraction':a,'payroll':p,'operation':o}} for n,a,p,o in [('ok','1','50','supported'),('bad','0','1000','supported'),('unknown','0','50','lease')]]
        x=branch_family(en,self.spec,atoms);y=branch_family(en,self.spec,list(reversed(atoms)))
        self.assertEqual(en.snapshot(),before);self.assertEqual({a['id']:a for a in x['atoms']},{a['id']:a for a in y['atoms']})
        self.assertEqual(x['summary']['mass'],{'Complete':'1/3','EconomicFundingDefault':'1/3','Unsupported':'1/3'})
        self.assertIsNone(x['summary']['mean']);self.assertFalse(x['summary']['normalised_over_successful_only'])
        z=branch_family(en,self.spec,atoms,'conditioning',{'ok':'1','bad':'1/2','unknown':'0'})
        self.assertEqual(z['summary']['mass']['Complete'],'2/3')
        self.assertEqual([a['weight'] for a in x['atoms']],['1/3']*3)

    def test_p03_p04_joint_adapter(self):
        from test_accounting_p03 import BASE,bindings
        from core0_frontends_v1 import compile_source
        b=bindings();c=compile_source(BASE,b);r=p03_family(c.ir,b)
        self.assertEqual(r['joint']['bounds']['lower']['value'],'5');self.assertEqual(r['joint']['bounds']['upper']['value'],'7')
        for e in r['endpoints']:self.assertEqual(F(e['fixed'])+F(e['floating']),100)
        self.assertIsNone(r['probabilities'])

    def test_branch_payroll_provenance_matches_consumed_input(self):
        en=run_northstar(self.spec)['historical_engine']
        atoms=[{'id':'changed','weight':'1','hypothesis':{'fixed_fraction':'1','payroll':'60','operation':'supported'}}]
        result=branch_family(en,self.spec,atoms)['atoms'][0]['execution']
        self.assertEqual(result['status'],'Complete');verify(result)
        self.assertEqual(result['statements']['income']['payroll'],'60')
        for supplied in result['inputs']:
            records=supplied['provenance'][1]['information_inputs']
            self.assertEqual(records['payroll'],stress_record('60'))
            if supplied['op'] in ('payroll_accrue','payroll_pay'):
                self.assertEqual(supplied['params']['amount'],records['payroll']['value'])
        # The family must call the same guarded constructor with the actual
        # hypothesis before either behaviour or measurement can consume it.
        def deny_payroll(value,at='2025-01-01'):
            record=stress_record(value,at)
            if str(value)=='60':record['roles']=['measurement']
            return record
        with patch('company_execution_v1.stress_record',side_effect=deny_payroll):
            rejected=branch_family(en,self.spec,atoms)['atoms'][0]['execution']
        self.assertEqual(rejected['status'],'Rejected')
        self.assertIn('role denied',rejected['reason'])
        self.assertEqual(rejected['last_committed_state'],en.snapshot())

    def test_invalid_branch_retains_mass_and_other_branches(self):
        en=run_northstar(self.spec)['historical_engine'];before=en.snapshot()
        atoms=[{'id':ident,'weight':'1/3','hypothesis':{'fixed_fraction':alpha,'payroll':pay,'operation':'supported'}}
               for ident,alpha,pay in [('bad_alpha','2','50'),('bad_payroll','1','NaN'),('valid','1','60')]]
        result=branch_family(en,self.spec,atoms)
        self.assertEqual(result['summary']['mass'],{'Rejected':'2/3','Complete':'1/3'})
        self.assertIsNone(result['summary']['mean'])
        self.assertFalse(result['summary']['normalised_over_successful_only'])
        self.assertEqual(en.snapshot(),before)
        reordered=branch_family(en,self.spec,list(reversed(atoms)))
        self.assertEqual({a['id']:a for a in result['atoms']},{a['id']:a for a in reordered['atoms']})
        for a in result['atoms']:
            if a['status']=='Rejected':
                self.assertEqual(a['execution']['last_committed_state'],before)
                self.assertEqual(a['execution']['journals'],[])
                self.assertIsNone(a['outcome'])
            else:verify(a['execution'])
        conditional=branch_family(en,self.spec,atoms,'conditioning',{'bad_alpha':'1','bad_payroll':'1','valid':'0'})
        self.assertEqual(conditional['summary']['mass']['Rejected'],'1')
        self.assertIsNone(conditional['summary']['mean'])
        invalid=deepcopy(atoms);invalid[0]['weight']='1/2'
        with patch('company_execution_v1.forecast_period',side_effect=AssertionError('law must be validated first')):
            with self.assertRaisesRegex(ValueError,'sum to one'):branch_family(en,self.spec,invalid)

    def test_apple_conditional_and_source_distinctions(self):
        r=apple_conditional();verify({**r,'status':'Complete'})
        self.assertEqual(r['delta_usd']['cash'],'-72875000');self.assertTrue(r['exposure_is_not_inferred_from_notional'])
        self.assertEqual(apple_conditional('0')['delta_usd']['cash'],'0')
        self.assertEqual(apple_conditional('1000000000')['delta_usd']['cash'],'-5000000')
        obs=r['source_observations'];self.assertEqual(len(obs),4)
        self.assertIn('principal',{o['measurement'] for o in obs});self.assertIn('carrying_amount',{o['measurement'] for o in obs})
        self.assertTrue(all(o['source_readings'] for o in obs));self.assertTrue(r['unresolved_operations'])
        self.assertEqual(r['delta_usd']['cash'],r['statements']['flat']['cash_change'])
        self.assertEqual(r['delta_usd']['profit'],r['statements']['income']['profit'])
        self.assertEqual(F(r['delta_usd']['equity']),F(r['statements']['equity']['closing'])-F(r['statements']['equity']['opening']))

    def test_period_boundary_and_real_case_default(self):
        self.unchanged(Engine(self.spec),self.make('purchase',{'units':'1'},period='2024H1',date_='2024-12-31'))
        r=apple_conditional('100000000000000')
        self.assertEqual(r['status'],'EconomicFundingDefault');self.assertIsNone(r['statements']);self.assertIsNone(r['delta_usd'])
        self.assertEqual(r['last_committed_state']['balances']['interest_payable'],'-500000000000')

    def test_deterministic_replay_and_asset_schedule(self):
        x=run_northstar(self.spec);y=run_northstar(self.spec)
        self.assertEqual(x['periods'],y['periods'])
        e=x['historical_engine'];self.assertEqual(sum(a['cost'] for a in e.assets),e.balances['plant_cost'])
        self.assertEqual(sum(a['accumulated'] for a in e.assets),-e.balances['accum_depreciation'])
        self.assertEqual(x['periods']['2025_fixed']['statements']['plant']['depreciation'],'13')

if __name__=='__main__':unittest.main()
