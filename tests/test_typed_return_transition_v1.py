"""Complete selected transition, raw identity, funding and semantic replay."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util, json, sys, unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import typed_return_transition_v1 as transition
spec=importlib.util.spec_from_file_location('return_composition_cases',ROOT/'data/accounting-master/typed-monetary-effects-20261024/examples.py')
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)
core=transition.core


def raw_args(state,event):
    s,e=core.canonical(state),core.canonical(event)
    return s,sha256(s).hexdigest(),e,sha256(e).hexdigest()


class ReturnCompositionTests(unittest.TestCase):
    def test_complete_retained_matches(self):
        for name,state,event in fixtures.selected_cases():
            before=deepcopy((state,event));args=raw_args(state,event)
            result=transition.propose(*args)
            try:
                after,journal,flows=transition.structure.native.transition(state,event)
            except transition.structure.native.Rejected as exc:
                self.assertEqual(result['status'],exc.status,name);continue
            self.assertEqual(result['status'],'proposed',(name,result))
            p=result['proposal']
            self.assertEqual((p['after'],p['journal'],p['flows']),(after,journal,flows),name)
            applied=transition.apply(*args,p)
            self.assertEqual(applied['status'],'applied_diagnostic',applied)
            self.assertEqual(applied['after'],after)
            self.assertEqual((state,event),before)
            for flag in transition.BOUNDARY:
                if flag!='scope':self.assertFalse(result[flag])

    def test_replay_all_proposal_fields_and_extra_fields(self):
        _,state,event=fixtures.selected_cases()[0];args=raw_args(state,event)
        p=transition.propose(*args)['proposal']
        edits=[lambda p:p['journal'].update(inventory='999/1'),
               lambda p:p['flows'][0].update(amount='0/1'),
               lambda p:p['after']['component'].update(settled=False),
               lambda p:p.update(monetary_definition='0'*64),
               lambda p:p.update(memory_definition='0'*64),
               lambda p:p.update(state_raw_sha256='0'*64),
               lambda p:p.update(implementation_bundle_sha256='0'*64),
               lambda p:p.update(committed=True),lambda p:p.update(extra='unauthorized'),
               lambda p:p['monetary_lineage']['n'].update(pointer='/wrong')]
        for edit in edits:
            candidate=deepcopy(p);edit(candidate)
            result=transition.apply(*args,candidate)
            self.assertEqual(result['status'],'invalid',result)
            self.assertNotIn('after',result)

    def test_raw_identity_and_strict_decoding(self):
        _,state,event=fixtures.selected_cases()[0];args=list(raw_args(state,event))
        args[0]+=b' '
        self.assertEqual(transition.propose(*args)['reason'],'raw_digest_mismatch')
        for bad in [b'{"kind":"sell","kind":"settle"}',b'{"x":NaN}',b'{"x":1.5}',b'\xff']:
            args=list(raw_args(state,event));args[2]=bad;args[3]=sha256(bad).hexdigest()
            self.assertEqual(transition.propose(*args)['status'],'invalid')
        args=list(raw_args(state,event));p=transition.propose(*args)['proposal']
        args[0]+=b' ';args[1]=sha256(args[0]).hexdigest()
        self.assertEqual(transition.propose(*args)['status'],'proposed')
        self.assertEqual(transition.apply(*args,p)['status'],'invalid')

    def test_duplicate_and_equal_date_order(self):
        _,state,event=fixtures.selected_cases()[0];p=transition.propose(*raw_args(state,event))['proposal']
        self.assertEqual(transition.propose(*raw_args(p['after'],event))['reason'],'duplicate_event')
        sale=deepcopy(fixtures.selected_cases()[1][2]);sale['date']=event['date']
        self.assertEqual(transition.propose(*raw_args(state,sale))['reason'],'unknown_lot')
        result=transition.propose(*raw_args(p['after'],sale))
        self.assertEqual(result['status'],'proposed',result)

    def test_preconditions_dates_and_cash_facts(self):
        _,state,event=fixtures.selected_cases()[0]
        edits=[({'date':'2024-12-31'},'invalid'),({'date':'2026-01-01'},'invalid'),
               ({'component_id':'wrong'},'invalid'),({'refund_cash':'39/1'},'invalid'),
               ({'handling_cash':'9/1'},'invalid'),({'actual_units':'0/1'},'invalid'),
               ({'unit_deterioration':'999/1'},'invalid'),({'inventory_nrv':'-1/1'},'invalid'),
               ({'all_rights_closed':False},'unsupported'),({'handling_is_selling_cost':False},'unsupported'),
               ({'refund_cash':'unknown'},'unresolved'),({'all_rights_closed':'unknown'},'unresolved')]
        for edit,status in edits:
            e=deepcopy(event);e.update(edit);result=transition.propose(*raw_args(state,e))
            self.assertEqual(result['status'],status,(edit,result));self.assertNotIn('proposal',result)

    def test_sale_preconditions_and_disposed_state(self):
        _,state,event=fixtures.selected_cases()[1]
        for edit,status in [({'fraction':'1/2'},'unsupported'),({'performance_complete':False},'unsupported'),
                            ({'proceeds':'-1/1'},'invalid'),({'proceeds':'unknown'},'unresolved'),
                            ({'lot_id':'absent'},'invalid')]:
            e=deepcopy(event);e.update(edit);self.assertEqual(transition.propose(*raw_args(state,e))['status'],status)
        p=transition.propose(*raw_args(state,event))['proposal'];event['id']='another_sale'
        self.assertEqual(transition.propose(*raw_args(p['after'],event))['reason'],'lot_already_disposed')

    def test_funding_failure_preserves_state(self):
        _,state,event=fixtures.selected_cases()[0]
        old_cash=transition.monetary.rational(state['balances']['cash'])
        state['balances']['cash']='0/1'
        state['balances']['capital']=transition.monetary.fmt(transition.monetary.rational(state['balances']['capital'])+old_cash)
        before=deepcopy(state);result=transition.propose(*raw_args(state,event))
        self.assertEqual(result['status'],'funding_failure',result)
        self.assertNotIn('proposal',result);self.assertEqual(state,before)

    def test_complete_structures_and_selected_profile(self):
        _,state,event=fixtures.selected_cases()[0]
        for edit in [lambda e:e.update(extra=True),lambda e:e.pop('source_pointer'),
                     lambda e:e.update(source_pointer='/bad~2'),lambda e:e.update(date='2025-02-30'),
                     lambda e:e.update(method='wrong')]:
            e=deepcopy(event);edit(e);self.assertEqual(transition.propose(*raw_args(state,e))['status'],'invalid')
        event['kind']='tax'
        self.assertEqual(transition.propose(*raw_args(state,event))['status'],'unsupported')
        _,state,event=fixtures.selected_cases()[0];state['context']['currency']='EUR'
        self.assertEqual(transition.propose(*raw_args(state,event))['status'],'unsupported')

    def test_unknown_unused_tax_and_declared_carry_context(self):
        _,state,event=fixtures.selected_cases()[0];state['tax_premises']['rate_enacted']='unknown'
        result=transition.propose(*raw_args(state,event));self.assertEqual(result['status'],'proposed')
        p=result['proposal'];declaration=p['prerequisites']['input_declarations']['c']
        self.assertEqual(declaration['type']['context']['at'],event['date'])
        self.assertEqual(p['prerequisite_lineage']['c']['pointer'],'/component/unit_cost')
        self.assertEqual(p['prerequisite_lineage']['c']['raw_sha256'],sha256(core.canonical(state)).hexdigest())

    def test_multiple_failures_preserve_findings_instead_of_first_error(self):
        _,state,event=fixtures.selected_cases()[0]
        event.update(all_rights_closed=False,unit_deterioration='999/1')
        result=transition.propose(*raw_args(state,event))
        self.assertEqual(result['status'],'invalid')
        findings={f['id']:f['consequence'] for f in result['prerequisites']['findings']}
        self.assertEqual(findings['all_rights_closed'],'unsupported')
        self.assertEqual(findings['quantities'],'invalid')
        with self.assertRaises(transition.structure.native.Rejected) as caught:
            transition.structure.native.transition(state,event)
        self.assertEqual(caught.exception.status,'unsupported')


if __name__=='__main__':unittest.main()
