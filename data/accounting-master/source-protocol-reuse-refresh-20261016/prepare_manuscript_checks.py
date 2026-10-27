from pathlib import Path
OUT=Path(__file__).resolve().parent;PRIOR=OUT.parent/'sector-company-composition-20261016'
s=(PRIOR/'check_manuscript.py').read_text()
s=s.replace('sector-company-composition','source-protocol-reuse-refresh').replace('manuscript-insurance-retrospective-measurement-20261016','manuscript-sector-company-composition-20261016')
s=s.replace('Version 3.36','Version 3.37').replace('Version 3.35','Version 3.36').replace("version='3.36'","version='3.37'").replace('protected 135','protected 136').replace('3.36 sector company composition','3.37 source protocol reuse refresh')
a=s.index("        elif rel == 'sections/company-composition.tex':");b=s.index("        check('preserved-argument/'",a)
s=s[:a]+"""        elif rel in ('sections/selected-reuse.tex','sections/future-validation.tex'):
            name='reuse-dependencies' if 'selected-reuse' in rel else 'joined-validation'
            after=after.removesuffix('\\n'+r'\\input{sections/'+name+'}\\n')
        elif rel=='references.bib':
            after=after.removesuffix((OUT/'reference-additions.bib').read_text())
""".replace("'\\n'","'\\\\n'").replace("+'}\\n'","+'}\\\\n'")+s[b:]
# Rewrite inserted literal newlines unambiguously using repr-built source lines.
a=s.index("        elif rel in");b=s.index("        check('preserved-argument/'",a)
lines=["        elif rel in ('sections/selected-reuse.tex','sections/future-validation.tex'):",
"            name='reuse-dependencies' if 'selected-reuse' in rel else 'joined-validation'",
"            after=after.removesuffix("+repr('\n')+"+r'\\input{sections/'+name+"+repr('}\n')+")",
"        elif rel=='references.bib':",
"            after=after.removesuffix((OUT/'reference-additions.bib').read_text())"]
s=s[:a]+'\n'.join(lines)+'\n'+s[b:]
s=s.replace("'A bank and insurer share a group close'","'The source declarations constrain the first environment'")
s=s.replace("'nonlinear insurance valuation still require their own methods'","'as separate evidence obligations'")
s=s.replace('sector company composition','source protocol reuse refresh')
# Include the independently located joined-validation pages and new bibliography.
a=s.index('    pages = sorted(');b=s.index('\n    indices =',a)
s=s[:a]+"""    validation=next(i+1 for i,p in enumerate(doc) if 'The joined calculations retain separate validation targets' in ' '.join(p.get_text().split()) and i>20)
    pages=sorted({1,8,len(doc)-3,len(doc)-2,len(doc)-1,len(doc)} | set(range(start-1,end+2)) | set(range(validation-1,validation+3)))
""".rstrip()+s[b:]
(OUT/'check_manuscript.py').write_text(s)
print('Prepared3.37 source-preservation and rendered checks')
