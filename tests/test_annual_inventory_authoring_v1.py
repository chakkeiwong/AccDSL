from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('inventory_authoring_examples',ROOT/'data/accounting-master/annual-inventory-authoring-20261025/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class AnnualInventoryAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=x.fixtures();cls.row=next(r for r in cls.rows if r['case']=='inventory_partial')

    def test_roundtrip_and_exact_lowering(self):
        for row in self.rows:
            with self.subTest(case=row['case']):
                self.assertEqual(m.lower(row['source']),row['program'])
                self.assertEqual(m.render(m.lower(row['source'])),row['source'])
                self.assertEqual(m.compile_text(row['source'],row['imports'])['request'],row['request'])
                self.assertEqual(m.compile_program(row['program'],row['imports'])['request'],row['request'])

    def test_compile_never_executes_root_or_financial_methods(self):
        with patch.object(m.runtime,'run',side_effect=AssertionError('hidden runtime')),patch.object(m.annual,'run',side_effect=AssertionError('hidden old runtime')),patch.object(m.annual.root,'run',side_effect=AssertionError('hidden root')):
            self.assertFalse(m.compile_text(self.row['source'],self.row['imports'])['executed'])
            self.assertFalse(m.compile_program(self.row['program'],self.row['imports'])['executed'])

    def test_full_execution_matches_direct_evaluator(self):
        for row in self.rows:
            with self.subTest(case=row['case']):
                a=m.execute_text(row['source'],row['imports']);b=m.execute_program(row['program'],row['imports'])
                self.assertEqual(a,b);self.assertEqual(a,m.runtime.run(row['request']))
                self.assertEqual(a['status'],row['expected_status'])
                self.assertEqual(a['stop']['status'] if a.get('stop') else None,row['expected_stop'])

    def test_existing_operation_compilation_unchanged(self):
        for row in self.rows:
            if row['legacy'] is None:continue
            prior=row['legacy'];expected=m.base.compile_text(prior['source'],prior['imports'])['request']
            result=m.compile_text(row['source'],row['imports'])['request']
            self.assertEqual({k:v for k,v in result.items() if k!='profile'},{k:v for k,v in expected.items() if k!='profile'})

    def test_legacy_profile_still_rejects_optional_operation(self):
        p=deepcopy(self.row['program']);p['profile']=m.base.PROFILE
        with self.assertRaises(m.Invalid):m.base.compile_program(p,self.row['imports'])

    def test_source_hash_spans_and_line_endings(self):
        row=self.row;source=row['source'];a=m.compile_text(source,row['imports'])
        b=m.compile_text('\n'+source.replace('operations;','operations;\n',1),row['imports'])
        self.assertEqual(a['request_sha256'],b['request_sha256']);self.assertNotEqual(a['source_text_sha256'],b['source_text_sha256']);self.assertNotEqual(a['source_spans'],b['source_spans'])
        self.assertEqual(a['source_text_sha256'],sha256(source.encode()).hexdigest())
        self.assertEqual(m.compile_text(source.replace('\n','\r\n'),row['imports'])['request'],row['request'])
        lines=source.splitlines()
        for span in a['source_spans']['operations']:
            self.assertTrue(lines[span['start_line']-1].startswith('operation '));self.assertEqual(lines[span['end_line']-1],'end_operation;')
            for field,numbers in span['field_lines'].items():
                for n in numbers:self.assertTrue(lines[n-1].startswith(field+' '))

    def test_missing_duplicate_and_unknown_fields_reject(self):
        source=self.row['source'];line=next(s for s in source.splitlines() if s.startswith('sold_units '));finding=next(s for s in source.splitlines() if s.startswith('finding '))
        for bad in [source.replace(line,line+'\n'+line,1),source.replace(line+'\n','',1),source.replace(line,'invented '+line,1),source.replace(finding,finding+'\n'+finding,1),source.replace(finding+'\n','',1),source.replace('end_program;',''),source+'operations;',source.replace(m.PROFILE,'Wrong/1')]:
            with self.subTest(source=bad[:80]):
                with self.assertRaises(m.Invalid):m.compile_text(bad,self.row['imports'])

    def test_scalar_date_profile_and_findings_shapes_reject(self):
        changes=[lambda e:e.update(sold_units='1/0'),lambda e:e.update(sold_units='2/2'),lambda e:e.update(proceeds=1.0),lambda e:e.update(date='2027-02-30'),lambda e:e.update(profile='Wrong/1'),lambda e:e['findings']['homogeneous_units'].update(value='true'),lambda e:e['findings']['homogeneous_units'].update(provenance=''),lambda e:e['findings'].update(invented={'status':'unknown','reason':'missing'}),lambda e:e['findings'].__setitem__('homogeneous_units',{'status':'unknown','reason':'missing','value':True})]
        for change in changes:
            p=deepcopy(self.row['program']);change(p['operations'][0]['event'])
            with self.assertRaises(m.Invalid):m.compile_program(p,self.row['imports'])

    def test_semantic_failures_remain_explicit_data(self):
        for name,status in [('inventory_unknown_findings','unresolved'),('inventory_false_findings','unsupported'),('inventory_oversale','invalid'),('inventory_wrong_method','unsupported')]:
            row=next(r for r in self.rows if r['case']==name)
            self.assertEqual(m.compile_text(row['source'],row['imports'])['request'],row['request'])
            self.assertEqual(m.execute_text(row['source'],row['imports'])['stop']['status'],status)

    def test_duplicate_ids_and_native_header_reject(self):
        p=deepcopy(self.row['program']);p['operations'].append(deepcopy(p['operations'][0]))
        with self.assertRaises(m.Invalid):m.compile_program(p,self.row['imports'])
        row=next(r for r in self.rows if r['case']=='legacy_native_only')
        bad=row['source'].replace('operation "native" "authored-native"','operation "native" "different"')
        with self.assertRaises(m.Invalid):m.compile_text(bad,row['imports'])

    def test_imports_are_bound_and_paths_rejected(self):
        with self.assertRaises(m.Invalid):m.compile_text(self.row['source'],{})
        imports=deepcopy(self.row['imports']);key=self.row['program']['root_sha256'];imports[key]['profile']='Wrong/1'
        with self.assertRaises(m.Invalid):m.compile_text(self.row['source'],imports)
        p=deepcopy(self.row['program']);p['root_sha256']='/tmp/root.json'
        with self.assertRaises(m.Invalid):m.compile_program(p,{})
        imports=deepcopy(self.row['imports']);imports[key]['boundary_sha256']='0'*64
        p=deepcopy(self.row['program']);p['root_sha256']=m.annual.book.digest(imports[key])
        with self.assertRaises(m.Invalid):m.compile_program(p,{p['root_sha256']:imports[key]})

    def test_strict_utf_json_and_trailing_tokens(self):
        source=self.row['source'];line=next(s for s in source.splitlines() if s.startswith('sold_units '))
        for bad in [b'\xff','\ufeff'+source,source+'\r',source+'\u2028',source.replace(line,line+' junk;',1),source.replace('"status":"known"','"status":"unknown","status":"known"',1)]:
            with self.assertRaises(m.Invalid):m.compile_text(bad,self.row['imports'])

    def test_input_and_output_aliases_are_isolated(self):
        p=deepcopy(self.row['program']);imports=deepcopy(self.row['imports']);before=m.annual.caller.canonical([p,imports])
        out=m.compile_program(p,imports);out['request']['operations'].clear();out['program']['operations'].clear()
        self.assertEqual(m.annual.caller.canonical([p,imports]),before)

    def test_residual_stock_and_tax_liability_survive_authored_carry(self):
        row=next(r for r in self.rows if r['case']=='inventory_residual_carry_and_sale')
        result=m.execute_text(row['source'],row['imports']);book=result['period_book']
        self.assertEqual(book['after']['balances']['cash'],'482/1');self.assertEqual(book['after']['balances']['income_tax_payable'],'-49/4')
        self.assertTrue(book['after']['lots']['recovered']['disposed']);self.assertEqual(len(book['period_archive']),1)

    def test_unicode_identity_and_provenance_preserved(self):
        row=next(r for r in self.rows if r['case']=='unicode_identity_provenance')
        self.assertEqual(m.compile_text(row['source'],row['imports'])['request'],row['request'])

if __name__=='__main__':unittest.main()
