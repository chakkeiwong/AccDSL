"""Record inspected source spans and bounded scope checks, once."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, os, platform, subprocess, sys, time
H=Path(__file__).resolve().parent; R=H.parents[2]
def h(p):return sha256(p.read_bytes()).hexdigest()
def save(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
def main():
    start=time.monotonic();assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (H/'source-audit.json').exists()
    source=R/'docs/design/research/p08-v3-preparation'
    spans=[('writeoff','IFRS 9 5.4.4',35218,35222,549),
           ('enforcement_policy','IFRS 7 35F(e)',31955,31958,499),
           ('enforcement_amount','IFRS 7 35L',32101,32103,501),
           ('portion_example','IFRS 9 B5.4.9',40190,40195,623),
           ('derecognition','IFRS 9 B3.2.16(r)',38366,38368,596),
           ('allowance_adjustment','IFRS 9 5.5.8',35353,35355,None),
           ('poci_changes','IFRS 9 5.5.13-14',35411,35421,None),
           ('cash_activity','IAS 7 15-16(e)-(f)',2818,2855,44),
           ('indirect_reporting','IAS 7 20',2928,2943,None)]
    lines=(source/'eu-2023-1803-original.txt').read_text().split('\n'); rows=[]
    for key,paragraph,first,last,page in spans:
        rows.append({'id':key,'paragraph':paragraph,'text_lines':[first,last],'pdf_page':page,
                     'text':'\n'.join(lines[first-1:last])})
    urls={
       'ifric-march-2019':'https://www.ifrs.org/news-and-events/updates/ifric/2019/ifric-update-march-2019/',
       'ifrs9-standard-page':'https://www.ifrs.org/issued-standards/list-of-standards/ifrs-9-financial-instruments/',
       'amortised-cost-project':'https://www.ifrs.org/projects/work-plan/amortised-cost-measurement/',
       'impairment-review':'https://www.ifrs.org/projects/completed-projects/2024/post-implementation-review-of-ifrs-9-impairment/'}
    online=[]
    selections={'ifric-march-2019':(326,336),'ifrs9-standard-page':(182,224),
                'amortised-cost-project':(193,226),'impairment-review':(194,201)}
    for name,url in urls.items():
        first,last=selections[name];s=(H/(name+'.txt')).read_text().splitlines()
        online.append({'id':name,'url':url,'retrieved_date':'2026-10-27',
            'html_sha256':h(H/(name+'.html')),'text_sha256':h(H/(name+'.txt')),
            'inspected_lines':[first,last],'text':'\n'.join(s[first-1:last]),
            'retrieval_command':'curl --fail --location --max-time 30 --silent --show-error --output '+str((H/(name+'.html')).relative_to(R))+' '+url})
    checks=[]
    def ck(name,passed):
        checks.append({'name':name,'passed':bool(passed)});assert passed,name
    by={x['id']:x['text'] for x in rows};on={x['id']:x['text'] for x in online}
    ck('writeoff_derecognition','derecognition event' in by['writeoff'])
    ck('enforcement_policy','enforcement activity' in by['enforcement_policy'])
    ck('enforcement_amount','contractual amount outstanding' in by['enforcement_amount'])
    ck('portion_distinct','portion of it' in by['portion_example'])
    ck('allowance_rule','loss allowance' in by['allowance_adjustment'])
    ck('poci_distinct','purchased or originated credit-impaired' in by['poci_changes'])
    ck('cash_entity_scope','financial institution' in by['cash_activity'])
    ck('curing_described','subsequently cured' in on['ifric-march-2019'])
    ck('curing_allowance_target','loss allowance' in on['ifric-march-2019'])
    ck('curing_no_explicit_writeoff_fact','write-off' not in on['ifric-march-2019'].lower() and 'written off' not in on['ifric-march-2019'].lower())
    ck('later_version_identified','2026 Issued' in on['ifrs9-standard-page'])
    ck('project_not_issued_standard','tentatively' in on['amortised-cost-project'] and 'Exposure Draft' in on['amortised-cost-project'])
    ck('writeoff_clarification_referral','write-off' in on['impairment-review'] and 'Amortised Cost' in on['impairment-review'])
    native=R/'data/accounting-master/credit-claim-continuity-20261027/attempt-01'
    v=json.loads((native/'verification.json').read_text());b=json.loads((native/'after-close-boundaries.json').read_text())
    ck('predecessor_verified',v['status']=='PASS' and v['cases']==9)
    ck('nine_direct_endpoint_refusals',len(b)==9 and all(x['result']['reason']=='event_after_close' for x in b))
    paths=[source/n for n in ['eu-2023-1803-original.pdf','eu-2023-1803-original.txt','source-preparation.json']]
    paths += [native/'verification.json',native/'after-close-boundaries.json']
    paths += [p for p in H.iterdir() if p.is_file()]
    protected={str(p.relative_to(R)):h(p) for p in paths}
    save('source-audit.json',{'status':'PASS_BOUNDED_SCOPE','historical_source':str(source.relative_to(R)),
         'original_url':'https://publications.europa.eu/resource/celex/32023R1803',
         'historical_spans':rows,'official_pages':online,'checks':checks,'protected_files':protected,
         'rule_change':False,'post_close_accounting_admission':False,'actual_receipt_supplied':False})
    save('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
        'command':'env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/credit-recovery-scope-20261027/record.py',
        'environment':{'python':platform.python_version(),'executable':sys.executable},
        'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic source checks',
        'wall_seconds':round(time.monotonic()-start,3),'completed_utc':datetime.now(timezone.utc).isoformat(),
        'data_version':protected,'plan':'docs/plans/accounting-credit-recovery-scope-20261027.md',
        'result':'data/accounting-master/credit-recovery-scope-20261027/result.md',
        'artifacts':{'source-audit.json':h(H/'source-audit.json')}})
    print(json.dumps({'status':'PASS_BOUNDED_SCOPE','source_checks':len(checks),'historical_spans':len(rows),'official_pages':len(online),'post_close_accounting_admission':False}))
if __name__=='__main__':main()
