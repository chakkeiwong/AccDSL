"""Matched declaration/record authoring with explicit malformed-input rejection."""
from copy import deepcopy
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import conditional_family_text_v1 as text
from test_joint_measurement_constraints_v1 import definition as joint_fixture, BUDGET as MEASUREMENT_BUDGET
from test_temporal_measurement_constraints_v1 import fixture as temporal_fixture
from test_conditional_history_family_v1 import fixture as monetary_fixture, BUDGET
from test_typed_affine_history_v1 import stock_fixture
from test_history_measurement_attachment_v1 import fixture as attachment_fixture


def inputs():
    return [(joint_fixture(),MEASUREMENT_BUDGET),(temporal_fixture(),MEASUREMENT_BUDGET),
            (monetary_fixture(),BUDGET),(stock_fixture(),BUDGET),(attachment_fixture(),BUDGET)]


def equivalent_result(d,b,r):
    d=text.exchange(d,b)['definition']
    module=text.MODULES[d['profile']]
    if hasattr(module,'verify_result'):return module.verify_result(d,b,r)
    direct=module.assess(d,b)
    if r['status']!=direct['status']:return False
    if d['profile']==text.temporal.PROFILE:
        r=r['joint_assessment'];d=text.temporal.lower(d,b)[0]
    if 'witness' in r:text.joint.check_witness(d,r['witness'])
    return True


