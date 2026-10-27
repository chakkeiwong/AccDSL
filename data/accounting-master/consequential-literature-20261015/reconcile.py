"""Append inspected supplemental evidence; preserve every historical ledger row."""
from pathlib import Path
import json,hashlib,copy,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];R=ROOT/'docs/design/research'
def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
names=['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omissions']
D={n:json.loads((R/(n+'.json')).read_text()) for n in names}
for n in names:
 assert D[n]==json.loads((OUT/'six-ledgers-before'/(n+'.json')).read_text()),'Ledger changed; inspect before appending'
add={n:[] for n in names};pins=[]
def pin(path):
 p=ROOT/path;assert p.is_file(),path;pins.append({'path':path,'sha256':sha(p)})
def claim(identifier,text,kind,source,anchor,limit,dossier):
 add['claim-support'].append({'id':identifier,'claim':text,'class':kind,'source':source,
  'anchor':anchor,'limit':limit,'dossier':dossier,'reconciliation_date':'2026-10-15'})
for directory,key in [('tableformer-paper-20261012','nassar2022tableformer'),('otsl-paper-20261012','lysak2023otsl')]:
 dossier='data/accounting-master/'+directory
 s=read(dossier+'/source-support.json');pin(dossier+'/source-support.json');pin(dossier+'/technical-review.md')
 if key=='nassar2022tableformer':
  path=s['copies'][0]['copy'];expected=s['copies'][0]['sha256'];anchor=s['anchors'];full=s['full_text'];version=s['version_check'];year=2022
 else:path=s['local_copy'];expected=s['sha256'];anchor=s['technical_anchors'];full=s['full_text'];version=s['version_limits'];year=2023
 assert sha(ROOT/path)==expected
 add['source-support'].append({'id':key,'title':s['title'],'authors':s['authors'],'year':year,'doi':s['doi'],
  'classification':s['class'],'local_path':path,'sha256':expected,'text_path':dossier+'/sources/paper.txt',
  'full_text_status':full,'inspected_technical_anchors':anchor,'version_note':version,
  'claims_allowed':s['allowed'],'claims_forbidden':s['forbidden'],'correction_check':s['correction_check'],
  'reading_record':dossier+'/technical-review.md','reconciliation_date':'2026-10-15'})
 if key=='nassar2022tableformer':
  p=s['copies'][1];assert sha(ROOT/p['copy'])==p['sha256']
  add['source-support'].append({'id':'nassar2022tableformersupp','title':s['title']+' — Supplement','authors':s['authors'],
   'year':2022,'classification':'DIRECT_METHOD','local_path':p['copy'],'sha256':p['sha256'],
   'text_path':dossier+'/sources/supplement.txt','inspected_technical_anchors':s['anchors'][1],
   'full_text_status':'All six pages inspected in retained source-specific review',
   'claims_allowed':['Matching can change structure and text assignment under the specified steps'],
   'claims_forbidden':['Universal extraction correctness or checkpoint equivalence'],
   'correction_check':s['correction_check'],'reading_record':dossier+'/technical-review.md'})
 for c in read(dossier+'/claim-support.json'):
  claim(key+'-'+c['id']+'-reconciled',c['claim'],c.get('class',c.get('support_class')),key,c['anchor'],c['limit'],dossier)
 for n in ['backward-snowball','forward-snowball','citation-venue']:
  x=copy.deepcopy(read(dossier+'/'+n+'.json'));x['seed']=key;x['dossier']=dossier;x['reconciliation_date']='2026-10-15'
  if n=='forward-snowball' and 'follow_up' in x:
   x['follow_up']['action']='technical read delivered in otsl-paper-20261012; retained source-specific limits apply'
   x['follow_up']['full_text']='arXiv v1 inspected; published equivalence not established'
  add[n].append(x);pin(dossier+'/'+n+'.json')
 add['omissions'].append({'id':key+'-20261015-disposition','title':s['title'],'status':'TECHNICAL_READING_DELIVERED_SCOPED',
  'supersedes_current_routing':'Earlier defer/read-next rows remain historical; this row governs current reading status.',
  'reason':'Exact primary copy, method/evaluation and technical limits inspected; current manuscript includes the material result.',
  'reviewer_risk':'Systematic forward/competitor coverage and version/checkpoint equivalence remain incomplete.',
  'next_action':'Inspect source-specific remaining comparator only before transferring its method or performance claim.',
  'acceptable_for_current_claims':'Yes within stated source-specific limits; not survey completion','dossier':dossier})

proof='data/accounting-master/certain-answers-proof-source-20261013'
s=read(proof+'/source-support-supplement.json');assert sha(ROOT/s['local_path'])==s['sha256']
s['reconciliation_date']='2026-10-15';add['source-support'].append(s);pin(proof+'/source-support-supplement.json');pin(proof+'/proof-review.md')
sql='data/accounting-master/accounting-sql-three-valued-logic-20261013'
s=read(sql+'/source-support-supplement.json');assert sha(ROOT/s['source'])==s['source_sha256']
add['source-support'].append({'id':'libkin2016sql','title':s['title'],'authors':[s['author']],'year':2016,
 'doi':s['crossref_doi'],'classification':'DIRECT_METHOD','local_path':s['source'],'sha256':s['source_sha256'],
 'full_text_status':'Retained author text and relevant proof/technical sections read in source-specific review',
 'inspected_technical_anchors':s['inspected'],'version_note':s['version_limit'],
 'claims_allowed':s['claims_allowed'],'claims_forbidden':s['claims_forbidden'],
 'correction_check':s['notice_limit'],'reading_record':sql+'/technical-review.md'})
