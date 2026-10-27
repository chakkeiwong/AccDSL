"""One-time construction after the documentary read; validate before writing."""
import importlib.util
import json
from pathlib import Path

U = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('insurance_source', U / 'compare.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
names = ['comparison.json', 'source-ledger.json', 'source-support-ledger.json',
         'citation-venue-ledger.json', 'backward-snowball-ledger.json',
         'forward-snowball-ledger.json', 'claim-support-ledger.json', 'omission-risk-ledger.json']
assert not any((U / name).exists() for name in names), 'one-time construction'
value = m.derive()
paths = {U / 'compare.py', U / 'build_records.py', U / 'source-plan-addendum.md',
         m.P / 'result.md', m.P / 'aasb17-edition.html', m.P / 'ifrs-supporting.html',
         m.P / 'retained-source-excerpts.txt', m.P / 'ifrs-derecognition-slides.txt'}
paths.update(p for p in (U / 'sources').iterdir() if p.is_file())
paths.update(p for p in (U / 'render').iterdir() if p.is_file())
anchors = []


def span(name, path, start, end):
    text = path.read_text()
    assert 0 <= start < end <= len(text)
    anchors.append({'id': name, 'source': m.bind(path), 'start': start, 'end': end,
                    'excerpt': text[start:end]})


def lines(name, path, first, last):
    rows = path.read_text().splitlines(keepends=True)
    assert 1 <= first <= last <= len(rows)
    span(name, path, sum(map(len, rows[:first-1])), sum(map(len, rows[:last])))


def token(name, path, phrase, context=200):
    text = path.read_text()
    pos = text.index(phrase)
    span(name, path, max(0, pos-context), min(len(text), pos+len(phrase)+context))


for first, last, name in [(1,44,'aasb-identity'), (45,154,'aasb-adoption'), (155,211,'aasb-nfp-rdr')]:
    lines(name, m.S / 'AASB-BC.txt', first, last)
for first, last, name in [(1,77,'ap2c-status-purpose'), (78,157,'ap2c-risk-context'),
                          (158,207,'ap2c-stakeholder-requests'), (208,322,'ap2c-risk-analysis'),
                          (323,382,'ap2c-transition-scope'), (383,425,'ap2c-transition-rationale'),
                          (426,470,'ap2c-oci-proposals'), (471,544,'ap2c-analysis-footnotes')]:
    lines(name, m.S / 'IASB-AP2C.txt', first, last)
for name, path, phrase in [
    ('aasb-separate-basis', m.P/'aasb17-edition.html', 'AASB17_07-17_BC_AASB17.pdf'),
    ('aasb-separate-iasb', m.P/'aasb17-edition.html', 'iasb-support-materials'),
    ('access-restriction', m.S/'IASB-support-sandbox.body', 'restricted to users in Australia'),
    ('project-lead', m.P/'ifrs-supporting.html', 'amendments-to-ifrs-17.html'),
    ('project-tabs', m.S/'IFRS-amendments-sandbox.body', 'IFRS.tabs('),
    ('script-tab-construction', m.S/'IFRS-site-script-sandbox.body', 'n.requestURL+"/"+s+".nocache.html"'),
    ('public-picker', m.S/'IFRS-meetings-sandbox.body', 'IFRS.projectMeetingPicker('),
    ('script-picker-construction', m.S/'IFRS-site-script-sandbox.body', 'this.requestURL=e.concat(".model.json")'),
    ('meeting-model', m.S/'IFRS-picker-sandbox.body', '/_2019/february/international-accounting-standards-board/master.html'),
    ('meeting-paper-link', m.S/'IASB-feb2019-sandbox.body', 'ap2c-transition-risk-migration-option-and-oci.pdf'),
]:
    token(name, path, phrase)

records = {
 'comparison.json': value,
 'source-ledger.json': {'bindings': [m.bind(p) for p in sorted(paths)], 'anchors': anchors,
                        'scope': 'source identity and finite public navigation; no new treatment or global absence inference'},
 'source-support-ledger.json': {'sources': [
    {'title':'AASB Basis for Conclusions accompanying AASB17','institution':'AASB',
     'edition':'retained compiled extract; URL includes07-17, printed90–93',
     'local':m.bind(m.S/'AASB-BC-sandbox.body'),'read':'all AusBC1–32',
     'status':'Australian-specific accompanying reasons, not part of AASB17',
     'allowed':'identity and adoption scope','forbidden':'substitution for IASB BC316–322'},
    {'title':'Transition—Risk mitigation option and amounts accumulated in other comprehensive income on transition',
     'institution':'IASB staff','authors':['Chalani Mohotti','Hagit Keren','Anne McGeachin'],
     'date':'February2019','agenda':'AP2C','local':m.bind(m.S/'IASB-AP2C-sandbox.body'),
     'read':'complete twelve pages, paragraphs1–33, footnotes1–8',
     'status':'public staff discussion paper; explicitly not Board views or acceptable-application ruling',
     'allowed':'dated staff analysis and reported transition rationale',
     'forbidden':'Board decision, current requirements, resolution of91/B135'}],
    'version_check':'actual official agenda link and PDF identity agree; no notice of replacement in inspected material; comprehensive correction search not done',
    'quarantine':'no specific notice found in these inspected sources; not an exhaustive clearance'},
 'citation-venue-ledger.json': {'date':'2026-10-20','venue':'official AASB material and public IASB meeting',
    'citation_count':'not available; not a relevance or authority criterion','academic_ranking':'not applicable'},
 'backward-snowball-ledger.json': {'leads':[
    {'source':'AP2C9','lead':'IFRS17 BC393','action':'reported rationale only; original Basis not inspected'},
    {'source':'AP2C20–22','lead':'C18(b),C19(b)(ii),C24(b)','action':'transition-scope references; no transfer to B135'},
    {'source':'AP2C footnote1','lead':'January2019 tentative risk-mitigation decision','action':'outside exact termination question; not independently confirmed'},
    {'source':'AASB AusBC1–32','lead':'AASB4/1023/1038/1056/1057,Interpretation1047,ED223/277','action':'Australian adoption context; not needed to decide document identity'}],
    'primary_remaining_lead':'IASB BC316–322 cited in retained recognition/derecognition webcast'},
 'forward-snowball-ledger.json': {'query':'actual retained IFRS supporting link to completed2020 project; public meetings picker; one February2019 meeting',
    'selected':'AP2C as a bounded transition-versus-policy-change relevance test',
    'limit':'not a forward citation survey; no comprehensive search for91/B135 examples',
    'board_update':'meeting summary link retained but not fetched; no Board-decision claim'},
 'claim-support-ledger.json': {'claims':[
    {'claim':'AASB extract is not the IASB Basis sought','support':'aasb-identity and separate official links'},
    {'claim':'AASB IASB-support access is geographically restricted','support':'redirect receipt and access-restriction'},
    {'claim':'AP2C addresses transition and cannot select the unfinished schedule treatment','support':'ap2c-status-purpose,transition-scope,analysis-footnotes plus predecessor exact question'},
    {'claim':'Both competing91/B135 readings remain unresolved here','support':'no directly matching source or complete new derivation; prior result preserved'}]},
 'omission-risk-ledger.json': {'open':['actual IASB BC316–322','direct applicable91/B135 example or complete derivation',
    'original88/89 attribution and last-release/termination ordering','current consolidated authority and actual contract applicability'],
    'independent_next':'continue an independently ready source/contract gap; no repeated balance calculation',
    'blocked_scope':'dependent accounting selector only; not a global continuation veto'}
}
for name, obj in records.items():
    with (U/name).open('x') as handle:
        json.dump(obj,handle,indent=2,ensure_ascii=False)
        handle.write('\n')
print(json.dumps({'constructed':True,'anchors':len(anchors),'bindings':len(paths),'acquisitions':8}))
