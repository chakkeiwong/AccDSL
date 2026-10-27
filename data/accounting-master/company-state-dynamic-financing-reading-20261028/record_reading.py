"""One-shot scoped reading record; retain earlier ledgers and task criteria."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
R=ROOT/'docs/design/research/company-state-program-20261028'
SID='N-STREBULAEV-WHITED-FINANCING'
def rel(p): return str(p.relative_to(ROOT))
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+chr(10))
source_path=ROOT/'docs/papers/Dynamic Models and Structural Estimation in Corporate Finance Strebulaev (2012).pdf'
assert sha(source_path)=='3ea7578f4e007d768f1b1570cc29457b8f54428a9dcc3b063fe454286e82dbaf'
assert json.loads((HERE/'convention-attempt-01/verification.json').read_text())['passed']
backup=HERE/'ledgers-before';backup.mkdir(exist_ok=False)
source=dict(id=SID,title='Strebulaev and Whited (2012), Dynamic Models and Structural Estimation in Corporate Finance',
 doi='10.1561/0500000035',path=rel(source_path),sha256=sha(source_path),classification='SURVEY_OR_TUTORIAL',
 full_text_status='Retained December2012 version;159 physical pages',reading_status='Scoped technical reading; not full-book/appendix closure',
 inspected='Physical69–98 sections3.1–3.6;106–114 section4.2 and transition; relevant references125–134',
 visually_inspected_physical_pages=[80,81,85,88,89,95,107,108,110],equation_anchors=['3.13–3.15','3.17','3.20–3.22','3.25','4.4'],
 earlier_scope='Section3.6 and Maliar comparison retained26October; not counted again',
 publication_integrity='Bounded8-result correction query has no explicit relevant notice; latest/published equivalence unresolved; publisher403',
 local_equation_import_status='Quarantined literal3.14/3.15 and unchanged-profit3.21/3.25; diagnostic discussion only pending resolution',
 allowed_claims='Inspected reduced-state assumptions and explicit local convention/identification deductions',
 forbidden_claims='Primary cited-paper theorems, full accounting state, latest-version clearance, author-code correctness, predictive superiority',
 official_code='Not located or audited; no implementation imported',continuation_note=rel(R/'dynamic-financing-and-state.md'))
dump(HERE/'source.json',source)
ledgers={}
for n in ['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omitted-paper-risk','search-log']:
 p=R/(n+'.json');(backup/p.name).write_bytes(p.read_bytes());ledgers[n]=json.loads(p.read_text())
assert not any(x['id']==SID for x in ledgers['source-support']['sources'])
ledgers['source-support']['sources'].append(source)
ledgers['citation-venue']['rows'].append(dict(id=SID,citation_count=263,citation_source='Retained OpenAlex W3125404141',access_date='2026-10-26',
 venue='Foundations and Trends in Finance',venue_metric=None,venue_metric_source='Not obtained; not acceptance evidence',
 note='Dated prior count, not current.28October citing-work queries return262 matches; not reconciled or exhaustive.'))
back=[('Gomes2001, Financing Investment','3.2','Equilibrium, constraints and evaluation'),
 ('Altinkilic/Hansen2000, Are There Economies of Scale in Underwriting Fees?','3.2','Empirical fixed/proportional fees'),
 ('Fazzari/Hubbard/Petersen1988, Financing Constraints and Corporate Investment','3.2','Investment/cash-flow discriminator'),
 ('Alti2003; Cooper/Ejarque2003','3.2','Competing correlation explanations'),
 ('Riddick/Whited2009, The Corporate Propensity to Save','3.3','Cash model, identification, estimation and appendices'),
 ('Bolton/Chen/Wang2011, A Unified Theory of Tobins q, Corporate Investment, Financing, and Risk Management','3.3','Continuous-time cash boundary conditions'),
 ('Hennessy/Whited2005, Debt Dynamics','3.4','Taxes, collateral, fire sales and implementation'),
 ('Hennessy/Whited2007, How Costly Is External Financing? Evidence from a Structural Estimation','3.4/4.2','Identification, estimation, uncertainty and code'),
 ('DeAngelo/DeAngelo/Whited2011, Capital Structure Dynamics and Transitory Debt','3.4','Transitory versus persistent leverage'),
 ('Gamba/Triantis2008, The Value of Financial Flexibility','3.5','Simultaneous cash/debt, transaction costs and appendices'),
 ('Moyen2004, Investment-Cash Flow Sensitivities: Constrained versus Unconstrained Firms','3.6','Risky-debt pricing and constraints'),
 ('Titman/Tsyplakov2007; Tsyplakov2008','3.6','Maturity, dilution, issuance and equilibrium debt pricing')]
for title,anchor,action in back:
 ledgers['backward-snowball']['rows'].append(dict(seed=SID,candidate=title,anchor=anchor,classification='DIRECT_METHOD',action='Read primary '+action,status='lead_not_technical_support'))
for f,order in [('forward-cited.json','cited_by_count:desc'),('forward-recent.json','publication_date:desc')]:
 d=json.loads((HERE/'sources'/f).read_text())
 for x in d['results']:
  ledgers['forward-snowball']['rows'].append(dict(seed=SID,source_file=rel(HERE/'sources'/f),query_date='2026-10-28',query_order=order,
   matched_population=d['meta']['count'],openalex_id=x['id'],title=x['title'],doi=x.get('doi'),date=x.get('publication_date'),citation_count=x.get('cited_by_count'),
   classification='COMPETITOR',screening_level='Title/metadata only',disposition='Inspect technical relevance, versions and evaluation; no result adopted'))
ledgers['forward-snowball']['rows'].append(dict(seed=SID,title='Dynamic Corporate Finance is Useful: A Comment on Welch (2013)',doi='10.1561/104.000000011',
 source_file=rel(HERE/'sources/correction-crossref.json'),classification='COMPETITOR',screening_level='Title metadata; citation link not established',disposition='Read original criticism and response together'))
claims=[('FINANCING-STATE-DISTINCTIONS','Reduced models distinguish capital, cash, debt and productivity under different assumptions.','3.1–3.5','No whole-company sufficiency.','PRIMARY_TECHNICAL_SUPPORT'),
 ('FINANCING-FIXED-COST-SIGN','Literal3.14/3.15 differs by2 eta0 from positive fixed/proportional-cost shareholder cash.','printed77–78;convention-attempt-01','Affected formula withheld; author code/other edition unchecked.','PROJECT_DERIVATION'),
 ('FINANCING-TAX-SHIELD','Substitution b=-p retains tau delta k, absent in3.21/3.25.','printed82,86,92;convention-attempt-01','Conditional on unchanged profit/depreciation definitions.','PROJECT_DERIVATION'),
 ('FINANCING-IDENTIFICATION','Independent linear relations invert; dependent moments or equal delta+phi need not separate parameters.','4.2.2;4.4;convention-attempt-01','Local algebra, not empirical identification.','PROJECT_DERIVATION'),
 ('FINANCING-NATIVE-SEPARATION','Dated contracts, accounting memory, behavior and information require explicit joins.','dynamic-financing-and-state.md;funding-case result','Design consequence, not simulator completion.','PROJECT_DERIVATION')]
for ident,claim,anchor,limits,kind in claims:
 ledgers['claim-support']['rows'].append(dict(id=ident,source_id=SID,claim=claim,anchor=anchor,limits=limits,support_class=kind))
for ident,candidate,reason,action in [
 ('OR-FINANCING-PRIMARY','Gamba/Triantis;Hennessy/Whited;DeAngelo et al.;Riddick/Whited;Bolton et al.','Survey does not replace primary method/appendix/evaluation/code.','Technical reading required; Gamba routes currently unresolved'),
 ('OR-FINANCING-VERSION','Strebulaev/Whited versions/corrections/code','Retained fixed-cost and tax-shield conventions mismatch.','Resolve definitions before direct import'),
 ('OR-FINANCING-MATURITY','Moyen;Titman/Tsyplakov;Tsyplakov;later default/liquidity/dilution work','Risk-free one-period balances omit these mechanisms.','Inspect direct competitors and forward leads')]:
 ledgers['omitted-paper-risk']['rows'].append(dict(id=ident,candidate=candidate,reason=reason,disposition=action,task='S06',acceptable_for_final_survey=False))
ledgers['search-log']['rows'].append(dict(date='2026-10-28',task='S06',provider='Built-in web;Crossref;OpenAlex;publisher/university public pages',
 queries=['Strebulaev Whited corrections','Gamba Triantis financial flexibility','Hennessy Whited debt dynamics','OpenAlex cites W3125404141 top5/recent5'],
 outcome='Two fresh web batches empty; Crossref8/title3 and OpenAlex two5-item samples succeed. Emerald403; Gamba404/stream/reset failures. No absence or unread-result inference.',evidence=rel(HERE/'query-log.json')))
for n,d in ledgers.items():dump(R/(n+'.json'),d)
dump(HERE/'query-log.json',dict(date='2026-10-28',sources=[dict(path=rel(p),sha256=sha(p)) for p in sorted((HERE/'sources').iterdir()) if p.is_file()],
 failed_discovery=['Two additional web batches returned no usable content','Emerald403','Gamba current Warwick guessed route404; former UMD author route404','Old Warwick metadata URL:curl92; trusted HTTP1.1 retry:curl56'],scope='Bounded discovery; no exhaustive correction or latest-version claim'))
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program);dump(HERE/'program-before.json',old)
t=next(x for x in program['tasks'] if x['id']=='S06');assert t['status']=='planned'
t['status']='in_progress';t['evidence'].extend([rel(HERE/'result.md'),source['continuation_note'],rel(HERE/'convention-attempt-01/verification.json')])
t['next_action']='Reuse26October3.6/Maliar and current3.1–3.5/4.2 review. Inspect direct primary cash/debt, capital-structure and maturity competitors; resolve conventions/official code before import.'
t['remaining']=['Primary competitor methods/theory/relevant appendices and empirical identification/evaluation','Edition/correction/code checks; affected literal equations withheld','Risky maturity/recovery/dilution and accounting-state comparison','Critical/backward/forward synthesis; metadata samples do not close coverage']
for a,b in zip(old['tasks'],program['tasks']):
 for k in ['id','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
 if a['id']!='S06':assert a==b
dump(p,program)
entry='''
## Financing survey and plan repair — 28 October 2026

S06 is now in_progress. Its stale request to repeat section3.6/Maliar work
is replaced with direct primary financing/maturity comparisons and version/
code checks. The new reading covers reduced investment, cash, debt and
identification models. Twenty exact checks establish two conditional source
equation mismatches; affected formulas are withheld from direct import.
Result: data/accounting-master/company-state-dynamic-financing-reading-20261028/result.md.

All40 task criteria/dependencies persist. S06 is not complete; no financing
default or empirical forecast is promoted. Main review remains288/831;
resume289. Fifteen original failure rows are reviewed,186 outside this pass.
Selected5.55-R1 and unselected5.56-D1 remain not_ready; E3 remains deferred.

'''
for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for n,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/n;d=json.loads(p.read_text());d[key]['financing_survey_20261028']=dict(result=rel(HERE/'result.md'),task='S06',status='in_progress',exact_checks=20,scope='No literal formula import; primary/version/code work remains');dump(p,d)
files=[p for p in HERE.rglob('*') if p.is_file() and 'ledgers-before' not in p.parts and p.name!='manifest.json']
dump(HERE/'manifest.json',dict(date='2026-10-28',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),plan='docs/plans/company-state-dynamic-financing-reading-20261028.md',result=rel(HERE/'result.md'),cpu_gpu='CPU-only; no accelerator imports',seeds='N/A deterministic',wall_time='Interactive reading; no runtime comparison',files=[dict(path=rel(p),sha256=sha(p)) for p in files]+[dict(path=rel(R/'dynamic-financing-and-state.md'),sha256=sha(R/'dynamic-financing-and-state.md'))]))
print(json.dumps(dict(task='S06',status='in_progress',checks=20,original_criteria_preserved=True)))

