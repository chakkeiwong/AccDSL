"""Construct the bounded failed-source disposition once."""
import importlib.util,json
from pathlib import Path
U=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('blocked_source',U/'compare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
names=['comparison.json','source-ledger.json','source-support-ledger.json','citation-venue-ledger.json',
       'backward-snowball-ledger.json','forward-snowball-ledger.json','claim-support-ledger.json','omission-risk-ledger.json']
assert not any((U/n).exists() for n in names)
value=m.derive()
paths={U/'compare.py',U/'build_records.py',m.OLD/'result.md',m.OLD/'source-status.json',
       m.R/'docs/design/research/retrieval-attempts.json',m.R/'docs/design/research/raw/tamer-landing.html',
       m.R/'docs/design/research/raw/tamer2010-search.json',m.R/'docs/plans/accounting-frontier-audit-20261020.md'}
paths.update((U/'sources').iterdir())
anchors=[]
for name,p,phrase in [('institutional-doi',m.R/'docs/design/research/raw/tamer-landing.html',m.DOI),
                       ('older-barriers',m.OLD/'result.md','Three distinct'),
                       ('ordinary-title',U/'sources/publisher-sandbox.body','<title>Just a moment...</title>'),
                       ('trusted-title',U/'sources/publisher-trusted.body','<title>Just a moment...</title>'),
                       ('ordinary-challenge',U/'sources/publisher-sandbox.headers','cf-mitigated: challenge'),
                       ('trusted-challenge',U/'sources/publisher-trusted.headers','cf-mitigated: challenge')]:
    text=p.read_text();pos=text.index(phrase);a=max(0,pos-70);b=min(len(text),pos+len(phrase)+200)
    anchors.append({'id':name,'source':m.bind(p),'start':a,'end':b,'excerpt':text[a:b]})
records={
 'comparison.json':value,
 'source-ledger.json':{'bindings':[m.bind(p) for p in sorted(paths)],'anchors':anchors,'scope':'source route/access evidence only'},
 'source-support-ledger.json':{'id':'tamer2010','title':'Partial Identification in Econometrics','author':'Elie Tamer',
    'doi':m.DOI,'identity_basis':'retained metadata/institutional link only','status':'SOURCE_BLOCKED',
    'full_text':'not acquired','inspected_technical_sections':[],'claims_allowed':[],
    'claims_forbidden':['technical content from title,abstract,metadata or error response']},
 'citation-venue-ledger.json':{'venue':'Annual Review of Economics,2010; inherited metadata',
    'citation_count':'not refreshed','correction_retraction_status':'not freshly checked; challenge prevents publisher reading',
    'metadata_role':'discovery only'},
 'backward-snowball-ledger.json':{'references':'not read; full text unavailable','new_source_lead':'recorded publisher DOI from institutional page',
    'not_claimed':'technical backward coverage'},
 'forward-snowball-ledger.json':{'scope':'one exact publisher route plus trusted repetition',
    'citation_survey':'not performed','prior_routes':'13October Harvard barriers preserved; no unchanged retry'},
 'claim-support-ledger.json':{'claims':[{'claim':'this publisher route is access-blocked','support':'both403 receipts,challenge headers and title'},
    {'claim':'no new technical paper evidence was obtained','support':'retained response bytes are HTML challenge,not PDF or article text'}]},
 'omission-risk-ledger.json':{'paper_status':'SOURCE_BLOCKED','next_source_step':'only a genuinely new legitimate lead or user-supplied authorised full text',
    'independent_next':'inspect still-unread technical sections in the retained England/Verrall/Wuthrich2019 paper after prior-scope audit',
    'limit':'local source blocker; no global source absence or research-direction rejection'}
}
for name,obj in records.items():
    with (U/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
print(json.dumps({'constructed':True,'bindings':len(paths),'anchors':len(anchors),'technical_reading':False}))