class ConditionalFamilyTextTests(unittest.TestCase):
    def test_all_profiles_roundtrip_exactly_through_text_and_utf8(self):
        for d,b in inputs():
            e=text.exchange(d,b);before=deepcopy(e);source=text.render(e)
            self.assertEqual(text.lower(source),e)
            self.assertEqual(text.lower(source.encode()),e)
            self.assertEqual(text.render(text.lower(source)),source)
            self.assertEqual(e,before)
            self.assertTrue(equivalent_result(d,b,text.assess_source(source)))

    def test_strict_json_exchange_matches_typed_interface(self):
        for d,b in inputs():
            e=text.exchange(d,b)
            self.assertEqual(text.decode_exchange(json.dumps(e)),e)
            self.assertEqual(text.decode_exchange(text.core.canonical(e)),e)

    def test_manual_source_declaration_order_maps_to_exact_ast(self):
        d=monetary_fixture();e=text.exchange(d,BUDGET)
        # Independently compose declarations rather than invoke render.
        js=lambda x:json.dumps(x,ensure_ascii=False)
        lines=['conditional_exchange '+js(text.EXCHANGE)+';','budget '+js(BUDGET)+';',
               'family "manual" '+js(d['profile'])+';']
        for key in ['scope','value_type','opening_date','dates','balance_premise','obligations']:
            lines.append(key+' '+js(d[key])+';')
        for command,field in [('account','accounts'),('memory','memory'),('template','templates')]:
            for key,value in d[field].items():lines.append(command+' '+js(key)+' '+js(value)+';')
        for command,field in [('event','events'),('measurement','measurements')]:
            for value in d[field]:lines.append(command+' '+js(value)+';')
        lines += ['end_family;','select "manual" '+js(e['selected_digest'])+';','end_exchange;']
        self.assertEqual(text.lower('\n'.join(lines)),e)

    def test_same_day_order_remains_semantically_significant(self):
        for sale_first,expected in [(False,'conditional_family_witness'),(True,'conditionally_infeasible')]:
            d=stock_fixture(sale_first);source=text.render(text.exchange(d,BUDGET))
            self.assertEqual(text.lower(source)['definition']['events'],d['events'])
            self.assertEqual(text.assess_source(source)['status'],expected)

    def test_attachment_embeds_complete_parents_not_witnesses(self):
        d=attachment_fixture();source=text.render(text.exchange(d,BUDGET));e=text.lower(source)
        self.assertEqual(e['definition'],d);self.assertEqual(source.count('family "'),3)
        r=text.assess_exchange(e);self.assertTrue(text.attachment.verify_result(e['definition'],BUDGET,r))
        self.assertTrue(r['replay']['both_parent_constraints_checked'])

    def test_missing_premises_and_zero_budgets_keep_status(self):
        d=stock_fixture();d['state_constraints'][0]['domain']['premise']=None
        self.assertEqual(text.assess_source(text.render(text.exchange(d,BUDGET)))['status'],'unresolved')
        for d,b in inputs():
            source=text.render(text.exchange(d,{**b,'max_cells':0}))
            self.assertEqual(text.assess_source(source)['status'],'unknown')

    def test_duplicate_json_keys_including_escaped_alias_reject(self):
        source=text.render(text.exchange(stock_fixture(),BUDGET))
        for old,new in [ ('"max_slots":4','"max_slots":4,"max_slots":4'),
                         ('"max_slots":4','"max_slots":4,"max_\\u0073lots":4'),
                         ('"currency:USD":1','"currency:USD":1,"currency:USD":1') ]:
            self.assertIn(old,source)
            with self.assertRaises(ValueError):text.lower(source.replace(old,new,1))
        e=text.core.canonical(text.exchange(stock_fixture(),BUDGET)).decode()
        with self.assertRaises(ValueError):text.decode_exchange(e.replace('"max_slots":4','"max_slots":4,"max_slots":4'))

    def test_duplicate_declarations_singletons_and_parents_reject(self):
        for d,b in [inputs()[3],inputs()[4]]:
            source=text.render(text.exchange(d,b));lines=source.splitlines()
            commands=['budget','account','event','scope'] if d['profile']==text.typed.PROFILE else ['use_history','binding','obligations']
            for command in commands:
                line=next(x for x in lines if x.startswith(command+' '))
                with self.assertRaises(ValueError):text.lower(source.replace(line,line+'\n'+line,1))

    def test_float_nonfinite_and_unbounded_integer_reject(self):
        source=text.render(text.exchange(stock_fixture(),BUDGET))
        for token in ['4.0','4e0','NaN','Infinity','-Infinity','1234567890123']:
            with self.assertRaises(ValueError):text.lower(source.replace('"max_slots":4','"max_slots":'+token))
        for token in ['true','"4"']:
            with self.assertRaises(ValueError):text.lower(source.replace('"max_slots":4','"max_slots":'+token))

    def test_bad_encoding_bom_surrogates_and_line_separators_reject(self):
        source=text.render(text.exchange(stock_fixture(),BUDGET))
        for invalid in [b'\xff',b'\xef\xbb\xbf'+source.encode(),'\ufeff'+source,
                        source+'\ud800',source+'\u2028',source.replace('\n','\r')]:
            with self.assertRaises(ValueError):text.lower(invalid)
        escaped=source.replace('Synthetic','bad\\ud800')
        with self.assertRaises(ValueError):text.lower(escaped)

    def test_crlf_and_ascii_whitespace_are_supported(self):
        e=text.exchange(stock_fixture(),BUDGET)
        source=' \t\r\n'+'\r\n'.join(' \t'+x+' \t' for x in text.render(e).splitlines())+'\r\n'
        self.assertEqual(text.lower(source),e)

    def test_size_depth_and_node_bounds_reject(self):
        with self.assertRaises(ValueError):text.lower('x'*(text.core.MAX_BYTES+1))
        with self.assertRaises(ValueError):text.decode_exchange('['*49+'0'+']'*49)
        with self.assertRaises(ValueError):text.bounded([None]*(text.MAX_NODES+1))
        with self.assertRaises(ValueError):text.bounded('x'*(text.core.MAX_SCALAR+1))

    def test_unknown_profile_field_command_and_wrong_hash_reject(self):
        source=text.render(text.exchange(stock_fixture(),BUDGET))
        for bad in [source.replace(text.typed.PROFILE,'NoProfile/9'),
                    source.replace('scope ','evaluate ',1),
                    source.replace('"provenance":','"unknown":',1),
                    source.replace(text.core.digest(stock_fixture()),'0'*64)]:
            with self.assertRaises(ValueError):text.lower(bad)

    def test_incomplete_after_end_or_trailing_tokens_reject(self):
        source=text.render(text.exchange(stock_fixture(),BUDGET))
        for bad in [source.replace('end_exchange;',''),source+'end_exchange;\n',
                    source.replace('end_family;','end_family; junk'),
                    source.replace('end_exchange;','end_exchange;;'),
                    source.replace('conditional_exchange','family',1)]:
            with self.assertRaises(ValueError):text.lower(bad)

    def test_forward_parent_unused_family_and_wrong_parent_profile_reject(self):
        source=text.render(text.exchange(attachment_fixture(),BUDGET))
        with self.assertRaises(ValueError):text.lower(source.replace('use_history "selected_history"',
                                                                     'use_history "later"'))
        with self.assertRaises(ValueError):text.lower(source.replace('use_history "selected_history"',
                                                                     'use_history "selected_measurements"'))
        single=text.render(text.exchange(stock_fixture(),BUDGET));lines=single.splitlines()
        block='\n'.join(lines[2:-2]).replace('family "selected"','family "unused"',1)
        with self.assertRaises(ValueError):text.lower(single.replace('select "selected"',block+'\nselect "selected"'))

    def test_absent_or_null_budget_cannot_be_defaulted(self):
        source=text.render(text.exchange(stock_fixture(),BUDGET));line=source.splitlines()[1]
        for bad in [source.replace(line,''),source.replace(line,'budget null;'),
                    source.replace(line,'budget {};')]:
            with self.assertRaises(ValueError):text.lower(bad)

    def test_map_permutations_normalize_but_event_order_does_not(self):
        def reverse_maps(value):
            if isinstance(value,dict):return {k:reverse_maps(v) for k,v in reversed(list(value.items()))}
            if isinstance(value,list):return [reverse_maps(v) for v in value]
            return value
        for d,b in inputs():
            e=text.exchange(d,b);alternate=text.exchange(reverse_maps(d),reverse_maps(b))
            self.assertEqual(text.render(e),text.render(alternate))
            self.assertTrue(equivalent_result(d,b,text.assess_exchange(alternate)))
        a=text.exchange(stock_fixture(),BUDGET);b=text.exchange(stock_fixture(True),BUDGET)
        self.assertNotEqual(a['selected_digest'],b['selected_digest'])

    def test_original_record_witness_checks_survive_map_normalization(self):
        for d,b in inputs():
            r=text.assess_exchange(text.exchange(d,b));module=text.MODULES[d['profile']]
            if hasattr(module,'replay_witness'):
                self.assertEqual(module.replay_witness(d,b,r['witness']),r['replay'])
            elif d['profile']==text.temporal.PROFILE:
                self.assertTrue(module.check_witness(d,b,r['joint_assessment']['witness']))
            else:self.assertTrue(module.check_witness(d,r['witness']))


if __name__=='__main__':unittest.main()
