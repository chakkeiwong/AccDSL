"""Economic categories preserve the original exact findings and structural failures."""
from copy import deepcopy
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import method_state_assessment_v1 as state
from test_method_collection_totals_v1 import fixture as total_fixture,known


def fixture():
    t,v=total_fixture()
    d={'profile':state.PROFILE,'method_id':'independent.category','version':'1','totals':t,
       'false_categories':{'total':'funding_failure'},'residual_prerequisites':['Caller-declared meaning of funding condition.']}
    return d,v
def run(d,v):return state.assess(d,v,[])


class StateAssessmentTests(unittest.TestCase):
    def test_active_false_category_preserves_original(self):
        d,v=fixture();v['globals']['expected']=known('0/1');before=deepcopy((d,v));r=run(d,v)
        self.assertEqual(r['status'],'funding_failure')
        self.assertEqual(r['original_assessment']['status'],'invalid')
        self.assertEqual(r['classified_findings'][0]['original_consequence'],'invalid')
        self.assertEqual(r['classified_findings'][0]['category'],'funding_failure')
        self.assertEqual(before,(d,v))
        for flag in ['executed','method_eligible','source_admission','accounting_admission']:self.assertFalse(r[flag])

    def test_unknown_inactive_and_true_are_not_reclassified(self):
        d,v=fixture();self.assertEqual(run(d,v)['status'],'state_requirements_satisfied')
        v['globals']['expected']={'status':'unknown','reason':'unobserved'}
        self.assertEqual(run(d,v)['status'],'unresolved')
        d['totals']['assessment']['requirements'][0]['guard']['value']=False
        r=run(d,v);self.assertEqual(r['status'],'state_requirements_satisfied')
        self.assertEqual(r['classified_findings'][0]['category'],'not_applicable')
        d['totals']['assessment']['required_known']=['expected']
        self.assertEqual(run(d,v)['status'],'unresolved')

    def test_structural_and_other_invalid_findings_keep_precedence(self):
        d,v=fixture();v['globals']['expected']=known('bad-number')
        self.assertEqual(run(d,v)['status'],'invalid')
        d,v=fixture();v['globals']['expected']=known('0/1')
        v['collections']['rows']['rows'][1]['id']=known('a')
        r=run(d,v);self.assertEqual(r['status'],'invalid')
        self.assertEqual(r['classified_findings'][0]['category'],'funding_failure')
        d,v=fixture();v['globals']['expected']=known('0/1')
        second=deepcopy(d['totals']['assessment']['requirements'][0]);second['id']='other'
        d['totals']['assessment']['requirements'].append(second)
        r=run(d,v);self.assertEqual(r['status'],'invalid')
        self.assertEqual([x['category'] for x in r['classified_findings']],['funding_failure','invalid'])

    def test_categories_cannot_map_missing_unsupported_or_structural_nodes(self):
        edits=[lambda d:d['false_categories'].update(absent='funding_failure'),
               lambda d:d['false_categories'].update(total='approved'),
               lambda d:d['totals']['assessment']['requirements'][0].update(on_false='unsupported')]
        for edit in edits:
            d,v=fixture();edit(d);self.assertEqual(run(d,v)['status'],'invalid')

    def test_capability_failure_remains_visible(self):
        d,v=fixture();d['totals']['assessment']['capabilities']=['missing']
        self.assertEqual(run(d,v)['status'],'unsupported')
        v['globals']['expected']=known('0/1');r=run(d,v)
        self.assertEqual(r['status'],'funding_failure')
        self.assertEqual(r['original_assessment']['assessment']['missing_capabilities'],['missing'])


if __name__=='__main__':unittest.main()
