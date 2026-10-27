"""Reuse bounded build/preservation utilities with explicit new scope."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'company-module-integration-20261023'
for name in ['build.py','verify.py']:
    assert not (HERE/name).exists()
    text=(OLD/name).read_text().replace('manuscript-company-modules-20261023','manuscript-company-returns-20261024')
    text=text.replace('accdsl-company-modules-20261023','accdsl-company-returns-20261024').replace('3.55','3.56')
    if name=='verify.py':
        old="allowed={'accounting-product-proposal.tex','chapters/06-language.tex','chapters/07-execution.tex','sections/company-family-language.tex'}"
        new="allowed={'accounting-product-proposal.tex','chapters/06-language.tex','sections/company-module-language.tex'}"
        assert old in text;text=text.replace(old,new)
        text=text.replace("added!={'sections/company-module-language.tex'}","added!={'sections/company-return-reference.tex'}")
        a=text.index('    phrases=');b=text.index('\n    locations=',a)
        text=text[:a]+"    phrases=['From a return declaration to the next annual opening','An author declares facts before choosing an event','One event changes one shared book','Tax accumulates within a year and resets at its boundary']"+text[b:]
    (HERE/name).write_text(text)
print('configured bounded build and exact source-preservation checks')
