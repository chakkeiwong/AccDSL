from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import conditional_company_continuation_v1 as continuation
import declared_operating_methods_v1 as helper
from test_conditional_company_opening_v1 import request as opening_request


def fixture(owner='alpha',selected=(10,2,3),amount='1/1'):
    engine=continuation.engine;core=continuation.core
    source_request=opening_request(owner,selected);opened=continuation.source.map_opening(source_request)
    book=opened['opening'];money=engine.money_type(book);ident='synthetic.distribution'
    cash=book['cash_account'];equity=next(k for k,v in book['accounts'].items() if v['classification']=='equity')
    zero=helper.constant(money,'0/1');negative=helper.binary('sub',zero,helper.ref('amount'))
    pre_types={'approved':core.BOOL,'amount':money,'cash':money}
    pre=helper.conditions(ident,pre_types,[('approved',helper.ref('approved'),['approved'],'unsupported'),
        ('positive',helper.binary('lt',deepcopy(zero),helper.ref('amount')),['amount'],'invalid'),
        ('cash_available',helper.binary('le',helper.ref('amount'),helper.ref('cash')),['amount','cash'],'invalid')])
    post=helper.conditions(ident,{'cash':money},[('cash_nonnegative',helper.binary('le',deepcopy(zero),helper.ref('cash')),['cash'],'invalid')])
    empty={'type':'object','properties':{},'required':[],'additionalProperties':False};h=core.digest(empty)
    method={'profile':engine.METHOD,'id':ident,'version':'1','context':deepcopy(book['context']),
        'account_map':{'cash':cash,'equity':equity},
        'preconditions':{'manifest':pre,'bindings':{'approved':helper.event('approved'),'amount':helper.event('amount'),'cash':helper.account('cash')}},
        'postconditions':{'manifest':post,'bindings':{'cash':helper.account('cash')}},
        'monetary':{'definition':{'profile':engine.monetary.PROFILE,'method_id':ident,'version':'1',
            'inputs':{'amount':helper.declaration(money,'amount')},'calculations':[],
            'accounts':{'cash':deepcopy(money),'equity':deepcopy(money)},'cash_account':'cash',
            'postings':[{'id':'cash','account':'cash','expression':deepcopy(negative),'requires':['amount']},
                        {'id':'equity','account':'equity','expression':helper.ref('amount'),'requires':['amount']}],
            'flows':[{'id':'distribution','activity':'financing','origin':'declared_distribution','expression':deepcopy(negative),'requires':['amount']}]},
            'bindings':{'amount':helper.event('amount')}},
        'memory':{'definition':{'profile':engine.memory.PROFILE,'state_schema':book['memory_schema'],'input_schema':h,'operations':[]},'input_bindings':{}},
        'residual_prerequisites':['Explicit synthetic distribution only; lawful dividend and accounting authority not established']}
    event={'id':'distribution.1','date':'2025-01-02','inputs':{
        'amount':{'type':deepcopy(money),'value':engine.known(amount),'provenance':'Synthetic distribution premise'},
        'approved':{'type':deepcopy(core.BOOL),'value':engine.known(True),'provenance':'Explicit synthetic applicability, no legal authority'}}}
    transaction={'profile':engine.PROFILE,'expected_state_sha256':core.digest(book),'expected_method_sha256':core.digest(method),
        'method':method,'event':event,'schemas':{**deepcopy(opened['schemas']),h:empty}}
    return {'profile':continuation.PROFILE,'opening_request':source_request,'opening_result':opened,
        'transition_request':transaction,'equity_movements':[{'id':'distribution','event_id':event['id'],'date':event['date'],
            'account':equity,'amount':continuation.reports.fmt(-continuation.reports.number(amount)),
            'description':'Explicit synthetic reduction in reported equity'}],'notes':[]}


class ConditionalContinuationTests(unittest.TestCase):
    def test_two_histories_two_charts_preserve_exact_evidence_and_results(self):
        for owner in ['alpha','beta']:
            for selected,expected in [((10,2,3),'5/1'),((8,3,4),'7/1')]:
                body=fixture(owner,selected);before=deepcopy(body);result=continuation.run(body)
                self.assertEqual(result['status'],'conditional_continuation',result)
                self.assertEqual(body,before)
                direct=continuation.engine.propose(body['opening_result']['opening'],body['transition_request'])
                self.assertEqual(result['transition'],direct)
                self.assertEqual(sorted(result['current']['balances'].values()),['-14/1','14/1'])
                self.assertEqual(result['current']['memory']['history']['sales/a~1'],expected)
                self.assertEqual(result['report']['income']['profit'],'0/1')
                self.assertEqual(result['report']['cash_flows']['activities']['financing']['net'],'-1/1')
                self.assertEqual(result['report']['equity']['closing'],'14/1')
                self.assertEqual(result['opening_result'],body['opening_result'])
                for flag in continuation.FLAGS:self.assertIs(result[flag],False)
                self.assertTrue(continuation.verify(body,result))

    def test_unresolved_opening_obligation_blocks_method_composition(self):
        body=fixture();body['opening_request']['attachment']['obligations'].append({
            'id':'contract','meaning':'Missing contract terms','affects':['execution']})
        body['opening_result']=continuation.source.map_opening(body['opening_request'])
        result=continuation.run(body);self.assertEqual(result['status'],'unresolved')
        self.assertNotIn('current',result);self.assertTrue(result['opening_result']['target_obligations'])

    def test_tampered_source_stale_request_and_foreign_context_refuse(self):
        for variant in ['source','state','context']:
            body=fixture()
            if variant=='source':body['opening_result']['opening']['memory']['history']['sales/a~1']='0/1'
            elif variant=='state':body['transition_request']['expected_state_sha256']='0'*64
            else:
                body['transition_request']['method']['context']['entity']='Other'
                body['transition_request']['expected_method_sha256']=continuation.core.digest(body['transition_request']['method'])
            result=continuation.run(body);self.assertEqual(result['status'],'invalid');self.assertNotIn('current',result)

    def test_unknown_false_insufficient_and_report_mismatch_refuse(self):
        for variant,status in [('unknown','unresolved'),('false','unsupported'),('cash','invalid'),('report','invalid')]:
            body=fixture(amount='16/1' if variant=='cash' else '1/1')
            if variant=='unknown':body['transition_request']['event']['inputs']['amount']['value']={'status':'unknown','reason':'Missing'}
            elif variant=='false':body['transition_request']['event']['inputs']['approved']['value']=continuation.engine.known(False)
            elif variant=='report':body['equity_movements']=[]
            before=deepcopy(body);result=continuation.run(body);self.assertEqual(body,before)
            self.assertEqual(result['status'],status,result);self.assertNotIn('current',result)

    def test_result_flag_and_provenance_tamper_refuse(self):
        body=fixture();result=continuation.run(body);self.assertEqual(result['status'],'conditional_continuation')
        result['execution_clearance']=True;self.assertFalse(continuation.verify(body,result))


if __name__=='__main__':unittest.main()
