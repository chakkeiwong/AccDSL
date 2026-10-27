#!/usr/bin/env python3
"""Structural evidence checks for proposal work; semantic review remains separate.

These checks never certify accounting validity, prose quality or human approval.
The master owns phase acceptance and derives readiness from completed reviews.
"""
import argparse
import json
from pathlib import Path

from accounting_master_support import digest, load_json, local_path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = {f'MC{i:02}' for i in range(1, 36)}
GAPS = {f'G{i}' for i in range(1, 19)}
STAGES = {
    'P15': 'coverage.json', 'P16': 'architecture.json', 'P17': 'methods.json',
    'P18': 'manuscript.json', 'P19': 'readiness.json',
}
CONTRACTS = {'evidence', 'history_families', 'uncertainty', 'accounting', 'time',
             'language_ir', 'persistence', 'interfaces', 'failure_semantics'}
DOMAINS = {'corporate', 'bonds_equity', 'groups_fx', 'banks', 'insurance',
           'ifrs', 'us_gaap', 'asbe', 'forecasting', 'literature', 'software_reuse'}


def check_proposal(root, phase):
    root = Path(root).resolve()
    checks, pins = [], {}

    def need(name, value):
        checks.append({'id': name, 'passed': bool(value)})
        if not value:
            raise ValueError(name)

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def anchor(row):
        need('source reference fields', isinstance(row, dict) and
             all(text(row.get(k)) for k in ('path', 'sha256')))
        name = row['path']
        p = local_path(root, name)
        need('canonical source path', '..' not in Path(name).parts and
             Path(name).as_posix() == name and not (root / name).is_symlink())
        need('nonempty source: ' + name, p.is_file() and p.stat().st_size > 0)
        actual = digest(p)
        need('source hash: ' + name, actual == row['sha256'])
        pins[name] = actual
        if 'quote' in row:
            need('source quote: ' + name, text(row['quote']) and
                 ' '.join(row['quote'].split()) in ' '.join(p.read_text().split()))
        return p

    def refs(rows):
        need('nonempty source references', isinstance(rows, list) and bool(rows))
        for row in rows:
            anchor(row)

    def coverage(rows, ids, final=False):
        need('complete unique coverage', isinstance(rows, list) and len(rows) == len(ids)
             and {r.get('id') for r in rows} == ids)
        for row in rows:
            need(row['id'] + ' substantive assessment', all(text(row.get(k)) for k in
                 ('assessment', 'remaining_work', 'design_consequence')))
            refs(row.get('evidence'))
            need(row['id'] + ' located evidence', any(text(r.get('quote')) or text(r.get('locator'))
                 for r in row['evidence']))
            if final:
                need(row['id'] + ' design specified', row.get('status') in {'specified', 'checked_design'})
                need(row['id'] + ' design contract', text(row.get('contract')) and
                     row.get('scope') in {'initial_profile', 'later_profile', 'whole_product'})
            else:
                need(row['id'] + ' honest coverage state', row.get('status') in
                     {'open', 'partial', 'specified', 'checked_design'})

    def decisions(rows, final=False):
        need('decision list', isinstance(rows, list))
        need('unique decisions', len({r['id'] for r in rows}) == len(rows))
        for row in rows:
            need('decision consequence', all(text(row.get(k)) for k in
                 ('id', 'question', 'proposed_answer', 'alternative', 'consequence', 'next_step')))
            need('explicit proposal blocking state', type(row.get('blocks_proposal')) is bool)
            if final:
                need('no unresolved proposal blocker: ' + row['id'], row['blocks_proposal'] is False)

    def previous(identifier, ref):
        expected = f'data/accounting-master/deliverables/{identifier}/{STAGES[identifier]}'
        need('exact stage dependency', ref.get('path') == expected)
        anchor(ref)
        other = check_proposal(root, identifier)
        need('valid prerequisite ' + identifier, other['passed'])
        pins.update(other['input_hashes'])

    def body(phase, d):
        need('proposal schema', d.get('schema_version') == 'accdsl.proposal.' + phase.lower() + '.v1')
        need('explicit evidence boundary', d.get('product_implemented') is False and
             d.get('human_acceptance') == 'pending' and text(d.get('limitations')))
        refs(d.get('source_evidence'))
        if phase == 'P15':
            coverage(d.get('requirements'), REQUIREMENTS)
            coverage(d.get('gaps'), GAPS)
            decisions(d.get('open_decisions'))
            need('initial profile remains a design choice', all(text(d.get(k)) for k in
                 ('candidate_initial_profile', 'profile_alternative', 'selection_question')))
            prototypes = d.get('prior_work', [])
            need('all historical phases accounted for', len(prototypes) == 15 and
                 {r.get('phase') for r in prototypes} == {f'P{i:02}' for i in range(15)})
            for row in prototypes:
                need('prior work disposition', row.get('role') in {'source_evidence', 'exploratory_probe', 'unexecuted'}
                     and all(text(row.get(k)) for k in ('scope', 'limitations', 'design_consequence')))
                refs(row.get('evidence'))
            refs(d.get('audit_note'))
        elif phase == 'P16':
            previous('P15', d['coverage'])
            rows = d.get('contracts', [])
            need('whole architecture contracts', len(rows) == len(CONTRACTS) and
                 {r.get('id') for r in rows} == CONTRACTS)
            for row in rows:
                need('contract semantics', all(text(row.get(k)) for k in
                     ('inputs', 'outputs', 'invariants', 'failure_behavior', 'alternatives', 'chosen_reason')))
                refs(row.get('specification'))
                refs(row.get('fixtures'))
            profile = d.get('initial_profile', {})
            need('bounded profile decision', all(text(profile.get(k)) for k in
                 ('name', 'rationale', 'included', 'excluded', 'acceptance_criteria', 'dependency_order')))
            need('first slice provisional until reviewed', profile.get('status') == 'proposed')
            decisions(d.get('open_decisions'))
        elif phase == 'P17':
            previous('P16', d['architecture'])
            rows = d.get('domains', [])
            need('requested domain coverage', len(rows) == len(DOMAINS) and {r.get('id') for r in rows} == DOMAINS)
            for row in rows:
                need('domain design and limits', all(text(row.get(k)) for k in
                     ('scope', 'method', 'assumptions', 'authority_limits', 'case', 'unresolved', 'interface')))
                need('honest source status', row.get('source_status') in {'inspected', 'partial', 'blocked'})
                refs(row.get('evidence'))
                refs(row.get('specification'))
            decisions(d.get('open_decisions'))
        elif phase == 'P18':
            previous('P16', d['architecture'])
            previous('P17', d['methods'])
            source = anchor(d['main_tex'])
            pdf = anchor(d['pdf'])
            need('actual LaTeX and PDF', source.suffix == '.tex' and pdf.suffix == '.pdf'
                 and pdf.read_bytes().startswith(b'%PDF-'))
            candidate_root = root / 'docs/design/proposal/manuscript'
            need('new integrated proposal candidate', source.is_relative_to(candidate_root) and pdf.is_relative_to(candidate_root))
            source_files = d.get('source_files', [])
            refs(source_files)
            need('main source in build inputs', d['main_tex'] in source_files)
            listed = {r['path'] for r in source_files}
            actual = {str(p.relative_to(root)) for p in candidate_root.rglob('*')
                      if p.is_file() and p.suffix in {'.tex', '.bib', '.sty', '.cls'}}
            need('all candidate sources pinned', actual <= listed)
            build = d.get('build', {})
            need('successful recorded build', text(build.get('command')) and build.get('exit_code') == 0
                 and type(build.get('exit_code')) is int and text(build.get('environment')))
            anchor(build['log'])
            recorder = anchor(build['recorder'])
            working = local_path(root, build['working_directory'])
            need('build working directory', working.is_dir())
            project_inputs, environment_inputs = set(), set()
            for line in recorder.read_text().splitlines():
                if line.startswith('PWD '):
                    need('recorder working directory', Path(line[4:]).resolve() == working)
                if line.startswith('INPUT '):
                    dependency = (working / line[6:]).resolve()
                    if dependency.is_relative_to(root):
                        project_inputs.add(dependency.relative_to(root).as_posix())
                    else:
                        environment_inputs.add(str(dependency))
            need('actual recorded project inputs', bool(project_inputs) and d['main_tex']['path'] in project_inputs)
            need('all build inputs pinned including figures and external project files', project_inputs <= listed)
            need('environment dependencies identified separately',
                 isinstance(build.get('environment_inputs'), list) and
                 set(build['environment_inputs']) == environment_inputs)
            build_record = load_json(anchor(build['record']))
            current_inputs = {r['path']: r['sha256'] for r in source_files}
            need('source bytes bound to successful build',
                 build_record.get('inputs_before') == current_inputs and
                 build_record.get('inputs_after') == current_inputs and
                 build_record.get('pdf_sha256') == d['pdf']['sha256'] and
                 type(build_record.get('exit_code')) is int and build_record['exit_code'] == 0)
            refs(d.get('rendered_pages'))
            refs(d.get('render_review'))
            refs(d.get('baseline_preservation_review'))
            need('render bound to PDF', d.get('rendered_pdf_sha256') == d['pdf']['sha256'])
            render = load_json(anchor(d['render_record']))
            page_hashes = {r['path']: r['sha256'] for r in d['rendered_pages']}
            need('unique rendered pages', len(page_hashes) == len(d['rendered_pages']))
            need('render command recorded', text(render.get('command')) and text(render.get('environment'))
                 and type(render.get('exit_code')) is int and render['exit_code'] == 0)
            need('render input bound to current PDF',
                 render.get('pdf_path') == d['pdf']['path'] and
                 render.get('pdf_sha256_before') == d['pdf']['sha256'] and
                 render.get('pdf_sha256_after') == d['pdf']['sha256'])
            need('render outputs bound to pages', render.get('page_hashes') == page_hashes)
            review = load_json(anchor(d['render_review_record']))
            need('review bound to render record',
                 review.get('render_record_path') == d['render_record']['path'] and
                 review.get('render_record_sha256') == d['render_record']['sha256'])
            need('review binds inspected pages and notes', review.get('page_hashes') == page_hashes and
                 review.get('review_hashes') == {r['path']: r['sha256'] for r in d['render_review']} and
                 all(text(review.get(k)) for k in ('reviewer', 'reviewed_at', 'scope')))
        elif phase == 'P19':
            for identifier in ('P15', 'P16', 'P17', 'P18'):
                previous(identifier, d['stage_evidence'][identifier])
            coverage(d.get('requirements'), REQUIREMENTS, final=True)
            coverage(d.get('gaps'), GAPS, final=True)
            decisions(d.get('open_decisions'), final=True)
            blockers = {}
            for identifier in ('P15', 'P16', 'P17'):
                upstream = load_json(local_path(root, d['stage_evidence'][identifier]['path']))
                for row in upstream['open_decisions']:
                    if row['blocks_proposal']:
                        blockers[(identifier, row['id'])] = row
            dispositions = d.get('decision_dispositions', [])
            need('upstream decision disposition list', isinstance(dispositions, list))
            keys = [(r.get('stage'), r.get('decision_id')) for r in dispositions]
            need('all upstream blockers explicitly disposed', len(keys) == len(set(keys)) and set(keys) == set(blockers))
            final_ids = {r['id'] for r in d['open_decisions']}
            for row in dispositions:
                need('supported blocker disposition', row.get('status') in {'resolved', 'superseded'} and
                     all(text(row.get(k)) for k in ('answer', 'rationale')))
                refs(row.get('evidence'))
                if row['status'] == 'superseded':
                    need('superseding nonblocking final decision exists', row.get('superseding_decision_id') in final_ids)
            need('readiness cannot authorise itself', d.get('status') == 'candidate_for_independent_review')
            refs(d.get('initial_profile'))
            refs(d.get('implementation_sequence'))
            refs(d.get('acceptance_fixtures'))
            refs(d.get('residual_work'))
        else:
            raise ValueError('unknown proposal phase')

    errors = []
    try:
        need('registered proposal phase', phase in STAGES)
        name = f'data/accounting-master/deliverables/{phase}/{STAGES[phase]}'
        path = local_path(root, name)
        d = load_json(path)
        need('nonempty proposal object', isinstance(d, dict) and bool(d))
        pins[name] = digest(path)
        result_name = f'data/accounting-master/deliverables/{phase}/result.md'
        result = local_path(root, result_name)
        need('substantive result note', result.is_file() and bool(result.read_text().strip()))
        pins[result_name] = digest(result)
        body(phase, d)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        errors.append(str(error))
    passed = not errors and bool(checks) and all(c['passed'] for c in checks)
    criteria_count = 4
    return {'schema_version': 'accdsl.proposal.check.v1', 'phase': phase,
            'passed': passed, 'tests': len(checks), 'checks': checks, 'errors': errors,
            'input_hashes': pins,
            'acceptance': {'phase_criteria_complete': passed,
                'criteria': {f'criterion_{i}': 'complete_bounded' if passed else 'incomplete'
                             for i in range(1, criteria_count + 1)},
                'scope': 'Structural evidence only; substantive design requires independent result review.',
                'product_implemented': False, 'human_acceptance': 'pending'}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', required=True, choices=STAGES)
    parser.add_argument('--check', action='store_true', required=True)
    args = parser.parse_args()
    report = check_proposal(ROOT, args.phase)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report['passed'] else 1)
