"""P11 conformance checks; mocked engines never establish integration."""
import copy
from dataclasses import replace
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import demo_debt_execution_v1 as d
import accounting_integrations_v1 as a
import core0_ir_v1 as ir
from core0_frontends_v1 import compile_source


class Frontends(unittest.TestCase):
    def compare(self, options, alpha, name):
        source, typed, bindings, textual, constructed=d.matched_case(**options)
        assignments={'share' if options.get('renamed') else 'alpha':alpha}
        left=d.execute(textual,bindings,assignments=assignments,alternative=name)
        right=d.execute(constructed,bindings,assignments=assignments,alternative=name)
        self.assertEqual(left,right)
        # Independently expressed Decimal oracle; no runtime rounding helper.
        p=Decimal(str(options.get('principal',100)))
        x=Decimal(alpha.numerator)/Decimal(alpha.denominator)
        rate=Decimal(options.get('stress','0.07'))
        interest=(p*(x*Decimal('0.05')+(1-x)*rate)).quantize(Decimal('0.01'),rounding=ROUND_HALF_EVEN)
        cash=Decimal(str(options.get('cash',p-5)))
        self.assertEqual(F(left['interest']),F(interest))
        if cash>=interest:
            expected={'cash':cash-interest,'debt':p,'profit':-interest,'equity':cash-p-interest}
            for key,value in expected.items(): self.assertEqual(F(left['reports'][key]),F(value))
            self.assertEqual(left['balances']['InterestExpense'],'0')
        return bindings,textual,left

    def test_baseline_endpoints(self):
        for x,name in [(F(1),'allFixed'),(F(0),'allFloating')]: self.compare({},x,name)

    def test_principal_and_stress(self):
        for x,name in [(F(1),'allFixed'),(F(0),'allFloating')]:
            self.compare({'principal':150,'stress':'0.08'},x,name)

    def test_conditioned_interior(self):
        self.compare({'interior':True},F(1,4),'conditioned')

    def test_renamed(self):
        self.compare({'renamed':True},F(0),'floating')

    def test_formatting(self):
        source,_,b,m,_=d.matched_case()
        formatted=compile_source('\n\n'+source.replace(';',';\n'),b)
        self.assertTrue(formatted.ok)
        self.assertEqual(ir.semantic_projection(m),ir.semantic_projection(formatted.ir))

    def test_half_even_and_execution_ties(self):
        for x,y in [('1.005','1'),('1.015','1.02'),('-1.005','-1'),('-1.015','-1.02')]:
            self.assertEqual(d.round_money(F(x)),F(y))
        for p in (100.10,100.30): self.compare({'principal':p},F(1),'allFixed')

    def test_default_atomicity(self):
        _,_,result=self.compare({'cash':4},F(1),'allFixed')
        self.assertEqual(result['status'],'Defaulted')
        self.assertEqual(result['unpaid_interest'],'5')
        self.assertEqual(result['balances']['Cash'],'4')
        self.assertEqual(result['balances']['InterestExpense'],'0')
        self.assertEqual([e['payload']['operation'] for e in result['events'].values()],['reset'])

    def test_branch_rejection_and_isolation(self):
        _,_,b,m,_=d.matched_case()
        before=copy.deepcopy(m)
        with self.assertRaisesRegex(ValueError,'BranchConstraint'): d.execute(m,b,assignments={'alpha':0},alternative='allFixed')
        with self.assertRaisesRegex(ValueError,'SymbolDomain'): d.execute(m,b,assignments={'alpha':2},alternative='allFixed')
        left=d.execute(m,b,assignments={'alpha':1},alternative='allFixed')
        right=d.execute(m,b,assignments={'alpha':0},alternative='allFloating')
        self.assertEqual(m,before); self.assertNotEqual(left['run_id'],right['run_id'])
        self.assertEqual(left,d.execute(m,b,assignments={'alpha':1},alternative='allFixed'))

    def test_invalid_context_unit_calendar(self):
        source,_,b,m,_=d.matched_case()
        for altered in [source.replace('100 USD','100 EUR'),source.replace('0.05 per year','0.05')]:
            self.assertFalse(compile_source(altered,b).ok)
        altered=copy.deepcopy(m);altered['books'][0]['currency']='EUR'
        with self.assertRaises(ValueError): d.execute(altered,b,assignments={'alpha':1},alternative='allFixed')
        with self.assertRaises(ValueError): d.execute(m,replace(b,calendar_name='Unknown'),assignments={'alpha':1},alternative='allFixed')

    def test_poison_expected_and_digest(self):
        package=json.loads(d.PACKAGE.read_text());package['expected']={'allFixed':{'interest':'999999'}}
        with tempfile.TemporaryDirectory() as directory:
            # P03 intentionally permits only its fixed package-relative path.
            # Use an isolated root; do not weaken that check or edit the fixture.
            path=Path(directory)/'docs/design/fixtures/demo-debt-package.json'
            path.parent.mkdir(parents=True);path.write_text(json.dumps(package))
            with patch.object(ir,'ROOT',Path(directory)):
                source,typed,b,m,n=d.matched_case(package_path=path)
                result=d.execute(m,b,assignments={'alpha':1},alternative='allFixed',package_path=path)
                self.assertEqual(result['interest'],'5')
                self.assertEqual(result,d.execute(n,b,assignments={'alpha':1},alternative='allFixed',package_path=path))
                path.write_text(path.read_text()+' ')
                with self.assertRaisesRegex(ValueError,'PackageDigest'): d.execute(m,b,assignments={'alpha':1},alternative='allFixed',package_path=path)

    def test_replay_conflict_and_unbalanced_atomicity(self):
        book=d.EventBook({'Cash':10,'Expense':0})
        self.assertTrue(book.commit('a',{'date':'2026-12-31'},{'Cash':-1,'Expense':1}))
        self.assertFalse(book.commit('a',{'date':'2026-12-31'},{'Cash':-1,'Expense':1}))
        before=dict(book.balances)
        with self.assertRaisesRegex(ValueError,'EventConflict'): book.commit('a',{'date':'2026-12-30'},{'Cash':-1,'Expense':1})
        with self.assertRaisesRegex(ValueError,'InvalidPosting'): book.commit('b',{}, {'Cash':-2,'Expense':1})
        self.assertEqual(book.balances,before)


