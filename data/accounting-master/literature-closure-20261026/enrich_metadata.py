"""Enrich checked identities from retained responses, not metadata relevance guesses."""
from pathlib import Path
import json, hashlib, re
p=Path(__file__).resolve().parent
root=p.parents[2]
def read(f):
    try:return json.loads(f.read_text())
    except (ValueError,FileNotFoundError):return None
def dump(name,obj):(p/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+chr(10))
def norm(s):return re.sub(r'[^a-z0-9]','',s.lower())
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
source=read(p/'source-support.json')
extras={'epstein':'10.1111/j.1467-937X.2007.00464.x','maliar':'10.1016/j.jmoneco.2021.07.004','duarte':'10.3386/w35283','strebulaev':'10.1561/0500000035','gneiting':'10.1198/016214506000001437','pflug':'10.1137/110825054','mccarthy':'10.2308/tar-4487748','pichler-shapiro-foundations':'10.1137/21m1390517'}
# Build a DOI-indexed set of actually retained Crossref records.
cr={}
for directory in [p/'sources',root/'data/accounting-master/simulation-literature-gaps-20261026/sources']:
    for f in directory.glob('*crossref*.json'):
        j=read(f)
        if not isinstance(j,dict):continue
        m=j.get('message',{})
        if not isinstance(m,dict):continue
        for item in m.get('items',[m]):
            if item.get('DOI'):cr[item['DOI'].lower()]=(item,f)
# A bounded title query is used only after its returned identity was inspected.
metrics=[];corrections=[]
for r in source['records']:
    key=r['id'];doi=extras.get(key,r.get('doi'))
    f=p/'sources'/f'{key}-metadata-openalex.json'
    if key=='strebulaev':f=p/'sources/strebulaev-metadata-correct-openalex.json'
    if key in ['probabilistic-adapted','kernel-topology','time-causal-vae']:f=p/'sources'/f'{key}-openalex.json'
    if key in ['mccarthy','pichler-shapiro-foundations']:
        f=p/'sources'/f'{key}-metadata-search.json';j=read(f);o=j['results'][0] if j else None
    else:o=read(f)
    assert o and str(o.get('doi','')).lower().removeprefix('https://doi.org/')==doi.lower(),(key,doi,o)
    if key=='strebulaev':assert norm(o['title'])==norm('Dynamic Models and Structural Estimation in Corporate Finance')
    r['title']=o['title'];r['authors']=[a['author']['display_name'] for a in o.get('authorships',[])]
    r['publication_identity_doi']=doi;r['metadata_publication_year']=o.get('publication_year')
    r['metadata_year_caveat']='Online/index year may differ from printed issue or retained working-paper date; retained edition controls technical anchors.'
    r['classification']='SURVEY_OR_TUTORIAL' if key in ['dro-survey','strebulaev'] else ('FOUNDATIONAL' if key in ['mccarthy','epstein','gneiting'] else 'DIRECT_METHOD')
    r['full_text_status']='Local PDF retained and hashed; inspected scope only as stated'
    r['publication_status']=o.get('type','not available')
    r['not_allowed']='No wider theorem, entire-paper reading, edition equivalence, production validity or empirical ranking beyond stated inspected scope.'
    r['retraction_check']={'date':'2026-10-26','source':str(f.relative_to(root)),'sha256':sha(f),'is_retracted':o.get('is_retracted','not available'),'interpretation':'Index flag only; false is not proof that no correction exists.'}
    assert o.get('is_retracted') is not True,('Quarantine required',key)
    item,cf=cr.get(doi.lower(),({},None))
    notices={k:item.get(k,'not present in returned record') for k in ['update-to','updated-by','relation']}
    r['correction_check']={'source':str(cf.relative_to(root)) if cf else 'not available','date':'2026-10-26','fields':notices,'status':'No notice in inspected fields; source-specific correction/version questions remain open','limitation':'No exhaustive publisher correction search or journal/working-paper equation identity is inferred.'}
    r['quarantine_status']='No retraction flag or correction conflict found in bounded checks; unrelated DOI candidate rejected separately'
    if key=='time-causal-vae':
        r['correction_check']['local_finding']='Retained v1 Theorem3.1 unrestricted policy-class claim fails exact singleton counterexample; do not use unqualified. Journal edition not matched.'
        r['quarantine_status']='Version-specific unrestricted theorem claim excluded; architecture and separately checked bounded-support argument remain scoped.'
    venue=(o.get('primary_location') or {}).get('source') or {}
    metrics.append(dict(id=key,title=r['title'],doi=doi,citation_count=o.get('cited_by_count','not available'),citation_source='OpenAlex retained response',access_date='2026-10-26',source_file=str(f.relative_to(root)),source_sha256=sha(f),venue=venue.get('display_name','not available'),venue_metric='not available',venue_metric_source='not available',venue_metric_access_date='not available',caveat='Counts/venue describe visibility only. No ranking or correctness inference.'))
    corrections.append(dict(id=key,doi=doi,openalex=r['retraction_check'],crossref=r['correction_check']))
dump('source-support.json',source)
dump('citation-venue.json',dict(date='2026-10-26',rule='Dated metadata only, not acceptance evidence',records=metrics))
dump('correction-checks.json',dict(date='2026-10-26',records=corrections,rejected_identity={'file':'sources/strebulaev-metadata-openalex.json','doi':'10.1561/0500000038','reason':'Returned Should Banks Stress Test Results be Disclosed; rejected, correct source DOI0500000035 verified'},provenance_incident={'files':['sources/shapiro-rectangular-crossref.json','sources/xin-goldberg-time-crossref.json'],'description':'A retry overwrote the first successful round10 search responses with429 bodies. Original response hashes survive in round10 manifest; fresh exact-DOI responses are retained under metadata-crossref names. The original response bytes cannot be reconstructed. Paper and code bytes are unaffected. Retrieval helper now archives an existing response by content hash before writing.'}))
claims=read(p/'claim-support.json');ids={r['id'] for r in source['records']}
for c in claims['records']:
    assert set(c['sources'])<=ids,(c['id'],set(c['sources'])-ids)
    c['support_classes']=['PRIMARY_TECHNICAL_SUPPORT','PROJECT_DERIVATION'] if c['sources'] else ['PROJECT_DERIVATION']
    if c['id'] in ['C13','C25']:c['support_classes']=['IMPLEMENTATION_EVIDENCE']
    c['scope']='Only the exact source/local proposition in evidence; no general simulation acceptance.'
dump('claim-support.json',claims)
print(json.dumps(dict(sources=len(source['records']),dated_metadata=len(metrics),claim_source_links='PASS',retracted_flags_found=0)))
