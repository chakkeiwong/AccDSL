"""Refresh located author dispositions without overwriting historical acceptance."""
import copy
import hashlib
import json
import re
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, value):
    (UNIT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


baseline = json.loads((UNIT / 'baseline.json').read_text())
prior = json.loads((ROOT / baseline['prior_assessment']).read_text())
comparison = json.loads((UNIT / 'source-comparison.json').read_text())
by_old = {p['old_path']: p for p in comparison}
candidate = ROOT / baseline['candidate']
assert sha(candidate / 'accounting-product-proposal.pdf') == baseline['candidate_pdf_sha256']
assert sha(ROOT / baseline['prior_assessment']) == baseline['prior_assessment_sha256']
units = {
    'conflict': 'jpmorgan-reference-conflict-20261013',
    'transition': 'insurance-transition-balances-20261013',
    'reinsurance': 'reinsurance-transition-recovery-20261013',
    'impairment': 'insurance-acquisition-recoverability-20261013',
    'incorporation': 'insurance-acquisition-incorporation-20261013',
    'new_contracts': 'munich-new-contracts-20261013',
    'measurement': 'munich-measurement-bridge-20261013',
}
new_evidence = {}
for key, name in units.items():
    path = ROOT / 'data/accounting-master' / name / 'result.md'
    new_evidence[key] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                         'role': 'Scoped completed author source/method evidence; not independent acceptance'}
updates = {
    'MC02': ('Actual Munich Re rows preserve source signs, blank CSM cells, rounded euros and GMM/VFA/PAA population distinctions. A hypothetical joint rounding witness is explicitly not hidden issuer data.', None, ['new_contracts', 'measurement']),
    'MC03': ('The added issuer readings interpret policy, table scope and the continued PAA exclusion footnote; the source-reference walkthrough separates literal attribution from supported navigation.', None, ['conflict', 'new_contracts', 'measurement']),
    'MC04': ('The actual JPMorgan source-reference conflict now has checked transcription, rejected and admitted navigation readings, preserved assertions and a worked supersession example. Existing extraction-error examples remain.', 'Independent review and actual human adjudication of the bounded case remain pending. No financial-measurement conflict is claimed; wider accounting admission and whole-package semantics remain separate.', ['conflict']),
    'MC07': ('Munich Re demonstrates a precisely sourced nested reporting scope: measurement components include PAA incurred claims but exclude PAA remaining coverage. Its differences from the full liability reconciliation are explicitly mapped.', None, ['measurement']),
    'MC08': ('Conditional transition/acquisition histories preserve group identity and linked balances. Actual Munich Re aggregates constrain reporting populations without identifying the underlying group histories.', None, ['transition', 'incorporation', 'measurement']),
    'MC10': ('Conditional model inputs, reported issuer amounts, hypothetical rounding values and unresolved actual facts stay distinct across the new examples. A refuted source locator is not an admissible accounting alternative.', None, ['conflict', 'new_contracts']),
    'MC11': ('Acquisition origination/renewal populations, impairment history, later incorporation and separate issued/reinsurance measurements now have worked memory consequences. Segment aggregation still cannot replace group state.', None, ['impairment', 'incorporation', 'reinsurance']),
    'MC13': ('The conditional acquisition example works asset derecognition, initial group measurement and a separate premium event. Two offsetting errors can preserve equity while component amounts are wrong.', None, ['incorporation']),
    'MC16': ('Transition, acquisition impairment/reversal and premium receipt have complete conditional balance/equity bridges. Actual CSM connects new business, period service and closing balances, preserving distinct cash/expense populations.', 'Join a complete real reporting period across the five statements and its material note/query dependencies, then develop admissible joint histories and conditional paths. Later report execution and independent conformance remain separate.', ['transition', 'impairment', 'incorporation', 'measurement']),
    'MC19': ('Historical AASB17 transition, loss-recovery, acquisition and recognition paragraphs support the bounded methods; actual Munich Re EU-IFRS disclosures remain a separate source class. No current operative edition is supplied.', None, ['transition', 'reinsurance', 'impairment', 'incorporation']),
    'MC22': ('Issued transition CSM/loss components, held-reinsurance recovery, acquisition impairment/reversal and incorporation are now derived and worked. Munich Re adds actual initial-recognition and CSM/population reconciliations.', 'Actual group valuation and transition reconstruction, priced guarantees, broader acquisition/reinsurance interactions, actuarial estimation and validation, and applicable operative authority remain unfinished. The acquisition-expense residual435 is still unassigned; no private asset is inferred.', ['transition', 'reinsurance', 'impairment', 'incorporation', 'new_contracts', 'measurement']),
    'MC25': ('The actual reference repair now tests negative-search selection dependencies and refreshed review annotations, preserving immutable old views. The storage and replay contract itself is unchanged.', None, ['conflict']),
    'MC27': ('The JPMorgan example now walks through Propose, layer-specific Accept, rejection of the refuted alternative and Supersede, with five dependent results identified for recomputation.', 'Independent/domain/human review and eventual workflow execution remain pending. The bounded actual source-reference case is delivered; do not schedule its creation again or claim complete E05 acceptance.', ['conflict']),
    'MC28': ('The preserved Northstar case is joined by seven further bounded integrations, including an actual conflict and insurer tables. These enrich local examples but do not join all of a real company\'s statement and operating dependencies.', 'Connect a declared real period across statements, note dependencies, admissible histories and all affected future results. Start with complete Apple FY2024 statement rows and relationships; retain external-package and private-fact gaps.', ['conflict', 'new_contracts', 'measurement']),
    'MC30': ('New source readings bind retained historical AASB17 and Munich Re pages to exact hashes. Three new Munich pages and five explicitly carried reviews support the last integration; no new source retrieval or current edition is claimed.', None, ['measurement']),
    'MC32': ('Version 2.59 is the 209-page current author candidate. Seven integrations preserve prior sources, equations and citations with bounded render inspection; the new insurance argument remains provisional.', None, list(units)),
    'MC33': ('Scoped arithmetic, source and document checks support the new examples. The author readiness supplement remains negative and explicitly carries twenty unchanged referenced-source judgments.', None, list(units)),
    'MC34': ('All 35 requirements and 18 gaps are reassessed after the seven repairs. The ready queue now prioritises a joined real statement case while preserving blocked sources, the historical controller and held implementation.', 'Maintain dependencies and original acceptance obligations; complete the selected real-case increment, then reassess its missing history/path links. No source count or example count closes the whole mission.', list(units)),
    'MC35': ('Internal source inspection, calculation, manuscript repair and comparison of ready tasks continue without outsourcing unresolved preparation. No paid, external or independent acceptance is invented.', None, list(units)),
}
assessment = copy.deepcopy(prior)
assessment.update({'candidate_version': '2.59', 'candidate_pdf_sha256': baseline['candidate_pdf_sha256'],
    'review_class': 'Author delta reassessment from Version2.52; explicit carried judgments for unchanged sources',
    'prior_assessment': {'path': baseline['prior_assessment'], 'sha256': baseline['prior_assessment_sha256']},
    'next_repair': 'Apple FY2024 complete statement rows and relationship network',
    'next_plan': 'docs/plans/accounting-apple-statement-network-20261013.md'})
