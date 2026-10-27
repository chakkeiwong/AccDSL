import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('state_program', ROOT/'scripts/check_company_state_program.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProgramChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)/'program'
        shutil.copytree(module.DEFAULT, self.directory, ignore=shutil.ignore_patterns('state-theory-attempt-*'))
    def tearDown(self):
        self.tmp.cleanup()
    def change(self, filename, mutate):
        p = self.directory/filename
        d = json.loads(p.read_text())
        mutate(d)
        p.write_text(json.dumps(d))
    def assert_invalid(self, fragment):
        result = module.validate(ROOT, self.directory)
        self.assertFalse(result['valid'])
        self.assertTrue(any(fragment in e for e in result['errors']), result['errors'])
    def test_current(self):
        self.assertTrue(module.validate(ROOT,self.directory)['valid'])
    def test_dependency_cycle(self):
        self.change('program.json',lambda d:d['tasks'][0]['depends_on'].append(d['tasks'][0]['id']))
        self.assert_invalid('cycle')
    def test_missing_dependency(self):
        self.change('program.json',lambda d:d['tasks'][0]['depends_on'].append('MISSING'))
        self.assert_invalid('missing dependency')
    def test_condition_tampering(self):
        self.change('acceptance-map.json',lambda d:d['rows'][0]['original_row']['original_condition'].update(acceptance='weaker criterion'))
        self.assert_invalid('original conditions changed')
    def test_clause_loss(self):
        self.change('clause-map.json',lambda d:d['rows'].pop())
        self.assert_invalid('original conditions changed')
    def test_evidence_missing(self):
        self.change('program.json',lambda d:d['tasks'][0].update(evidence=[]))
        self.assert_invalid('complete task has no evidence')
    def test_failed_hash(self):
        self.change('source-lock.json',lambda d:d.update({'docs/AccDSL-latest.pdf':'bad'}))
        self.assert_invalid('identity changed')
    def test_unmapped_failure(self):
        self.change('failure-map.json',lambda d:d['rows'][0].update(tasks=[]))
        self.assert_invalid('unmapped failure')
    def test_held_never_ready(self):
        self.change('program.json',lambda d:d['tasks'][0].update(status='held'))
        self.assertNotIn('B01',module.validate(ROOT,self.directory)['ready'])


if __name__=='__main__':unittest.main()
