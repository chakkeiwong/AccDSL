from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('authoring_examples',ROOT/'data/accounting-master/annual-program-authoring-20261025/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class AnnualProgramAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=x.fixtures();cls.row=cls.rows[0]

    def test_roundtrip_and_identical_lowering(self):
        for row in self.rows:
            with self.subTest(case=row['case']):
                self.assertEqual(m.lower(row['source']),row['program'])
                self.assertEqual(m.render(m.lower(row['source'])),row['source'])
                self.assertEqual(m.compile_text(row['source'],row['imports'])['request'],row['request'])
                self.assertEqual(m.compile_program(row['program'],row['imports'])['request'],row['request'])

    def test_compilation_never_executes_financial_evaluator(self):
        with patch.object(m.annual,'run',side_effect=AssertionError('hidden evaluation')):
            self.assertFalse(m.compile_text(self.row['source'],self.row['imports'])['executed'])
            self.assertFalse(m.compile_program(self.row['program'],self.row['imports'])['executed'])

    def test_full_text_and_typed_execution_match_including_refusals(self):
        for row in self.rows:
            with self.subTest(case=row['case']):
                a=m.execute_text(row['source'],row['imports']);b=m.execute_program(row['program'],row['imports'])
                self.assertEqual(a,b);self.assertEqual(a['status'],row['expected_status'])
                self.assertEqual(a['stop']['status'] if a.get('stop') else None,row['expected_stop'])

    def test_raw_and_semantic_hashes_have_distinct_roles(self):
        a=m.compile_text(self.row['source'],self.row['imports'])
        source='\n'+self.row['source'].replace('operations;','operations;\n',1)
        b=m.compile_text(source,self.row['imports'])
        self.assertEqual(a['request_sha256'],b['request_sha256']);self.assertEqual(a['program_sha256'],b['program_sha256'])
        self.assertNotEqual(a['source_text_sha256'],b['source_text_sha256'])
        self.assertNotEqual(a['source_spans'],b['source_spans'])

    def test_source_spans_match_actual_operation_and_field_lines(self):
        c=m.compile_text(self.row['source'],self.row['imports']);lines=self.row['source'].splitlines()
        self.assertEqual(len(c['source_spans']['operations']),len(self.row['request']['operations']))
        for span in c['source_spans']['operations']:
            self.assertTrue(lines[span['start_line']-1].startswith('operation '))
            self.assertEqual(lines[span['end_line']-1],'end_operation;')
            for field,numbers in span['field_lines'].items():
                for n in numbers:self.assertTrue(lines[n-1].startswith(field+' '))

    def test_duplicate_unknown_and_missing_declarations_reject(self):
        source=self.row['source'];line=next(s for s in source.splitlines() if s.startswith('mode '))
        cases=[source.replace(line,line+'\n'+line,1),source.replace(line,'invented '+line,1),
               source.replace(line+'\n','',1),source.replace('end_program;','end_program;\noperations;'),
               source.replace('end_operations;',''),source.replace('AnnualProgramAuthoring/1','Wrong/1')]
        info=next(s for s in source.splitlines() if s.startswith('information '));cases.append(source.replace(info,info+'\n'+info,1))
        for s in cases:
            with self.subTest(source=s[:80]):
                with self.assertRaises(m.Invalid):m.compile_text(s,self.row['imports'])

    def test_invalid_scalar_and_dates_reject_structurally(self):
        for mutate in [lambda p:p['operations'][0]['event']['interval'].update(activity_through='2027-02-30'),
                       lambda p:p['operations'][1]['event'].update(amount='1/0'),
                       lambda p:p['operations'][1]['event'].update(amount='2/2'),
                       lambda p:p['operations'][1]['event'].update(amount=1.0),
                       lambda p:p['operations'][1]['event']['authorization'].update(value='true')]:
            p=deepcopy(self.row['program']);mutate(p)
            with self.assertRaises(m.Invalid):m.compile_program(p,self.row['imports'])

    def test_duplicate_operation_ids_and_native_header_reject(self):
        p=deepcopy(self.row['program']);p['operations'].append(deepcopy(p['operations'][0]))
        with self.assertRaises(m.Invalid):m.compile_program(p,self.row['imports'])
        row=next(r for r in self.rows if r['case']=='native_only');source=row['source'].replace('operation "native" "authored-native"','operation "native" "different"')
        with self.assertRaises(m.Invalid):m.compile_text(source,row['imports'])

    def test_imports_are_exact_and_never_paths(self):
        with self.assertRaises(m.Invalid):m.compile_text(self.row['source'],{})
        imports=deepcopy(self.row['imports']);key=self.row['program']['root_sha256'];imports[key]['operations']=[]
        with self.assertRaises(m.Invalid):m.compile_text(self.row['source'],imports)
        p=deepcopy(self.row['program']);p['root_sha256']='/tmp/root.json'
        with self.assertRaises(m.Invalid):m.compile_program(p,{})

    def test_strict_utf_json_and_line_endings(self):
        source=self.row['source']
        bad=[b'\xff', '\ufeff'+source,source+'\r',source+'\u2028',source.replace('mode "first";','mode "first"; junk;',1)]
        for s in bad:
            with self.assertRaises(m.Invalid):m.compile_text(s,self.row['imports'])
        self.assertEqual(m.compile_text(source.replace('\n','\r\n'),self.row['imports'])['request'],self.row['request'])
        duplicate=source.replace('"selected":{','"selected":{},"selected":{',1)
        with self.assertRaises(m.Invalid):m.compile_text(duplicate,self.row['imports'])

    def test_unknowns_and_provenance_preserved(self):
        for name in ['unknown_rate','unknown_capacity','false_carry_findings_preserved']:
            row=next(r for r in self.rows if r['case']==name)
            self.assertEqual(m.compile_text(row['source'],row['imports'])['request'],row['request'])

    def test_input_values_are_not_mutated(self):
        p=deepcopy(self.row['program']);imports=deepcopy(self.row['imports']);before=m.annual.caller.canonical([p,imports])
        m.compile_program(p,imports);m.compile_text(self.row['source'],imports)
        self.assertEqual(m.annual.caller.canonical([p,imports]),before)

if __name__=='__main__':unittest.main()
