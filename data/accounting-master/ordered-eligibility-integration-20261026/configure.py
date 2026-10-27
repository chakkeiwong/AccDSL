from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE.parent/'method-specialization-integration-20261026/integrate.py').read_text()
start=text.index('def expected(name, text):');end=text.index('def prepare():',start)
replacement='''def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        old='Version 5.6 (proposal candidate)'
        assert text.count(old)==1
        return text.replace(old,'Version 5.7 (proposal candidate)')
    if name == 'sections/authored-event-contract.tex':
        marker=BS+'input{sections/common-program-authoring}'
        assert text.count(marker)==1
        return text.replace(marker,BS+'input{sections/ordered-event-eligibility}'+chr(10)*2+marker)
    if name == 'sections/method-specialization.tex':
        first='Both constructors work with the native specializer disabled in their checks.'
        last='boundaries.'
        start=text.index(first);end=text.index(last,start)+len(last)
        revised='Both constructors work with the native specializer disabled in their checks.\\nTheir construction interface leaves full-intent eligibility separate; the next\\nsection supplies an explicit ordered alternative for the retained contracts.\\nFixed chart context, role mapping and unit-cost choices remain declared scope.\\nThe earlier complete program composition and invariant source continue to\\nprovide their own boundaries.'
        return text[:start]+revised+text[end:]
    return text

'''
text=text[:start]+replacement+text[end:]
pairs=[
('Version 5.6 integration of typed method specialization','Version 5.7 integration of ordered full-intent eligibility'),
("SOURCE = ROOT / 'docs/design/proposal/manuscript-observation-quotient-20261026'","SOURCE = ROOT / 'docs/design/proposal/manuscript-method-specialization-20261026'"),
("TARGET = ROOT / 'docs/design/proposal/manuscript-method-specialization-20261026'","TARGET = ROOT / 'docs/design/proposal/manuscript-ordered-eligibility-20261026'"),
('7ace3886763d77dc068340a38fc7e8f1167617b2206516d7fcfe1101b8e842ce','b8b487bde8e661cb469b3cf7f71a1b2bc5ffc8f9e8644df713ce9a1eb3f46819'),
('assert len(sources) == 216','assert len(sources) == 217'),
("unit = HERE.parent / 'ordered-assessment-expansion-20261026'","unit = HERE.parent / 'ordered-event-eligibility-20261026'"),
("checks['full_request_transition_cases'] == 20","checks['complete_events'] == 38 and checks['all_refusal_cases'] == 34 and checks['controls'] == 70"),
("['result.md','checks.json','run-manifest.json','expander.py','verify.py','design.md','cases.json','controls.json','inclusive-variant.json','source-lock.json']","['result.md','checks.json','run-manifest.json','gate.py','verify.py','design.md','cases.json','controls.json','refusals.json','source-lock.json','repair-note.md']"),
("(TARGET / 'sections/method-specialization.tex').write_bytes((HERE / 'specialization.tex').read_bytes())","(TARGET / 'sections/ordered-event-eligibility.tex').write_bytes((HERE / 'eligibility.tex').read_bytes())"),
("added_source='sections/method-specialization.tex', new_section_sha256=sha(HERE / 'specialization.tex')","added_source='sections/ordered-event-eligibility.tex', new_section_sha256=sha(HERE / 'eligibility.tex')"),
("'candidate':'5.6'","'candidate':'5.7'"),
("assert 'Version 5.6' in doc[0].get_text()","assert 'Version 5.7' in doc[0].get_text()"),
("if 'A sale method must insert the claim' in text","if 'A customer can be unknown before a collection' in text"),
("if 'portable authoring of every event-contract condition' in text","if 'independent implementation acceptance remain open' in text"),
("version='5.6'","version='5.7'")]
for old,new in pairs:
    assert old in text,old;text=text.replace(old,new)
start=text.index("    previous=HERE.parent/'parameterized-method-construction-20261026'")
end=text.index('    for name in sources:',start)
text=text[:start]+text[end:]
assert not (HERE/'integrate.py').exists();(HERE/'integrate.py').write_text(text)
print('Configured preserved Version 5.7 main-only integration')
