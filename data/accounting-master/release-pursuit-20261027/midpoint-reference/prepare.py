from pathlib import Path
import json
import hashlib
import shutil

D = Path(__file__).resolve().parent
R = D.parents[3]
base = json.loads((D / 'baseline.json').read_text())
B = R / base['baseline']
T = R / 'docs/design/proposal/manuscript-reference-v554r3-20261027'
assert not T.exists()
T.mkdir()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for row in base['files']:
    p = B / row['path']
    assert sha(p) == row['sha256']
    q = T / row['path']
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_bytes(p.read_bytes())
C = T / 'companions/reference-computations'
C.mkdir()
shutil.copy2(D / 'verify_reference.py', C / 'verify_reference.py')
for original, name in [('check_examples.py', 'teaching-original.py'), ('arithmetic.json', 'teaching-expected.json')]:
    p = R / 'data/accounting-master/simulation-monograph-20261026' / original
    assert sha(p) == base['inputs'][str(p.relative_to(R))]
    shutil.copy2(p, C / name)
lock = {'inputs': {n: sha(C/n) for n in ['teaching-original.py', 'teaching-expected.json']},
        'original_unit': 'data/accounting-master/simulation-monograph-20261026',
        'scope': 'Original169 teaching arithmetic checks preserved exactly; no empirical validation',
        'plan': 'docs/plans/accounting-midpoint-reference-20261027.md'}
(C / 'provenance.json').write_text(json.dumps(lock, indent=2) + '\n')
(C / 'README.md').write_text('''# Deterministic reference computations

From this component, run with an existing Python3.11+ interpreter:

```sh
python3 -I -B verify_reference.py --output-dir /tmp/accdsl-reference-new-output
```

Choose a new output directory. The verifier copies the exact historical
teaching checker into that output, executes the copy and compares its complete
result with teaching-expected.json. Never execute teaching-original.py in this
component: it is preserved with its original write-beside-source behavior.
The wrapper adds exact rational midpoint-grid cases and the n=4/5 and10/11
nonmonotonic-error examples. Its outputs include every threshold case, original
result, stdout/stderr and a run manifest. It refuses existing output directories.

The universal threshold error bound comes from the manuscript floor proof.
Finite rational checks alone do not prove it. The original169 checks cover
selected deterministic teaching examples throughout the simulation volume;
they are not a complete solver, company forecast or stochastic comparison.
The standard library is sufficient. No installation, network service or GPU
is used. provenance.json records original source/result identities.
''')
p = T / 'simulation/18-computation-cases.tex'
s = p.read_text()
old = "The mean check passes perfectly while the breach estimate differs from 0.7. Increasing $n$ improves the discretization in this example, but its error depends on the threshold's location relative to the grid. A convergence study should examine the queried event, not only smooth moments."
new = r'''The mean check passes perfectly while the breach estimate differs from 0.7. More grid points need not reduce that error at every refinement. With $n=5$, the strict breach event includes only $0.5$, $0.7$ and $0.9$, so its estimate is $0.6$. The absolute error rises from $0.05$ at $n=4$ to $0.1$ at $n=5$. At $n=10$ the estimate is exactly $0.7$, whereas $n=11$ gives $8/11$. Alignment with the threshold matters even as the grid becomes finer.

A bound explains what refinement does guarantee. For a threshold $t\in[0,1]$, let $p_n(t)$ be the fraction of the $n$ midpoints strictly above $t$. A midpoint is at or below $t$ precisely when $i\leq nt+1/2$. There are therefore $\lfloor nt+1/2\rfloor$ such points, and

\begin{equation}
\label{eq:midpoint-threshold-bound}
p_n(t)=1-\frac{\lfloor nt+1/2\rfloor}{n},
\qquad
\bigl|p_n(t)-(1-t)\bigr|\leq\frac{1}{2n}.
\end{equation}

To obtain the bound, write $k=\lfloor nt+1/2\rfloor$. The defining inequalities $k\leq nt+1/2<k+1$ give $-1/2\leq nt-k<1/2$. Dividing by $n$ bounds $p_n(t)-(1-t)$. Thus the maximum permitted error shrinks to zero, although the actual error can rise between successive grids. The result holds for this uniform midpoint rule and one threshold event; a convergence study must still examine the event actually being queried.'''
assert s.count(old) == 1
s = s.replace(old, new).replace('A random sample of size 100 has probability', 'An independent random sample of size 100 has probability')
old = 'The accompanying arithmetic script checks the deterministic examples and records its scope.'
new = r'''The retained arithmetic script checks selected deterministic examples and records its scope. The package companion \texttt{companions/reference-computations} reproduces its complete checked values and adds the midpoint-boundary examples above. The all-threshold conclusion rests on the floor argument in equation~\eqref{eq:midpoint-threshold-bound}, not on the number of rational examples tested.'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
for name in ['accounting-product-proposal', 'simulation-foundations']:
    p = T / (name + '.tex')
    s = p.read_text()
    assert s.count('Version 5.54-R2 ') == 1
    p.write_text(s.replace('Version 5.54-R2 ', 'Version 5.54-R3 '))
p = T / 'README.md'
s = p.read_text()
p.write_text('''# AccDSL 5.54-R3 — numerical reference clarification

This protected successor corrects the midpoint-grid convergence statement and
adds its exact error bound, counterexamples and portable teaching companion.
The four preceding components are retained unchanged. PACKAGE-REVISION.json
describes the historical5.54-R2 package revision2; this successor has its own
manifest and build records under release-pursuit-20261027/midpoint-reference.
The release remains not_ready.

'''+s.replace('# AccDSL 5.54-R2 — internal package revision 2', '# Predecessor package documentation', 1))
p = T / 'DEPENDENCIES.md'
p.write_text('''# Additional reference companion in 5.54-R3

companions/reference-computations requires only Python3.11+ and reproduces the
retained169 arithmetic checks plus the new exact rational midpoint examples.
Its README specifies a fresh output directory and the scope of each result.
The manuscript proof supplies the bound for all real thresholds. No empirical
method ranking or full-evidence closure follows. Current build/relocation records
are under data/accounting-master/release-pursuit-20261027/midpoint-reference/.

The following dependency record is inherited from the preserved predecessor.

'''+p.read_text())
added = [str(p.relative_to(T)) for p in C.iterdir()]
(D / 'candidate.json').write_text(json.dumps({'baseline': base['baseline'],
    'candidate': str(T.relative_to(R)), 'added_files': sorted(added),
    'changed_sources': ['README.md', 'DEPENDENCIES.md', 'accounting-product-proposal.tex',
                        'simulation-foundations.tex', 'simulation/18-computation-cases.tex']}, indent=2)+'\n')
print('Prepared', T, 'with', len(added), 'companion files')
