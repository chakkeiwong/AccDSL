from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import company_book_carry_v1 as carry
spec=importlib.util.spec_from_file_location('company_carry_examples',ROOT/'data/accounting-master/company-book-carry-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)


def rehash(body):
    req=body['report_request']
    for key in ['opening','closing','mapping']:req['expected_'+key+'_sha256']=carry.digest(req[key])
    body['expected_report_sha256']=carry.digest(carry.reports.report(req))


class CompanyCarryTests(unittest.TestCase):
    def result(self,body,status='proposed'):
        original=deepcopy(body);result=carry.propose(body);self.assertEqual(result['status'],status,result)
        self.assertEqual(body,original)
        for flag in carry.FLAGS:self.assertFalse(result[flag])
        return result

    def test_independent_and_native_balance_comparisons(self):
        r=ex.compare();self.assertEqual(len(r['cases']),4);self.assertEqual([x['name'] for x in r['checks'] if not x['passed']],[])

    def test_profit_and_loss_closing_signs(self):
        for loss,expected,journal in [(False,'-130/1','-25/1'),(True,'-102/1','3/1')]:
            body=ex.fixture(loss=loss);r=self.result(body)
            self.assertEqual(r['next_opening']['balances']['capital.alpha'],expected)
            self.assertEqual(r['journal']['capital.alpha'],journal)
            self.assertEqual(r['next_opening']['balances']['sales.alpha'],'0/1')
            self.assertEqual(r['next_opening']['balances']['cost.alpha'],'0/1')
            self.assertEqual(r['next_opening']['memory'],body['report_request']['closing']['memory'])

    def test_typed_reset_and_next_start_policy(self):
        body=ex.fixture();book=body['report_request']['closing']
        book['memory']['loan']['paid']='7/1';rehash(body)
        body['memory_policies']['/loan/paid']={'kind':'reset','type':book['memory_types']['/loan/paid'],'value':'0/1','provenance':'Explicit period counter reset'}
        body['memory_policies']['/loan/last_date']={'kind':'next_period_start','provenance':'Explicit authored start-date policy'}
        r=self.result(body);self.assertEqual(r['next_opening']['memory']['loan']['last_date'],'2028-01-01')
        self.assertEqual(r['next_opening']['memory']['loan']['paid'],'0/1')
        self.assertEqual(r['closed_book']['memory'],book['memory'])

    def test_missing_extra_unknown_or_empty_policy_refused(self):
        for kind in ['missing','extra','unknown','empty']:
            body=ex.fixture()
            if kind=='missing':body['memory_policies'].pop('/loan/paid')
            elif kind=='extra':body['memory_policies']['/absent']={'kind':'preserve','provenance':'supplied'}
            elif kind=='unknown':body['memory_policies']['/loan/paid']['kind']='infer'
            else:body['memory_policies']['/loan/paid']['provenance']=''
            self.result(body,'invalid')

    def test_reset_units_and_date_types_cannot_be_changed(self):
        body=ex.fixture();typ=deepcopy(body['report_request']['closing']['memory_types']['/loan/paid']);typ['dimensions']={'goods:unit':1}
        body['memory_policies']['/loan/paid']={'kind':'reset','type':typ,'value':'0/1','provenance':'wrong unit'};self.result(body,'invalid')
        body=ex.fixture();body['memory_policies']['/loan/paid']={'kind':'next_period_start','provenance':'wrong type'};self.result(body,'invalid')

    def test_period_endpoint_required_without_completeness_promotion(self):
        body=ex.fixture();body['report_request']['closing']['date']='2027-12-30';rehash(body)
        self.assertEqual(self.result(body,'invalid')['reason'],'last_period_day_required')
        for day in ['2028-01-01','2027-12-31','tomorrow']:
            body=ex.fixture();body['next_end_exclusive']=day;self.result(body,'invalid')
        self.assertFalse(self.result(ex.fixture())['fiscal_complete'])

    def test_named_equity_account_and_close_identity(self):
        for account in ['bank.alpha','missing']:
            body=ex.fixture();body['retained_account']=account;self.result(body,'invalid')
        body=ex.fixture();body['close_id']='sale';self.assertEqual(self.result(body,'invalid')['reason'],'duplicate_close_id')

    def test_stale_report_and_invalid_report_refused(self):
        body=ex.fixture();body['expected_report_sha256']='0'*64;self.result(body,'invalid')
        body=ex.fixture();body['report_request']['equity_movements']=[];rehash(body);self.result(body,'invalid')

    def test_rehashed_tampered_results_rejected(self):
        for kind in ['flag','memory','journal','archive']:
            body=ex.fixture();r=self.result(body)
            if kind=='flag':r['committed']=0
            elif kind=='memory':r['next_opening']['memory']['untouched']['tag']='lost'
            elif kind=='journal':r['journal']['capital.alpha']='0/1'
            else:r['archive']['report_sha256']='0'*64
            self.assertEqual(carry.apply(body,r)['status'],'invalid')

    def test_archive_binds_all_prior_and_successor_values(self):
        body=ex.fixture();r=self.result(body);a=r['archive']
        self.assertEqual(a['report_sha256'],carry.digest(r['report']))
        self.assertEqual(a['closing_before_sha256'],carry.digest(body['report_request']['closing']))
        self.assertEqual(a['next_opening_sha256'],carry.digest(r['next_opening']))
        self.assertEqual(a['memory_policies_sha256'],carry.digest(body['memory_policies']))

    def test_dependency_and_invalid_literal(self):
        with patch.object(carry,'REPORT_SHA256','0'*64):self.result(ex.fixture(),'invalid')
        body=ex.fixture();typ=body['report_request']['closing']['memory_types']['/loan/paid']
        body['memory_policies']['/loan/paid']={'kind':'reset','type':typ,'value':'unknown','provenance':'cannot invent reset'}
        self.result(body,'invalid')

    def test_zero_profit_has_zero_closing_journal(self):
        req=ex.reports.payment();req['closing']['date']='2027-12-31';req['expected_closing_sha256']=carry.digest(req['closing'])
        body=carry.request(req,'zero-close','capital.alpha','2029-01-01',ex.policies(req['closing']))
        r=self.result(body);self.assertEqual(set(r['journal'].values()),{'0/1'})
        self.assertEqual(r['next_opening']['balances'],req['closing']['balances'])

    def test_explicit_retained_account_preserves_other_equity(self):
        body=ex.fixture();req=body['report_request']
        for book in [req['opening'],req['closing']]:
            book['accounts']['retained']={'classification':'equity'};book['balances']['retained']='0/1'
        req['mapping']['lines'].append({'id':'retained','label':'Retained income','classification':'equity','accounts':['retained']})
        body['retained_account']='retained';rehash(body);r=self.result(body)
        self.assertEqual(r['next_opening']['balances']['retained'],'-25/1')
        self.assertEqual(r['next_opening']['balances']['capital.alpha'],'-105/1')

    def test_next_period_report_and_second_close_keep_lifetime_history(self):
        body=ex.fixture();first=self.result(body);opening=first['next_opening'];closing=deepcopy(opening);closing['date']='2028-12-31'
        old=body['report_request'];req=carry.reports.request(opening,closing,old['schemas'],old['mapping'])
        next_body=carry.request(req,'close.2028','capital.alpha','2030-01-01',ex.policies(closing));second=self.result(next_body)
        self.assertEqual(second['next_opening']['seen'],['sale','capital_contribution','close.2027','close.2028'])
        self.assertEqual(second['next_opening']['balances'],first['next_opening']['balances'])
        next_body['close_id']='close.2027';self.result(next_body,'invalid')

    def test_fiscal_period_endpoint_is_explicit(self):
        body=ex.fixture();req=body['report_request']
        for book in [req['opening'],req['closing']]:book['period']['end_exclusive']='2027-07-01'
        req['closing']['date']='2027-06-30';body['next_end_exclusive']='2028-07-01';rehash(body)
        r=self.result(body);self.assertEqual(r['next_opening']['period'],{'start':'2027-07-01','end_exclusive':'2028-07-01'})


if __name__=='__main__':unittest.main()
