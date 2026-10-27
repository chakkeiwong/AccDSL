from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE.parent/'ordered-eligibility-integration-20261026/integrate.py').read_text()
start=text.index('def expected(name, text):');end=text.index('def prepare():',start)
replacement='''def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        old='Version 5.7 (proposal candidate)'
        assert text.count(old)==1
        return text.replace(old,'Version 5.8 (proposal candidate)')
    if name == 'sections/authored-event-contract.tex':
        marker=BS+'input{sections/common-program-authoring}'
        assert text.count(marker)==1
        return text.replace(marker,BS+'input{sections/declarative-event-program}'+chr(10)*2+marker)
    if name == 'sections/ordered-event-eligibility.tex':
        first='These comparisons establish a finite declarative alternative for eligibility'
        last='independent implementation acceptance remain open.'
        start=text.index(first);end=text.index(last,start)+len(last)
        revised='These comparisons establish a finite declarative alternative for eligibility\\nand method construction. Complete-program composition adds a different question:\\ndo reports, carry and invariant failures preserve the same current state and\\nsuccessful prefix? The following extension checks that execution boundary\\nwhile retaining opening admission as a separate prerequisite. General company\\nrules and independent implementation acceptance remain open.'
        return text[:start]+revised+text[end:]
    return text

'''
text=text[:start]+replacement+text[end:]
pairs=[
('Version 5.7 integration of ordered full-intent eligibility','Version 5.8 integration of declarative event program execution'),
("SOURCE = ROOT / 'docs/design/proposal/manuscript-method-specialization-20261026'","SOURCE = ROOT / 'docs/design/proposal/manuscript-ordered-eligibility-20261026'"),
("TARGET = ROOT / 'docs/design/proposal/manuscript-ordered-eligibility-20261026'","TARGET = ROOT / 'docs/design/proposal/manuscript-declarative-program-20261026'"),
('b8b487bde8e661cb469b3cf7f71a1b2bc5ffc8f9e8644df713ce9a1eb3f46819','735c69c9a9907d17d6986f50eb1bdb13bde19998179bded8b7f14fd12e21f084'),
('assert len(sources) == 217','assert len(sources) == 218'),
("unit = HERE.parent / 'ordered-event-eligibility-20261026'","unit = HERE.parent / 'declarative-event-program-20261026'"),
("checks['complete_events'] == 38 and checks['all_refusal_cases'] == 34 and checks['controls'] == 70","checks['complete_commands'] == 22 and checks['new_complete_commands'] == 22 and checks['adverse_programs'] == 26 and checks['controls'] == 11"),
("['result.md','checks.json','run-manifest.json','gate.py','verify.py','design.md','cases.json','controls.json','refusals.json','source-lock.json','repair-note.md']","['result.md','checks.json','run-manifest.json','composer.py','verify.py','design.md','comparisons.json','new-comparisons.json','controls.json','adverse.json','source-lock.json','repair-note.md']"),
("(TARGET / 'sections/ordered-event-eligibility.tex').write_bytes((HERE / 'eligibility.tex').read_bytes())","(TARGET / 'sections/declarative-event-program.tex').write_bytes((HERE / 'composition.tex').read_bytes())"),
("added_source='sections/ordered-event-eligibility.tex', new_section_sha256=sha(HERE / 'eligibility.tex')","added_source='sections/declarative-event-program.tex', new_section_sha256=sha(HERE / 'composition.tex')"),
("'candidate':'5.7'","'candidate':'5.8'"),
("assert 'Version 5.7' in doc[0].get_text()","assert 'Version 5.8' in doc[0].get_text()"),
("if 'A customer can be unknown before a collection' in text","if 'A collection that works in isolation can still fail' in text"),
("if 'independent implementation acceptance remain open' in text","if 'The four complete programs, adverse cases and full comparisons' in text"),
("version='5.7'","version='5.8'")]
for old,new in pairs:
    assert old in text,old;text=text.replace(old,new)
assert not (HERE/'integrate.py').exists();(HERE/'integrate.py').write_text(text)
print('Configured preserved Version 5.8 main-only integration')