assessment['evidence'].update(new_evidence)
for row in assessment['requirements']:
    row['prior_assessment_text'] = row['current_assessment']
    row['review_basis'] = 'Prior author disposition carried; current sources checked by hash, no new independent acceptance'
    row['current_sources'] = [
        {'path': by_old[r['path']]['new_path'], 'sha256': by_old[r['path']]['new_sha256'],
         'review_basis': 'Exact source unchanged; prior judgment carried' if by_old[r['path']]['equal'] else 'Changed passage inspected; bounded author delta review'}
        for r in row['current_sources']]
    if row['id'] in updates:
        current, remaining, refs = updates[row['id']]
        row['current_assessment'] = current
        if remaining:
            row['remaining_work'] = remaining
        row['supplemental_evidence'] = sorted(set(row['supplemental_evidence']) | set(refs))
        row['review_basis'] = 'Current change and relevant scoped results inspected; unchanged contracts carried'
    if row['id'] in {'MC04', 'MC27'}:
        row['dependency'] = 'Bounded walkthrough delivered; independent/human review and later implementation remain distinct'
    if row['id'] in {'MC01', 'MC03', 'MC16', 'MC28'}:
        row['dependency'] = 'Retained annual statement source and completed note records -> joined statement case -> joint history/path dependencies'

