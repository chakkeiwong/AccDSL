from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
import receivable_source_contract_v1 as source
import declared_receivable_text_v1 as command_text
spec = importlib.util.spec_from_file_location('source_claim_examples',ROOT/'data/accounting-master/populated-source-contracts-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


class ReceivableSourceTests(unittest.TestCase):
    def checked(self, request, status='conditional_execution', reason=None):
        before=deepcopy(request); result=source.run(request)
        self.assertEqual(request,before);self.assertEqual(result['status'],status,result.get('reason'))
        for flag in source.FLAGS:self.assertIs(result[flag],False)
        if reason:self.assertEqual(result['reason'],reason)
        if status in ['invalid','unresolved']:self.assertNotIn('execution',result)
        return result

    def test_two_claims_reports_carry_and_receipts_in_both_charts(self):
        for owner in ['alpha','beta']:
            request,roles,_=ex.fixture(owner); result=self.checked(request); execution=result['execution']
            self.assertEqual(execution['status'],'complete_provisional',execution.get('stop'))
            annual=next(row['result'] for row in execution['reports'] if row['id']=='annual')
            self.assertEqual(annual['balance_sheet']['total_assets'],'170/1')
            self.assertEqual(annual['income']['profit'],'50/1')
            self.assertEqual(annual['cash_flows']['activities']['operating']['net'],'10/1')
            boundary=next(row['result'] for row in execution['trace'] if row['command'].get('id')=='boundary')
            memory=boundary['next_opening']['memory']
            self.assertEqual(memory,boundary['closed_book']['memory'])
            self.assertEqual([row['remaining'] for row in memory['claims'].values()],['20/1','40/1'])
            self.assertEqual(execution['current']['balances'][roles['cash']],'170/1')
            self.assertEqual(execution['current']['balances'][roles['receivables']],'0/1')
            self.assertEqual(execution['reports'][-1]['result']['income']['profit'],'0/1')
            self.assertEqual(execution['reports'][-1]['result']['cash_flows']['activities']['operating']['net'],'60/1')
            self.assertEqual(result['selection']['selected_ids'],['A.original','B.original'])
            self.assertEqual(len(result['source_evidence']['assertions']),3)
            self.assertEqual(result['sale_lineage']['sale.1']['reading']['customer'],'Customer A')

    def test_available_revision_changes_due_assessment_only(self):
        request,_,_=ex.fixture(); old=self.checked(request)
        request['view']['cutoff']='2027-04-01T00:00:00Z';new=self.checked(request)
        self.assertEqual(new['selection']['selected_ids'],['B.original','A.corrected'])
        def feb(result):
            return next(row['observation']['claims'] for row in result['execution']['trace'] if row['command'].get('event',{}).get('id')=='assess.feb')
        self.assertEqual(feb(old)[0]['overdue'],'20/1');self.assertEqual(feb(new)[0]['overdue'],'0/1')
        self.assertEqual(feb(old)[1],feb(new)[1])
        self.assertEqual(old['execution']['current']['balances'],new['execution']['current']['balances'])
        for a,b in zip(old['execution']['reports'],new['execution']['reports']):
            for key in ['balance_sheet','income','cash_flows','equity']:
                self.assertEqual(a['result'][key],b['result'][key])
        self.assertEqual(len(new['execution']['current']['memory']['claims']),2)
        self.assertEqual(old['sale_lineage']['sale.1']['id'],'A.original')

    def test_original_and_ingestion_views_retain_old_assertion(self):
        request,_,_=ex.fixture(); request['view']['cutoff']='2027-04-01T00:00:00Z'
        request['view']['system_as_of']='2027-03-15T23:00:00Z'
        self.assertEqual(source.compile_program(request)['sale_lineage']['sale.1']['id'],'A.original')
        request['view'].update(mode='original',system_as_of='2027-04-01T00:00:00Z')
        self.assertEqual(source.compile_program(request)['sale_lineage']['sale.1']['id'],'A.original')

    def test_future_unknown_and_conflicting_sources_do_not_execute(self):
        request,_,_=ex.fixture();request['view']['cutoff']='2027-01-01T00:00:00Z'
        result=self.checked(request,'unresolved');self.assertEqual(result['unresolved'][0]['reason'],'source_unavailable')
        request,_,_=ex.fixture();key=request['assertions'][2]['span']['document'];request['documents'][key]['available']='unknown'
        result=self.checked(request,'unresolved');self.assertEqual(result['unresolved'][0]['reason'],'assertion_timing_unknown')
        request,_,_=ex.fixture();request['assertions'][2]['supersedes']=[];request['view']['cutoff']='2027-04-01T00:00:00Z'
        result=self.checked(request,'unresolved');self.assertEqual(result['unresolved'][0]['reason'],'conflicting_assertions')

    def test_missing_amount_or_terms_keep_missingness_tag(self):
        for field in ['units','consideration','due']:
            request,_,_=ex.fixture();reading=deepcopy(request['assertions'][0]['reading'])
            reading[field]={'status':'unknown','reason':'unreadable'};ex.replace_reading(request,0,reading)
            result=self.checked(request,'unresolved')
            self.assertEqual(result['unresolved'][0]['field'],field);self.assertEqual(result['unresolved'][0]['missingness'],'unreadable')

    def test_byte_span_and_reading_corruption_have_distinct_refusals(self):
        request,_,_=ex.fixture();row=request['assertions'][0];request['documents'][row['span']['document']]['content']+='changed'
        self.checked(request,'invalid','document_digest')
        request,_,_=ex.fixture();request['assertions'][0]['span']['sha256']='0'*64
        self.checked(request,'invalid','source_span_digest')
        request,_,_=ex.fixture();request['assertions'][0]['span']['end_exclusive']=True
        self.checked(request,'invalid','source_span_bounds')
        request,_,_=ex.fixture();request['assertions'][0]['reading']['consideration']['value']='999/1'
        self.checked(request,'invalid','source_reading_mismatch')

    def test_revision_cannot_change_claim_or_context(self):
        request,_,_=ex.fixture();reading=deepcopy(request['assertions'][2]['reading']);reading['customer']='Customer B'
        ex.replace_reading(request,2,reading);self.checked(request,'invalid','revision_claim_identity')
        request,_,_=ex.fixture();request['assertions'][2]['context']['currency']='EUR'
        self.checked(request,'invalid','assertion_context')
        request,_,_=ex.fixture();request['assertions'][2]['supersedes']=['B.original']
        self.checked(request,'invalid','SUPERSESSION_SCOPE_MISMATCH')

    def test_duplicate_claim_lineage_and_unbound_sale_refuse(self):
        request,_,_=ex.fixture();request['assertions'][2]['lineage']='another';request['assertions'][2]['supersedes']=[]
        self.checked(request,'invalid','duplicate_claim_lineage')
        request,_,_=ex.fixture();del request['sale_bindings']['sale.2']
        self.checked(request,'invalid','complete_sale_bindings')
        request,_,_=ex.fixture();request['sale_bindings']['sale.2']='claim.A'
        self.checked(request,'invalid','lineage_used_twice')

    def test_unknown_method_approval_is_separate_from_source_reading(self):
        request,_,_=ex.fixture();request['template']['commands'][0]['event']['inputs']['approved']['value']={'status':'unknown','reason':'Recognition facts unavailable'}
        result=self.checked(request);self.assertEqual(result['execution']['successful_commands'],0)
        self.assertEqual(result['execution']['stop']['status'],'unresolved')

    def test_text_typed_and_exact_replay_match(self):
        request,_,_=ex.fixture();result=self.checked(request);program=result['program']
        text,imports=command_text.from_program(program)
        self.assertEqual(command_text.compile_text(text,imports)['program'],program)
        self.assertEqual(command_text.execute_text(text,imports),result['execution'])
        self.assertTrue(source.verify(request,result))
        altered=deepcopy(result);altered['execution']['current']['memory']['claims'].clear()
        self.assertFalse(source.verify(request,altered))

    def test_native_prefix_survives_receipt_refusal(self):
        request,_,_=ex.fixture();request['template']['commands'][2]['event']['inputs']['amount']['value']['value']='31/1'
        result=self.checked(request)['execution'];self.assertEqual(result['successful_commands'],2)
        self.assertEqual(result['status'],'stopped_provisional')
        self.assertEqual(result['current'],result['trace'][1]['result']['after'])

    def test_dependency_origin_and_timestamp_refuse(self):
        request,_,_=ex.fixture()
        with patch.dict(source.PINS,{'context_chronology_v1.py':'0'*64}):self.checked(request,'invalid','source_dependency:context_chronology_v1.py')
        request['documents'][request['assertions'][0]['span']['document']]['origin']='actual_invoice'
        self.checked(request,'invalid','constructed_scope_only')
        request,_,_=ex.fixture();request['view']['cutoff']='2027-04-01'
        self.checked(request,'invalid','utc_instant_required')

    def test_independent_typed_program_and_all_signed_balances(self):
        for owner in ['alpha','beta']:
            for corrected in [False,True]:
                request,roles,_=ex.fixture(owner)
                expected=deepcopy(request['template'])
                if corrected:
                    request['view']['cutoff']='2027-04-01T00:00:00Z'
                    expected['commands'][0]['event']['inputs']['due']['value']['value']='2027-03-31'
                for index,assertion_index in [(0,2 if corrected else 0),(1,1)]:
                    assertion=request['assertions'][assertion_index]
                    for field in ['claim_id','customer','due','units','consideration']:
                        expected['commands'][index]['event']['inputs'][field]['provenance']='Constructed assertion:'+assertion['id']+':'+assertion['span']['sha256']+':'+field
                    # The template's monetary placeholders cannot become evidence.
                    request['template']['commands'][index]['event']['inputs']['consideration']['value']['value']='999/1'
                result=self.checked(request)
                self.assertEqual(result['program'],expected)
                self.assertEqual(result['execution'],source.life.run(expected))
                execution=result['execution']
                target={account:'0/1' for account in roles.values()}
                target.update({roles['cash']:'170/1',roles['capital']:'-120/1',roles['retained']:'-50/1'})
                self.assertEqual(execution['current']['balances'],target)
                boundary=next(t['result'] for t in execution['trace'] if t['command'].get('id')=='boundary')
                closing=dict(target)
                closing.update({roles['cash']:'110/1',roles['receivables']:'60/1',roles['retained']:'0/1',roles['revenue']:'-70/1',roles['cost_of_sales']:'20/1'})
                annual_state=next(t['request']['closing'] for t in execution['trace'] if t['command'].get('id')=='annual')
                self.assertEqual(annual_state['balances'],closing)
                opening=dict(target);opening.update({roles['cash']:'110/1',roles['receivables']:'60/1'})
                self.assertEqual(boundary['next_opening']['balances'],opening)
                annual=next(t['result'] for t in execution['reports'] if t['id']=='annual')
                next_report=execution['reports'][-1]['result']
                for report,income,expense,profit,opening_equity,opening_cash,closing_cash,receipts in [
                    (annual,'70/1','20/1','50/1','120/1','100/1','110/1','10/1'),
                    (next_report,'0/1','0/1','0/1','170/1','110/1','170/1','60/1')]:
                    self.assertEqual(report['balance_sheet'],{'total_assets':'170/1','total_liabilities':'0/1','equity_including_profit':'170/1'})
                    self.assertEqual(report['income'],{'income':income,'expenses':expense,'profit':profit})
                    self.assertEqual({k:report['equity'][k] for k in ['opening','direct_movements','profit','closing']},
                                     {'opening':opening_equity,'direct_movements':'0/1','profit':profit,'closing':'170/1'})
                    flow=report['cash_flows']
                    self.assertEqual([flow[k] for k in ['opening_cash','closing_cash','net_movement']],[opening_cash,closing_cash,receipts])
                    self.assertEqual(flow['activities'],{'operating':{'receipts':receipts,'payments':'0/1','net':receipts},
                        'investing':{'receipts':'0/1','payments':'0/1','net':'0/1'},'financing':{'receipts':'0/1','payments':'0/1','net':'0/1'}})
                    self.assertEqual(report['reconciliations'],{'balance_sheet':'0/1','cash':'0/1','equity':'0/1'})

    def test_exact_availability_and_ingestion_boundaries(self):
        request,_,_=ex.fixture()
        request['view'].update(cutoff='2027-03-15T11:59:59Z',system_as_of='2027-03-16T09:00:00Z')
        self.assertEqual(source.compile_program(request)['sale_lineage']['sale.1']['id'],'A.original')
        request['view']['cutoff']='2027-03-15T12:00:00Z'
        self.assertEqual(source.compile_program(request)['sale_lineage']['sale.1']['id'],'A.corrected')
        request['view']['system_as_of']='2027-03-16T08:59:59Z'
        self.assertEqual(source.compile_program(request)['sale_lineage']['sale.1']['id'],'A.original')

    def test_supersession_graph_and_availability_refuse(self):
        for parent,reason in [('missing','DANGLING_SUPERSESSION'),('A.corrected','SUPERSESSION_CYCLE')]:
            request,_,_=ex.fixture();request['assertions'][2]['supersedes']=[parent]
            self.checked(request,'invalid',reason)
        request,_,_=ex.fixture();request['assertions'][0]['supersedes']=['A.corrected']
        self.checked(request,'invalid','SUPERSESSION_CYCLE')
        request,_,_=ex.fixture()
        request['documents'][request['assertions'][2]['span']['document']]['available']='2027-01-01T00:00:00Z'
        self.checked(request,'invalid','supersession_availability_order')

    def test_json_duplicate_keys_and_numeric_literals_refuse(self):
        for token,reason in [('1','source_numeric_literal_forbidden'),('NaN','source_numeric_literal_forbidden'),
                             ('{"x":"one","x":"two"}','duplicate_source_key')]:
            request,_,_=ex.fixture();row=request['assertions'][0]
            raw=token.encode('utf-8');digest=sha256(raw).hexdigest()
            old=request['documents'][row['span']['document']]
            request['documents'][digest]={**old,'content':token}
            row['span']={'document':digest,'start':0,'end_exclusive':len(raw),'sha256':digest}
            self.checked(request,'invalid',reason)

    def test_unknown_ingestion_and_invalid_dates(self):
        request,_,_=ex.fixture()
        request['documents'][request['assertions'][2]['span']['document']]['ingested']='unknown'
        result=self.checked(request,'unresolved')
        self.assertEqual(result['unresolved'][0]['reason'],'assertion_timing_unknown')
        for instant,reason in [('2027-02-30T00:00:00Z','invalid_utc_instant'),
                               ('2027-01-01T24:00:00Z','invalid_utc_instant'),
                               ('2027-01-01T00:00:00+00:00','utc_instant_required')]:
            request,_,_=ex.fixture();request['view']['cutoff']=instant
            self.checked(request,'invalid',reason)

    def test_source_identity_cannot_rebind_another_sale(self):
        request,_,_=ex.fixture();request['sale_bindings']={'sale.1':'claim.B','sale.2':'claim.A'}
        self.checked(request,'invalid','sale_event_source_identity')
        request,_,_=ex.fixture();request['template']['commands'][0]['event']['date']='2027-01-03'
        self.checked(request,'invalid','sale_event_source_identity')

    def test_amount_correction_reconstructs_a_distinct_history(self):
        request,roles,_=ex.fixture();reading=deepcopy(request['assertions'][2]['reading'])
        reading['consideration']['value']='35/1';ex.replace_reading(request,2,reading)
        original=self.checked(request)
        request['view']['cutoff']='2027-04-01T00:00:00Z';corrected=self.checked(request)
        annual=next(t['result'] for t in corrected['execution']['reports'] if t['id']=='annual')
        self.assertEqual(annual['balance_sheet']['total_assets'],'175/1')
        self.assertEqual(annual['income']['profit'],'55/1')
        balances=corrected['execution']['current']['balances']
        self.assertEqual([balances[roles[k]] for k in ['cash','receivables','retained']],['170/1','5/1','-55/1'])
        self.assertEqual(len(corrected['execution']['current']['memory']['claims']),2)
        self.assertEqual(original['execution']['current']['balances'][roles['receivables']],'0/1')
        self.assertEqual(corrected['program']['opening'],original['program']['opening'])

    def test_source_missingness_tags_and_owner_context(self):
        for reason in sorted(source.MISSING):
            request,_,_=ex.fixture();reading=deepcopy(request['assertions'][0]['reading'])
            reading['consideration']={'status':'unknown','reason':reason};ex.replace_reading(request,0,reading)
            result=self.checked(request,'unresolved')
            self.assertEqual(result['unresolved'][0]['missingness'],reason)
        for field in ['entity','book','basis','unit','calendar']:
            request,_,_=ex.fixture();request['assertions'][0]['context'][field]='different'
            self.checked(request,'invalid','assertion_context')


if __name__=='__main__':unittest.main()
