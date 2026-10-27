from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from datetime import datetime,timezone
import json,zipfile,xml.etree.ElementTree as E,time,sys,platform
import fitz
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def sha(p):return sha256(p.read_bytes()).hexdigest()
def h(raw):return sha256(raw).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def read(p):return json.loads(p.read_text())
def local(t):return t.rsplit('}',1)[-1]
NS={'x':'http://www.xbrl.org/2003/instance','l':'http://www.xbrl.org/2003/linkbase','a':'http://www.w3.org/1999/xlink','d':'http://xbrl.org/2006/xbrldi'}
A='{'+NS['a']+'}'
ROLE='http://www.apple.com/role/CONSOLIDATEDSTATEMENTSOFCASHFLOWS'
ISSUANCE='ProceedsFromIssuanceOfLongTermDebt'
CONCEPTS={
 'PaymentsRelatedToTaxWithholdingForShareBasedCompensation':('cash_flow.award_tax','-1'),
 'PaymentsOfDividends':('cash_flow.dividends','-1'),
 'PaymentsForRepurchaseOfCommonStock':('cash_flow.repurchases','-1'),
 ISSUANCE:('cash_flow.debt_issuance','1'),
 'RepaymentsOfLongTermDebt':('cash_flow.debt_repayments','-1'),
 'ProceedsFromRepaymentsOfCommercialPaper':('cash_flow.commercial_paper','1'),
 'ProceedsFromPaymentsForOtherFinancingActivities':('cash_flow.financing_other','1'),
 'NetCashProvidedByUsedInFinancingActivities':('cash_flow.financing','1')}
