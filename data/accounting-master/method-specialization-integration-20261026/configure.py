from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE.parent/'adopted-profile-integration-20261026/integrate.py').read_text()
start=text.index('def expected(name, text):');end=text.index('def prepare():',start)
replacement='''def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        old='Version 5.5 (proposal candidate)'
        assert text.count(old)==1
        return text.replace(old,'Version 5.6 (proposal candidate)')
    if name == 'sections/authored-event-contract.tex':
        marker=BS+'input{sections/common-program-authoring}'
        assert text.count(marker)==1
        return text.replace(marker,BS+'input{sections/method-specialization}'+chr(10)*2+marker)
    return text

'''
text=text[:start]+replacement+text[end:]
pairs=[
 ('Version 5.4 integration of adopted-profile common readers','Version 5.6 integration of typed method specialization'),
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-insurance-identity-20261026'","SOURCE = ROOT / 'docs/design/proposal/manuscript-observation-quotient-20261026'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-adopted-profiles-20261026'","TARGET = ROOT / 'docs/design/proposal/manuscript-method-specialization-20261026'"),
 ('1f83ca1205813a28cc3cbe4576653531ecd6c4b8d80c6ef70e88684110cf5e63','7ace3886763d77dc068340a38fc7e8f1167617b2206516d7fcfe1101b8e842ce'),
 ('assert len(sources) == 214','assert len(sources) == 216'),
 ("unit = HERE.parent / 'adopted-profile-effects-20261026'","unit = HERE.parent / 'ordered-assessment-expansion-20261026'"),
 ("checks['saved_effects_recomputed'] == 959","checks['full_request_transition_cases'] == 20"),
 ("['result.md','checks.json','run-manifest.json','providers.py','verify.py','schema_descriptor.py','composition_assess.py','reader-delta.json','effects.jsonl','compositions.json']","['result.md','checks.json','run-manifest.json','expander.py','verify.py','design.md','cases.json','controls.json','inclusive-variant.json','source-lock.json']"),
 ('sections/adopted-profile-effects.tex','sections/method-specialization.tex'),
 ("HERE / 'adopted-profiles.tex'","HERE / 'specialization.tex'"),
 ("'candidate':'5.4'","'candidate':'5.6'"),
 ("assert 'Version 5.4' in doc[0].get_text()","assert 'Version 5.6' in doc[0].get_text()"),
 ("if 'A corrected request index is useful only' in text","if 'A sale method must insert the claim' in text"),
 ("if 'These comparisons preserve checked protocol meanings' in text","if 'portable authoring of every event-contract condition' in text"),
 ("version='5.4'","version='5.6'")
]
for a,b in pairs:
    assert a in text,a;text=text.replace(a,b)
marker="    for name in sources:"
extra='''    previous=HERE.parent/'parameterized-method-construction-20261026'
    for name in ['result.md','checks.json','run-manifest.json','constructor.py','verify.py','design.md','cases.json','controls.json','algorithm-variant.json']:
        evidence[str((previous/name).relative_to(ROOT))]=sha(previous/name)
'''
assert marker in text;text=text.replace(marker,extra+marker,1)
assert not (HERE/'integrate.py').exists();(HERE/'integrate.py').write_text(text)
print('Configured preserved Version 5.6 main-only integration')
