from pathlib import Path
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import fitz

D = Path(__file__).resolve().parent
R = D.parents[3]
base = json.loads((D/'baseline.json').read_text())
c = json.loads((D/'candidate.json').read_text())
B, T = R/c['baseline'], R/c['candidate']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, value):
    p.write_text(json.dumps(value, indent=2)+'\n')

assert not (D/'package-record.json').exists()
# Replace inherited present-tense instructions rather than leaving contradictory
# package identities under a new heading. Historical source bytes stay in B.
(T/'README.md').write_text('''# AccDSL 5.54-R3 — internal review candidate

The governing proposal has 836 pages. The simulation volume has 265 total pages
and 244 body pages. The release remains **not_ready**. This protected successor
clarifies midpoint-grid convergence, proves its exact threshold-error bound and
adds a reproducible teaching-arithmetic companion. All four earlier executable
components are retained byte for byte. Whole-document, source, specification and
independent acceptance work remains open.

Run integrity verification from this directory with
python3 -I -B verify_package.py.
package-manifest.json pins every included file; its hash is retained outside
the package. This checks integrity against that record, not independent
authenticity. Generated TeX intermediates, caches and run outputs are excluded.
PACKAGE-REVISION.json is the unchanged historical record of predecessor
5.54-R2 package revision2, not this successor's build record. Current source,
build and relocation records are in
data/accounting-master/release-pursuit-20261027/midpoint-reference/.

| Component | Reproduced scope | Instructions |
| --- | --- | --- |
| historical-core0 | Historical language and reference fixtures | companions/historical-core0 |
| selected-term | Bounded modern term execution | companions/selected-term |
| refinancing-domain | Dated cash examples and two counterexamples | companions/refinancing-domain/README.md |
| source-history-replay | 37 retained source/history/opening/report exchanges | companions/source-history-replay/README.md |
| reference-computations | 169 retained arithmetic checks and exact midpoint cases | companions/reference-computations/README.md |

Each component has its own environment, fresh-output rule and exact comparison
scope. Follow its README; never execute archived preparation writers. The
source/history archive must be validated and extracted before replay.

Build both documents in a writable copy with the recorded TeX Live 2026 tools.
Create .tex-cache in that copy and set TEXMFVAR and TEXMFCACHE to its absolute
path. Run latexmk -g -lualatex -interaction=nonstopmode -halt-on-error
-no-shell-escape accounting-product-proposal.tex; then use the same options
for simulation-foundations.tex. Exact executed command arrays are retained
in the current build records.

LuaLaTeX, BibTeX, latexmk and the imported TeX packages must already be
available. No installation is implicit. PDF bytes can differ with build
metadata; full normalized page-text comparison is recorded separately.

Historical contracts under spec/ and fixtures/ retain their original identities.
Later profile definitions govern their stated extensions. Repository evidence
paths in the text are not all included: the package contains only its declared
subset. Original issuer filings, papers and accounting standards remain separately
held. DEPENDENCIES.md states remaining access and reproduction limits.
This is an internal review package, with no publication or redistribution grant.
''')
p = T/'DEPENDENCIES.md'
s = (B/'DEPENDENCIES.md').read_text()
old = '''Internal package revision 2 contains the unchanged 5.54-R2 manuscript and four
bounded executable components. PACKAGE-REVISION.json records this package
change separately from the manuscript edition.'''
new = '''The 5.54-R3 package contains five bounded executable components.
PACKAGE-REVISION.json preserves the historical 5.54-R2 package-revision record.
Current 5.54-R3 build and relocation records are retained under
data/accounting-master/release-pursuit-20261027/midpoint-reference/.'''
assert old in s
s = s.replace(old, new)
s = s.replace('Four working components\ndo not reproduce every result in an 835-page manuscript.',
              'Five working components\ndo not reproduce every result in an 836-page manuscript.')
s = s.replace('The exact\n5.54-R2 source and PDFs have separate-copy reproduction evidence linked by\nPACKAGE-REVISION.json.',
              'Predecessor 5.54-R2 source and PDFs have separate-copy reproduction evidence\nlinked by PACKAGE-REVISION.json. Current 5.54-R3 reproduction has its own record.')
s = s.replace('| source-history-replay |', '| reference-computations | 169 retained arithmetic checks and 6,552 exact rational midpoint examples | Python 3.11+ standard library; universal bound follows from the written proof, no stochastic validation |\n| source-history-replay |', 1)
s = s.replace('Current package execution record:\ndata/accounting-master/release-pursuit-20261027/replay-package/.',
              'Current package execution record:\ndata/accounting-master/release-pursuit-20261027/midpoint-reference/.\nPredecessor package record:\ndata/accounting-master/release-pursuit-20261027/replay-package/.')
s = s.replace('Exact manuscript repair/build record:', 'Predecessor financing repair/build record:')
p.write_text(s)

