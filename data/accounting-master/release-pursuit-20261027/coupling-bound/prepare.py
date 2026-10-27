from pathlib import Path
import json,hashlib,shutil
D=Path(__file__).resolve().parent;R=D.parents[3];B=R/'docs/design/proposal/manuscript-release-prep-v552r1-20261027';T=R/'docs/design/proposal/manuscript-release-prep-v552r2-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((D/'exact-results.json').read_text())['passed'];assert (R/'docs/AccDSL-latest.tex').resolve().parent==B
T.mkdir(exist_ok=False);manifest=json.loads((B/'package-manifest.json').read_text());baseline=[]
for row in manifest['files']:
 p=B/row['path'];assert sha(p)==row['sha256'];baseline.append({'path':row['path'],'sha256':sha(p)})
 if p.suffix=='.pdf':continue
 q=T/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(D/'baseline.json').write_text(json.dumps({'source':str(B.relative_to(R)),'candidate':str(T.relative_to(R)),'inputs':baseline,'package_manifest_sha256':sha(B/'package-manifest.json')},indent=2)+chr(10))
for name in ['accounting-product-proposal.tex','simulation-foundations.tex']:
 p=T/name;s=p.read_text();assert s.count('Version 5.52-R1')==1;p.write_text(s.replace('Version 5.52-R1','Version 5.52-R2'))
p=T/'simulation/lit-09-approximation-4.tex';s=p.read_text();start=s.index('A stronger but directly checkable condition');end=s.index('For finite kernels with common outcome labels',start)
replacement='''A stronger but directly checkable condition can avoid averaging actions.
Consider a finite horizon of $T$ transitions. Keep a persistent contract type
$§theta$ fixed and let a history record the actor's observations and past
actions. In both the full model and a reduced model, require the same feasible
actions at paired histories. Specify a relation between their states and couple
the initial states so that they belong to this relation, their initial
observations agree, and every requested current output agrees almost surely.
An equal opening signal alone does not establish these other conditions.

At each paired history and common action, suppose a joint coupling of the next
state, observation and reported output leaves the states in the relation and
the observation/output records equal with conditional probability at least
$1-§delta_t$, where $0§leq§delta_t§leq1$. This condition includes every history
and action reachable before a mismatch; fitting one historical policy is
insufficient. A common deterministic policy chooses the same action while its
retained information histories agree. Randomized policies can use the same
independent random draws if both models permit that randomization. Neither
policy may depend on a discarded private signal.

Let $E_t$ mean that the initial pairing and all comparisons through transition
$t$ have succeeded. Under the initial condition, $§Prob(E_0)=1$. Integrating
the conditional success bound over the surviving histories gives
$§Prob(E_t)§geq(1-§delta_t)§Prob(E_{t-1})$. This unconditional recurrence also
applies when no histories survive; it does not condition on an event of zero
probability. Iterating it gives
§begin{equation}
§Prob(E_T^c)§le1-§prod_{t=1}^T(1-§delta_t)
§le§sum_{t=1}^T§delta_t.
§label{sim:lit-finite-coupling}
§end{equation}

The requested path loss must also be preserved by a successful comparison.
Assume that the two models use the same measurable loss functional of the
retained observations, actions and requested outputs, with values in $[0,B]$.
Its two path evaluations therefore agree on $E_T$ and can differ by at most
$B$ otherwise. Applying the triangle inequality to the expectation under the
chosen coupling yields
§begin{equation}
|§E L-§widetilde§E L|
§le B§Prob(E_T^c)
§le B§left§{1-§prod_{t=1}^T(1-§delta_t)§right§}.
§label{sim:lit-finite-cost}
§end{equation}
The two expectations refer to the same loss functional under the respective
model laws. No convexity or fractional issuance is required. A default
indicator is covered when default is one of the compared outputs, or is
determined by the matched retained records. A loss depending on a hidden
recovery allocation that was discarded is not covered merely because its
values are bounded.

Initial and within-pair approximation errors can be included explicitly. If
$§Prob(E_0)§geq1-§delta_0$ and the two losses differ by at most $§rho$ on
$E_T$, with $0§leq§rho§leq B$, define
§begin{align}
§Delta_T&=1-(1-§delta_0)§prod_{t=1}^T(1-§delta_t),
§label{sim:lit-initial-coupling}§§
|§E L-§widetilde§E L|&§leq
§rho+(B-§rho)§Delta_T.
§label{sim:lit-matched-loss}
§end{align}
Indeed, with $p=§Prob(E_T^c)§leq§Delta_T$, the coupled expected absolute
loss difference is at most $§rho(1-p)+Bp$. The earlier bound is the special
case $§delta_0=§rho=0$. These terms have distinct meanings: $§delta_0$
measures failure of the initial pairing; $§rho$ is a loss discrepancy even
when the paired path remains valid. With no transitions, identical signals
but different opening cash already show why transition errors cannot cover
an omitted initial report. Likewise, matching cash paths does not bound an
unreported creditor-allocation loss. The initial relation and requested loss
must therefore be chosen before the comparison.

'''.replace('§',chr(92))
s=s[:start]+replacement+s[end:];p.write_text(s)
p=T/'README.md';s=p.read_text().replace('5.52-R1','5.52-R2');needle='This is a protected successor to 5.52.';assert needle in s;s=s.replace(needle,'This is a protected successor to 5.52-R1. It also states the initial-pairing and common-loss assumptions needed by the finite-coupling bound.',1);p.write_text(s)
(D/'diagnosis.md').write_text('''# Finite-coupling statement diagnosis

Read the complete source argument and standalone physical pages 79–82, printed
64–67. The target reader is a financially literate implementer choosing a
compression method for discrete financing decisions. The passage explains why
conditional averaging can violate feasible actions, then supplies a coupling
alternative. Its comparison at date zero and the loss being compared need
explicit conditions before the product bound is used.

The prior text assumes matching initial observations, then uses a survival
event starting with probability one. It also asserts loss equality on matching
paths without tying the loss to the matched records. Those are missing
hypotheses, not numerical failures in the supplied three-period example. A
zero-transition initial-output counterexample and a discarded hidden-loss
counterexample show the issue. Exact rational fixtures preserve the original
3423/2000 bound. The new version states the initial relation, same feasible
information-based policy and common measurable bounded loss; adds the explicit
initial/within-match error extension; and avoids conditioning on null events.

All four original rendered pages were viewed at normal reading resolution.
The reader should now be able to identify what must match at date zero, why
the same decision remains admissible, which loss is bounded, how persistent
type is retained, and what to do when initial or matched-loss equality fails.
The protected successor changes the argument in the manuscript itself.
No imported theorem, financial fixture or source claim is broadened.
''')
print(json.dumps({'candidate':str(T.relative_to(R)),'baseline_files':len(baseline),'repair':'explicit initial-pairing and common-loss conditions; generalized error bound','status':'source_prepared_build_pending'}))
