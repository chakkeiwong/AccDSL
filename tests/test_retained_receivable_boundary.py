from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'data/accounting-master/retained-receivable-boundary-20261025'
spec=importlib.util.spec_from_file_location('retained_receivable_boundary',DIRECTORY/'boundary.py')
boundary=importlib.util.module_from_spec(spec);spec.loader.exec_module(boundary)


class RetainedReceivableBoundaryTests(unittest.TestCase):
    def test_three_views_preserve_observations_and_original_package(self):
        for view,count,notes in [('annual',6,1),('interim',6,1),('combined',12,2)]:
            request=boundary.fixture(view);before=deepcopy(request);result=boundary.evaluate(request)
            self.assertEqual(request,before);self.assertEqual(len(result['observations']),count)
            self.assertEqual(len(result['notes']),notes)
            base=boundary.readiness.evaluate(request['readiness_request'])
            self.assertEqual(result['preserved_package'],base['preserved_package'])
            self.assertEqual(result['readiness_result_sha256'],boundary.readiness.digest(base))
            self.assertIsNone(result['claims']);self.assertIsNone(result['executable_program'])
            for field in ['executed','source_admission','accounting_admission','historical_execution_established']:
                self.assertIs(result[field],False)

    def test_all_field_requirements_remain_explicit(self):
        result=boundary.evaluate(boundary.fixture());rows={r['field']:r for r in result['field_mapping']}
        self.assertEqual(set(rows),set(boundary.contract.READING_FIELDS+boundary.EXTRA_FIELDS))
        self.assertEqual(len(rows),18)
        for field in boundary.contract.READING_FIELDS:self.assertEqual(rows[field]['status'],'unresolved')
        self.assertEqual(rows['source_document']['status'],'supported')
        self.assertEqual(rows['vendor_method']['status'],'unsupported')
        for row in rows.values():
            self.assertTrue(row['reason']);self.assertEqual(len(row['observation_refs']),12);self.assertEqual(len(row['note_refs']),2)

    def test_retained_values_and_net_versus_cash_flow_meaning(self):
        result=boundary.evaluate(boundary.fixture())
        expected={'annual.balance.receivables':'33,410','annual.opening.balance.receivables':'29,508',
            'annual.balance.vendor_receivables':'32,833','annual.opening.balance.vendor_receivables':'31,477',
            'annual.cash_flow.receivables':'(3,788)','annual.cash_flow.vendor_receivables':'(1,356)',
            'interim.balance.receivables':'29,639','interim.opening.balance.receivables':'33,410',
            'interim.balance.vendor_receivables':'29,667','interim.opening.balance.vendor_receivables':'32,833',
            'interim.cash_flow.receivables':'3,597','interim.cash_flow.vendor_receivables':'3,166'}
        self.assertEqual({r['observation']['record']['key']:r['observation']['record']['body']['literal'] for r in result['observations']},expected)
        for row in result['observations']:
            observation=row['observation'];body=observation['record']['body']
            self.assertEqual(body['value']['tag'],'known_displayed')
            self.assertEqual(observation['context']['perimeter'],'Apple Inc. consolidated')
            self.assertEqual(observation['context']['unit'],'USD million')
            if body['row_id'].removeprefix('opening.')=='balance.receivables':
                self.assertEqual(row['original']['label'],'Accounts receivable, net')

    def test_notes_preserve_vendor_method_difference_and_unknown_times(self):
        result=boundary.evaluate(boundary.fixture())
        for note in result['notes']:
            text=' '.join(note['extracted_text'].split())
            self.assertIn('does not reflect the sale of these components in products net sales',text)
            self.assertIn('reduction of products cost of sales when the related final products are sold',text)
        for row in result['observations']:
            source=row['original']['source_version']['body']
            self.assertEqual(source['supersedes_refs'],[])
            for field in ['public_at','ingested_at','reviewed_at']:self.assertEqual(source[field]['tag'],'unknown')

    def test_changed_target_view_or_issuer_refuses(self):
        request=boundary.fixture();request['target_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'target identity'):boundary.evaluate(request)
        for field,value in [('issuer','Different'),('information_mode','historical_asof')]:
            request=boundary.fixture();request['readiness_request'][field]=value
            with self.assertRaises(Exception):boundary.evaluate(request)
        request=boundary.fixture();packet=boundary.readiness.load_packet()
        request['readiness_request']['view_ref']=packet['aliases']['view.later']
        with self.assertRaisesRegex(ValueError,'view outside'):boundary.evaluate(request)

    def test_forged_claim_or_removed_obligation_fails_replay(self):
        request=boundary.fixture();result=boundary.evaluate(request)
        self.assertTrue(boundary.verify(request,result))
        for mutate in [lambda r:r.update(claims=[]),lambda r:r.update(executed=True),
                       lambda r:r['field_mapping'].pop(),lambda r:r['preserved_package']['obligations'].clear(),
                       lambda r:r['observations'][0]['observation']['record']['body'].update(literal='0')]:
            changed=deepcopy(result);mutate(changed);self.assertFalse(boundary.verify(request,changed))

    def test_byte_and_original_reading_corruption_refuse(self):
        request=boundary.fixture()
        with patch.object(boundary,'sha',return_value='0'*64):
            with self.assertRaisesRegex(ValueError,'target identity'):boundary.evaluate(request)
        packet=boundary.readiness.load_packet();base=boundary.readiness.evaluate(request['readiness_request'])
        observation=deepcopy(next(r for r in base['known_evidence']['annual_refs'] if r['record']['body']['row_id']=='balance.receivables'))
        observation['record']['body']['literal']='0'
        with self.assertRaisesRegex(ValueError,'reading literal'):boundary.source_row(packet,observation)
        with patch.dict(boundary.NOTE_SOURCES,{'annual':(boundary.NOTE_SOURCES['annual'][0],'0'*64)}):
            with self.assertRaisesRegex(ValueError,'note source bytes'):boundary.notes_for({'annual'})


if __name__=='__main__':unittest.main()