gupdates = {
    'G4': ('Conditional insurance bridges now supplement corporate/FX reference cases. Actual issuer reconciliations preserve measurement populations and residuals.', None),
    'G5': ('The real cases now include a source conflict and actual insurer reconciliations, but they remain separate bounded pieces. Complete note retention and many local examples do not supply a joined company path.', 'Connect complete Apple FY2024 statement rows and existing note dependencies, then develop joint admissible histories and conditional paths. Preserve external package and private-fact limitations.'),
    'G7': ('Historical-source transition, reinsurance recovery and acquisition methods are worked; actual Munich Re initial/CSM disclosures add scoped evidence.', 'Operative authority, actual group/contract facts, priced guarantees, broader financing/credit methods and actuarial validation remain. Do not call the delivered conditional acquisition/transition methods wholly absent.'),
    'G11': ('Source-reference review and precise issuer table/population readings extend material semantics; complete package and query coverage remain unestablished.', None),
    'G12': ('The Munich Re full/subset reconciliation supplies an actual nested-population mapping with an explicit PAA exclusion footnote.', None),
    'G15': ('Actual and conditional values, hypothetical rounding witnesses, source blanks and rejected navigation alternatives have distinct admission consequences.', 'Keep those distinctions in real-case joins and later cross-category conformance. Do not infer treatment, probability or missing journal causes from an arithmetic residual.'),
    'G16': ('The worked acquisition lifecycle retains origination/renewal allocation and impairment history; actual segment tables still leave private group memory unresolved.', None),
    'G17': ('The actual source-reference walkthrough now includes proposed layer decisions, preserved/rejected readings, supersession, negative-search dependencies and selective recomputation.', 'Independent review, actual human adjudication and later workflow execution remain pending. The bounded example is delivered; broader E05 acceptance stays open.'),
    'G10': ('This author reassessment preserves every original obligation and the negative historical P19 while crediting seven checked integrations.', 'Resolve the substantive real-case, authority, literature and interface gaps; obtain applicable independent acceptance separately. Counts and clean builds do not confer readiness.'),
}
for gap in assessment['gaps']:
    gap['prior_assessment_text'] = gap['current_assessment']
    gap['review_basis'] = 'Prior author judgment carried; relevant current requirement dispositions inspected'
    if gap['id'] in gupdates:
        current, remaining = gupdates[gap['id']]
        gap['current_assessment'] = current
        if remaining:
            gap['remaining_work'] = remaining
        gap['review_basis'] = 'Current scoped results and requirement interactions inspected'
    if gap['id'] in {'G5', 'G11'}:
        gap['dependency'] = 'Retained statements and checked note records; then actual history/path dependencies'
    if gap['id'] == 'G17':
        gap['dependency'] = 'Delivered example; independent/human acceptance and later execution'

checks = {'35_requirements': {r['id'] for r in assessment['requirements']} == {f'MC{i:02d}' for i in range(1, 36)},
          '18_gaps': {r['id'] for r in assessment['gaps']} == {f'G{i}' for i in range(1, 19)},
          'not_ready_preserved': assessment['ready'] is False and assessment['status'] == 'not_ready',
          'five_obligations_preserved': assessment['remaining_blockers'] == ['E01', 'E05', 'E07', 'E08', 'E14'],
          'implementation_held': assessment['implementation_enabled'] is False,
          'prior_assessment_preserved': sha(ROOT / baseline['prior_assessment']) == baseline['prior_assessment_sha256'],
          'historical_p19_preserved': sha(ROOT / 'data/accounting-master/deliverables/P19/readiness.json') == baseline['historical_p19_sha256'],
          'requirements_preserved': sha(ROOT / 'docs/plans/accounting-mission-requirements.md') == baseline['requirements_sha256']}
original = {}
for line in (ROOT / 'docs/plans/accounting-mission-requirements.md').read_text().splitlines():
    if re.match(r'\| MC\d\d \|', line):
        columns = [c.strip() for c in line.split('|')[1:-1]]
        original[columns[0]] = columns
for old, row in zip(prior['requirements'], assessment['requirements']):
    checks['original_obligation:' + row['id']] = row['requirement'] == original[row['id']][1] and row['acceptance_obligation'] == original[row['id']][2]
    checks['status_not_promoted:' + row['id']] = row['status'] == old['status']
    checks['evidence_resolves:' + row['id']] = all(key in assessment['evidence'] for key in row['supplemental_evidence'])
for old, gap in zip(prior['gaps'], assessment['gaps']):
    checks['gap_preserved:' + gap['id']] = old['original_obligation'] == gap['original_obligation'] and old['status'] == gap['status']
for p in comparison:
    checks['source_current:' + p['new_path']] = sha(ROOT / p['new_path']) == p['new_sha256']
for key, ev in assessment['evidence'].items():
    checks['evidence_hash:' + key] = sha(ROOT / ev['path']) == ev['sha256']
checks['next_plan_exists'] = (ROOT / assessment['next_plan']).is_file()
failed = [k for k, value in checks.items() if not value]
save('assessment.json', assessment)
save('integrity-checks.json', {'checks': checks, 'passed': sum(checks.values()), 'failed': failed,
                              'source_files': len(comparison), 'unchanged_sources': sum(p['equal'] for p in comparison)})
lines = ['# Requirement dispositions after Version 2.59', '',
    'Author delta reassessment; readiness **not_ready**. Original acceptance wording is preserved in assessment.json.',
    'Twenty of 23 referenced files are unchanged from the prior author assessment. Their judgments are carried, not newly independently reviewed.', '',
    '| Requirement | Status | Current evidence | Remaining acceptance work |', '| --- | --- | --- | --- |']
for row in assessment['requirements']:
    lines.append(f"| {row['id']} | {row['status']} | {row['current_assessment']} | {row['remaining_work']} |")
lines += ['', '| Gap | Status | Current evidence | Remaining acceptance work |', '| --- | --- | --- | --- |']
for row in assessment['gaps']:
    lines.append(f"| {row['id']} | {row['status']} | {row['current_assessment']} | {row['remaining_work']} |")
(UNIT / 'dispositions.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({'passed': sum(checks.values()), 'failed': failed, 'requirements': 35, 'gaps': 18, 'unchanged_sources': 20}))
raise SystemExit(bool(failed))