def main():
 start=time.monotonic();out=H/'source-inspection-01';out.mkdir(exist_ok=False)
 old=read(B/'cash-population-reconciliation-20261025/source-ledger.json')
 archive=R/'docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.zip'
 pdf=R/'docs/design/cases/apple/annual-2024.pdf'
 for p in [archive,pdf]:assert sha(p)==old['source_sha256'][str(p.relative_to(R))]
 with zipfile.ZipFile(archive) as z:
  raws={n:z.read(n) for n in z.namelist()}
  assert {n:h(v) for n,v in raws.items()}==old['archive_member_sha256']
 root=E.fromstring(raws['aapl-20240928_htm.xml']);contexts={};units={}
 for c in root.findall('x:context',NS):
  ent=c.find('x:entity',NS);i=ent.find('x:identifier',NS);period=c.find('x:period',NS)
  dims=[E.tostring(x,encoding='unicode') for x in c.iter() if local(x.tag) in ['explicitMember','typedMember']]
  other=[E.tostring(x,encoding='unicode') for x in c if local(x.tag) not in ['entity','period']]
  other+=[E.tostring(x,encoding='unicode') for x in ent if local(x.tag)!='identifier']
  contexts[c.attrib['id']]=dict(entity=dict(scheme=i.attrib['scheme'],identifier=i.text),period={local(x.tag):x.text for x in period},dimensions=dims,other_children=other,raw_xml=E.tostring(c,encoding='unicode'))
 for u in root.findall('x:unit',NS):
  m=u.findall('x:measure',NS)
  units[u.attrib['id']]=dict(raw_xml=E.tostring(u,encoding='unicode'),measure='{http://www.xbrl.org/2003/iso4217}USD' if len(u)==len(m)==1 and m[0].text=='iso4217:USD' else 'unsupported:'+E.tostring(u,encoding='unicode'))
 links={};labels={};presentation={};weights={}
 for suffix in ['lab','pre','cal']:
  tree=E.fromstring(raws['aapl-20240928_'+suffix+'.xml']);matched=[]
  for link in tree:
   locs={n.attrib.get(A+'label'):n.attrib.get(A+'href') for n in link.findall('l:loc',NS)}
   for arc in link:
    f=arc.attrib.get(A+'from');t=arc.attrib.get(A+'to')
    if f not in locs and t not in locs:continue
    source=locs.get(f,f);dest=locs.get(t,t)
    if not any('#us-gaap_'+c in str(source)+' '+str(dest) for c in CONCEPTS):continue
    item=dict(role=link.attrib.get(A+'role'),source=source,target=dest,attributes=dict(arc.attrib))
    if suffix=='lab':
     vals=[dict(text=n.text,role=n.attrib.get(A+'role'),language=n.attrib.get('{http://www.w3.org/XML/1998/namespace}lang')) for n in link.findall('l:label',NS) if n.attrib.get(A+'label')==t]
     item['labels']=vals;labels[source.rsplit('#',1)[-1].removeprefix('us-gaap_')]=vals
    if suffix=='pre' and link.attrib.get(A+'role')==ROLE:presentation[dest.rsplit('#',1)[-1].removeprefix('us-gaap_')]=item
    if suffix=='cal' and source and source.endswith('#us-gaap_NetCashProvidedByUsedInFinancingActivities') and link.attrib.get(A+'role')==ROLE:weights[dest.rsplit('#',1)[-1].removeprefix('us-gaap_')]=arc.attrib['weight']
    matched.append(item)
  links[suffix]=matched
 facts=[]
 for n in root:
  concept=local(n.tag)
  if concept not in CONCEPTS or 'contextRef' not in n.attrib:continue
  raw=E.tostring(n,encoding='unicode')
  fact=dict(concept=n.tag,id=n.attrib['id'],value=n.text,decimals=n.attrib.get('decimals'),nil=n.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}nil') in ['true','1'],context_ref=n.attrib['contextRef'],context=contexts[n.attrib['contextRef']],unit_ref=n.attrib['unitRef'],unit=units[n.attrib['unitRef']]['measure'],unit_xml=units[n.attrib['unitRef']]['raw_xml'],raw_xml=raw,fact_sha256=h(raw.encode()),archive_sha256=sha(archive),instance_sha256=h(raws['aapl-20240928_htm.xml']),pdf_sha256=sha(pdf),labels=labels.get(concept,[]),presentation_role=presentation.get(concept,{}).get('role'),calculation_weight=weights.get(concept))
  terse=[x['text'] for x in fact['labels'] if x['role']=='http://www.xbrl.org/2003/role/terseLabel'];fact['pdf_label']=terse[0] if len(terse)==1 else None;facts.append(fact)
 doc=fitz.open(pdf);page=doc[35];text=page.get_text();page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(out/'annual-page36.png')
 (out/'annual-page36.txt').write_text(text)
 originals=read(B/'statement-context-coverage-20261024/statements.json')['CompanyOperationsDraft/1:combined']
 protected=[archive,pdf,B/'statement-context-coverage-20261024/statements.json',B/'cash-population-reconciliation-20261025/source-ledger.json',R/'docs/design/research/standards/xbrl-oim.txt',R/'docs/design/research/standards/xbrl-oim.html',Path(__file__),H/'source_reading.py',H/'audit.md',R/'docs/plans/accounting-debt-dash-source-20261027.md']
 lock={str(p.relative_to(R)):sha(p) for p in protected}
 dump(out/'source-lock.json',lock);dump(out/'facts.json',facts);dump(out/'links.json',links)
 dump(out/'selected-originals.json',dict(observation=originals['observations']['annual.cash_flow.debt_issuance'],relations=[r for r in originals['relations'] if r['id'] in ['annual.financing_cash','annual.diagnostic:term_debt']]))
 dump(out/'manifest.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),git_commit='unavailable',command='CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/debt-dash-source-20261027/inspect_source.py',python=sys.version,executable=sys.executable,platform=platform.platform(),cpu_gpu='CPU only; no GPU or numerical framework imported',random_seeds='N/A deterministic source inspection',wall_seconds=time.monotonic()-start,archive_members={n:h(v) for n,v in raws.items()},plan='docs/plans/accounting-debt-dash-source-20261027.md',result='data/accounting-master/debt-dash-source-20261027/result.md'))
 selected=[f for f in facts if local(f['concept'])==ISSUANCE and f['context_ref']=='c-1']
 print(json.dumps(dict(passed=True,facts=len(facts),selected=[{k:f[k] for k in ['id','value','decimals','context_ref','pdf_label','fact_sha256','archive_sha256','instance_sha256','pdf_sha256']} for f in selected])))
if __name__=='__main__':main()
