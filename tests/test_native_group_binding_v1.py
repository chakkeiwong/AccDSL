from copy import deepcopy
from datetime import timedelta
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import native_group_binding_v1 as binding

def fixture(snapshot='initial'):
    packet,_=binding.load_native();native=packet[snapshot+'_world'];r=packet['record_registry']
    state=r[native['head']['digest']]['body'];books={};components={}
    for member in ['P','S']:
        books[member]={'entity':member,'book':member,'currency':'USD','sector':'corporate',
            'state_ref':binding.core.digest(binding.selector(native['head'],member)),
            'source_ref':packet['aliases']['source']['digest'],'view_ref':native['view']['digest']}
        components[member+'.corporate']={'owner':member,'sector':'corporate','profile':'CompanyComposition/1',
            **{k:books[member][k] for k in ['state_ref','source_ref','view_ref']},
            'status':'unresolved','obligation_ids':['no-independent-books']}
    world={'profile':binding.world.PROFILE,'context':{'world_id':'retained-P-S','currency':'USD',
        'calendar':'gregorian','case_id':'native-group-'+snapshot,'mode':'conditional'},
        'books':books,'components':components,'control_edges':[{'id':'P-controls-S','parent':'P','child':'S',
            'ownership_fraction':str(Fraction(state['parent_fraction']).numerator)+'/'+str(Fraction(state['parent_fraction']).denominator),
            'start':state['date'],'end_exclusive':(binding.core.scalar(state['date'],'date')+timedelta(days=1)).isoformat(),
            'control_premise':'Supplied native control premise:'+native['head']['digest']}],
        'obligations':[{'id':'no-independent-books','meaning':'Native member selections retain shared group state; no independent executable book admission',
            'affects':['posting','consolidation','sector-composition']}]}
    return {'profile':binding.PROFILE,'world':world,'snapshot':snapshot,
        'members':{'P':'P.corporate','S':'S.corporate'},'control_edge_id':'P-controls-S'}

