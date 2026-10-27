"""Bind the inspected 3.44 integration; do not freeze its ongoing reading ledger."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

import fitz


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'data/accounting-master/navigation-repair-20261018'
SOURCE = ROOT / 'data/accounting-master/early-conversion-source-20261018'
PDF = ROOT / 'docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf'
EXPECTED = 'afbbdbe73d6ac25a9e59ea6f39e25b2e579ebd1e5fcad0ac9959e87cc6ab5d80'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return str(path.relative_to(ROOT))


def write(name, value):
    path = OUT / name
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    assert sha(PDF) == EXPECTED
    checks = json.loads((OUT / 'candidate-checks.json').read_text())
    financial = json.loads((OUT / 'financial-consequences.json').read_text())
    assert checks['source_bindings_passed'] and checks['references_resolved']
    assert checks['pdf_sha256'] == EXPECTED and checks['displayed_equations'] == 208
    assert not checks['build_warnings'] and not checks['text_bounds']
    assert len(financial['checks']) == financial['checks_passed'] == 37
    assert all(row['passed'] for row in financial['checks'])
    index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
    with fitz.open(PDF) as document:
        links = [link for link in document[373].get_links()
                 if link.get('page') == 184
                 and link.get('nameddest') == 'subsection.10.2.6']
        assert len(links) == 1
        words = [word for word in document[373].get_text('words')
                 if word[4] == '10.2.6' and fitz.Rect(word[:4]).intersects(links[0]['from'])]
        assert len(words) == 1, words
        label = words[0][4]
        assert 'Actual conversion, expiry and incomplete terms' in document[184].get_text()
        link_check = dict(source_physical_page=374, visible_label=label,
                          destination_physical_page=185,
                          destination_name=links[0]['nameddest'], passed=True)
    write('hyperlink-check.json', dict(pdf_sha256=EXPECTED, checks=[link_check]))
    review = dict(
        date='2026-10-18', candidate_version='3.44', pdf=rel(PDF), pdf_sha256=EXPECTED,
        status='local_author_inspection_complete_ordered_regression_pending',
        physical_pages_actually_viewed=[1, 182, 185, 186, 374, 386],
        viewing_mode='Separate normal-resolution local inspections; not a continuous chapter or document read.',
        renders=[dict(page=n, path=rel(OUT / 'local-review-current' / f'page-{n:03}.png'),
                      sha256=sha(OUT / 'local-review-current' / f'page-{n:03}.png'))
                 for n in (1, 182, 185, 186, 374, 386)],
        comprehension=dict(
            verdict='local_author_answers_available',
            evidence='Pages 182/185/186 identify the original any-time holder right, carrying-value transfer and separate actual/potential share windows. Appendix 374 distinguishes the unchanged maturity-only company exchange.',
            limits='Chapter continuity, whole-document comprehension, independent implementability and human voice remain unassessed on this build.'),
        mathematical_integrity=dict(
            verdict='correct_within_supplied_exact_arithmetic',
            evidence='37 rational checks preserve the 9,200 transfer, original 800 equity, two 400 interest periods in the redemption world, only one in early conversion, and nonoverlapping 92-day share windows.',
            limits='No valuation engine, tax determination, actual-company computation or new EPS selection theorem is established.'),
        source_fidelity=dict(
            verdict='bounded_interpretation_explicit',
            evidence='Section 10.2.6 attributes early exercise treatment to BDO 4.5 and distinguishes IAS32.AG32 maturity wording, IFRIC19 exclusion, IFRS9 alternative and the IAS8 hierarchy. Bibliography page 386 identifies the inspected material and excluded inconsistent table.',
            limits='Practice interpretation is not express early-exercise wording in IAS32 or current-law admission. Actual terms, equity classification, tax facts and applicable authority remain necessary.'),
        rendered_interface=dict(
            verdict='no_local_clipping_observed_pointer_corrected',
            evidence='Title 3.44/date legible; current six local pages read at normal resolution. The visible 10.2.6 reference and actual hyperlink from appendix 374 reach physical 185.',
            limits='Text-bound/build diagnostics and local inspection do not establish an entire-document read.'),
        cold_reader_answers=[
            dict(question='Which right is exercised?', answer='The equity-classified holder option recognized at issue, exercisable any time before 1 January 2026, unchanged and settled only in 600 shares; no inducement or extra derivative feature.'),
            dict(question='What transfers to equity?', answer='After the October coupon, the liability carrying amount 9,200 transfers; original equity 800 remains equity.'),
            dict(question='Why is remaining interest not accelerated?', answer='That is the selected BDO 4.5 interpretation for original permitted exercise; the remaining 400 is not recognized at conversion.'),
            dict(question='What is source wording and what is interpretation?', answer='AG32 expressly addresses maturity. BDO describes treating permitted early exercise as maturity; IFRIC19 exclusion alone supplies no measurement rule.'),
            dict(question='Why do shares not overlap?', answer='The later 92 days enter basic EPS as actual shares; diluted EPS adds only the preceding 92 days of potential shares and the preconversion net expense 300.'),
            dict(question='What still prevents actual-company admission?', answer='Complete actual terms, classification, applicable authority, consistent policy and tax facts; independent technical/domain and human acceptance remain pending.')],
        ordered_regression='pending; initialized separately with no inferred reading from render identity',
        prior_local_record='attempt-01/chapter10-review.json retracts its former ordered-segment claim; retained observations are local only',
        independent_reader='pending', human_acceptance='pending', proposal_status='not_ready')
    write('rendered-review.json', review)
    result = '''# Version 3.44: bounded original-term early-conversion integration

18 October 2026. P15/P17/P18/P19; R03/R04/R07/R08;
MC17/19/24/26/29/30/32–35. **Not ready.**

The rebuilt 396-page candidate explicitly selects the BDO June 2026 section
4.5 interpretation for an unchanged original equity-classified holder option.
The October conversion transfers the liability carrying amount 9,200 to equity;
the original 800 stays in equity and remaining interest 400 is not accelerated.
Its synthetic tax effects remain supplied facts. The separate company exchange
continues to test conversion at maturity. No general early-conversion method,
actual-company admission, tax authority or independent acceptance follows.

PDF: `docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf`.
SHA256: `afbbdbe73d6ac25a9e59ea6f39e25b2e579ebd1e5fcad0ac9959e87cc6ab5d80`.
Comparator: protected Version 3.43, 395 pages, SHA256
`fbb29aa3c6b75d66c723c48af440a8df609ba81bcce723bec6b5d024eacbe800`.

## Evidence and limits

The exact command and environment are in `build-manifest.json`: CPU-only
LuaLaTeX; no installation or empirical execution. The successful second build
has a supervised elapsed upper bound of 51.742 seconds, including polling;
exact process wall time was not captured. The first build and its sources,
checks and review record are preserved under `attempt-01/`.

All 143 source bindings pass. Four source files change, preserving 208 displays,
716 earlier citation occurrences and all prior labels; two citations and one
dedicated subsection label are added. References resolve; build warnings and
text-bound diagnostics are empty. Page comparison records reflow after the new
material; render identity is never evidence of reading. All 37 independent
exact financial checks pass, including the unchanged fully diluted fraction.
These checks establish conditional arithmetic, not a standards implementation.

BDO's retained technical discussion and the historical primary standards are
compared in `../early-conversion-source-20261018/source-reading.md`.
IAS32.AG32 expressly concerns maturity; BDO supplies an interpretation of
permitted early exercise. IFRIC19's original-terms exclusion is distinguished
from an affirmative measurement rule. The strongest general IFRS9 alternative
and IAS8 hierarchy remain explicit. The unrelated inconsistent table on BDO
page 16 is excluded from support.

Local current-build reading covers physical 1/182/185/186/374/386. Separate
comprehension, mathematical, source and rendered-interface judgments are in
`rendered-review.json`. The appendix's visible 10.2.6 reference and PDF hyperlink
now reach the actual-conversion subsection on physical 185. This repairs the
first build's pointer to the denominator subsection 10.2.1.

The first-build chapter review's former continuity claim was retracted: its
observations are local inspections, not ordered reading. The current inventory
contains 659 nodes and 396 pages with judgments initially pending. Neither the
protected complete 3.42 review nor inherited 3.43 observations count as a new
3.44 read. Full affected-chapter, ordered whole-document, equation, chapter,
cumulative-prefix and final regression remain separate pending obligations.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain bounded policy as a provisional documentary repair | Local reader questions answered; all 37 financial checks pass | No source-binding, preservation, reference, clipping or hyperlink failure in checked scope | Actual terms, classification, policy authority and tax facts | Complete chapter 10/appendix A and full successor regression; continue independent source/protocol/dependency work | Universal treatment, runtime validity or whole-company completeness |
| Keep proposal not_ready | Full regression and original substantive obligations remain open | No global continuation veto; missing evidence vetoes only its dependent claim | Independent technical/domain review and human comprehension | Preserve all 53 obligations, six interactions and 46 operations in the exact-candidate assessment | Independent or human acceptance |

This is deterministic documentary work; no stochastic ranking is proposed.
The strongest alternative explanation is that the practice analogy does not
apply to a real instrument's terms. An incompatible classification, changed
right or controlling contrary authority would overturn that application.
The weakest evidence is actual-company applicability, which remains unadmitted.
This narrows a source residual; it does not reject or complete the wider research
direction. Pending review is no reason to stop feasible internal preparation.
'''
    result_path = OUT / 'result.md'
    assert not result_path.exists()
    result_path.write_text(result)
    evidence_paths = [OUT / 'result.md', OUT / 'rendered-review.json', OUT / 'hyperlink-check.json',
                      OUT / 'candidate-checks.json', OUT / 'financial-consequences.json',
                      OUT / 'build-manifest.json', SOURCE / 'source-reading.md',
                      SOURCE / 'acquisition-manifest.json']
    evidence = [dict(path=rel(p), sha256=sha(p)) for p in evidence_paths]
    prior = json.loads((PRIOR / 'assessment-successor.json').read_text())
    new = deepcopy(prior)
    delta = ('3.44 integrates a bounded original-term early-conversion interpretation, '
             'with explicit equity-right/unchanged-terms premises, a 9,200 carrying-value transfer, '
             'no acceleration of remaining 400 interest and conditional supplied tax effects. '
             '37 exact arithmetic checks and source/document preservation pass. '
             'The maturity-only company exchange is retained; its appendix pointer now reaches 10.2.6. '
             'Six current local pages were inspected; ordered successor regression and '
             'independent technical/domain/human acceptance remain pending. No whole-row closure.')
    new.update(date='2026-10-18', candidate_version='3.44', candidate_pdf=rel(PDF),
               candidate_pdf_sha256=EXPECTED, predecessor=rel(PRIOR / 'assessment-successor.json'),
               predecessor_sha256=sha(PRIOR / 'assessment-successor.json'),
               assessment_scope=delta,
               author_review_status='local_inspection_complete_full_regression_pending')
    affected = {'MC17', 'MC19', 'MC24', 'MC26', 'MC29', 'MC30', 'MC32', 'MC33', 'MC34', 'MC35',
                'G7', 'G8', 'G10', 'G16', 'G17'}
    for row in new['rows']:
        row.update(previous_candidate_version='3.43', candidate_version='3.44',
                   candidate_pdf=rel(PDF), candidate_pdf_sha256=EXPECTED,
                   delta_assessment=delta if row['id'] in affected else
                   'Inherited obligation/method judgment; not freshly reviewed by this bounded integration.')
        if row['id'] in affected:
            row.setdefault('evidence_updates', []).extend(deepcopy(evidence))
    for row in new['interactions']:
        row['current_candidate_review'] = (
            'Inherited interaction judgment. This bounded early-conversion source/arithmetic '
            'integration does not establish a new general cross-domain join or acceptance.')
    immutable = ('id', 'label', 'original_obligation', 'acceptance', 'recorded_status', 'historical_status')
    preservation = [dict(name=a['id'], passed=all(a[k] == b[k] for k in immutable))
                    for a, b in zip(prior['rows'], new['rows'])]
    preservation += [dict(name='all53', passed=len(new['rows']) == len(prior['rows']) == 53),
                     dict(name='six-interactions', passed=len(new['interactions']) == 6 and
                          all(all(a[k] == b[k] for k in ('id', 'question', 'status'))
                              for a, b in zip(prior['interactions'], new['interactions'])))]
    assert all(row['passed'] for row in preservation)
    write('assessment-successor.json', new)
    write('assessment-checks.json', dict(checks=len(preservation), failures=0, detail=preservation))
    old_ops = json.loads((PRIOR / 'operation-successor.json').read_text())
    ops = deepcopy(old_ops)
    ops.update(candidate_version='3.44', candidate_pdf=rel(PDF), candidate_pdf_sha256=EXPECTED,
               recorded_utc=datetime.now(timezone.utc).isoformat(),
               predecessor=rel(PRIOR / 'operation-successor.json'),
               predecessor_sha256=sha(PRIOR / 'operation-successor.json'), current_increment=delta)
    for row in ops['rows']:
        if row['id'] in ('P17-05.03', 'P17-05.04'):
            row['current_increment'] = delta
            row['evidence'].extend(deepcopy(evidence))
        assert row['full_requirement_closed'] is False
    op_checks = [dict(name=a['id'], passed=all(a[k] == b[k] for k in ('id', 'operation', 'original_row'))
                     and b['full_requirement_closed'] is False)
                 for a, b in zip(old_ops['rows'], ops['rows'])]
    assert len(op_checks) == len(ops['rows']) == 46 and all(c['passed'] for c in op_checks)
    write('operation-successor.json', ops)
    write('operation-checks.json', dict(checks=46, failures=0, detail=op_checks))
    assert subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT) == index
    write('integration-bindings.json', dict(
        created_utc=datetime.now(timezone.utc).isoformat(), pdf=rel(PDF), pdf_sha256=EXPECTED,
        evidence=evidence,
        assessment=dict(path=rel(OUT / 'assessment-successor.json'), sha256=sha(OUT / 'assessment-successor.json')),
        operations=dict(path=rel(OUT / 'operation-successor.json'), sha256=sha(OUT / 'operation-successor.json')),
        index_sha256=hashlib.sha256(index).hexdigest(),
        scope='Immutable local integration/assessment evidence only; mutable controls and ongoing regression excluded.',
        status='not_ready'))
    print(json.dumps(dict(version='3.44', financial_checks=37, assessment_checks=55,
                          operations_preserved=46, hyperlink='passed', status='not_ready')))


if __name__ == '__main__':
    main()
