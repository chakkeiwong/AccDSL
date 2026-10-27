"""Reconcile inherited evidence without promoting documentary review to proof."""
from pathlib import Path
from hashlib import sha256
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
OLD = ROOT / 'data/accounting-master/current-design-reconciliation-20261025/audit-status.json'
def digest(p): return sha256(p.read_bytes()).hexdigest()
def save(name, obj): (OUT/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')

# Packages are closure obligations, not claims that their bounded predecessors are absent.
specs = [
('W01','Disclosure meaning and historical availability',[], 'MC01 MC03 MC04 MC05 MC19 MC27 MC28 G5 G11 G13 G17 I01 I02',
 'A reported consolidated balance is admitted as a legal-book opening; a later document enters an earlier information set.',
 'Retained source, statement, network and population histories; recursive source inventories; exact information-time projections; E03 conditional contract-summary dependency inventory.',
 'For each selected source dependency retain exact bytes, span, edition, precision and availability interval; translate the actual qualification or preserve an unresolved obligation; show admissible, contradicted and unresolved family outcomes.',
 'Follow E03 with a new evidenced lead for the underlying indenture and actual series terms; bind applicability, event/notice facts and availability to a bounded partial history. The prior failed 2018 acquisition remains recorded.',
 'Actual legal-book records may remain unidentified; a coherent partial family is acceptable only with the excluded population and consequences visible.'),
('W02','Admissible history construction and mappings',['W01'], 'MC02 MC06 MC07 MC08 MC09 MC10 MC28 G1 G5 G12 G15 P17-08.01 P17-08.07',
 'Separate marginal alternatives create an impossible company; omitted contracts disappear from a completeness claim.',
 'Finite/affine candidate generation, retained joint histories, explicit population overlaps and carried claims.',
 'Declare template/domain scope, joint constraints, context and population relations; retain all feasible alternatives within that scope or expose search remainder; check negative and outside-scope examples against independent solutions.',
 'Extend a concrete missing event or non-affine relationship required by W01; do not rebuild existing affine families.',
 'No solver may invent legal findings, disjointness, unknown transactions or probabilities.'),
('W03','Information, inference and persistent ambiguity',[], 'MC08 MC10 MC12 MC14 G6 G14 G15 P17-08.06 L02 L07',
 'An uninformative observation deletes a type; replacement evidence is conjoined with the superseded assertion; a policy sees future outcomes.',
 'Exact finite filtering/path enumeration, original PMCMC proof note, revision/information runtime fixtures, actor-time contracts and E02 extended-target exchange/correction diagnostics.',
 'Specify persistent state, actor observation kernels, evidence identity and permitted policy class; compare recursive and path results under informative/uninformative/conflicting/revised evidence; retain unweighted sets when a measure is unjustified.',
 'After E02, inspect modern waste-free and quantitative/resampling dependencies and define an immutable-vintage inference request; separately bind actor information to multi-period policies.',
 'Company likelihoods, priors and strategic disclosure models require identification; finite exact examples do not establish general inference accuracy.'),
('W04','Compression and controlled state growth',['W02','W03'], 'MC11 MC26 G16 P17-08.04 L01',
 'Equal cash or means conceal different refinancing rights; a small smooth error changes a default decision.',
 'Observation-sensitive finite quotient and finite discrete-action coupling/error derivations with exact checks.',
 'State query, horizon, policy and observation class; prove exact joint-kernel equivalence or provide computable output-error and feasible-policy-transfer premises; retain detail and invalidate grouping when scope changes.',
 'Construct one mixed/continuous contract example whose observation and guard margins can be bounded; compare lazy shared-state execution against full enumeration on small instances.',
 'Storage sharing is not semantic merging; sampling is not an exact bound; general worst-case combinatorial complexity remains.'),
('W05','Financing settlement and contractual memory',[], 'MC13 MC15 MC16 MC17 MC18 G4 G7 I05 I06 P17-05.01 P17-05.02 L03',
 'An unfunded payment stops execution and the obligation vanishes from subsequent simulation; late cash rewrites earlier payment status.',
 'Dated financing accrual/schedules, limited unpaid-rights examples, one-period quote-policy cases, typed issuance/share memory, E01 complete maturity/partial/late-settlement paths and E03 selected default/remedy conditions.',
 'Connect due recognition, partial settlement, missed payment, later recovery and reports in the common typed executor; preserve face, carrying amount, past-due claim, cash, event dates and failed prefixes against an independent complete-state oracle.',
 'Expose E01 reusable claim/share/history invariants and opening admission; bind E03 event/default/acceleration/rescission distinctions to the common typed executor, then supported dated funding and rights-changing events.',
 'Synthetic no-fee/no-tax/no-penalty/no-acceleration convention; general default, insolvency and actual accounting admission remain separate.'),
('W06','Endogenous debt, equity and control',['W03','W05'], 'MC13 MC14 MC17 G6 I03 I06 P17-05.03 P17-05.04 L03',
 'Lenders price a policy owners abandon; a positive quote cannot be funded; conversion changes control but future decisions use old ownership.',
 'Finite price-policy fixed-point enumeration, priority/participation examples, diluted ownership and multi-world EPS methods.',
 'Specify information and commitment timing, owner liquidity/participation, creditor payoff/priority, dated settlement and post-conversion control; solve multi-period/mixed-policy cases or explicitly establish missing existence/selection premises.',
 'Add a two-date finite financing decision with an independent exhaustive strategy comparator and a governance-changing conversion case.',
 'Economic share value, accounting equity and regulatory capital differ; no unique equilibrium or bargaining allocation is presumed.'),
('W07','Corporate accounting methods and authority',['W01'], 'MC15 MC16 MC19 MC20 G7 G15 P17-04.01 P17-04.02 P17-04.03 P17-04.04 P17-04.05 P17-04.06 P17-04.07 P17-04.08 P17-04.09 P17-04.10 P17-04.11 P17-04.13',
 'An eligible treatment in one edition is applied to a different issuer or date; zero reversal weights are replaced with arbitrary allocations.',
 'Bounded customer, inventory, benefits, assets, leases, tax and statement methods with retained authority limits.',
 'For each operation retain applicable edition/transition, factual findings, complete formulas and same-fact competing treatments; test original/modified/unsupported cases and consequential journals/reports.',
 'Resolve zero-weight CGU reversal under a new primary-authority lead; then broader mixed promises, calendars, tax origins and costing according to actual case dependencies.',
 'Balanced journals and author review cannot establish authority or real eligibility; source gaps block only their dependent conclusions.'),
('W08','Group, ownership, hedge and currency composition',['W01','W06','W07'], 'MC06 MC17 MC20 I03 I06 P17-04.12 P17-05.03 P17-05.04 P17-05.05 P17-05.06 P17-05.07 P17-05.08 P17-05.09 P17-05.10',
 'Consolidated cash funds an inaccessible subsidiary; heterogeneous hedge origins are allocated by nominal fractions; EPS uses an arbitrary world minimum.',
 'Native group bindings, conditional group reporting, origin-matched reserve and finite rights examples.',
 'Preserve legal owners, control dates, transfer constraints, reciprocal identities and tax/FX origins; define arbitrary nonadditive EPS selection or refuse it; exercise an acquisition/hedge/financing composition.',
 'Choose a retained heterogeneous-origin or nonadditive-EPS counterexample and finish its exact rule and authority analysis before common integration.',
 'A group adjustment must not mutate legal books; valuation and control facts remain supplied findings.'),
('W09','Bank credit, funding and regulatory methods',['W01','W05'], 'MC21 I04 I05 P17-06.01 P17-06.02 P17-06.03 P17-06.04 P17-06.05 P17-06.06',
 'Book write-off erases legal recovery; multiple effective-rate roots are collapsed; a requested funding line is treated as cash.',
 'Shared exact credit state, conditional classified cash, finite ECL/POCI/commitment and funding/capital methods.',
 'Specify floating resets, write-off allocation, root identity, cash classification, settlement and regulatory perimeter; compare full credit states and shared-company statements including adverse cases.',
 'Extend the exact credit case with an explicit unpaid/right/write-off distinction and a supported multi-root or reset method only when needed.',
 'Actual credit/recovery and operative regulatory findings are not inferred from synthetic cases; calibration remains deferred.'),
('W10','Insurance valuation and company interaction',['W01','W08'], 'MC22 I04 P17-07.01 P17-07.02 P17-07.03 P17-07.04 P17-07.05 P17-07.06 P17-07.07 P17-07.08',
 'Equal group balances hide cohorts; nonlinear treaty losses use quota formulas; finance and service origins offset incorrectly.',
 'Insurance fiscal carry, statement bridge, component identity repair, loss/recovery and finite valuation methods.',
 'Bind group membership, transition history, FCF/RA/service/finance origins and treaty dependence to exact state/report examples; retain actual actuarial assumptions and separate physical/pricing measures.',
 'Complete mixed-origin early-termination or changing treaty allocation with a shared-group report comparator; match the published valuation paper and official code.',
 'A finite actuarial law or calendar-year fixture does not establish general valuation or historical admission.'),
('W11','General language and compatible rule composition',[], 'MC13 MC20 MC23 MC24 G2 G4 I04 P17-08.07',
 'A command wrapper is mistaken for source-defined validation; flattening joins same-named terms from different claims.',
 'Complete method/program authoring, declarative openings/eligibility, Unicode repair, nested queries/templates, event membership and the six-component term semantic bundle, integrated in Version 5.14.',
 'Expose general grouping/cardinality/ordered-selection rules; compare complete typed/source states and refusal behavior with native baselines disabled; specify unsupported constructs and cross-profile migrations.',
 'Preserve the live term-structural-admission plan and successors. The bounded semantic bundle is checked; exact native structure/migration admission, direct nested source authoring and event/carry binding remain.',
 'Do not duplicate concurrent nested-query work or promote one receivable grammar to an all-method language.'),
('W12','Identity, revision, persistence and recovery',['W11'], 'MC04 MC05 MC25 MC27 G17 G18 I01 I04 P17-07.08 P17-08.05',
 'A stale cache survives a source revision; lost acknowledgement repeats a journal; different publication flags are copied between profiles.',
 'PublicationEffects/1 compares 1892 retained exchanges; identity successor, local process restart and immutable correction views exist.',
 'Specify migration and effect ownership across current profiles; prove replay/idempotence under real store transactions, stale views and concurrent writers with recorded fault boundaries.',
 'Audit concrete migration dependencies and query invalidation; design a bounded store-fault harness before any durability promotion.',
 'Documentary crash worlds and process exits do not establish power-loss durability; production execution stays held.'),
('W13','Numerical domains and solver certification',['W02'], 'MC18 MC26 G3 P17-08.01 P17-08.02 P17-08.03 L06',
 'A local root is reported as the unique financing solution; timeout becomes infeasibility; independent interval endpoints make an impossible book.',
 'Exact rational/affine and shared algebraic-root credit projections, boundary and residual-objective counterexamples.',
 'Define each added formula class, rounding and root semantics; return witnesses, certified infeasibility/bounds or unresolved coverage; verify financial outputs and guards against independent exact cases.',
 'Use the smallest intended mixed-sign or non-affine operation to justify the next numerical fragment; audit learned gradients/objectives before any training.',
 'Residual fit is explanatory unless the target-specific downstream criterion is met; no training authorized by this plan.'),
('W14','Matched software and executable adapters',[], 'MC23 MC25 MC31 G9 L05 L06',
 'Expected ACTUS fixture arithmetic is called ACTUS execution; package versions or publication semantics do not match.',
 'Pinned specs, dictionaries, official code blobs, adapter contracts and independent fixture arithmetic.',
 'Retain matching release/source/dependencies/licence and execute admitted exchanges with missing-input, calendar and reset cases; identify authentic replication linkage and source-version differences.',
 'Find new legitimate ACTUS core and Duarte-Fonseca package leads; compare TC-VAE published equations with retained preprint and pinned code.',
 'Unavailable code is an access residual; installations and performance campaigns need their own reviewed environment plan.'),
('W15','Primary literature, proof dependencies and competitors',[], 'MC29 MC30 G8 L04 L09',
 'A metadata hit substitutes for technical reading; a theorem is transferred without its policy or topology assumptions.',
 '27-source/claim ledger, backward/forward records, original PMCMC target proof and source-specific edition/access dispositions.',
 'For every consequential claim retain primary method/theory/appendix anchors and official code where available; fairly reproduce arguments, derive local transfers and record unsatisfied premises; disposition every remaining named competitor.',
 'Read available Benzoni/Dewatripont and adapted-topology dependencies; pursue Francis-Rowell, Gentry and Strebulaev edition gaps using new leads only.',
 'An access log is not a reading; acquired text is not blocked work; no exhaustive-literature claim follows.'),
('W16','Integrated failure and conformance cases',['W02','W03','W05','W11'], 'MC16 MC18 MC28 MC33 MC34 G5 G10 I01 I02 I03 I04 I05 I06 L03 L07',
 'Every module passes while interfaces disagree on event IDs, dates, ownership, information or completeness.',
 'Six inherited interaction rows, 67 simulation failures, later literature failures, finite I1/I2 runtime integration and E01 complete settlement paths.',
 'Map every documented failure to scoped evidence or an executable next test; exercise full original/revised/failed-prefix company paths and independent complete outputs, including unweighted and failed branches.',
 'Retain checked E01 maturity/settlement composition; next combine information revisions, conversion/control, default/guarantees and compression under explicit contracts.',
 'Unit-test count is not interaction coverage or complete-company admission; add newly discovered failures.'),
('W17','Manuscript consistency and implementation acceptance',['W07','W08','W09','W10','W11','W15','W16'], 'MC23 MC24 MC28 MC32 MC33 G10',
 'Hundreds of additive pages leave contradictory main-chapter semantics; local rendered review is called whole-document acceptance.',
 'Protected 741-page main and 183-page simulation volume; archive/latest links and scoped integration checks.',
 'Reconcile definitions and obsolete scope statements across the entire candidate; preserve equations/citations/qualifications; build both volumes, inspect changed and connected rendered pages, then obtain separate reader/domain/independent implementability evidence.',
 'Maintain companion execution notes now; integrate a coherent checked increment into a new protected successor rather than changing frozen PDFs.',
 'Human feedback is pending acceptance, not a reason to stop internal preparation; no paid engagement is authorized.'),
('W18','Target-specific evaluation and production staging',['W01','W02','W03','W04','W06','W13','W14','W16','W17'], 'MC12 MC33 MC34 MC35 G6 G10 P17-06.07 P17-08.08 L08',
 'Synthetic correctness or a clean PDF promotes a predictor/default; failed issuers and failed branches disappear from evaluation.',
 'Saved E3 target/vintage/baseline/uncertainty protocol and staged master controls.',
 'Keep S6 held and E3 deferred until their stated prerequisites are supported; later declare actual workload, fair tuned comparator ladder, target-specific training/inference budgets and uncertainty-supported downstream criteria.',
 'Continue ready design/source/conformance dependencies; do not launch forecasting, paid review or a background campaign.',
 'No default promotion, comparative performance ranking or production-readiness claim is made.'),
]
packages=[]
for id,title,deps,refs,failure,support,criterion,next_action,limit in specs:
 packages.append(dict(id=id,title=title,depends_on=deps,requirements=refs.split(),failure=failure,existing_support=support,closure_evidence=criterion,next_action=next_action,limits=limit,status='open'))
# Cross-cutting MC35 remains an internal obligation in every package. Wider
# numerical/contract residuals must not vanish behind a settlement-only route.
extra_routes={'W01':['MC35'],'W03':['MC35'],'W05':['MC35'],
 'W07':['MC35','P17-05.02'],'W11':['MC35'],'W13':['P17-05.01','P17-06.02'],
 'W14':['MC35'],'W15':['MC35'],'W16':['MC35'],'W17':['MC35']}
for p in packages:
 for requirement in extra_routes.get(p['id'],[]):
  if requirement not in p['requirements']:p['requirements'].append(requirement)
by_id={p['id']:p for p in packages}
old=json.loads(OLD.read_text())
groups={}
for group, rows in old['groups'].items():
 groups[group]=[]
 for row in rows:
  routes=[p['id'] for p in packages if row['id'] in p['requirements']]
  assert routes, row['id']
  groups[group].append({**row,'review_status':'inherited_scoped_review_with_current_delta_trace',
    'inherited_record':row,'inherited_review_source':str(OLD.relative_to(ROOT)),
    'closure_packages':routes,
    'remaining_work_and_next_action':' '.join(k+': '+by_id[k]['next_action']+' Closure: '+by_id[k]['closure_evidence'] for k in routes),
    'current_trace_status':'Not a fresh independent revalidation of every native operation',
    'full_requirement_closed':False,'acceptance':'not_promoted'})
deltas=[
 ('D01','Publication effects and identity','MC13 MC20 MC25 G18 I04 P17-07.08','profile-publication-effects-20261026','Four publication meanings and the metadata identity successor have bounded evidence; generic runtime/durability and wider migrations remain.'),
 ('D02','Conditional credit cash','MC16 MC21 G7 I05 P17-04.11 P17-06.01 P17-06.04','credit-cash-integration-20261026','Classified credit cash is no longer wholly absent: supplied origin policies now yield conditional reports. Actual policy/principal-interest facts remain.'),
 ('D03','Complete authored methods/programs','MC13 MC23 MC24 G2 G4','common-program-authoring-20261026','Complete retained definitions and programs are authored and compared; general domain algorithms and composition remain.'),
 ('D04','Opening and selected source','MC09 MC20 MC24 MC28 G1 G2','complete-claims-integration-20261026','Supplied nonempty openings and full selected programs are integrated; actual-source completeness is not admitted.'),
 ('D05','Precise information clocks','MC05 MC14 G13 G14 I02','exact-information-time-20261026','Submicrosecond supplied instants have exact projections; truth/precision of actual availability remains a source task.'),
 ('D06','Literature and finite methods','MC08 MC11 MC12 MC14 MC17 MC29 MC30 G8 G16','literature-closure-20261026','Finite compression/filtering/price-policy and I1/I2 runtime checks are delivered; general inference, mixed-state error premises and dynamic financing remain.'),
 ('D07','Unicode invariant repair','MC24 MC25 MC33 G2','invariant-unicode-rebased-20261026','Current main is 5.13 with preserved literature; generic string correctness does not establish nested financial relations.'),
 ('D08','Nested row projection','MC20 MC24 MC25 G2','nested-map-projection-20261026','44 retained projections preserve parent groups and lineage; later D10/D11 extend grouped selection and guards.'),
 ('D09','Original PMCMC proof chain','MC12 MC29 MC30 G8','literature-closure-20261026','Original PMCMC/pseudo-marginal target proof and retained-estimate counterexample are checked in pmcmc-dependency.md; quantitative SMC2 transfer is still open.'),
 ('D10','Grouped row queries','MC20 MC24 MC25 G2','grouped-row-query-20261026','606 original-dictionary comparisons preserve group identity, typed matching, greatest rows and explicit empty/ambiguous/unknown outcomes. This is not yet the complete term validator.'),
 ('D11','Guarded query composition','MC20 MC24 MC25 G2','query-guard-composition-20261026','18 truth-table cases and 108 complete comparisons are recorded by the concurrent work. Generic per-parent/per-child templates are the live next dependency.'),
 ('D12','Dated settlement reference','MC13 MC15 MC16 MC17 MC18 MC24 MC28 MC33 G4 G7 I05 I06 P17-05.01 P17-05.02','gap-program-20261026','E01 checks complete early/late-funded settlement paths and catches nonjournal memory omissions; general contractual and accounting admission remain open.'),
 ('D13','SMC2 exchange and evidence replacement','MC12 MC14 MC26 MC29 MC30 G8 G14','gap-program-20261026','E02 derives and exactly checks the auxiliary exchange ratio and corrected-evidence support restoration; static modern code agrees on the scoped retention/exchange operations, not full runtime acceptance.'),
 ('D14','Contract-specific default and remedy conditions','MC01 MC03 MC05 MC13 MC16 MC17 MC19 MC28 MC35 G4 G5 G7 I05 I06 P17-05.01 P17-05.02','gap-program-20261026','E03 preserves 20 source dependency rows and checks 58 hypothetical condition cases with 12 contrary-policy controls; actual contract admission and common-runtime integration remain open.'),
 ('D15','Concurrent complete nested semantic integration','MC20 MC24 MC25 MC28 MC33 MC34 G2 G4 I04','nested-invariant-integration-20261026','Concurrent Version 5.14 integrates the six-component semantic bundle with retained 51 comparisons/36 controls/576 assertions and 106 protected dependencies. This trace credits that scoped result, not a new re-execution; structural admission, nested source and event/carry binding remain.'),
]
delta_rows=[]
for id,title,refs,folder,judgment in deltas:
 leaf={'D09':'pmcmc-dependency.md','D12':'settlement-result.md','D13':'smc2-transfer.md','D14':'contract-conditions.md'}.get(id,'result.md')
 path=Path('data/accounting-master')/folder/leaf
 assert (ROOT/path).is_file(),path
 d=dict(id=id,title=title,requirements=refs.split(),evidence=str(path),sha256=digest(ROOT/path),current_disposition=judgment)
 delta_rows.append(d)
 for rows in groups.values():
  for r in rows:
   if r['id'] in d['requirements']:r.setdefault('successor_deltas',[]).append(id)
literature=[]
for i in range(1,10):
 id=f'L{i:02d}'
 literature.append(dict(id=id,source='data/accounting-master/literature-closure-20261026/gap-status.md',closure_packages=[p['id'] for p in packages if id in p['requirements']],status='partial; scoped results retained; broad closure open'))
failures=json.loads((ROOT/'data/accounting-master/simulation-monograph-20261026/failure-cases.json').read_text())['cases']
routes={'evidence':['W01','W16'],'history':['W02','W16'],'information':['W03','W16'],'scenario':['W03','W16'],'debt':['W05','W06','W16'],'equity':['W06','W08','W16'],'accounting':['W07','W16'],'group':['W08','W16'],'memory':['W04','W07','W09'],'compression':['W04','W16'],'approximation':['W04','W13'],'numerics':['W13'],'horizon':['W05','W06'],'evaluation':['W18'],'interaction':['W16'],'model risk':['W02','W16']}
failure_rows=[{**r,'closure_packages':routes[r['category']],'evidence_status':'Inherited documented mechanism; do not infer runtime coverage from this row'} for r in failures]
extra=[]
for line in (ROOT/'data/accounting-master/literature-closure-20261026/failure-coverage.md').read_text().splitlines():
 if not line.startswith('|') or line.startswith('|---') or 'Mechanism |' in line:continue
 cells=[x.strip() for x in line.strip('|').split('|')]
 if len(cells)==4:extra.append(dict(id=f'LIT-F{len(extra)+1:03d}',failure=cells[0],inherited_discriminating_evidence=cells[1],required_treatment=cells[2],residual=cells[3],closure_packages=['W15','W16'],status='Inherited scoped evidence; exact scope remains at original source'))
# Explicit technical ownership, in addition to literature/conformance review.
lit_routes={1:'W02',2:'W03',3:'W03',4:'W03',5:'W04',6:'W04',7:'W04',8:'W04',9:'W03 W04',10:'W02 W03',
 11:'W03',12:'W03',13:'W03 W04',14:'W01 W03 W12',15:'W03',16:'W05 W06',17:'W05 W06',18:'W06',19:'W06 W08',20:'W06 W08',
 21:'W06',22:'W06',23:'W06',24:'W03',25:'W03',26:'W03',27:'W14',28:'W14',29:'W13',30:'W13',31:'W13 W14',32:'W13',
 33:'W03 W14',34:'W13 W18',35:'W01 W18',36:'W18',37:'W03 W18',38:'W17',39:'W04',40:'W04 W13',41:'W03 W04',42:'W03 W06',
 43:'W06',44:'W06',45:'W03 W12',46:'W05',47:'W06',48:'W05'}
for i,row in enumerate(extra,1):row['closure_packages']=list(dict.fromkeys(lit_routes[i].split()+row['closure_packages']))
cross=[
 ('X01','Correction changes a previously accepted merge','W01 W03 W04 W12','Withdraw a fixed-rate fact after two periods; reopened floating type must recover earlier uncertainty without repricing settled cash.'),
 ('X02','Delayed equity misses debt maturity','W05 W06','Both branches finish with the same cash, but only on-time funding can settle the maturity on time; preserve the missed-payment event.'),
 ('X03','Accounting write-off and creditor rights','W05 W09','A lender write-off cannot silently cancel borrower face or a guarantee; require a distinct rights-changing event.'),
 ('X04','Conversion changes future policy','W06 W08','Equal current total equity with different voting rights must lead to different admitted future control policies when rights so specify.'),
 ('X05','Competing funding uses one collateral pool','W05 W06 W08','Two independently feasible facilities together exceed the same pledgeable estate; reject the joint allocation without inventing cross-entity liquidity.'),
 ('X06','Compressed rare type changes policy feasibility','W03 W04 W06','A small-probability maturity/refinancing type disappears under resampling; preserve its conditional results or a stated error and omitted mass.'),
 ('X07','Real source to synthetic complete population','W01 W02 W11','A partial claim disclosure must not inherit a synthetic whole-population completeness flag at method admission.'),
 ('X08','Unknown receipt after lost acknowledgement','W05 W12','The actor cannot spend a merely possible receipt; reconcile both storage/settlement worlds and prevent duplicate posting.'),
 ('X09','Term amendments alter historical assessment','W05 W11','Keep each old assessment tied to the applicable historical term; new due dates must not retroactively erase overdue status.'),
 ('X10','Maturity just beyond terminal horizon','W04 W05 W06','A policy shifts repayment one day beyond the report; terminal rights and feasible continuation still constrain the decision.'),
 ('X11','Off-support action changes disclosure likelihood','W03 W06 W18','Two historical fits imply different silence after a refinancing action; report identified alternatives rather than an unjustified posterior.'),
 ('X12','Different sources share one numerical symbol','W02 W08 W13','Coincidentally equal quoted rates or balances with independent origins must not become one root or one latent variable.'),
]
cross_rows=[dict(id=i,failure=f,closure_packages=p.split(),discriminating_case=c,status='design obligation; execution not inferred') for i,f,p,c in cross]
for row in cross_rows:
 if row['id']=='X02':row.update(status='bounded E01 runtime reference checked; general issuer/contract case open',evidence='data/accounting-master/gap-program-20261026/settlement-result.md')
cross_rows += [dict(id='X13',failure='Auxiliary exchange passes marginal check but changes next update',closure_packages=['W03','W15'],discriminating_case='Two-type auxiliary exchange without weights retains theta marginal 1/2 immediately, but a subsequent valid PMMH move yields 65/112; complete joint-target comparison detects it.',status='E02 exact finite counterexample checked; full inference runtime open',evidence='data/accounting-master/gap-program-20261026/smc2-transfer.md')]
cross_rows += [dict(id='X14',failure='Payment, default, remedy and legal owner collapse into one status',closure_packages=['W01','W05','W06','W07','W08','W16'],discriminating_case='Separate principal and interest duration, unknown and absent notice, 2013/2018 thresholds, declaration/automatic acceleration, cure/rescission, consent and cross-series status; do not spend consolidated cash as a legal-issuer balance.',status='E03 source-linked conditional reference checked; operative terms, actual events and typed-runtime composition remain open',evidence='data/accounting-master/gap-program-20261026/contract-conditions.md')]
paths=[OLD,ROOT/'data/accounting-master/simulation-monograph-20261026/failure-cases.json',ROOT/'data/accounting-master/literature-closure-20261026/failure-coverage.md',ROOT/'data/accounting-master/literature-closure-20261026/gap-status.md']+[ROOT/d['evidence'] for d in delta_rows]
save('trace-source-lock.json',{'files':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in dict.fromkeys(paths)]})
save('closure-packages.json',{'date':'2026-10-26','packages':packages,'scope':'Known gaps and new interface challenges; not exhaustive; no production promotion'})
save('audit-status.json',{'baseline':'Entry manuscript 5.13; concurrent current manuscript 5.14; inherited all-row assessment 4.40 explicitly retained','judgment':'Trace reconciliation, not independent acceptance','groups':groups,'literature':literature,'successor_deltas':delta_rows,'reviewed_counts':{k:len(v) for k,v in groups.items()},'protected_original_counts':{'obligations':53,'interactions':6,'operations':46}})
save('failure-register.json',{'original':failure_rows,'literature_extensions':extra,'cross_interface':cross_rows,'scope':'Overlapping mechanisms retained with provenance; counts do not measure test coverage'})
lines=['# Current gap closure program','', '26 October 2026. This program preserves all 35 mission requirements, 18 original gaps, six interactions, 46 operations, nine literature gaps and the simulation failure records. The old 105-row review is inherited evidence; the successor map explicitly records later work. It does not reclassify every old operation as newly audited or closed.','', '## Order and interpretation','', 'W01, W03, W05, W11, W14 and W15 have ready independent work. Other packages can perform local synthetic/design work while their actual-source or integration prerequisites remain open. Dependencies are promotion prerequisites, not blanket reasons to stop all internal preparation. E01, E02 and E03 are now checked within their recorded scope. W11 retains the live term-structural-admission work after the concurrent Version 5.14 integration, without competing edits. W18 remains deferred.','', '| Package | Depends on | Next discriminating action |','|---|---|---|']
for p in packages:lines.append('| '+p['id']+' — '+p['title']+' | '+(', '.join(p['depends_on']) or 'Ready')+' | '+p['next_action']+' |')
for p in packages:
 lines += ['', '## '+p['id']+' — '+p['title'], '', '**Requirements:** '+', '.join(p['requirements'])+'.', '', p['failure'], '', '**Existing work:** '+p['existing_support'], '', '**Closure evidence:** '+p['closure_evidence'], '', '**Next:** '+p['next_action'], '', '**Limits:** '+p['limits']]
lines += ['', '## Reconciled successor evidence', '']
for d in delta_rows:lines += ['- '+d['id']+': '+d['current_disposition']+' Evidence: `'+d['evidence']+'`.']
lines += ['', '## Cross-interface challenges', '']
for r in cross_rows:lines += ['- '+r['id']+' ('+', '.join(r['closure_packages'])+'): '+r['discriminating_case']]
(OUT/'closure-program.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'obligations':53,'interactions':6,'operations':46,'literature':len(literature),'packages':len(packages),'original_failures':len(failure_rows),'literature_extensions':len(extra),'cross_interface':len(cross_rows)}))
