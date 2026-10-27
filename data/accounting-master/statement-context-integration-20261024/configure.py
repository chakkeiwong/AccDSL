"""Reuse bounded build and content-preservation checks with explicit new scope."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'company-source-integration-20261024'
for name in ['build.py','verify.py']:
    assert not (HERE/name).exists()
    text=(OLD/name).read_text().replace('manuscript-company-source-20261024','manuscript-statement-context-20261024')
    text=text.replace('accdsl-company-source-20261024','accdsl-statement-context-20261024').replace('3.57','3.58')
    if name=='verify.py':
        old="allowed={'accounting-product-proposal.tex','chapters/06-language.tex','sections/company-module-language.tex','sections/company-return-reference.tex'}"
        new="allowed={'accounting-product-proposal.tex','chapters/06-language.tex','sections/company-source-state.tex'}"
        assert old in text;text=text.replace(old,new)
        text=text.replace("added!={'sections/company-source-state.tex'}","added!={'sections/statement-context-relations.tex'}")
        a=text.index('    phrases=');b=text.index('\n    locations=',a)
        text=text[:a]+"    phrases=['Reading the statements together without inventing history','A reporting period can contain several balance dates','A subtotal needs an independent target to be a check','Local compatibility is not a company history']"+text[b:]
    (HERE/name).write_text(text)
print('configured protected successor build')
