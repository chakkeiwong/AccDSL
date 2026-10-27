"""Retained Note9 constraints: reported principal, carrying values and maturities."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction as Q
import argparse,hashlib,json,re,subprocess,sys,time,xml.etree.ElementTree as E,zipfile

ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();checks=[]
    def check(name,a,b):checks.append(dict(name=name,passed=a==b,actual=a,expected=b))
    pdf=ROOT/'docs/design/cases/apple/annual-2024.pdf';archive=ROOT/'docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.zip'
    prior=ROOT/'data/accounting-master/company-state-source-card-20261028/attempt-01/source-lock.json';lock=json.loads(prior.read_text())
    for p in [pdf,archive]:check('retained identity '+p.name,sha(p),lock[str(p.relative_to(ROOT))])
    text=subprocess.check_output(['pdftotext','-f','46','-l','46','-layout',str(pdf),'-'],text=True);(out/'note9-page46.txt').write_text(text)
    check('printed page',bool(re.search(r'Form 10-K\s*\|\s*43',text)),True)
    check('note identity','Note 9' in text and 'Term Debt' in text,True)
    with zipfile.ZipFile(archive) as z:raw=z.read('aapl-20240928_htm.xml')
    xml=E.fromstring(raw);ns={'x':'http://www.xbrl.org/2003/instance'}
    context=next(x for x in xml.findall('x:context',ns) if x.get('id')=='c-21')
    check('issuer',context.find('x:entity/x:identifier',ns).text,'0000320193');check('instant',context.find('x:period/x:instant',ns).text,'2024-09-28')
    check('no segment',context.find('x:entity/x:segment',ns),None);check('no scenario',context.find('x:scenario',ns),None)
    unit=next(x for x in xml.findall('x:unit',ns) if x.get('id')=='usd');check('USD measure',unit.find('x:measure',ns).text,'iso4217:USD')
    expected=[('f-942','DebtInstrumentCarryingAmount',97341,'Total term debt principal',1),
      ('f-944','DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet',321,'Unamortized premium/(discount) and issuance costs, net',-1),
      ('f-946','HedgeAccountingAdjustmentsRelatedToLongTermDebt',358,'Hedge accounting fair value adjustments',-1),
      ('f-948','LongTermDebt',96662,'Total term debt',1),
      ('f-950','LongTermDebtCurrent',10912,'Less: Current portion of term debt',-1),
      ('f-952','LongTermDebtNoncurrent',85750,'Total non-current portion of term debt',1),
      ('f-955','LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths',10930,'2025',1),
      ('f-956','LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo',12342,'2026',1),
      ('f-957','LongTermDebtMaturitiesRepaymentsOfPrincipalInYearThree',9936,'2027',1),
      ('f-958','LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFour',7800,'2028',1),
      ('f-959','LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFive',5153,'2029',1),
      ('f-960','LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive',51180,'Thereafter',1),
      ('f-961','DebtInstrumentCarryingAmount',97341,'Total term debt principal',1)]
    facts=[]
    for identity,tag,amount,caption,sign in expected:
        matches=[x for x in xml if x.get('id')==identity];check('unique '+identity,len(matches),1);f=matches[0]
        check('tag '+identity,f.tag.split('}',1)[1],tag);check('reported amount '+identity,str(Q(f.text)/1000000),str(amount))
        check('context '+identity,f.get('contextRef'),'c-21');check('unit '+identity,f.get('unitRef'),'usd');check('precision '+identity,f.get('decimals'),'-6')
        lines=[line.strip() for line in text.splitlines() if line.strip().startswith(caption)]
        check('PDF caption amount '+identity,any(re.search(r'(?<![0-9])'+re.escape(f'{amount:,}')+r'(?![0-9])',line) for line in lines),True)
        if sign<0:check('PDF deduction '+identity,any('('+f'{amount:,}'+')' in line for line in lines),True)
        facts.append(dict(id=identity,concept=f.tag,context='c-21',reported_usd=f.text,decimals=f.get('decimals'),pdf_caption=caption,reported_usd_million=amount,pdf_reconciliation_sign=sign))
    check('maturity buckets sum',sum(r[2] for r in expected[6:12]),97341)
    check('principal to carrying value',97341-321-358,96662);check('current noncurrent split',10912+85750,96662)
    check('principal versus carrying gap',97341-96662,679);check('next bucket not current carrying',10930-10912,18)
    selected=ROOT/'data/accounting-master/selected-reading-history-20261027/attempt-01/result.json';history=json.loads(selected.read_text())
    check('preserved target obligations',sum(len(a['target_obligations']) for a in history['attachments'].values()),180)
    deps=ROOT/'data/accounting-master/company-cases-current-20261028/attempt-01/current-decisions.json';decisions=json.loads(deps.read_text())
    check('issuer dependency rows',len(decisions['rows']),15);check('no issuer target admitted',all(r['original_target_ready'] is False for r in decisions['rows']),True)
    card=dict(issuer='Apple Inc.',source_pdf=str(pdf.relative_to(ROOT)),physical_page=46,printed_page=43,as_of='2024-09-28',unit='reported USD million',instance_sha256=hashlib.sha256(raw).hexdigest(),context=E.tostring(context,encoding='unicode'),facts=facts,
      mathematical_scope='Exact arithmetic on displayed amounts; not exact latent economic quantities or standards admission',
      constraints={'reported_principal':97341,'reported_carrying':96662,'reported_deductions':[321,358],'reported_current_carrying':10912,'reported_noncurrent_carrying':85750,'maturity_labels':['2025','2026','2027','2028','2029','Thereafter'],'maturity_reported_values':[10930,12342,9936,7800,5153,51180]},
      distinctions=['The generic XBRL DebtInstrumentCarryingAmount tag is tied to a printed principal caption; tag name alone does not supply financial meaning.','Adjustment fact values are positive in the instance but deductions in the printed reconciliation; sign comes from the selected table relationship.','The summary coupon range does not define floating economic exposure because the note describes swaps.','Current carrying amount differs from the next payment bucket; the18 difference is not allocated to instruments here.'],
      missing=['Exact instrument identities and legal obligors','Dated principal and coupon cashflows within printed buckets','Currency, coupon, swap and hedge linkage by instrument','Allocation of premiums/discounts/costs and hedge adjustments by instrument','Supported source publication/ingestion and actor access','Complete contract population and full company opening'],
      source_admission=False,accounting_admission=False,actual_history='unknown',probabilities=None,
      next_evidence='Bind selected note/exhibit contractual instruments and exact dates; preserve notes/derivatives linkage, authority and legal context before simulation.')
    failed=[c for c in checks if not c['passed']]
    paths=[Path(__file__),ROOT/'docs/plans/company-state-debt-source-20261028.md',pdf,archive,prior,selected,deps]
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=sys.version,cpu_gpu='CPU-only XML/ZIP/Poppler; no accelerator imports',random_seeds='N/A source identity and exact arithmetic',data_version='retained2024 PDF and XBRL bytes',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=str(paths[1].relative_to(ROOT)),result_file='data/accounting-master/company-state-debt-source-20261028/result.md',inputs={str(p.relative_to(ROOT)):sha(p) for p in paths})
    for name,obj in [('source-to-state.json',card),('verification.json',dict(status='fail' if failed else 'pass',count=len(checks),failed=failed,checks=checks)),('run-manifest.json',manifest)]:
        (out/name).write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(dict(count=len(checks),failed=len(failed),output=str(out))))
    return bool(failed)
if __name__=='__main__':raise SystemExit(main())