class NativeGroupBindingTests(unittest.TestCase):
    def checked(self,request,reason=None):
        before=deepcopy(request);result=binding.bind(request);self.assertEqual(request,before)
        self.assertEqual(result['status'],'invalid' if reason else 'group_references_resolved',result.get('reason'))
        if reason:self.assertEqual(result['reason'],reason)
        for flag in binding.FLAGS:
            if flag!='selected_references_resolved':self.assertIs(result[flag],False)
        return result

    def test_initial_and_final_preserve_complete_group_and_selected_books(self):
        for snapshot,p_cash,s_cash,fraction in [('initial','500','100','4/5'),('final','983/2','305/2','9/10')]:
            request=fixture(snapshot);result=self.checked(request);packet,_=binding.load_native()
            self.assertEqual(result['native_snapshot'],packet[snapshot+'_world'])
            self.assertEqual(result['native_state'],packet['record_registry'][packet[snapshot+'_world']['head']['digest']]['body'])
            self.assertEqual(result['world'],request['world']);self.assertEqual(result['unresolved_obligations'],request['world']['obligations'])
            self.assertEqual(result['native_state']['parent_fraction'],fraction)
            for member,cash in [('P',p_cash),('S',s_cash)]:
                selected=result['member_selections'][member]
                self.assertEqual(selected['selector']['pointer'],'/books/'+member)
                self.assertEqual(selected['balances'],result['native_state']['books'][member])
                self.assertEqual(selected['balances']['cash'],cash)
            for key in ['returns','compound','lot','tax_closes','flows','ownership_purchase']:self.assertIn(key,result['native_state'])
            self.assertEqual(result['source_scope'],'historical_conditional_not_current_admission')
            self.assertTrue(binding.verify(request,result))

    def test_group_state_cannot_impersonate_legal_book(self):
        request=fixture();packet,_=binding.load_native();h=packet['initial_world']['head']['digest']
        request['world']['books']['P']['state_ref']=h;request['world']['components']['P.corporate']['state_ref']=h
        self.checked(request,'native_member_selector_binding')

    def test_wrong_member_currency_and_source_view_refuse(self):
        request=fixture();request['world']['books']['P']['book']='Consolidated'
        self.checked(request,'native_member_owner')
        request=fixture();request['world']['context']['currency']='EUR'
        for book in request['world']['books'].values():book['currency']='EUR'
        self.checked(request,'native_currency_binding')
        for field in ['source_ref','view_ref']:
            request=fixture();request['world']['books']['P'][field]='0'*64;request['world']['components']['P.corporate'][field]='0'*64
            self.checked(request,'native_source_view_binding')

    def test_snapshot_cannot_extend_ownership_over_control_interval(self):
        request=fixture('final');request['world']['control_edges'][0]['ownership_fraction']='4/5'
        self.checked(request,'native_ownership_fraction')
        request=fixture('final');request['world']['control_edges'][0]['start']='2024-01-01'
        self.checked(request,'native_snapshot_interval')
        request=fixture();request['world']['control_edges'][0]['control_premise']='Ownership establishes control'
        self.checked(request,'native_control_premise')

    def test_member_population_and_snapshot_are_closed(self):
        request=fixture();request['members']['S']='P.corporate';self.checked(request,'duplicate_member_component')
        request=fixture();request['members']['S']='missing';self.checked(request,'missing_component')
        request=fixture();request['snapshot']='middle';self.checked(request,'native_snapshot')

    def test_native_record_and_blob_corruption_refuse_exactly(self):
        packet,schemas=binding.load_native();roots=[packet['initial_world']['head']]
        altered=deepcopy(packet);altered['record_registry'][roots[0]['digest']]['body']['books']['P']['cash']='501'
        with self.assertRaisesRegex(Exception,'^native_record_digest$'):binding.resolve(altered,schemas,roots)
        bad=deepcopy(roots);bad[0]['kind']='View'
        with self.assertRaisesRegex(Exception,'^native_reference_type$'):binding.resolve(packet,schemas,bad)
        bad=deepcopy(roots);bad[0]['digest']='0'*64
        with self.assertRaisesRegex(Exception,'^missing_native_record$'):binding.resolve(packet,schemas,bad)
        source=packet['record_registry'][packet['aliases']['source']['digest']]['body']['reading']
        fake={**source,'byte_length':source['byte_length']+1};index={fake['sha256']:fake}
        with self.assertRaisesRegex(Exception,'^blob_length$'):binding.checked_blob(fake,index)
        fake={**source,'sha256':'0'*64};index={fake['sha256']:fake}
        with self.assertRaisesRegex(Exception,'^blob_digest$'):binding.checked_blob(fake,index)

    def test_unknown_sector_component_and_obligations_are_preserved(self):
        request=fixture();request['world']['books']['Bank']={'entity':'Bank','book':'legal','currency':'USD','sector':'bank',
            'state_ref':'1'*64,'source_ref':'2'*64,'view_ref':'3'*64}
        request['world']['components']['bank']={'owner':'Bank','sector':'bank','profile':'BankAssessment/1',
            'state_ref':'1'*64,'source_ref':'2'*64,'view_ref':'3'*64,'status':'unresolved','obligation_ids':['no-independent-books']}
        result=self.checked(request);self.assertEqual(result['world'],request['world'])
        self.assertFalse(result['references_resolved']);self.assertTrue(result['selected_references_resolved'])

    def test_pins_and_changed_results_refuse(self):
        request=fixture()
        with patch.dict(binding.PINS,{'portable-exchanges.json':'0'*64}):self.checked(request,'native_bytes:portable-exchanges.json')
        result=self.checked(request);result['native_state']['lot'].clear()
        self.assertFalse(binding.verify(request,result))
        result=self.checked(request);result['member_selections']['P']['balances']['cash']='0'
        self.assertFalse(binding.verify(request,result))

    def test_complete_request_is_bounded_before_copy_or_hash(self):
        request=fixture();request['control_edge_id']='x'*(binding.core.MAX_SCALAR+1)
        self.checked(request,'text:world_scalar')
        request=fixture();request['members']['P']=[];request['members']['P'].append(request['members']['P'])
        result=binding.bind(request)
        self.assertEqual(result['reason'],'world_structure_limit')
        self.assertFalse(result['selected_references_resolved'])
        for request in [None,[],{}, {'profile':False}]:
            self.assertEqual(binding.bind(request)['status'],'invalid')

    def test_rehashed_invalid_records_reach_semantic_checks(self):
        packet,schemas=binding.load_native();base=packet['record_registry'][packet['initial_world']['head']['digest']]
        def rejected(record,reason):
            h=sha256(('accdsl.portable.v1/'+record['schema']).encode()+bytes([0])+binding.core.canonical(record)).hexdigest()
            altered=deepcopy(packet);altered['record_registry'][h]=record
            ref={k:record[k] for k in ['kind','schema']};ref['digest']=h
            with self.assertRaisesRegex(Exception,'^'+reason+'$'):binding.resolve(altered,schemas,[ref])
        bad=deepcopy(base);bad['schema']='wrong';rejected(bad,'native_schema')
        bad=deepcopy(base);del bad['body']['currency'];rejected(bad,'native_body_schema')
        bad=deepcopy(base);bad['body']['books']['P']['cash']='1000/2';rejected(bad,'native_noncanonical_rational')
        bad=deepcopy(base);bad['dependencies']=[packet['aliases']['source']];rejected(bad,'native_dependencies')
        view=packet['record_registry'][packet['initial_world']['view']['digest']]
        for digest,reason in [(packet['aliases']['source']['digest'],'native_reference_type'),('0'*64,'missing_native_record')]:
            bad=deepcopy(view)
            bad['body']['profile']['digest']=digest
            deps={binding.core.canonical(r):r for r in binding.references(bad['body'])}
            bad['dependencies']=[deps[k] for k in sorted(deps)];rejected(bad,reason)

    def test_depth_limit_on_independently_hashed_reference_chain(self):
        # Test-only schema isolates traversal bounds; it is not a native accounting case.
        schemas={'schema_ids':{'Node':'test.node/1'},'$defs':{'Node':{'type':'object'}}}
        packet={'record_registry':{},'blobs':{}};ref=None
        for i in range(50):
            record={'kind':'Node','schema':'test.node/1','key':str(i),
                    'body':{} if ref is None else {'child':ref},'dependencies':[] if ref is None else [ref]}
            h=sha256(b'accdsl.portable.v1/test.node/1'+bytes([0])+binding.core.canonical(record)).hexdigest()
            packet['record_registry'][h]=record;ref={'kind':'Node','schema':'test.node/1','digest':h}
        with self.assertRaisesRegex(Exception,'^native_closure_limit$'):binding.resolve(packet,schemas,[ref])

if __name__=='__main__':unittest.main()
