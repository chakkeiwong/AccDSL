from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE.parent/'opening-binding-integration-20261026/integrate.py').read_text()
start=text.index('def expected(name, text):');end=text.index('def prepare():',start)
replacement='''def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        old='Version 5.9 (proposal candidate)'
        assert text.count(old)==1
        return text.replace(old,'Version 5.10 (proposal candidate)')
    if name == 'sections/common-program-authoring.tex':
        marker=BS+'input{sections/invariant-source-authoring}'
        assert text.count(marker)==1
        return text.replace(marker,marker+chr(10)*2+BS+'input{sections/selected-company-source}')
    if name == 'sections/declared-opening-binding.tex':
        old='Earlier company-source\\nfrontends retain their older target until a successor exposes these algorithms\\nin source.'
        new='Earlier company-source\\nfrontends retain their older target. Section~'+BS+'ref{sec:selected-company-source}\\nintroduces the successor that expresses these algorithms directly.'
        assert text.count(old)==1
        return text.replace(old,new)
    return text

'''
text=text[:start]+replacement+text[end:]
start=text.index('    unit = HERE.parent');end=text.index('    for name in sources:',start)
evidence='''    units={
        'ordered-eligibility-source-20261026':(72,35),
        'opening-admission-source-20261026':(82,20),
        'method-recipe-source-20261026':(38,20),
        'selected-company-source-20261026':(30,15)}
    evidence={}
    for unit_name,(count,controls) in units.items():
        unit=HERE.parent/unit_name
        checks=json.loads((unit/'checks.json').read_text())
        assert checks['passed'] and checks['controls']==controls
        if unit_name.startswith('selected-company'):
            assert checks['complete_programs']==4 and checks['complete_commands']==44 and checks['adverse_programs']==26
        for path in unit.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and 'control-before' not in path.parts:
                evidence[str(path.relative_to(ROOT))]=sha(path)
'''
text=text[:start]+evidence+text[end:]
pairs=[
('Preserved Version 5.9 integration of declared opening and selected execution','Preserved Version 5.10 integration of directly authored selected programs'),
("SOURCE = ROOT / 'docs/design/proposal/manuscript-declarative-program-20261026'","SOURCE = ROOT / 'docs/design/proposal/manuscript-opening-binding-20261026'"),
("TARGET = ROOT / 'docs/design/proposal/manuscript-opening-binding-20261026'","TARGET = ROOT / 'docs/design/proposal/manuscript-selected-source-20261026'"),
('c8ed77cdbcd92b9d0081b2708840b73d2c404cc01efbca446b1fd433000db017','b0fd28fa2db053cbc841456d54ed0ad66e9fce8d036599ede12a06904916a6f8'),
('assert len(sources) == 219','assert len(sources) == 220'),
("(TARGET / 'sections/declared-opening-binding.tex').write_bytes((HERE / 'opening.tex').read_bytes())","(TARGET / 'sections/selected-company-source.tex').write_bytes((HERE / 'source.tex').read_bytes())"),
("added_source='sections/declared-opening-binding.tex', new_section_sha256=sha(HERE / 'opening.tex')","added_source='sections/selected-company-source.tex', new_section_sha256=sha(HERE / 'source.tex')"),
("'candidate':'5.9'","'candidate':'5.10'"),
("assert 'Version 5.9' in doc[0].get_text()","assert 'Version 5.10' in doc[0].get_text()"),
("if 'A balanced, typed opening book can still violate' in text","if 'A generated method can calculate the right journal' in text"),
("if 'The opening comparisons and bound programs are retained' in text","if 'The complete source examples and result pairs are' in text"),
("version='5.9'","version='5.10'")]
for old,new in pairs:
    assert old in text,old
    text=text.replace(old,new)
assert not (HERE/'integrate.py').exists()
(HERE/'integrate.py').write_text(text)
print('Configured preserved Version 5.10 source integration')
