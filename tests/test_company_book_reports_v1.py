from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import company_book_reports_v1 as reports
spec=importlib.util.spec_from_file_location('company_report_examples',ROOT/'data/accounting-master/company-book-reports-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)


def rehash(body):
    for key in ['opening','closing','mapping']:body['expected_'+key+'_sha256']=reports.digest(body[key])


class CompanyReportTests(unittest.TestCase):
    def result(self,body,status):
        original=deepcopy(body);result=reports.report(body)
        self.assertEqual(result['status'],status,result);self.assertEqual(body,original)
        for flag in reports.FLAGS:self.assertFalse(result[flag])
        return result

    def test_independent_and_native_comparisons(self):
        result=ex.compare();self.assertEqual(len(result['cases']),5);self.assertEqual(len(result['checks']),42)
        self.assertEqual([x['name'] for x in result['checks'] if not x['passed']],[])

    def test_complete_sale_and_capital_statements(self):
        result=self.result(ex.sale_and_equity(),'reported')
        self.assertEqual(result['balance_sheet'],{'total_assets':'160/1','total_liabilities':'30/1','equity_including_profit':'130/1'})
        self.assertEqual(result['income'],{'income':'40/1','expenses':'15/1','profit':'25/1'})
        self.assertEqual(result['cash_flows']['activities'],{
            'operating':{'receipts':'40/1','payments':'0/1','net':'40/1'},
            'investing':{'receipts':'0/1','payments':'0/1','net':'0/1'},
            'financing':{'receipts':'5/1','payments':'0/1','net':'5/1'}})
        self.assertEqual(result['equity']['opening'],'100/1');self.assertEqual(result['equity']['direct_movements'],'5/1')

    def test_grouped_map_preserves_all_accounts(self):
        body=ex.sale_and_equity();assets=[x for x in body['mapping']['lines'] if x['classification']=='asset']
        body['mapping']['lines']=[x for x in body['mapping']['lines'] if x['classification']!='asset']
        body['mapping']['lines'].append({'id':'assets','label':'All declared assets','classification':'asset','accounts':[k for row in assets for k in row['accounts']]});rehash(body)
        result=self.result(body,'reported');self.assertEqual(result['statement_lines']['asset'][0]['closing'],'160/1')

    def test_missing_duplicate_unknown_and_wrong_class_accounts(self):
        for kind in ['missing','duplicate','unknown','wrong_class','duplicate_line']:
            body=ex.payment();lines=body['mapping']['lines']
            if kind=='missing':lines.pop()
            elif kind=='duplicate':lines[0]['accounts'].append(lines[1]['accounts'][0])
            elif kind=='unknown':lines[0]['accounts']=['not-declared']
            elif kind=='wrong_class':lines[0]['classification']='liability'
            else:lines[1]['id']=lines[0]['id']
            rehash(body);self.result(body,'invalid')

    def test_missing_and_incorrect_equity_explanations(self):
        for kind in ['missing','amount','account','duplicate','unrecorded','date']:
            body=ex.sale_and_equity();row=body['equity_movements'][0]
            if kind=='missing':body['equity_movements']=[]
            elif kind=='amount':row['amount']='4/1'
            elif kind=='account':row['account']=body['opening']['cash_account']
            elif kind=='duplicate':body['equity_movements'].append(deepcopy(row))
            elif kind=='unrecorded':row['event_id']='invented'
            else:row['date']='2028-01-01'
            self.result(body,'invalid')

    def test_cash_flow_omission_and_unexplained_extra_flow(self):
        body=ex.payment();body['closing']['flows']=[];rehash(body)
        self.assertEqual(self.result(body,'invalid')['reason'],'statement_reconciliation')
        body=ex.payment();row=deepcopy(body['closing']['flows'][0]);row['id']='extra';body['closing']['flows'].append(row);rehash(body)
        self.result(body,'invalid')

    def test_gross_flows_preserve_receipts_and_payments(self):
        body=ex.payment();row=body['closing']['flows'][0];row['amount']='-10/1'
        receipt=deepcopy(row);receipt.update(id='refund',amount='13/2');body['closing']['flows'].append(receipt);rehash(body)
        result=self.result(body,'reported')
        self.assertEqual(result['cash_flows']['activities']['financing'],{'receipts':'13/2','payments':'10/1','net':'-7/2'})
        self.assertEqual(result['cash_flows']['gross_origins'],body['closing']['flows'])

    def test_opening_closed_period_and_history_requirements(self):
        body=ex.sale_and_equity();body['opening']['balances'].update({'sales.alpha':'-1/1','capital.alpha':'-99/1'});rehash(body)
        self.assertEqual(self.result(body,'invalid')['reason'],'opening_temporary_balance')
        body=ex.payment();body['opening']['date']='2027-01-02';rehash(body);self.result(body,'invalid')
        body=ex.payment();body['opening']['seen']=['old'];rehash(body);self.result(body,'invalid')

    def test_snapshot_correspondence_and_stale_hashes(self):
        body=ex.payment();body['closing']['date']='2027-01-03';self.result(body,'invalid')
        for key in ['context','period','accounts','cash_account']:
            body=ex.payment()
            if key=='context':body['mapping']['context']['entity']='other'
            elif key=='period':body['closing']['period']['end_exclusive']='2029-01-01'
            elif key=='accounts':body['closing']['accounts']['machine.alpha']['classification']='expense'
            else:body['closing']['cash_account']='machine.alpha'
            rehash(body);self.result(body,'invalid')

    def test_notes_keep_unknowns_and_cannot_claim_completeness(self):
        body=ex.payment();result=self.result(body,'reported');self.assertEqual(result['notes'],body['notes'])
        body['notes'][0]['status']='complete';self.result(body,'invalid')
        body=ex.payment();body['notes'].append(deepcopy(body['notes'][0]));self.result(body,'invalid')
        body=ex.payment();body['notes'][0]['reason']='';self.result(body,'invalid')

    def test_contra_income_and_expense_signs_remain_signed(self):
        body=ex.sale_and_equity();closing=body['closing']
        closing['balances'].update({'sales.alpha':'5/1','cost.alpha':'-2/1','bank.alpha':'117/1'})
        closing['flows'][0]['amount']='12/1';rehash(body)
        result=self.result(body,'reported');self.assertEqual(result['income'],{'income':'-5/1','expenses':'-2/1','profit':'-3/1'})
        self.assertEqual(result['equity']['closing'],'102/1')

    def test_native_annual_memory_can_change_without_reporting_migration(self):
        body,native=ex.native_annual();self.assertNotEqual(body['opening']['memory_schema'],body['closing']['memory_schema'])
        result=self.result(body,'reported');self.assertEqual(result['income']['profit'],'99/2')
        self.assertEqual(result['cash_flows']['closing_cash'],'983/2')
        self.assertEqual(result['equity']['closing'],'1343/2')
        self.assertIn('Indirect operating cash-flow bridge',result['unresolved'])

    def test_replay_is_type_sensitive_and_complete(self):
        body=ex.payment();result=self.result(body,'reported');self.assertTrue(reports.verify(body,result))
        for key,value in [('fiscal_complete',0),('income',{}),('notes',[]),('scope','annual_complete')]:
            altered=deepcopy(result);altered[key]=value;self.assertFalse(reports.verify(body,altered))

    def test_dependency_and_resource_limits(self):
        from unittest.mock import patch
        body=ex.payment()
        with patch.object(reports,'BOOK_SHA256','0'*64):self.result(body,'invalid')
        body=ex.payment();body['mapping']['lines'][0]['label']='x'*4097;rehash(body);self.result(body,'invalid')
        body=ex.payment();body['mapping']['lines']*=257;rehash(body);self.result(body,'invalid')

    def test_prior_event_cannot_supply_current_period_cash_flow(self):
        body=ex.payment();body['opening']['seen']=['historic'];body['closing']['seen'].insert(0,'historic')
        body['closing']['flows'][0]['event_id']='historic';rehash(body)
        self.result(body,'invalid')


if __name__=='__main__':unittest.main()
