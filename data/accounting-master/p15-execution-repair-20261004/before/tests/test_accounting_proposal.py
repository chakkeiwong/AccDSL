"""Integrity of proposal evidence and readiness; fixtures make no design claim."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from accounting_master_support import atomic_json, digest, load_json
from check_accounting_proposal import check_proposal, REQUIREMENTS, GAPS, CONTRACTS, DOMAINS, STAGES
from run_accounting_master import Master, ACCEPTED, CATALOG, stable_hash


class ProposalTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.write('docs/source.md', b'Original inspected source. Evidence is bounded.\n')
        self.spec = self.write('docs/specification.md', b'Proposed interface and fixture; synthetic test only.\n')
        self.documents = {}
        for phase in STAGES:
            d = {'schema_version': f'accdsl.proposal.{phase.lower()}.v1',
                 'product_implemented': False, 'human_acceptance': 'pending',
                 'limitations': 'Synthetic integrity fixture, not an accounting specification.',
                 'source_evidence': [self.source]}
            if phase == 'P15':
                d.update(requirements=self.coverage(REQUIREMENTS), gaps=self.coverage(GAPS),
                         open_decisions=[], candidate_initial_profile='Candidate A',
                         profile_alternative='Candidate B', selection_question='Which bounded first profile?',
                         prior_work=[{'phase': f'P{i:02}', 'role': 'exploratory_probe',
                             'scope': 'Bounded prototype', 'limitations': 'No product validity established',
                             'design_consequence': 'Compare against proposed interfaces',
                             'evidence': [self.source]} for i in range(15)], audit_note=[self.spec])
            elif phase == 'P16':
                d.update(coverage=self.stage_ref('P15'), open_decisions=[],
                    contracts=[{'id': c, **{k: 'Synthetic interface condition' for k in
                        ('inputs', 'outputs', 'invariants', 'failure_behavior', 'alternatives', 'chosen_reason')},
                        'specification': [self.spec], 'fixtures': [self.spec]} for c in sorted(CONTRACTS)],
                    initial_profile={**{k: 'Proposed fixture profile' for k in
                        ('name', 'rationale', 'included', 'excluded', 'acceptance_criteria', 'dependency_order')},
                        'status': 'proposed'})
            elif phase == 'P17':
                d.update(architecture=self.stage_ref('P16'), open_decisions=[],
                    domains=[{'id': c, **{k: 'Explicit bounded method assumption' for k in
                        ('scope', 'method', 'assumptions', 'authority_limits', 'case', 'unresolved', 'interface')},
                        'source_status': 'partial', 'evidence': [self.source],
                        'specification': [self.spec]} for c in sorted(DOMAINS)])
            elif phase == 'P18':
                base = 'docs/design/proposal/manuscript/'
                tex = self.write(base + 'main.tex', b'\\documentclass{article}\\begin{document}Fixture\\end{document}')
                pdf = self.write(base + 'main.pdf', b'%PDF-1.4\nSynthetic header; no render-quality claim.\n')
                log = self.write(base + 'build.log', b'Synthetic successful build record\n')
                page = self.write(base + 'page.png', b'Synthetic image placeholder\n')
                figure = self.write(base + 'figure.png', b'Included figure before change\n')
                external = self.write('docs/fixture-input.csv', b'value\n12\n')
                recorder = self.write(base + 'main.fls',
                    (f'PWD {self.root / base}\nINPUT main.tex\nINPUT figure.png\n'
                     'INPUT ../../../fixture-input.csv\nINPUT /usr/share/texmf/fixture.sty\n').encode())
                inputs = {r['path']: r['sha256'] for r in [tex, figure, external]}
                build_record = self.write(base + 'build-record.json', json.dumps({
                    'inputs_before': inputs, 'inputs_after': inputs,
                    'pdf_sha256': pdf['sha256'], 'exit_code': 0}).encode())
                d.update(architecture=self.stage_ref('P16'), methods=self.stage_ref('P17'),
                    main_tex=tex, pdf=pdf, source_files=[tex, figure, external],
                    build={'command': 'fixture only', 'exit_code': 0, 'environment': 'unit test', 'log': log,
                           'recorder': recorder, 'record': build_record, 'working_directory': base.rstrip('/'),
                           'environment_inputs': ['/usr/share/texmf/fixture.sty']},
                    rendered_pages=[page], render_review=[self.spec], baseline_preservation_review=[self.spec],
                    rendered_pdf_sha256=pdf['sha256'])
            elif phase == 'P19':
                d.update(stage_evidence={p: self.stage_ref(p) for p in ('P15', 'P16', 'P17', 'P18')},
                    requirements=self.coverage(REQUIREMENTS, final=True), gaps=self.coverage(GAPS, final=True),
                    open_decisions=[], status='candidate_for_independent_review',
                    initial_profile=[self.spec], implementation_sequence=[self.spec],
                    acceptance_fixtures=[self.spec], residual_work=[self.spec])
            self.documents[phase] = d
            self.save(phase)
            self.write(f'data/accounting-master/deliverables/{phase}/result.md', b'Synthetic result; review still required.\n')

    def write(self, name, content):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return {'path': name, 'sha256': digest(p), 'locator': 'whole synthetic fixture'}

    def stage_ref(self, phase):
        name = f'data/accounting-master/deliverables/{phase}/{STAGES[phase]}'
        return {'path': name, 'sha256': digest(self.root / name)}

    def save(self, phase):
        atomic_json(self.root / f'data/accounting-master/deliverables/{phase}/{STAGES[phase]}', self.documents[phase])

    def coverage(self, ids, final=False):
        return [{'id': c, 'status': 'specified' if final else 'open',
                 'assessment': 'Current evidence is partial', 'remaining_work': 'Design validation',
                 'design_consequence': 'Explicit specification required', 'evidence': [self.source],
                 **({'contract': 'docs/specification.md', 'scope': 'whole_product'} if final else {})}
                for c in sorted(ids)]

    def assert_fails(self, phase, fragment):
        report = check_proposal(self.root, phase)
        self.assertFalse(report['passed'])
        self.assertIn(fragment, ' '.join(report['errors']))
        self.assertFalse(report['acceptance']['phase_criteria_complete'])

    def test_complete_chain_reports_structural_evidence_only(self):
        for phase in STAGES:
            report = check_proposal(self.root, phase)
            self.assertTrue(report['passed'], report['errors'])
            self.assertGreater(report['tests'], 0)
            self.assertFalse(report['acceptance']['product_implemented'])
            self.assertEqual(report['acceptance']['human_acceptance'], 'pending')
        self.assertIn(self.source['path'], report['input_hashes'])
        self.assertIn('docs/design/proposal/manuscript/page.png', report['input_hashes'])

    def test_missing_or_duplicate_requirement_cannot_hide_coverage_gap(self):
        original = copy.deepcopy(self.documents['P15']['requirements'])
        for rows in (original[:-1], original[:-1] + [original[0]]):
            self.documents['P15']['requirements'] = rows
            self.save('P15')
            self.assert_fails('P15', 'complete unique coverage')

    def test_mutated_original_source_invalidates_entire_chain(self):
        (self.root / self.source['path']).write_text('Altered evidence\n')
        self.assert_fails('P15', 'source hash')
        self.assert_fails('P19', 'source hash')

    def test_fabricated_quote_fails_even_when_file_hash_matches(self):
        self.documents['P15']['source_evidence'] = [{**self.source, 'quote': 'This sentence was not in the source'}]
        self.save('P15')
        self.assert_fails('P15', 'source quote')

    def test_design_must_declare_failure_behavior(self):
        del self.documents['P16']['contracts'][0]['failure_behavior']
        self.save('P16')
        self.assert_fails('P16', 'contract semantics')

    def test_changed_prerequisite_does_not_reuse_stale_design_review(self):
        self.documents['P16']['initial_profile']['included'] = 'Different product scope'
        self.save('P16')
        self.assert_fails('P17', 'source hash')
        self.assert_fails('P19', 'source hash')

    def test_pdf_build_and_render_evidence_are_required_and_bound(self):
        original = copy.deepcopy(self.documents['P18'])
        for key, value, failure in [('rendered_pdf_sha256', '0' * 64, 'render bound'),
                                     ('rendered_pages', [], 'nonempty source references')]:
            self.documents['P18'] = {**copy.deepcopy(original), key: value}
            self.save('P18')
            self.assert_fails('P18', failure)
        self.documents['P18'] = original
        original['build']['exit_code'] = 1
        self.save('P18')
        self.assert_fails('P18', 'successful recorded build')

    def test_added_unpinned_latex_source_invalidates_candidate(self):
        self.write('docs/design/proposal/manuscript/extra.tex', b'Unreviewed chapter')
        self.assert_fails('P18', 'all candidate sources pinned')

    def test_included_figure_and_external_data_must_be_bound(self):
        original = copy.deepcopy(self.documents['P18']['source_files'])
        for name in ('docs/design/proposal/manuscript/figure.png', 'docs/fixture-input.csv'):
            self.documents['P18']['source_files'] = [r for r in original if r['path'] != name]
            self.save('P18')
            self.assert_fails('P18', 'all build inputs pinned')
        self.documents['P18']['source_files'] = original
        self.save('P18')
        self.assertTrue(check_proposal(self.root, 'P18')['passed'])

    def test_changed_figure_closes_reviewed_proposal_gate(self):
        master, _, _ = self.reviewed_master()
        self.assertTrue(master.proposal_gate()['ready'])
        (self.root / 'docs/design/proposal/manuscript/figure.png').write_bytes(b'Changed figure')
        self.assertFalse(master.proposal_gate()['ready'])

    def test_repinning_changed_source_without_rebuild_fails(self):
        for name in ('docs/design/proposal/manuscript/main.tex', 'docs/design/proposal/manuscript/figure.png'):
            ref = self.write(name, b'Newer bytes than the built PDF')
            d = self.documents['P18']
            d['source_files'] = [ref if r['path'] == name else r for r in d['source_files']]
            if name.endswith('.tex'): d['main_tex'] = ref
            self.save('P18')
            self.assert_fails('P18', 'source bytes bound to successful build')

    def test_open_product_decision_blocks_readiness(self):
        self.documents['P19']['open_decisions'] = [{
            'id': 'D1', 'question': 'Unresolved scope?', 'proposed_answer': 'Option A',
            'alternative': 'Option B', 'consequence': 'Different interfaces', 'next_step': 'Review the scope',
            'blocks_proposal': True}]
        self.save('P19')
        self.assert_fails('P19', 'no unresolved proposal blocker')

    def test_boolean_self_approval_cannot_replace_candidate_status(self):
        self.documents['P19']['status'] = 'ready'
        self.documents['P19']['ready'] = True
        self.save('P19')
        self.assert_fails('P19', 'readiness cannot authorise itself')

    def reviewed_master(self):
        catalog = load_json(Path(__file__).resolve().parents[1] / CATALOG)
        atomic_json(self.root / CATALOG, catalog)
        master = Master(self.root)
        for phase in STAGES:
            record = master.state['phases'][phase]
            report = check_proposal(self.root, phase)
            record.update(status=ACCEPTED, accepted_phase_hash=stable_hash(master.phases[phase]),
                          accepted_dependencies=master.review_dependencies(master.phases[phase]),
                          evidence_hashes=report['input_hashes'])
        review_path = 'data/accounting-master/runs/synthetic/P19/review_result-0.response.json'
        review = {'verdict': 'AGREE', 'summary': 'Synthetic review fixture',
                  **{k: [] for k in ('steps', 'assumptions', 'checks', 'evidence', 'issues', 'residuals', 'next_actions')}}
        process_path = review_path.replace('.response.json', '.process.json')
        atomic_json(self.root / review_path, review)
        atomic_json(self.root / process_path, {'exit_code': 0, 'reason': None, 'surviving_group_members': []})
        record.update(accepted_review_path=review_path)
        record['evidence_hashes'].update({p: digest(self.root / p) for p in (review_path, process_path)})
        return master, review_path, process_path

    def test_reviewed_proposal_still_cannot_enable_product_execution(self):
        master, _, _ = self.reviewed_master()
        gate = master.proposal_gate()
        self.assertTrue(gate['ready'], gate['reason'])
        self.assertFalse(gate['implementation_enabled'])
        self.assertEqual(gate['human_acceptance'], 'pending')
        self.assertIn('blocked_by_proposal_gate', master.phase_block('P08'))

    def test_missing_or_changed_independent_review_process_closes_gate(self):
        for change in ('unbound', 'changed', 'missing'):
            master, _, process = self.reviewed_master()
            if change == 'unbound':
                del master.state['phases']['P19']['evidence_hashes'][process]
            elif change == 'changed':
                atomic_json(self.root / process, {'exit_code': 1, 'reason': 'timeout'})
            else:
                (self.root / process).unlink()
            self.assertFalse(master.proposal_gate()['ready'], change)

    def test_acceptance_must_bind_sources_and_render_bytes(self):
        master, _, _ = self.reviewed_master()
        del master.state['phases']['P19']['evidence_hashes']['docs/design/proposal/manuscript/page.png']
        self.assertFalse(master.proposal_gate()['ready'])

    def test_invalid_or_empty_json_is_a_failed_check(self):
        p = self.root / self.stage_ref('P15')['path']
        for value in ('', 'null', '[]', '{"schema_version": false}'):
            p.write_text(value)
            self.assertFalse(check_proposal(self.root, 'P15')['passed'])


if __name__ == '__main__':
    unittest.main()
