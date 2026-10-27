"""Retain build attempt 1, then apply the audited local grammar amendment once."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil
from check_candidate import check

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'docs/design/proposal/manuscript-readability-20261021'
C = R / 'docs/design/proposal/manuscript-readability-20261022'
A = U / 'attempts/1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = check()
assert checks['pdf_sha256'] == '28ece05611ea3bf831b7092961daf906d92bd1d5eddbe95748bdc551f039f0c3'
assert not A.exists()

pairs = [
    ('nehmer1997', r'\citet{nehmer1997}, especially Sections 2--5, supplies',
     r'\citet{nehmer1997}, especially Sections 2--5, supply'),
    ('babcinetchi2022', r'\citet{babcinetchi2022}, pp.~342--345, offers',
     r'\citet{babcinetchi2022}, pp.~342--345, offer'),
    ('behn2019', r'\citet{behn2019}, Section 2, makes',
     r'\citet{behn2019}, Section 2, make'),
    ('green2007', r'\citet{green2007}, Definitions 3.1--3.2 and Section 4, treats',
     r'\citet{green2007}, Definitions 3.1--3.2 and Section 4, treat'),
    ('snodgrass1986', '\\citet{snodgrass1986} distinguishes historical validity from the time facts\nare stored. The archived paper is \\emph{Temporal Databases}, by Snodgrass and\nAhn (1986).\nIts snapshot, rollback, historical and temporal examples',
     'In \\emph{Temporal Databases}, \\citet{snodgrass1986} distinguish historical\nvalidity from the time facts are stored. Their snapshot, rollback, historical\nand temporal examples'),
    ('giacomini2021', 'working version, shows how a class of priors',
     'working version, show how a class of priors'),
    ('hoeting1999', r'\citet{hoeting1999}, equations (1)--(3), gives',
     r'\citet{hoeting1999}, equations (1)--(3), give'),
    ('vandeursen2000', r'\citet{vandeursen2000} surveys',
     r'\citet{vandeursen2000} survey'),
    ('mernik2005', 'treats application libraries as serious competitors and distinguishes deciding,',
     'treat application libraries as serious competitors and distinguish deciding,'),
    ('merigoux2021', r'\citet{merigoux2021}, Sections 3--4 and Figures 8--9, provides',
     r'\citet{merigoux2021}, Sections 3--4 and Figures 8--9, provide'),
    ('jones2000', '\\citet{jones2000}, Sections 3--5, builds complex financial contracts from\ncombinators and separates',
     '\\citet{jones2000}, Sections 3--5, build complex financial contracts from\ncombinators and separate'),
    ('damoura2008', r'\citet{damoura2008}, Sections 2--3, describes',
     r'\citet{damoura2008}, Sections 2--3, describe'),
    ('vandeMeent2018', r'\citet{vandeMeent2018} develops',
     r'\citet{vandeMeent2018} develop')
]
name = 'chapters/03-literature.tex'
updated = (C / name).read_text()
replacements = []
for key, old, new in pairs:
    assert updated.count(old) == 1, key
    updated = updated.replace(old, new, 1)
    replacements.append(dict(path=name, id='RR347-local-grammar-' + key, old=old, new=new))

A.mkdir(parents=True)
shutil.copytree(C, A / 'candidate')
for p in sorted(U.iterdir()):
    if p.is_file():
        shutil.copy2(p, A / p.name)
shutil.copytree(U / 'rendered', A / 'rendered')
shutil.copy2(R / 'docs/plans/accounting-readability-repair-20261022.md', A / 'plan.md')
(A / 'candidate-checks.json').write_text(json.dumps(checks, indent=2) + '\n')
(A / 'review.md').write_text('''# First-build local reading

Version 3.47 attempt 1; PDF SHA256
28ece05611ea3bf831b7092961daf906d92bd1d5eddbe95748bdc551f039f0c3.
Read actual rendered pages 1,27–29,73–78,97–102,169–172,212–215 in their
ordered local segments, including the final six pages after session recovery.
Cash/escrow amounts, rounding and liquidity consequences remain. The thesis
date and temporal/public-availability distinction remain. The compilation
pointer reaches Section 7.4 and its CompileRequest boundary. Historical rule
dates, ASBE adoption/tax timing and current-authority qualifications remain.
The instrument-reduction pointer now reaches following Section 10.12.10;
the distinct purchase, gain histories, reserve and profit equations remain.
No clipping was seen. Thirteen author-subject passages require agreement
repair, confirmed against the source and bibliography before mutation.
See the audited grammar amendment. This is a retained local attempt, not a
final-build reading or a whole-document regression.
''')
bindings = {str(p.relative_to(R)): sha(p) for p in sorted(A.rglob('*')) if p.is_file()}
(A / 'preservation.json').write_text(json.dumps({'bindings': bindings}, indent=2) + '\n')

(C / name).write_text(updated)
lock = json.loads((U / 'source-lock.json').read_text())
lock['replacements'].extend(replacements)
lock['amendment'] = 'docs/plans/accounting-readability-repair-20261022-amendment.md'
lock['retained_attempt_1'] = str(A.relative_to(R))
diffs = []
for row in lock['files']:
    name = row['path']
    row['candidate_sha256'] = sha(C / name)
    row['changed'] = row['baseline_sha256'] != row['candidate_sha256']
    if row['changed']:
        diffs.extend(difflib.unified_diff((B / name).read_text().splitlines(True),
            (C / name).read_text().splitlines(True), fromfile='3.46/' + name, tofile='3.47/' + name))
(U / 'source-lock.json').write_text(json.dumps(lock, indent=2) + '\n')
(U / 'source-delta.patch').write_text(''.join(diffs))
result = check(source_only=True)
print(json.dumps(dict(status=result['status'], amended_passages=len(pairs),
    retained_attempt_files=len(bindings), displays=result['displays_preserved'], citations=result['citations_preserved'])))