pin(sql+'/source-support-supplement.json');pin(sql+'/technical-review.md')
claim('certain-primary-proof-reconciled','Direct evaluation as a greatest lower bound requires the source domain/order/genericity/representation conditions.',
 'PRIMARY_TECHNICAL_SUPPORT','libkin2016certain','Definitions4–7, Theorem2 and proof, pp11–18',
 'Financial-language hypotheses not established; no general accounting theorem transfer',proof)
claim('certain-input-output-reconciled','The guarded relational specialization distinguishes closed-world input from open-world answers.',
 'PRIMARY_TECHNICAL_SUPPORT','libkin2016certain','Proposition9 and Corollary3, p20',
 'Input filing completeness does not follow from the output interpretation',proof)
claim('sql-sound-incomplete-reconciled','Modified three-valued relational evaluation gives sound positive/negative answers; its unknown value carries no guarantee.',
 'PRIMARY_TECHNICAL_SUPPORT','libkin2016sql','Theorem5.3 and Corollary5.4; closed-world set semantics',
 'No completeness, bag/aggregate or full financial-language guarantee',sql)
claim('sql-unknown-counterexample-reconciled','A proposition true in every completion may evaluate unknown under the modified approximation.',
 'PROJECT_DERIVATION','libkin2016sql','derivation.json; T={(1,null)} and the equality/excluded-middle query',
 'Finite local consequence of inspected rules; not a database runtime result',sql)
for key,dossier in [('libkin2016certain',proof),('libkin2016sql',sql)]:
 add['backward-snowball'].append({'seed':key,'dossier':dossier,'inspected_context':'Retained source-specific proof/technical review',
  'candidates':[],'scope_note':'No newly extracted exhaustive reference list. External preservation results and preliminary-version equivalence remain specifically uninspected; original Libkin2014 backward leads retained.'})
 add['forward-snowball'].append({'seed':'libkin2014','citing_work':key,'dossier':dossier,'date':'2026-10-15',
  'status':'Previously discovered primary follow-up now technically inspected','coverage':'Specific follow-up only; no new citing-work census or current ranking'})
 add['omissions'].append({'id':key+'-20261015-disposition','title':key,'status':'TECHNICAL_READING_DELIVERED_SCOPED',
  'reason':'Source-specific inspection now integrated into the six-ledger index; historical deferral preserved.',
  'dossier':dossier,'next_action':'Retain source hypotheses; inspect outside proof dependencies before stronger claims.',
  'acceptable_for_current_claims':'Scoped support only','reviewer_risk':'Final-publisher and preliminary-version equivalence not established.'})

# Fresh bounded notice metadata is supplemental and cannot certify absence of notices.
for name,key in [('tableformer','nassar2022tableformer'),('otsl','lysak2023otsl'),('certain','libkin2016certain'),('sql','libkin2016sql')]:
 p=OUT/'notice-checks'/f'{name}.json';m=json.loads(p.read_text())['message'];pin(str(p.relative_to(ROOT)))
 add['citation-venue'].append({'id':key,'date':'2026-10-15','source':'Crossref exact DOI record','raw_path':str(p.relative_to(ROOT)),
  'cited_by_count':m.get('is-referenced-by-count','not available'),'venue':m.get('container-title'),
  'venue_ranking':'not available','correction_relations':m.get('relation'),
  'update_to':m.get('update-to'),'updated_by':m.get('updated-by'),
  'limit':'No adverse relation field in returned metadata is not comprehensive correction clearance. Counts are dated visibility only.'})

# Root general claims remain historical; named source-specific dossiers refine them.
add['omissions'].append({'id':'consequential-coverage-20261015','title':'Remaining source and competitor scope',
 'status':'OPEN_SCOPED_SURVEY','reason':'The four original blocked sources, systematic forward coverage, external preservation theorems and uninspected actuarial competitor methods remain unresolved.',
 'next_action':'Use the explicit claim/competitor reconciliation and R05 comparator protocol; no unchanged retries of blocked originals.',
 'acceptable_for_current_claims':'Only the scoped current claims; no survey-completeness, novelty or performance advantage claim.'})
before={n:len(D[n]['records']) for n in names}
for n in names:
 D[n]['records'].extend(add[n]);D[n].setdefault('supplement_updates',[]).append({'date':'2026-10-15',
  'dossier':str(OUT.relative_to(ROOT)),'historical_date_preserved':D[n]['date'],'purpose':'Integrate already-inspected source-specific repairs; preserve historical rows and exact limits'})
 write(R/(n+'.json'),D[n])
 baseline=json.loads((OUT/'six-ledgers-before'/(n+'.json')).read_text())
 assert D[n]['records'][:before[n]]==baseline['records']
write(OUT/'ledger-reconciliation.json',{'before':before,'added':{n:len(add[n]) for n in names},
 'after':{n:len(D[n]['records']) for n in names},'dossier_pins':pins,'original_rows_preserved':True,
 'historical_dates_preserved':True,'not_claimed':['complete scholarly survey','new technical reading of all cited papers','new performance ranking']})
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
print(json.dumps({'added':{n:len(add[n]) for n in names},'index_preserved':True,'original_rows_preserved':True}))
