"""Preserve inspected sources and check their identity/locatable anchors once."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import os
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / 'source-attempt-02'

def digest(p):
    return sha256(p.read_bytes()).hexdigest()

def main():
    start = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    out = HERE / 'verification-attempt-01'
    out.mkdir(exist_ok=False)
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert os.environ.get('PYTHONDONTWRITEBYTECODE') == '1'
    acquired = json.loads((SOURCE / 'acquisition.json').read_text())
    checks = []
    register = []
    for entry in acquired:
        pdf = HERE / entry['path']
        assert digest(pdf) == entry['sha256'], entry['id']
        assert pdf.stat().st_size == entry['bytes']
        checks.append({'id': entry['id'] + '-acquisition-hash', 'pass': True})
        register.append(dict(entry, text_path=str(pdf.with_suffix('.txt').relative_to(ROOT))))
    extra = SOURCE / 'aasb18-full.pdf'
    headers = (SOURCE / 'aasb18-full.headers').read_text()
    assert headers.startswith('HTTP/2 200')
    assert extra.stat().st_size == 1234123 and extra.read_bytes().startswith(b'%PDF-')
    extra_record = dict(
        id='aasb18-full', url='https://www.aasb.gov.au/admin/file/content105/c9/AASB18_06-24.pdf',
        path=str(extra.relative_to(ROOT)), bytes=extra.stat().st_size, sha256=digest(extra),
        response_status=200, response_date_utc='2026-10-26T14:29:27Z',
        retrieval_start_utc=None,
        retrieval_note='Recovered successful download; response Date retained. Exact start and full original argv not retained in this unit; no re-download.',
        text_path=str(extra.with_suffix('.txt').relative_to(ROOT)))
    register.append(extra_record)
    checks.append({'id':'aasb18-full-recovered-headers-size', 'pass':True})
    old = ROOT / 'docs/design/research/standards/aasb132.pdf'
    register.append(dict(id='aasb132-retained', path=str(old.relative_to(ROOT)),
                         bytes=old.stat().st_size, sha256=digest(old),
                         text_path=str(old.with_suffix('.txt').relative_to(ROOT)),
                         retrieval_note='Previously retained primary source; original provenance and frozen authority register remain unchanged.'))
    texts = {x['id']: (ROOT / x['text_path']).read_text().split('\f') for x in register}
    anchors = [
        ('aasb9-2026',7,'compilation scope','before 1 January 2027'),
        ('aasb9-2026',8,'2.1(a)','those interests in subsidiaries, associates and joint ventures'),
        ('aasb9-2026',15,'4.1.1','business model'),
        ('aasb9-2026',16,'4.2.1','amortised cost'),
        ('aasb9-2026',17,'4.3.2','entire hybrid contract'),
        ('aasb9-2026',17,'4.3.3','closely related'),
        ('aasb9-2026',18,'5.1.1A','transaction price'),
        ('aasb9-2026',18,'5.2.2','impairment requirements'),
        ('aasb9-2026',45,'Appendix A amortised cost','maturity amount'),
        ('aasb9-2026',46,'Appendix A derivative/EIR','not specific to a party to the contract'),
        ('aasb9-2026',46,'Appendix A EIR','shall not consider the expected credit losses'),
        ('aasb9-2026',70,'B4.1.14 Instrument F','convertible bond in its entirety'),
        ('aasb9-2026',74,'B4.3.5','not closely related'),
        ('aasb132-retained',8,'15','on initial recognition'),
        ('aasb132-retained',9,'16','fixed amount of any currency'),
        ('aasb132-retained',12,'22','Except as stated in paragraph 22A'),
        ('aasb132-retained',13,'25','beyond the control of both'),
        ('aasb132-retained',13,'26','all of the settlement alternatives'),
        ('aasb132-retained',14,'31','equity component is assigned the residual amount'),
        ('aasb132-retained',25,'AG29','all terms and conditions agreed between members of the group'),
        ('aasb132-retained',25,'AG30','only to issuers'),
        ('aasb132-retained',25,'AG31','comparable credit status'),
        ('aasb132-retained',25,'AG32','at maturity'),
        ('aasb2022-9',5,'4','1 July 2026'),
        ('aasb2022-9',12,'18','Aus4.1'),
        ('aasb18-full',51,'C1','1 January 2027'),
        ('aasb18-full',51,'AusC1.1','1 January 2028'),
        ('aasb18-appendix-d',14,'AASB9 amendment header','B4.1.2A'),
        ('aasb18-appendix-d',17,'7.1.11','7.2.1'),
        ('aasb18-appendix-d',51,'AASB132 amendment header','AG29'),
        ('aasb18-appendix-d',52,'97U','96A')
    ]
    for sid, page, paragraph, phrase in anchors:
        normalized = ' '.join(texts[sid][page-1].split())
        assert phrase in normalized, (sid,page,paragraph,phrase)
        checks.append(dict(id=f'{sid}:{page}:{paragraph}', pass_check=True))
    for record in register:
        sid = record['id']
        record['physical_pages'] = len(texts[sid]) - (not texts[sid][-1].strip())
        record['inspected_anchors'] = [dict(physical_page=p, paragraph=q) for i,p,q,_ in anchors if i==sid]
    applicability = {
        'aasb9-2026': 'Annual starts 2026-07-01 <= start < 2027-01-01; not a complete 2027 edition.',
        'aasb132-retained': 'Retained 2023 compilation; frozen package window ends before 2026-07-01. Later amendments assessed separately, not admitted.',
        'aasb2022-9': 'Specified amendments apply from annual starts 2026-07-01; earlier application permitted; inspect entity scope.',
        'aasb18-full': 'C1 general start 2027-01-01; AusC1.1 named entities 2028-01-01; early application and transition explicit.',
        'aasb18-appendix-d': 'Amendments conditional on application of AASB18; complete 2027/2028 chain remains open.'}
    for row in register:
        row['applicability_review'] = applicability[row['id']]
    protected = [p for p in HERE.rglob('*') if p.is_file() and out not in p.parents]
    protected += [old, old.with_suffix('.txt'), ROOT/'docs/design/research/p08-v1/authority-register.json',
                  ROOT/'docs/design/research/p08-v3/authority-register.json']
    catalog = json.loads((ROOT/'scripts/accounting_master_catalog.json').read_text())['active_execution_note']
    for key in ['current_pdf','standalone_pdf']:
        p = ROOT/catalog[key]
        assert digest(p) == catalog[key+'_sha256']
        protected.append(p)
    lock = {str(p.relative_to(ROOT)):digest(p) for p in protected}
    (out/'source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
    (HERE/'source-register.json').write_text(json.dumps(register,indent=2)+'\n')
    (SOURCE/'aasb18-full-acquisition-recovered.json').write_text(json.dumps(extra_record,indent=2)+'\n')
    (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    result = dict(status='PASS', mechanical_checks=len(checks), sources=len(register), protected_files=len(lock),
                  scope='Identity and anchor location only; semantic conclusions are the bounded reviewed matrix.',
                  candidate=catalog['current_candidate'])
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    manifest = dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                    command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(ROOT)),
                    environment=sys.version, cpu_gpu='CPU; GPU devices intentionally hidden', random_seeds='N/A: deterministic source verification',
                    data_version='source-lock.json and ../source-register.json',
                    started_utc=started, wall_seconds=time.monotonic()-start,
                    plan='docs/plans/accounting-contingent-conversion-authority-20261026.md',
                    result=str((HERE/'result.md').relative_to(ROOT)), output_directory=str(out.relative_to(ROOT)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
