"""Check bounded source dispositions and preserve original library evidence."""
import hashlib,json
from pathlib import Path
from lxml import html
U=Path(__file__).resolve().parent;R=U.parents[2];checks={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((U/'baseline.json').read_text())
receipts=sorted((U/'sources').glob('*.receipt.json'));checks['four_requests']=len(receipts)==4
statuses={'rutgers-author':'200','scholarly-discovery':'200','rutgers-faculty':'404','rutgers-current':'200'}
for p in receipts:
    x=json.loads(p.read_text());label=p.name.removesuffix('.receipt.json');body=R/x['path']
    checks[label+':hash']=sha(body)==x['sha256']
    checks[label+':http']=x['curl_receipt'].splitlines()[0]==statuses[label]
    checks[label+':bounded']=x['command'][x['command'].index('--max-time')+1]=='25' and x['command'][x['command'].index('--max-filesize')+1]=='12582912'
    checks[label+':not_pdf']=not body.read_bytes().startswith(b'%PDF')
    checks[label+':not_blocked_acm_route']='dl.acm.org' not in x['url']
author=html.fromstring((U/'sources/rutgers-author.body').read_bytes())
checks['exact_redirect']=author.xpath('//meta[@http-equiv="refresh"]')[0].get('content')=='0; url=https://www.cs.rutgers.edu/faculty/tomasz-imielinski'
faculty=html.fromstring((U/'sources/rutgers-faculty.body').read_bytes())
checks['actual_current_profile_link']='/people/professors/details/tomasz-imielinski' in faculty.xpath('//a/@href')
current=html.fromstring((U/'sources/rutgers-current.body').read_bytes())
checks['profile_identity']=current.findtext('.//title')=='Imielinski, Tomasz'
checks['no_target_pdf_link']=not any('.pdf' in h.lower() or '1634.1886' in h for h in current.xpath('//a/@href'))
lead=json.loads((U/'discovery-leads.json').read_text())
checks['unsupported_leads_rejected']=lead['leads']==[] and 'rejected' in lead['correction']
checks['rejected_list_preserved']=(U/'rejected-discovery-leads.json').is_file()
for group in ['candidate_files','frozen','dependencies']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
catalog=json.loads((R/'docs/design/research/catalog.json').read_text());row=next(x for x in catalog if x['id']=='imielinski1984')
checks['original_source_still_blocked']=row['status'].startswith('SOURCE_BLOCKED') and row['local_path'] is None
checks['next_primary_available']=(R/'docs/papers/Incomplete Data - What Went Wrong, and How to Fix It Libkin (2014).pdf').is_file()
failed=[k for k,v in checks.items() if not v]
(U/'checks.json').write_text(json.dumps({'checks':checks,'passed':sum(checks.values()),'failed':failed},indent=2)+'\n');print(json.dumps({'passed':sum(checks.values()),'failed':failed,'full_text_acquired':False}));raise SystemExit(bool(failed))