class Adapters(unittest.TestCase):
    def test_ledger_selection_all_combinations(self):
        for mask in range(8):
            rows=[{'name':n,'status':'Available' if mask & (1<<i) else 'Unavailable',
                   'version':'test-only','location':'mock-only'} for i,n in enumerate(a.LEDGER_ORDER)]
            expected=next((r['name'] for r in rows if r['status']=='Available'),None)
            self.assertEqual(a.select_ledger(list(reversed(rows))),expected)

    def test_timeout_and_malformed_output(self):
        result=a.capture([sys.executable,'-B','-c','import time; time.sleep(1)'],timeout=0.02)
        self.assertTrue(result['timeout'])
        with self.assertRaisesRegex(ValueError,'timeout'):a.decode_exchange(result)
        for text in ['{}','not-json','[]']:
            with self.assertRaises(ValueError):a.decode_exchange({'timeout':False,'exit_code':0,'stdout':text})

    def test_no_import_only_success(self):
        record=a.request_record('test',None,['valuation.json'],{'currency':'USD'},'lballabio/QuantLib')
        a.validate_record(record)
        record['status']='Passed'
        with self.assertRaisesRegex(ValueError,'without'):a.validate_record(record)

    def test_fixture_hash_rejection(self):
        row=a.request_record('test',None,['valuation.json'],{},'lballabio/QuantLib')
        row['inputs'][0]['bytes']='poison'
        with self.assertRaisesRegex(ValueError,'hash'):a.validate_record(row)

    def test_success_payload_requires_semantic_evidence_and_pin(self):
        # Synthetic response checks the validator only, never engine availability.
        row=a.request_record('QuantLib',None,['valuation.json'],{},'lballabio/QuantLib')
        engine={'version':'test-only','location':'mock-only','status':'Available'}
        value={'present_value':100.0,'absolute_error':'0','year_fraction':1,
               'currency':'USD','evaluation_date_restored':True,
               'evaluation_date':'2025-12-31','payment_date':'2026-12-31'}
        response={'executed':True,'version':'test-only','location':'mock-only','result':value}
        row.update(status='Passed',engine=engine,evidence_class='upstream_execution_attempt',
                   normalized_output=value,execution={'timeout':False,'exit_code':0,'stdout':json.dumps(response)})
        self.assertTrue(a.validate_record(row))
        wrong=copy.deepcopy(row);wrong['engine']['version']='changed'
        with self.assertRaisesRegex(ValueError,'version'):a.validate_record(wrong)
        for key,new_value in [('present_value',101),('year_fraction',2),('currency','EUR'),
                              ('evaluation_date_restored',False),('evaluation_date','2024-12-31'),
                              ('payment_date','2027-12-31')]:
            wrong=copy.deepcopy(row);wrong['normalized_output'][key]=new_value
            changed=copy.deepcopy(response);changed['result']=wrong['normalized_output']
            wrong['execution']['stdout']=json.dumps(changed)
            with self.assertRaisesRegex(ValueError,'semantics'):a.validate_record(wrong)

    def test_selected_failure_never_substitutes_backend(self):
        candidates=[{'name':name,'status':'Available','version':'test-only','location':'mock-only',
                     'reason':'simulated discovery; boundary test only'}
                    for name in a.LEDGER_ORDER]
        self.assertEqual(a.select_ledger(candidates),'beancount')
        row=a.request_record('ledger',candidates[0],['journal.beancount'],{},'beancount/beancount')
        failure={'exit_code':1,'timeout':False,'stdout':'','stderr':'test failure'}
        with patch.object(a,'capture',return_value=failure) as capture:
            a.run_exchange(row,'beancount')
        self.assertEqual(row['status'],'Failed')
        self.assertEqual(row['engine']['name'],'beancount')
        self.assertEqual(capture.call_count,1)
        with self.assertRaises(ValueError):a.select_ledger(candidates+[candidates[0]])

    def test_unavailable_exchange_has_no_output(self):
        row=a.request_record('QuantLib',None,['valuation.json'],{},'lballabio/QuantLib')
        row['normalized_output']={}
        with self.assertRaisesRegex(ValueError,'Unavailable'):a.validate_record(row)

    def test_failed_ledger_discovery_is_not_unavailable(self):
        def module_probe(module, distribution):
            return {'name':module,'distribution':distribution,'version':None,'location':None,
                    'status':'Failed' if module=='beancount' else 'Unavailable',
                    'reason':'probe timeout' if module=='beancount' else 'module absent','probe':None}
        def cli_probe(name):
            return {'name':name,'version':None,'location':None,'status':'Unavailable',
                    'reason':'executable absent','probe':None}
        with patch.object(a,'probe_python',side_effect=module_probe), patch.object(a,'probe_executable',side_effect=cli_probe):
            records=a.collect()
        row=next(r for r in records['adapters'] if r['family']=='ledger')
        self.assertIsNone(records['ledger_selection']['selected_backend'])
        self.assertEqual(row['status'],'Failed')
        self.assertEqual(row['diagnostics'][0]['reason'],'probe timeout')
        self.assertIsNone(row['execution'])
        self.assertTrue(a.validate_record(row))

    def test_extraction_failure_cannot_pass_with_expected_cells(self):
        doc={'document':{'tables':[]},'status':'success',
             'table_cells':[['Account','USD'],['Cash','90'],['Debt','100']]}
        a.validate_output('Docling',doc)
        for status in ['partial_success','failure',None]:
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError,'semantics'):
                    a.validate_output('Docling',dict(doc,status=status))
        with self.assertRaisesRegex(ValueError,'diagnostics'):
            a.validate_output('Arelle',{'diagnostics':['schemaImportError'],'facts':[]})

    def test_ledger_checks_dates_and_individual_postings(self):
        postings=[{'Assets:Cash':'95','Liabilities:Debt':'-100','Equity:Retained':'5'},
                  {'Expenses:Interest':'5','Assets:Cash':'-5'},
                  {'Equity:Retained':'5','Expenses:Interest':'-5'}]
        result={'balances':{'Assets:Cash':'90','Liabilities:Debt':'-100',
                            'Equity:Retained':'10','Expenses:Interest':'0'},'errors':[],
                'transactions':[{'date':date,'postings':[{'account':k,'amount':v,'currency':'USD'}
                                  for k,v in p.items()]} for date,p in zip(
                                  ['2025-12-31','2026-12-31','2026-12-31'],postings)]}
        a.validate_output('ledger',result)
        wrong=copy.deepcopy(result);wrong['transactions'][1]['date']='2026-12-30'
        with self.assertRaisesRegex(ValueError,'dates'):a.validate_output('ledger',wrong)
        wrong=copy.deepcopy(result);wrong['transactions'][1]['postings'][0]['amount']='6'
        with self.assertRaisesRegex(ValueError,'postings'):a.validate_output('ledger',wrong)


if __name__=='__main__': unittest.main()
