"""Reuse the preceding bounded build checks with explicit successor scope."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'statement-context-integration-20261024'
for name in ['build.py','verify.py']:
    assert not (HERE/name).exists()
    text=(OLD/name).read_text().replace('manuscript-statement-context-20261024',
                                       'manuscript-method-requirements-20261024')
    text=text.replace('accdsl-statement-context-20261024','accdsl-method-requirements-20261024')
    text=text.replace('3.58','3.59')
    if name=='verify.py':
        old="allowed={'accounting-product-proposal.tex','chapters/06-language.tex','sections/company-source-state.tex'}"
        new="allowed={'accounting-product-proposal.tex','chapters/06-language.tex','chapters/17-portable-reference.tex'}"
        assert old in text
        text=text.replace(old,new)
        text=text.replace("added!={'sections/statement-context-relations.tex'}",
                          "added!={'sections/method-requirement-language.tex'}")
        a=text.index('    phrases=')
        b=text.index('\n    locations=',a)
        text=text[:a]+"    phrases=['What must be known before a method can run','A known contradiction survives an unrelated unknown','The same requirement in text and typed form','Content identity leaves authority with the caller']"+text[b:]
    (HERE/name).write_text(text)
print('configured protected method-requirement successor')
