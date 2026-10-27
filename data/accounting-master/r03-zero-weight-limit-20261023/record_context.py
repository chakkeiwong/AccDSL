"""One-time source-boundary bindings for a local mathematical deduction."""
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def main():
    output = U / 'source-boundary.json'
    assert not output.exists()
    method = R / 'docs/design/proposal/methods/impairment-floors-20261014.md'
    primary = R / 'data/accounting-master/zero-weight-cgu-source-20261018/sources/aasb136-dec2022.txt'
    original = R / 'data/accounting-master/zero-weight-cgu-source-20261018/sources/aasb136-dec2022.pdf'
    notes = [R / ('data/accounting-master/' + folder + '/source-reading.md') for folder in
             ('zero-weight-cgu-source-20261018', 'zero-weight-cgu-publisher-followup-20261018')]
    anchors = []
    for ident, p, first, last in [
        ('method-allocation', method, 'Allocate the remaining loss pro rata', 'If capacity is exhausted'),
        ('method-reversal', method, 'On a qualified reversal', '## Connected cost-model case'),
        ('primary-122-125', primary, '122        A reversal', '\nDisclosure'),
        ('prior-cap-set', notes[0], '## Local mathematical diagnosis', '## Access failures'),
        ('prior-limit-gap', notes[1], 'The strongest tempting inference', '## Source arithmetic')]:
        text = p.read_text()
        lo = text.index(first)
        hi = text.index(last, lo)
        anchors.append({'id': ident, 'binding': bind(p), 'character_span': [lo, hi],
                        'lines_by_newline': [text[:lo].count('\n') + 1, text[:hi].count('\n') + 1],
                        'quote': text[lo:hi]})
    record = {
        'question': 'Whether the existing positive-weight rule has a canonical all-zero limit',
        'support_class': 'PROJECT_DERIVATION', 'derivation': bind(U / 'derivation.md'),
        'baseline_method': bind(method), 'historical_primary_pdf': bind(original),
        'reused_notes': [bind(p) for p in notes], 'anchors': anchors,
        'previous_source_manifests': [bind(p.parent / 'source-manifest.json') for p in notes],
        'primary_source_scope': 'AASB136 compilation3, Dec2022, registered Feb2023; historical technical support only. Paragraphs122–125 reread; prior technical/example scope preserved.',
        'new_acquisition': False, 'new_literature_survey': False,
        'claims': [
            {'id': 'ZL01', 'claim': 'Existing proposal uses carrying weights and returns allocation_basis_unresolved at zero', 'support': ['method-allocation', 'method-reversal'], 'class': 'local proposed baseline'},
            {'id': 'ZL02', 'claim': 'Historical standard specifies carrying pro rata and asset ceilings; the retained examples do not select all-zero weights', 'support': ['primary-122-125'], 'class': 'bounded historical source statement; prior example reading reused'},
            {'id': 'ZL03', 'claim': 'Positive-weight final balances satisfy min(C_i,lambda b_i)', 'support': ['derivation.md equation (1)'], 'class': 'PROJECT_DERIVATION'},
            {'id': 'ZL04', 'claim': 'All attainable zero-weight limits equal the cap-and-total feasible set under fixed C,T', 'support': ['derivation.md equations (2)–(3)'], 'class': 'PROJECT_DERIVATION'},
            {'id': 'ZL05', 'claim': 'A canonical all-zero accounting allocation is not established', 'support': ['method-reversal', 'prior-cap-set', 'prior-limit-gap'], 'class': 'SOURCE_GAP_BLOCKER; mathematical result supplies no authority'}],
        'omissions': ['Current applicable accounting authority and actual asset facts remain unadmitted',
                      'Other source routes were not queried or retried',
                      'Changing ceilings, mixed-zero inputs and quantized rounding are outside the theorem',
                      'No independent or human acceptance'],
        'citation_venue_metadata': 'N/A local deduction and retained accounting standards; no new literature ranking or coverage'}
    with output.open('x') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(json.dumps({'source_anchors': len(anchors), 'scoped_claims': len(record['claims']), 'new_acquisition': False}))


if __name__ == '__main__':
    main()
