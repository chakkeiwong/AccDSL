from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE.parent/'declarative-program-integration-20261026/integrate.py').read_text()
start=text.index('def expected(name, text):');end=text.index('def prepare():',start)
replacement='''def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        old='Version 5.8 (proposal candidate)'
        assert text.count(old)==1
        return text.replace(old,'Version 5.9 (proposal candidate)')
    if name == 'sections/authored-event-contract.tex':
        marker=BS+'input{sections/common-program-authoring}'
        assert text.count(marker)==1
        return text.replace(marker,BS+'input{sections/declared-opening-binding}'+chr(10)*2+marker)
    if name == 'sections/declarative-event-program.tex':
        first='Opening admission is still a separate native prerequisite in this comparison.'
        last='financial language, accounting validity or independent implementation acceptance.'
        start=text.index(first);end=text.index(last,start)+len(last)
        revised='Opening admission remains a separate native prerequisite for this composer\\ncomparison. The original validation checks the retained opening/program before\\nnative functions are disabled. The next extension declares those opening\\nconditions and binds them to the exact program selected for execution. The\\nearlier company-source frontend retains its own native-contract target.\\nGeneral opening populations, a complete financial language, accounting validity\\nand independent implementation acceptance remain separate questions.'
        return text[:start]+revised+text[end:]
    return text

'''
text=text[:start]+replacement+text[end:]
pairs=[
('Version 5.8 integration of declarative event program execution','Version 5.9 integration of declared opening and selected execution'),
("SOURCE = ROOT / 'docs/design/proposal/manuscript-ordered-eligibility-20261026'","SOURCE = ROOT / 'docs/design/proposal/manuscript-declarative-program-20261026'"),
("TARGET = ROOT / 'docs/design/proposal/manuscript-declarative-program-20261026'","TARGET = ROOT / 'docs/design/proposal/manuscript-opening-binding-20261026'"),
('735c69c9a9907d17d6986f50eb1bdb13bde19998179bded8b7f14fd12e21f084','c8ed77cdbcd92b9d0081b2708840b73d2c404cc01efbca446b1fd433000db017'),
('assert len(sources) == 218','assert len(sources) == 219'),
("unit = HERE.parent / 'declarative-event-program-20261026'","unit = HERE.parent / 'admitted-program-binding-20261026'"),
("checks['complete_commands'] == 22 and checks['new_complete_commands'] == 22 and checks['adverse_programs'] == 26 and checks['controls'] == 11","checks['complete_commands'] == 44 and checks['complete_execution_comparisons'] == 30 and checks['controls'] == 22"),
("['result.md','checks.json','run-manifest.json','composer.py','verify.py','design.md','comparisons.json','new-comparisons.json','controls.json','adverse.json','source-lock.json','repair-note.md']","['result.md','checks.json','run-manifest.json','binding.py','verify.py','design.md','cases.json','controls.json','source-lock.json']"),
("(TARGET / 'sections/declarative-event-program.tex').write_bytes((HERE / 'composition.tex').read_bytes())","(TARGET / 'sections/declared-opening-binding.tex').write_bytes((HERE / 'opening.tex').read_bytes())"),
("added_source='sections/declarative-event-program.tex', new_section_sha256=sha(HERE / 'composition.tex')","added_source='sections/declared-opening-binding.tex', new_section_sha256=sha(HERE / 'opening.tex')"),
("'candidate':'5.8'","'candidate':'5.9'"),
("assert 'Version 5.8' in doc[0].get_text()","assert 'Version 5.9' in doc[0].get_text()"),
("if 'A collection that works in isolation can still fail' in text","if 'A balanced, typed opening book can still violate' in text"),
("if 'The four complete programs, adverse cases and full comparisons' in text","if 'The opening comparisons and bound programs are retained' in text"),
("version='5.8'","version='5.9'")]
for old,new in pairs:
    assert old in text,old;text=text.replace(old,new)
marker='    for name in sources:'
extra='''    previous=HERE.parent/'declared-opening-admission-20261026'
    for name in ['result.md','checks.json','run-manifest.json','admission.py','verify.py','design.md','cases.json','controls.json','repair-note.md']:
        evidence[str((previous/name).relative_to(ROOT))]=sha(previous/name)
'''
assert marker in text;text=text.replace(marker,extra+marker,1)
assert not (HERE/'integrate.py').exists();(HERE/'integrate.py').write_text(text)
print('Configured preserved Version 5.9 main-only integration')
