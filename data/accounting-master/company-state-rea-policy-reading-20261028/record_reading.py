"""One-shot retention of the completed primary reading and live ledger changes."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RESEARCH = ROOT / 'docs/design/research/company-state-program-20261028'
BACKUP = OUT / 'ledgers-before'
if BACKUP.exists():
    raise SystemExit('one-shot script: backup already exists')
BACKUP.mkdir()
SID = 'N-GEERTS-MCCARTHY-POLICY'
def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + chr(10))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def relative(path):
    return str(path.relative_to(ROOT))

source = {
    'id': SID, 'title': 'Geerts and McCarthy (2006), Policy-Level Specifications in REA Enterprise Information Systems',
    'doi': '10.2308/jis.2006.20.2.37',
    'path': relative(OUT / 'sources/geerts-mccarthy-2006.pdf'),
    'sha256': sha(OUT / 'sources/geerts-mccarthy-2006.pdf'),
    'retrieval_url': 'https://www.williamemccarthy.com/s/Policy-level-Specifications-in-REA-Enterprise-Information-Systems_2006.pdf',
    'physical_pages': 27, 'print_page_rule': 'physical+36',
    'full_text_status': 'retained author-hosted published article',
    'reading_status': 'complete technical text, examples, footnotes and references read',
    'inspected': 'Sections I-V, Figures 1-18 with descriptions, Tables 1-2; all six footnotes and references; no separate appendix',
    'visually_inspected_physical_pages': [3,9,10,13,14,16,18,20,21,22,23,24,25,26],
    'classification': 'DIRECT_METHOD',
    'scope': 'Conceptual policy distinctions and type/group relations; not behavioral or legal commitment execution',
    'publication_integrity': 'Crossref identity and pagination agree; no returned update relation; bounded eight-result correction query finds no relevant notice; OpenAlex is_retracted=false. Not exhaustive.',
    'allowed_claims': 'Separate derivations, constraints and targets; typification versus membership; explicitly heuristic/nonexhaustive patterns; procedural budget grouping.',
    'forbidden_claims': 'Complete simulator, legal enforceability, admitted actor information, behavioral prediction, empirical superiority or universal aggregation sufficiency.',
    'official_code': 'Article and retained author-page links inspected; REACH publication lead, no source repository audited. No implementation imported.',
    'next_action': 'Inspect commitment/extended ontology, direct automation and empirical/database competitors; bind policy effects separately to native owners.',
    'continuation_note': 'docs/design/research/company-state-program-20261028/rea-policy-and-state.md'
}
dump(OUT / 'source.json', source)
queries = [
    ('geerts-mccarthy-2006.pdf', source['retrieval_url'], 'author-hosted complete primary text'),
    ('crossref-title-search.json', 'https://api.crossref.org/works?' + urlencode({'query.title':'Policy-Level Specifications in REA Enterprise Information Systems','rows':3}), 'identity and direct automation lead'),
    ('crossref-correction-search.json', 'https://api.crossref.org/works?' + urlencode({'query.bibliographic':'Geerts McCarthy Policy-Level Specifications REA correction erratum','rows':8}), 'bounded correction search'),
    ('openalex-work.json', 'https://api.openalex.org/works/https://doi.org/10.2308/jis.2006.20.2.37', 'dated metadata'),
    ('forward-cited.json', 'https://api.openalex.org/works?' + urlencode({'filter':'cites:W2069101183','per-page':5,'sort':'cited_by_count:desc'}), 'bounded forward leads'),
    ('forward-recent.json', 'https://api.openalex.org/works?' + urlencode({'filter':'cites:W2069101183','per-page':5,'sort':'publication_date:desc'}), 'bounded forward leads')
]
dump(OUT / 'query-log.json', {'date':'2026-10-28','successful':[{'path':relative(OUT/'sources'/f),'url':u,'purpose':p,'sha256':sha(OUT/'sources'/f)} for f,u,p in queries], 'failed':[{'tool':'web.run','result':'empty body; no source evidence'},{'tool':'curl initial title query','result':'title split by shell argument parsing; unrelated output and hostname failures; excluded; quoted retry retained'}]})
ledgers = {}
for name in ['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omitted-paper-risk']:
    path = RESEARCH / (name+'.json')
    (BACKUP/path.name).write_bytes(path.read_bytes())
    ledgers[name] = json.loads(path.read_text())
ledgers['source-support']['sources'].append(source)
ledgers['citation-venue']['rows'].append({'id':SID,'citation_count':88,'citation_source':'OpenAlex W2069101183 retained record','access_date':'2026-10-28','venue':'Journal of Information Systems','venue_metric':None,'venue_metric_source':'not obtained; not acceptance evidence','note':'Citing-work query returns 87. Counts are visibility diagnostics only.'})
for title, action in [
    ('Geerts/McCarthy2000, The ontological foundation of REA enterprise information systems','Inspect full commitment and primitive semantics; reconcile with later published article'),
    ('Motschnig-Pitrik/Storey1995, Modeling of set membership: The notion and issues','Inspect heterogeneous groups and membership theory'),
    ('Rockwell/McCarthy1999, REACH: Automated database design','Inspect method and original implementation before adoption'),
    ('Clancey1985, Heuristic classification','Compare heuristic match to inference semantics'),
    ('Fowler1997; Hay1996; Scheer1998; Silverston2001, conceptual/data model patterns','Competing pattern construction and bill-of-materials variants'),
    ('Dunn/Cherrington/Hollander2005, Enterprise Information Systems','Compare integrated enterprise applications'),
    ('McCarthy1982, REA accounting model','Reuse retained full technical reading; do not repeat'),
]:
    ledgers['backward-snowball']['rows'].append({'seed':SID,'anchor':'printed62-63 references; technical citations in38-61','candidate':title,'classification':'FOUNDATIONAL','action':action,'status':'existing_primary_reading' if title.startswith('McCarthy1982') else 'lead_not_technical_support'})
for filename, order in [('forward-cited.json','cited_by_count:desc'),('forward-recent.json','publication_date:desc')]:
    for x in json.loads((OUT/'sources'/filename).read_text())['results']:
        ledgers['forward-snowball']['rows'].append({'seed':SID,'source_file':relative(OUT/'sources'/filename),'query_order':order,'openalex_id':x['id'],'title':x['title'],'date':x.get('publication_date'),'citation_count':x.get('cited_by_count'),'doi':x.get('doi'),'classification':'COMPETITOR' if any(s in x['title'] for s in ['Claims, Debt','ORSO','REA, Triple']) else 'BACKGROUND','disposition':'Inspect technical relevance before using any claim; not read','screening_level':'title/metadata only','version_status':'not checked'})
ledgers['forward-snowball']['rows'].append({'seed':SID,'source_file':relative(OUT/'sources/crossref-title-search.json'),'title':'Sedbrook/Newmark2008, Automating REA Policy Level Specifications with Semantic Web Technologies','doi':'10.2308/jis.2008.22.2.249','classification':'DIRECT_METHOD','disposition':'Direct implementation comparison; retrieve and inspect full method and software','screening_level':'title metadata; citation linkage not independently checked','version_status':'not checked'})
for ident, claim, anchor, limits, kind in [
    ('REA-POLICY-EFFECTS','Derivable information, validation rules and targets have distinct meanings.','39-40,48,54-62','No decision rule or behavioral prediction follows.','PRIMARY_TECHNICAL_SUPPORT'),
    ('REA-POLICY-MEMBERSHIP','Type definitions and collections differ; membership is not automatically transitive.','41-46,Table1,Figures2-6','Mass-item aggregation is a compromise, not a universal sufficient statistic.','PRIMARY_TECHNICAL_SUPPORT'),
    ('REA-POLICY-LIMITS','The five patterns are heuristic and nonexhaustive.','52,Figure10','Heterogeneous groups are explicitly omitted.','PRIMARY_TECHNICAL_SUPPORT'),
    ('REA-POLICY-NATIVE','Native settlement generation, rule validation and target comparison must retain different effects.','rea-policy-and-state.md; company-policy-20261023/policy.py','Local design consequence; broader implementation and actor admission remain open.','PROJECT_DERIVATION')
]:
    ledgers['claim-support']['rows'].append({'id':ident,'source_id':SID,'claim':claim,'anchor':anchor,'limits':limits,'support_class':kind})
for row in ledgers['omitted-paper-risk']['rows']:
    if row.get('id')=='OR-REA-EXTENSIONS':
        row['previous_disposition']=row['disposition']
        row['disposition']='Geerts/McCarthy2006 fully read in current continuation; extended ontology/commitments and2019 monograph remain uninspected.'
ledgers['omitted-paper-risk']['rows'].extend([
    {'id':'OR-REA-AUTOMATION','candidate':'Sedbrook/Newmark2008 automation; Rockwell/McCarthy1999 REACH','reason':'Conceptual patterns do not establish executable rule semantics or implementation quality.','disposition':'primary method/code reading required; no software adopted','task':'S01','acceptable_for_final_survey':False},
    {'id':'OR-REA-GROUPING','candidate':'Motschnig-Pitrik/Storey1995 membership theory','reason':'2006 patterns explicitly omit heterogeneous grouping; general inference across membership links unsupported.','disposition':'technical reading required for broader grouping support','task':'S01','acceptable_for_final_survey':False}
])
for name, obj in ledgers.items():
    dump(RESEARCH/(name+'.json'), obj)
files = [p for p in OUT.rglob('*') if p.is_file() and 'ledgers-before' not in p.parts]
dump(OUT/'manifest.json', {'date':'2026-10-28','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/company-state-rea-policy-reading-20261028.md','result':relative(OUT/'result.md'),'environment':platform.python_version(),'cpu_gpu':'CPU-only document retrieval/rendering; no GPU framework imported','seeds':'N/A: deterministic document reading','wall_time':'Interactive reading; no comparative runtime claim','commands':['bounded curl source and metadata retrievals recorded in query-log.json','pdftotext -layout source.pdf source.txt','PyMuPDF/PIL rendering of fourteen specified pages','python3 -B '+relative(Path(__file__))],'files':[{'path':relative(p),'sha256':sha(p)} for p in files]})
print(json.dumps({'recorded':SID,'ledgers':{n:len(x.get('rows',x.get('sources',[]))) for n,x in ledgers.items()}}))
