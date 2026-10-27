from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE.parent/'complete-claims-integration-20261026/integrate.py').read_text()
start=text.index('def expected(name, text):');end=text.index('def prepare():',start)
replacement=r'''def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        old='Version 5.11 (proposal candidate)'
        assert text.count(old)==1
        return text.replace(old,'Version 5.12 (proposal candidate)')
    if name == 'sections/selected-company-source.tex':
        old='semantic error that is known only at stage or document scope is reported at\nthat scope.'
        new=old+' The corrected nested-invariant reader described in\nSection~'+BS+'ref{sec:complete-claims-opening} also preserves quoted Unicode\nseparator characters as data rather than treating them as source line endings.'
        assert text.count(old)==1
        return text.replace(old,new)
    if name == 'sections/complete-claims-opening.tex':
        old='instead of asserting precision the inner parser does not provide.'
        new=old+'\n\nA source line ends at LF, with an optional preceding CR; a quoted string may\ncontain other Unicode separator characters. The inherited invariant parser\nincorrectly split such strings at U+0085, U+2028 and U+2029. The corrected\nreader and nested rule renderer keep these characters inside the string.\nNine comparisons place each character in an invariant residual, a nested\nrule residual and an input source reference. Each reproduces the earlier\nparser failure and preserves the corrected typed program and complete result.\nAll eight retained programs and 32 prior controls also remain exact. This\nrepair changes source handling only; the financial evaluators are unchanged.\nThe repaired invariant and complete company source implementations are under\n'+BS+'begingroup'+BS+'raggedright\n'+BS+'path{data/accounting-master/invariant-unicode-repair-20261026/}.\n'+BS+'par'+BS+'endgroup'
        assert text.count(old)==1
        return text.replace(old,new)
    return text

'''
text=text[:start]+replacement+text[end:]
start=text.index('    units = {');end=text.index('    evidence = {}',start)
text=text[:start]+"    units = {'invariant-unicode-repair-20261026': (41, 2782)}\n"+text[end:]
pairs=[
('Preserved Version 5.11 integration of complete supplied claim openings','Preserved Version 5.12 nested invariant source correction'),
("SOURCE = ROOT / 'docs/design/proposal/manuscript-selected-source-20261026'","SOURCE = ROOT / 'docs/design/proposal/manuscript-complete-claims-20261026'"),
("TARGET = ROOT / 'docs/design/proposal/manuscript-complete-claims-20261026'","TARGET = ROOT / 'docs/design/proposal/manuscript-invariant-unicode-20261026'"),
('75e96cd056682fa198c6015b41d32731fea077f40e3965593b3015c498a30f9a','05ff78c88e9b3c1a1ec3cc87bc5d0df6b718ca1fd8a206c0003b65928e4b2a90'),
('assert len(sources) == 221','assert len(sources) == 222'),
("    (TARGET / 'sections/complete-claims-opening.tex').write_bytes((HERE / 'source.tex').read_bytes())\n",''),
(", added_source='sections/complete-claims-opening.tex', new_section_sha256=sha(HERE / 'source.tex')",''),
("    assert sha(TARGET / preservation['added_source']) == preservation['new_section_sha256']\n",''),
("set(preservation['sources']) | {preservation['added_source']}","set(preservation['sources'])"),
("'candidate':'5.11'","'candidate':'5.12'"),
("assert 'Version 5.11' in doc[0].get_text()","assert 'Version 5.12' in doc[0].get_text()"),
("if 'A new reporting period need not begin with an empty receivables register.' in text","if 'The corrected nested-invariant reader described in' in text"),
("    language = next(i+1 for i, text in enumerate(texts) if 'The current design has several checked, bounded language profiles.' in text)\n    pages = sorted({1, language, language+1, *range(start-1,end+2)})","    pages = sorted({1, *range(start-1,end+2)})"),
("version='5.11'","version='5.12'")]
for old,new in pairs:
    assert old in text,old
    text=text.replace(old,new)
assert not (HERE/'integrate.py').exists()
(HERE/'integrate.py').write_text(text)
print('Configured preserved Version 5.12 correction')
