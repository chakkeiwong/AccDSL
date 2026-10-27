"""Reuse prior bounded build checks with explicit successor scope."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'company-return-integration-20261024'
for name in ['build.py','verify.py']:
    assert not (HERE/name).exists()
    text=(OLD/name).read_text().replace('manuscript-company-returns-20261024','manuscript-company-source-20261024')
    text=text.replace('accdsl-company-returns-20261024','accdsl-company-source-20261024').replace('3.56','3.57')
    if name=='verify.py':
        old="allowed={'accounting-product-proposal.tex','chapters/06-language.tex','sections/company-module-language.tex'}"
        new="allowed={'accounting-product-proposal.tex','chapters/06-language.tex','sections/company-module-language.tex','sections/company-return-reference.tex'}"
        assert old in text;text=text.replace(old,new)
        text=text.replace("added!={'sections/company-return-reference.tex'}","added!={'sections/company-source-state.tex'}")
        a=text.index('    phrases=');b=text.index('\n    locations=',a)
        text=text[:a]+"    phrases=['A company program begins with the state it can justify','Selecting methods for a complete retained company','What the disclosed balance sheet leaves unresolved','Fiscal dates belong to the source','A rounding assumption constrains a measurement']"+text[b:]
    (HERE/name).write_text(text)
print('configured bounded source preservation and build checks')
