"""Create this integration driver from the checked prior bounded workflow."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
prior=HERE.parent/'insurance-identity-integration-20261026/integrate.py'
text=prior.read_text()
start=text.index('def expected(name, text):')
end=text.index('def prepare():',start)
replacement='''def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        assert text.count('Version 5.3 (proposal candidate)') == 1
        return text.replace('Version 5.3 (proposal candidate)', 'Version 5.4 (proposal candidate)')
    if name == 'sections/profile-interfaces.tex':
        marker = BS + 'subsection{Checked examples and remaining scope}'
        assert text.count(marker) == 1
        return text.replace(marker, BS + 'input{sections/adopted-profile-effects}'+chr(10)*2+marker)
    return text

'''
text=text[:start]+replacement+text[end:]
for before,after in [
 ('Version 5.3 integration of insurer identity-policy adoption','Version 5.4 integration of adopted-profile common readers'),
 ("SOURCE = ROOT / 'docs/design/proposal/manuscript-invariant-source-20261026'","SOURCE = ROOT / 'docs/design/proposal/manuscript-insurance-identity-20261026'"),
 ("TARGET = ROOT / 'docs/design/proposal/manuscript-insurance-identity-20261026'","TARGET = ROOT / 'docs/design/proposal/manuscript-adopted-profiles-20261026'"),
 ('88ecbf06b093035690680dd4079a7f28ad57ccb0120efaf4670ca1e815f48ca9','1f83ca1205813a28cc3cbe4576653531ecd6c4b8d80c6ef70e88684110cf5e63'),
 ('assert len(sources) == 213','assert len(sources) == 214'),
 ("unit = HERE.parent / 'insurance-identity-adoption-20261026'","unit = HERE.parent / 'adopted-profile-effects-20261026'"),
 ("checks['saved_exchanges_revalidated'] == 686","checks['saved_effects_recomputed'] == 959"),
 ("['result.md','checks.json','run-manifest.json','native.py','successor.py','verify.py','adapted_protocol.py','protocol-delta.json','semantic-contract.md','portable-successor.json']","['result.md','checks.json','run-manifest.json','providers.py','verify.py','schema_descriptor.py','composition_assess.py','reader-delta.json','effects.jsonl','compositions.json']"),
 ('sections/insurance-identity-adoption.tex','sections/adopted-profile-effects.tex'),
 ("HERE / 'insurance-identity.tex'","HERE / 'adopted-profiles.tex'"),
 ("'candidate':'5.3'","'candidate':'5.4'"),
 ("assert 'Version 5.3' in doc[0].get_text()","assert 'Version 5.4' in doc[0].get_text()"),
 ("if 'An acquisition payment of 8' in text","if 'A corrected request index is useful only' in text"),
 ("if 'exact two-expression protocol' in text","if 'These comparisons preserve checked protocol meanings' in text"),
 ("version='5.3'","version='5.4'")]:
    assert before in text,before
    text=text.replace(before,after)
assert not (HERE/'integrate.py').exists()
(HERE/'integrate.py').write_text(text)
print('Prepared bounded integration driver')
