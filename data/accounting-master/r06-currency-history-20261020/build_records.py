"""Construct this source-adequacy unit once after read-only diagnostic checks."""
import importlib.util
import json
from pathlib import Path

U = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('currency_history', U / 'compare.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
R, B = m.R, m.B

def write(name, value):
    with (U / name).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')

names = ['history.json','source-ledger.json','acquisitions.json','source-support-ledger.json',
         'citation-venue-ledger.json','backward-snowball-ledger.json',
         'forward-snowball-ledger.json','claim-support-ledger.json','omission-risk-ledger.json']
assert not any((U / name).exists() for name in names), 'one successful construction only'
value = m.derive()
paths = {U/'compare.py', U/'build_records.py', U/'source_view.py', U/'source-plan-addendum.md',
         m.FACTS, m.UNITS, m.CONTEXTS, B/'r06-unit-measures-20261020/result.md',
         B/'r06-unit-measures-20261020/source-ledger.json', B/'r06-context-periods-20261020/result.md',
         R/'docs/design/proposal/manuscript-early-conversion-20261018/sections/adapter-methods.tex'}
paths.update(p for p in (U/'sources').iterdir() if p.is_file())
paths.update(p for p in (U/'rendered').iterdir() if p.is_file())
xbrl = B/'r06-enumeration-domain-20261020/sources/03-xbrl21.visible.txt'
paths.add(xbrl)
spans = [(xbrl, [(3375,3418)]),
         (U/'sources/SIX-index.visible.txt',[(409,420),(452,500),(606,613)]),
         (U/'sources/SIX-currency.visible.txt',[(378,405)]),
         (m.source('list-one'),[(1,22),(547,555),(1766,1782)]),
         (m.source('list-three'),[(1,20),(809,824)]),
         (U/'sources/amendment-94.txt',[(1,44)]),
         (U/'sources/amendment-158.txt',[(1,61)]),
         (U/'sources/amendment-160.txt',[(1,177)])]
anchors=[]
for path, ranges in spans:
    lines=path.read_text().splitlines()
    for first,last in ranges:
        assert 1<=first<=last<=len(lines), (path.name,first,last,len(lines))
        anchors.append({'source':m.bind(path),'first_line':first,'last_line':last,
                        'excerpt':'\n'.join(lines[first-1:last])})
write('history.json',value)
write('source-ledger.json',{'bindings':[m.bind(p) for p in sorted(paths)],'anchors':anchors,
    'scope':'source adequacy for exact historical currency periods; no current-law or compliance advice',
    'visual_inspection':['amendment94 p1','amendment158 p1','amendment160 pp1,3'],
    'text_reading':'all five pages of the three amendments; only four rendered pages inspected'})
write('acquisitions.json',{'attempts':[m.bind(p) for p in sorted((U/'sources').glob('*-receipt.json'))],
                          'upstream_execution':False})
write('source-support-ledger.json',{
    'sources':['SIX maintenance index and contact page','SIX list one, published2026-09-17',
               'SIX list three, published2026-01-01','SIX amendment index worksheet',
               'ISO4217 amendments94,158,160'],
    'allowed':['current-list identities','exact historical notices within their terms',
               'source fields and chronology limitations','873 exact fact/context/unit joins'],
    'forbidden':['uninterrupted historical currency validity from current membership',
                 'global EUR withdrawal from a country row','USD removal from USS notice',
                 '1999 as currency-code inception','complete amendment chronology or full XBRL validity'],
    'quarantine_status':'no identity conflict observed; date/context overreach explicitly rejected',
    'source_basis':'primary official maintenance sources, not peer-reviewed research papers'})
write('citation-venue-ledger.json',{'status':'not applicable to the primary software/standards maintenance inquiry',
                                  'authority_metadata':'SIX states its official maintenance role; that is not proof of historical interval coverage'})
write('backward-snowball-ledger.json',{
    'resolved':['maintenance-page actual links','worksheet relationships for94,158,160','complete selected amendment texts'],
    'open':['period-specific historical membership evidence','later amendments promised by94',
            'complete chronology or an authoritative historical validity statement'],
    'not_a_whole_archive_read':True})
write('forward-snowball-ledger.json',{
    'finding':'live maintenance page names180; retrieved index maximum179',
    'effect':'index is not evidence of complete current amendment chronology',
    'scope':'exact acquired sources; no global archive absence claim'})
write('claim-support-ledger.json',{'claims':[
    {'claim':'873 partial facts require143 contexts and10 period forms','support':'history.json source joins','class':'PROJECT_DERIVATION'},
    {'claim':'EUR issue preceded adoption date','support':'amendment94 p1,dated21April1997','class':'PRIMARY_TECHNICAL_SUPPORT'},
    {'claim':'amendment158 removesUSS,notUSD','support':'amendment158 p1,28March2014','class':'PRIMARY_TECHNICAL_SUPPORT'},
    {'claim':'amendment160 changes US country naming','support':'amendment160 pp1–3,19June2015','class':'PRIMARY_TECHNICAL_SUPPORT'},
    {'claim':'selected records do not supply checked uninterrupted validity intervals','support':'exact list fields and selected amendment scopes','class':'SOURCE_GAP_BLOCKER'}]})
write('omission-risk-ledger.json',{
    'open':['historical designation evidence across required periods','full registry/filing-specific unit restrictions',
            'installed processor correspondence','independent/domain/human acceptance'],
    'next':'seek a period-specific authoritative registry snapshot or an explicit continuous validity account; preserve partial statuses meanwhile',
    'boundary':'this is a narrow source gap; no whole-program continuation veto or professional referral'})
print(json.dumps({'facts':value['fact_count'],'contexts':value['context_count'],'periods':len(value['raw_periods']),
                  'anchors':len(anchors),'bindings':len(paths),'acquisitions':len(list((U/'sources').glob('*-receipt.json')))}))