checks, delta, changed = [], [], []
for row in base['files']:
    assert sha(B/row['path']) == row['sha256']
    checks.append('baseline:'+row['path'])
    if sha(T/row['path']) != row['sha256']:
        changed.append(row['path'])
        if (T/row['path']).suffix != '.pdf':
            delta.extend(difflib.unified_diff((B/row['path']).read_text().splitlines(True),
                (T/row['path']).read_text().splitlines(True),
                fromfile='5.54-R2/'+row['path'], tofile='5.54-R3/'+row['path']))
assert set(changed) == set(c['changed_sources']) | {'accounting-product-proposal.pdf','simulation-foundations.pdf'}
a = (B/'simulation/18-computation-cases.tex').read_text()
b = (T/'simulation/18-computation-cases.tex').read_text()
pattern = r'\\cite[a-zA-Z]*\*?(?:\[[^]]*\])*\{([^}]+)\}'
assert re.findall(pattern,a) == re.findall(pattern,b)
assert b.count('label{eq:midpoint-threshold-bound}') == 1
# All original inline mathematics survives the repair. Original chapter has
# no displays; the sole new display is the locally derived bound.
from collections import Counter
inline = r'(?<!\\)\$(.*?)(?<!\\)\$'
assert not (Counter(re.findall(inline,a,re.S))-Counter(re.findall(inline,b,re.S)))
assert json.loads((D/'check-01/result.json').read_text())['passed']
volumes = []
for name in ['accounting-product-proposal','simulation-foundations']:
    assert json.loads((D/'build'/f'{name}.json').read_text())['exit_code'] == 0
    log = (T/(name+'.log')).read_text(errors='replace')
    assert not re.search(r'undefined|Overfull|multiply defined', log, re.I)
    doc = fitz.open(T/(name+'.pdf'))
    assert '5.54-R3' in doc[0].get_text()
    clipped = []
    for i,page in enumerate(doc):
        for w in page.get_text('words'):
            if w[0]<-1 or w[1]<-1 or w[2]>page.rect.width+1 or w[3]>page.rect.height+1:
                clipped.append((i+1,w[4]))
    assert not clipped, clipped[:8]
    volumes.append({'name':name,'pages':len(doc),'sha256':sha(T/(name+'.pdf'))})
checks += ['exact_change_set','citations_preserved','all_inline_math_preserved',
           'bound_label_unique','reference_arithmetic','both_builds_resolved',
           'both_volumes_unclipped','covers_current']
(D/'source-delta.patch').write_text(''.join(delta))
dump(D/'verification.json', {'passed':True,'checks':checks,'changed_files':changed,
                            'volumes':volumes,'whole_document_acceptance':False})
viewed = [('accounting-product-proposal',n,f'main-{n:04}.png') for n in [1,*range(189,195),195]]
viewed += [('simulation-foundations',n,f'simulation-{n:04}.png') for n in [1,179,180,184]]
dump(D/'rendered-review.json', {'scope':'Complete chapter18 main189–194 and listed covers/adjacent pages; author only',
    'pages':[{'volume':v,'page':n,'pdf_sha256':sha(T/(v+'.pdf')),
              'image_sha256':sha(D/'rendered'/f),'review':'author_viewed'} for v,n,f in viewed],
    'independent_reader':'pending','human_acceptance':'pending'})
m = json.loads((B/'package-manifest.json').read_text())
m.update(candidate='5.54-R3;not_ready', manifest_self_hash='Stored outside package in release-pursuit-20261027/midpoint-reference/package-record.json')
for path in c['added_files']:
    m['files'].append({'path':path})
for row in m['files']:
    p = T/row['path']
    row.update(sha256=sha(p),bytes=p.stat().st_size)
dump(T/'package-manifest.json',m)
run = subprocess.run(['python3','-I','-B','verify_package.py'],cwd=T,capture_output=True,text=True)
assert run.returncode == 0, run.stdout+run.stderr
dump(D/'package-record.json', {'passed':True,'files':len(m['files']),
    'manifest_sha256':sha(T/'package-manifest.json'),'verification':json.loads(run.stdout),
    'predecessor_manifest_sha256':base['baseline_manifest_sha256']})
out = D/'relocation'
out.mkdir(exist_ok=False)
dest = Path(tempfile.mkdtemp(prefix='accdsl-v554r3-relocated-'))
for row in m['files']:
    p = dest/row['path']
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes((T/row['path']).read_bytes())
shutil.copy2(T/'package-manifest.json',dest/'package-manifest.json')
dump(out/'location.json',{'target':str(dest),'manifest_sha256':sha(T/'package-manifest.json')})
print(json.dumps({'passed':True,'checks':len(checks),'files':len(m['files']),
                  'volumes':volumes,'relocated':str(dest)}))
