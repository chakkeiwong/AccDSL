"""One-shot record of inspected source/version limits and remaining critiques."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
RESEARCH=ROOT/'docs/design/research/company-state-program-20261028'
backup=OUT/'ledgers-before'
if backup.exists():raise SystemExit('one-shot backup exists')
backup.mkdir()
SID='N-GEERTS-MCCARTHY-ONTOLOGY'
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+chr(10))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
source=dict(id=SID,title='Geerts/McCarthy, An ontological analysis of the economic primitives of the extended-REA enterprise information architecture',
    doi='10.1016/S1467-0895(01)00020-3',path=rel(OUT/'sources/extended-rea.pdf'),sha256=sha(OUT/'sources/extended-rea.pdf'),
    retrieval_url='https://www.williamemccarthy.com/s/An-Ontological-Analysis-of-the-Primitives-of-the-Extended_REA-Enterprise-Information-Architecture.pdf',
    physical_pages=19,classification='DIRECT_METHOD',full_text_status='retained author-hosted manuscript',
    reading_status='full primary author version inspected',
    inspected='All19 physical pages; Sections1-5; two footnotes; references; six figures; no separate appendix',
    visually_inspected_physical_pages=[1,7,8,11,14,15,16,17,18,19],
    version_status='Title/authors match published2002 metadata; author version19 pages versus published1-16. Exact textual equivalence not checked. Use physical manuscript anchors.',
    scope='Conceptual commitments/events/relationships and explicitly preliminary ontology; no executable lifecycle',
    publication_integrity='No returned Crossref update relation; bounded correction query finds no relevant notice; OpenAlex is_retracted=false. Direct published discussion remains unread.',
    allowed_claims='Section4.1 commitment/event distinction; Section4.2 Executes/Involvement/Reserved/Reciprocal relations; Section4.3 contracting/scheduling; Section5 procedural incompleteness.',
    forbidden_claims='Complete company ontology, empirical superiority, legal recognition/enforceability, general simulator, published-version equivalence or resolved critique.',
    official_code='No implementation imported. Primary manuscript references prior implementations; none audited here.',
    next_action='Inspect Lampe2002 discussion and Geerts/McCarthy2000 foundation; specify local commitment lifecycle before operations.',
    continuation_note='docs/design/research/company-state-program-20261028/rea-commitments-and-events.md')
dump(OUT/'source.json',source)
queries=[
 ('extended-rea.pdf',source['retrieval_url'],'200'),
 ('crossref-doi.json','https://api.crossref.org/works/10.1016/s1467-0895(01)00020-3','200'),
 ('crossref-correction.json','https://api.crossref.org/works?'+urlencode({'query.bibliographic':'Geerts McCarthy ontological analysis economic primitives extended REA correction erratum','rows':8}),'200'),
 ('openalex-work.json','https://api.openalex.org/works/https://doi.org/10.1016/s1467-0895(01)00020-3','200'),
 ('discussion-crossref.json','https://api.crossref.org/works/10.1016/s1467-0895(01)00021-5','200'),
 ('discussion-openalex.json','https://api.openalex.org/works/https://doi.org/10.1016/s1467-0895(01)00021-5','200'),
 ('discussion-repository.html','https://bearworks.missouristate.edu/articles-cob/119','200; metadata only'),
 ('discussion-publisher-response.txt','https://api.elsevier.com/content/article/PII:S1467089501000215?httpAccept=text/plain','400; invalid view, no full text'),
 ('discussion-publisher-full.xml','https://api.elsevier.com/content/article/PII:S1467089501000215?view=FULL&httpAccept=text/xml','401; no full text')]
for file,order in [('forward-cited.json','cited_by_count:desc'),('forward-recent.json','publication_date:desc')]:
 queries.append((file,'https://api.openalex.org/works?'+urlencode({'filter':'cites:W2048732161','per-page':5,'sort':order}),'200; metadata sample'))
dump(OUT/'query-log.json',dict(date='2026-10-28',queries=[dict(path=rel(OUT/'sources'/f),url=u,result=s,sha256=sha(OUT/'sources'/f)) for f,u,s in queries],web_search='empty built-in result; no source or negative finding'))
ledgers={}
for name in ['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omitted-paper-risk']:
 p=RESEARCH/(name+'.json');(backup/p.name).write_bytes(p.read_bytes());ledgers[name]=json.loads(p.read_text())
ledgers['source-support']['sources'].append(source)
ledgers['citation-venue']['rows'].append(dict(id=SID,citation_count=295,citation_source='OpenAlex W2048732161 retained record',access_date='2026-10-28',venue='International Journal of Accounting Information Systems',venue_metric=None,venue_metric_source='not obtained; not acceptance criterion',note='295 citing-work query results; ten sampled rows, editions may duplicate.'))
for candidate,action in [
 ('Geerts/McCarthy2000b, The ontological foundation of REA enterprise information systems','Priority: detailed commitment and full-REA definitions'),
 ('Geerts/McCarthy2000a, Augmented intensional reasoning in knowledge-based accounting systems','Inspect procedural axioms and limits before implementation'),
 ('Wand/Weber1990; Weber1997; Bunge1977 ontology','Direct alternative representational assumptions; technical comparison required'),
 ('Sowa1999, Knowledge Representation','Inspect primary categorical argument before importing any completeness claim'),
 ('Geerts/McCarthy1997a/1997b/1999 business processes and tasks','Workflow and value-chain extensions excluded from present analysis'),
 ('Cherrington et al1993, Event-driven business solutions: Implementation experiences and issues','Find full implementation/evaluation evidence')]:
 ledgers['backward-snowball']['rows'].append(dict(seed=SID,anchor='physical pages4,9-13; Sections2.2/4.3/5 and references',candidate=candidate,classification='COMPETITOR' if candidate.startswith('Wand') else 'FOUNDATIONAL',action=action,status='lead_not_technical_support'))
for file,order in [('forward-cited.json','cited_by_count:desc'),('forward-recent.json','publication_date:desc')]:
 for x in json.loads((OUT/'sources'/file).read_text())['results']:
  ledgers['forward-snowball']['rows'].append(dict(seed=SID,source_file=rel(OUT/'sources'/file),query_order=order,openalex_id=x['id'],title=x['title'],date=x.get('publication_date'),citation_count=x.get('cited_by_count'),doi=x.get('doi'),classification='COMPETITOR' if 'Flow Accounting' in x['title'] else 'BACKGROUND',disposition='Title screening only; compare exact versions and technical relevance before use',screening_level='title/metadata only',version_status='not checked'))
ledgers['forward-snowball']['rows'].append(dict(seed=SID,title='Lampe2002, Discussion of an ontological analysis of the economic primitives of the extended-REA enterprise information architecture',doi='10.1016/S1467-0895(01)00021-5',source_file=rel(OUT/'sources/discussion-crossref.json'),classification='CRITICAL_RESPONSE',screening_level='metadata and access paths only',disposition='Priority technical reading; current publisher/repository routes provide no full text; criticism not inferred'))
for ident,claim,anchor,limits,kind in [
 ('REA-COMMITMENT-EVENT','Commitments represent obligations to partners rather than completed acquisition/consumption events.','Section4.1 physical7','Enforceability varies; no local legal/accounting recognition supplied.','PRIMARY_TECHNICAL_SUPPORT'),
 ('REA-COMMITMENT-RELATIONS','Commitments link to events, agents, resources and reciprocal commitments; contracting/scheduling bundle them.','Section4.2 physical8; Section4.3 physical9-10; Figure4 physical17','No complete fulfillment/amendment/cancellation algorithm.','PRIMARY_TECHNICAL_SUPPORT'),
 ('REA-ONTOLOGY-LIMITS','Task components are excluded and procedural accounting axioms require further development.','Section2.2 physical4; Section5 physical11','No completeness or empirical superiority claim adopted.','PRIMARY_TECHNICAL_SUPPORT'),
 ('REA-NATIVE-COMMITMENT-GAP','Native trade claims and policy-generated collections do not supply commitment identities, reservation or lifecycle operations.','rea-commitments-and-events.md; CompanyOperationPathDraft/1 schema','Local source/code comparison, not implementation or standards conclusion.','PROJECT_DERIVATION')]:
 ledgers['claim-support']['rows'].append(dict(id=ident,source_id=SID,claim=claim,anchor=anchor,limits=limits,support_class=kind))
for row in ledgers['omitted-paper-risk']['rows']:
 if row.get('id')=='OR-REA-EXTENSIONS':
  row['disposition']='2006 policy article and19-page author version of2002 extended-primitives analysis read; detailed2000 foundation,2019 monograph and2002 critical discussion remain open.'
ledgers['omitted-paper-risk']['rows'].extend([
 dict(id='OR-REA-LAMPE',candidate='Lampe2002 direct published discussion',reason='Direct critical response cannot be inferred from metadata; full text not yet recovered.',disposition='publisher400 corrected to401; repository metadata only; investigate other legal access routes; no paid/outreach authorization',task='S01',acceptable_for_final_survey=False),
 dict(id='OR-REA-VERSION',candidate='Published2002 version versus retained author manuscript',reason='19-page author layout differs from16-page published pagination; exact wording equivalence not checked.',disposition='Use explicit author-version anchors; obtain publisher version for comparison if available',task='S01',acceptable_for_final_survey=False)])
for n,x in ledgers.items():dump(RESEARCH/(n+'.json'),x)
inputs=[p for p in OUT.rglob('*') if p.is_file() and 'ledgers-before' not in p.parts]
dump(OUT/'manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),plan='docs/plans/company-state-rea-commitment-reading-20261028.md',result=rel(OUT/'result.md'),environment=platform.python_version(),cpu_gpu='CPU-only document reading/rendering; no GPU framework imports',random_seeds='N/A deterministic',wall_time='Interactive reading; no runtime comparison',commands=['bounded curl requests in query-log.json','pdftotext -layout source.pdf source.txt','PyMuPDF/PIL ten-page rendering','python3 -B '+rel(Path(__file__))],files=[dict(path=rel(p),sha256=sha(p)) for p in inputs]))
print(json.dumps(dict(recorded=SID,ledgers={n:len(x.get('rows',x.get('sources',[]))) for n,x in ledgers.items()})))
