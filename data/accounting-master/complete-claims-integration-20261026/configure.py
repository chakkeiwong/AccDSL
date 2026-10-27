"""Configure a new integration; never rerun predecessor writers."""
from pathlib import Path
HERE = Path(__file__).resolve().parent
text = (HERE.parent / 'selected-source-integration-20261026/integrate.py').read_text()
start = text.index('def expected(name, text):')
end = text.index('def prepare():', start)
replacement = r'''def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        old = 'Version 5.10 (proposal candidate)'
        assert text.count(old) == 1
        return text.replace(old, 'Version 5.11 (proposal candidate)')
    if name == 'chapters/06-language.tex':
        old = 'the wider financial language or establish accounting applicability.'
        assert text.count(old) == 1
        new = old + '\nSection~' + BS + 'ref{sec:complete-claims-opening} extends the opening contract\n'
        new += 'to live carried claims under an explicit supplied-population declaration\n'
        new += 'and the independently selected full invariant. The source states that\n'
        new += 'premise without inferring completeness from a successful continuation.'
        return text.replace(old, new)
    if name == 'sections/common-program-authoring.tex':
        marker = BS + 'input{sections/selected-company-source}'
        assert text.count(marker) == 1
        return text.replace(marker, marker + '\n\n' + BS + 'input{sections/complete-claims-opening}')
    if name == 'sections/selected-company-source.tex':
        old = 'declared opening and execution path together.'
        assert text.count(old) == 1
        new = old + ' The opening template in\nthis profile still requires an empty claim map. Section~'
        new += BS + 'ref{sec:complete-claims-opening}\nextends that boundary for explicitly complete supplied carried claims.'
        return text.replace(old, new)
    return text

'''
text = text[:start] + replacement + text[end:]
start = text.index('    units={')
end = text.index('    for name in sources:', start)
evidence = '''    units = {
        'nonempty-opening-audit-20261026': (5, 76),
        'complete-claims-opening-20261026': (38, 326),
        'complete-claims-source-20261026': (32, 787)}
    evidence = {}
    for unit_name, (controls, assertions) in units.items():
        unit = HERE.parent / unit_name
        checks = json.loads((unit / 'checks.json').read_text())
        assert checks['passed'] and checks.get('controls', checks.get('invalid_state_controls')) == controls and checks['assertions'] == assertions
        for path in unit.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                evidence[str(path.relative_to(ROOT))] = sha(path)
'''
text = text[:start] + evidence + text[end:]
pairs = [
    ('Preserved Version 5.10 integration of directly authored selected programs', 'Preserved Version 5.11 integration of complete supplied claim openings'),
    ("SOURCE = ROOT / 'docs/design/proposal/manuscript-opening-binding-20261026'", "SOURCE = ROOT / 'docs/design/proposal/manuscript-selected-source-20261026'"),
    ("TARGET = ROOT / 'docs/design/proposal/manuscript-selected-source-20261026'", "TARGET = ROOT / 'docs/design/proposal/manuscript-complete-claims-20261026'"),
    ('b0fd28fa2db053cbc841456d54ed0ad66e9fce8d036599ede12a06904916a6f8', '75e96cd056682fa198c6015b41d32731fea077f40e3965593b3015c498a30f9a'),
    ('assert len(sources) == 220', 'assert len(sources) == 221'),
    ("(TARGET / 'sections/selected-company-source.tex').write_bytes", "(TARGET / 'sections/complete-claims-opening.tex').write_bytes"),
    ("added_source='sections/selected-company-source.tex'", "added_source='sections/complete-claims-opening.tex'"),
    ("'candidate':'5.10'", "'candidate':'5.11'"),
    ("assert 'Version 5.10' in doc[0].get_text()", "assert 'Version 5.11' in doc[0].get_text()"),
    ("if 'A generated method can calculate the right journal' in text", "if 'A new reporting period need not begin with an empty receivables register.' in text"),
    ("if 'The complete source examples and result pairs are' in text", "if 'The checked successor therefore admits these complete supplied carried books' in text"),
    ("pages = sorted({1, *range(start-1,end+2)})", "language = next(i+1 for i, text in enumerate(texts) if 'The current design has several checked, bounded language profiles.' in text)\n    pages = sorted({1, language, language+1, *range(start-1,end+2)})"),
    ("version='5.10'", "version='5.11'")]
for old, new in pairs:
    assert old in text, old
    text = text.replace(old, new)
assert not (HERE / 'integrate.py').exists()
(HERE / 'integrate.py').write_text(text)
print('Configured preserved Version 5.11 integration')
