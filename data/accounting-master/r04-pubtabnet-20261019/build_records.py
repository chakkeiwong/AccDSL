"""One-time construction of this source inquiry's explicit records."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
U=Path(__file__).resolve().parent
R=U.parents[2]

def put(name,value):
    with (U/name).open('x') as f:
        json.dump(value,f,indent=2);f.write('\n')

def binding(p):
    return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

commit='8ffde9024bd331f5a61c3c549fdf30dd3c3e43a5'
acqs=[
 ('01-version.body','01-version.headers','https://arxiv.org/abs/1911.10683v5',0.376010),
 ('02-paper.pdf','02-paper.headers','https://arxiv.org/pdf/1911.10683v5',1.341757),
 ('03-repository.body','03-repository.headers','https://github.com/ibm-aur-nlp/PubTabNet',1.202704),
 ('04-tree.body','04-tree.headers',f'https://github.com/ibm-aur-nlp/PubTabNet/tree/{commit}/src',1.348780),
 ('05-metric.py','05-metric.headers',f'https://raw.githubusercontent.com/ibm-aur-nlp/PubTabNet/{commit}/src/metric.py',0.500639),
 ('06-metric-readme.md','06-metric-readme.headers',f'https://raw.githubusercontent.com/ibm-aur-nlp/PubTabNet/{commit}/src/README.md',0.571496)]
rows=[]
for body,headers,url,secs in acqs:
    b,h=U/'sources'/body,U/'sources'/headers
    rows.append({'url':url,'effective_url':url,'body':binding(b),'headers':binding(h),
                 'status':200,'redirects':0,'bytes':b.stat().st_size,'curl_total_seconds':secs,
                 'receipt_provenance':'Tool-returned curl JSON, manually transcribed fields; retained headers/body are independently bound.',
                 'command':f"curl --silent --show-error --location --connect-timeout 10 --max-time 35 --max-filesize 12582912 --proto =https --proto-redir =https --dump-header {h.relative_to(R)} --output {b.relative_to(R)} --write-out '%{{json}}\\n' {url}",
                 'permissions':'trusted require_escalated; curl prefix'})
anchors=[
 ('paper-version','02-paper.txt','arXiv:1911.10683v5 [cs.CV] 4 Mar 2020','title, physical p1'),
 ('crop-resolution','02-paper.txt','72 pixels per inch','III, physical p3'),
 ('split-text','02-paper.txt','60%/20%/20%','III, physical p3'),
 ('training-count','02-paper.txt','548,592','III, physical p3'),
 ('heldout-balance','02-paper.txt','5,000 tables','III, physical p4'),
 ('metric-wording','02-paper.txt','similarity [38]','V, physical p4; rendered'),
 ('metric-nontd','02-paper.txt','the cost is 1 if either','V, physical p4; rendered'),
 ('train-subset','02-paper.txt','399k samples','VI.A, physical p6'),
 ('input-scale','02-paper.txt','448 × 448','VI.A, physical p6'),
 ('synthetic','02-paper.txt','420K/40k/40k','VI.E, physical p8'),
 ('given-locations','02-paper.txt','documents is given by users','VII, physical p10'),
 ('no-model','03-readme.txt','source code of the model will not be released','captured root README; local statement only'),
 ('new-boxes','03-readme.txt','21/July/2020','captured root README release history'),
 ('code-distance','05-metric.py','float(distance.levenshtein(*sequences)) / self.maximum(*sequences)','CustomConfig.normalized_distance'),
 ('code-rename','05-metric.py','if (node1.tag != node2.tag)','CustomConfig.rename'),
 ('code-td','05-metric.py',"if node1.tag == 'td':",'CustomConfig.rename'),
 ('code-return','05-metric.py','return 0.','CustomConfig.rename equal attributes and empty/matching content'),
 ('code-descendants','05-metric.py','len(pred.xpath(".//*"))','TEDS.evaluate; raw descendants'),
 ('code-select','05-metric.py',"pred.xpath('body/table')[0]",'TEDS.evaluate; first direct table'),
 ('code-tokenize','05-metric.py',"self.__tokens__.append('<%s>' % node.tag)",'TEDS.tokenize; inline tag tokens'),
 ('code-leaf','05-metric.py',"if node.tag != 'td':",'TEDS.load_html_tree; cells become leaves'),
 ('code-predmissing','05-metric.py',"pred_json.get(filename, '')",'TEDS.batch_evaluate; missing prediction'),
 ('code-truthkeys','05-metric.py','samples = true_json.keys()','TEDS.batch_evaluate; denominator population'),
 ('metric-readme','06-metric-readme.md','1 means perfect matching','README; requires accepted input domain')]
passages=[]
for ident,file,needle,section in anchors:
    p=U/'sources'/file;t=p.read_text();assert needle in t,ident
    passages.append({'id':ident,'path':str(p.relative_to(R)),'needle':needle,'section':section,
                     'first_line':t[:t.index(needle)].count('\n')+1})
binds=[U/'sources'/n for n in ['02-paper.txt','03-readme.txt','paper-03.png','paper-04.png']]
binds += [R/'docs/design/proposal/manuscript-early-conversion-20261018/chapters/03-literature.tex',
          R/'docs/design/research/text/smock2022.txt']
put('source-ledger.json',{'scope':'Exact six-URL source acquisition and documentary reading; no dataset/model acquisition',
 'acquisitions':rows,'bindings':[binding(p) for p in binds],'passages':passages,
 'pin':commit,'paper_edition':'arXiv v5 2020-03-04; published version not acquired',
 'web_search':{'queries':['exact title + erratum correction retraction','1911.10683 TEDS site:arxiv.org'],
 'result':'No readable result content returned by web tool; no result-based claim admitted'},
 'code_scope':'Entire retained metric.py and metric README read; no EDD model source read',
 'data_scope':'Dataset not downloaded; no sample membership, leakage, labels or scores independently checked'})

def ledger(name,entries,scope):put(name+'-ledger.json',{'scope':scope,'entries':entries})
ledger('source-support',[
 {'id':'zhong-v5','classification':['DIRECT_METHOD','COMPETITOR'],'title':'Image-based table recognition: data, model, and evaluation',
 'authors':['Xu Zhong','Elaheh ShafieiBavani','Antonio Jimeno Yepes'],'edition':'arXiv1911.10683v5, 4 March 2020',
 'publication_status':'preprint inspected; root repository reports ECCV20 acceptance; published text not verified',
 'technical_read':'I–VII, equations1–3, tablesI–III, error/generalization analysis and references; no appendix in retained 11-page PDF',
 'rendered_read':'physical3–4; confirms split and metric wording',
 'retraction_status':'No notice seen in retained arXiv metadata; external search returned no readable content; no exhaustive clearance',
 'allowed':'Describe this edition, its reported protocol, scores and limitations; separate static code findings',
 'forbidden':'Current SOTA, replicated scores, leakage-free partition, financial correctness, universal metric implementation equality'},
 {'id':'ibm-metric','classification':['IMPLEMENTATION_OR_SOFTWARE'],'commit':commit,
 'technical_read':'All of src/metric.py and src/README.md; root README and pinned src listing',
 'allowed':'Static dependency/API/tokenization/normalization observations for retained bytes',
 'forbidden':'Installed equivalence, transitive implementation validation, EDD model availability across all repos, reproduction of original experiments'}],
 'Additive primary support; inherited six ledgers are not rewritten')
ledger('citation-venue',[
 {'id':'zhong-v5','citation_count':None,'citation_source':'not available','access_date':'2026-10-19',
 'venue':'ECCV20 acceptance asserted by official repository; original arXiv edition read',
 'venue_metric':None,'venue_metric_source':'not available','caveat':'No ranking or quality inference from counts/venue'}],
 'Dated metadata, not correctness evidence')
back=[]
groups=[([2,3,10,37,38],'FOUNDATIONAL','Metric/benchmark ancestry; primary derivations not imported without separate reads'),
 ([4,5,6,7,8,9],'COMPETITOR','Data/detection/recognition alternatives; [4],[5],[7] are direct next inquiry candidates'),
 (list(range(11,33)),'COMPETITOR','Detection/structure families; scoped source-only candidate inventory, not individually read'),
 ([33,34,39,40],'DIRECT_METHOD','Attention, image-to-markup, ResNet and Adam; no target default promotion'),
 ([35,36],'BACKGROUND','Dual-decoder examples in other tasks; no claim of financial transfer'),
 ([1],'BACKGROUND','Biomedical information motivation; outside financial method claim')]
for refs,kind,action in groups:
 for n in refs:back.append({'reference':n,'classification':kind,'action':action,'primary_read_in_this_unit':False})
assert sorted(x['reference'] for x in back)==list(range(1,41))
ledger('backward-snowball',back,'All 40 reference entries considered; classifications are triage, not technical admissions')
ledger('forward-snowball',[
 {'id':'retained-smock2022','source':'docs/design/research/text/smock2022.txt reference23','status':'Known retained citation lead; this unit does not rerun its full review'},
 {'id':'retained-tableformer','source':'current chapter3 and prior source dossier','status':'Known downstream comparator; exact data/code alignment remains separate'},
 {'id':'online-forward-search','query':'1911.10683 TEDS site:arxiv.org','date':'2026-10-19','status':'No readable tool content; not a completed forward-citation search'},
 {'id':'separate-edd-route','url':'https://github.com/ibm-aur-nlp/EDD','status':'Model-recalled unverified candidate URL, not a search discovery'},
 {'id':'published-edition-route','url':'https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123660562.pdf','status':'Model-recalled unverified candidate URL; edition reconciliation needed'}],
 'Known retained successors and explicitly incomplete forward coverage')
ledger('claim-support',[
 {'claim':'Cropped-table recognition differs from whole-report extraction','support':'PRIMARY_TECHNICAL_SUPPORT','anchor':'VII p10; chapter3 lines201–240','disposition':'Current warning supported; no manuscript repair needed from this claim'},
 {'claim':'TEDS measures structure and content but cannot alone establish financial context','support':'PROJECT_DERIVATION','anchor':'witnesses.json external_unit and sign; result.md','disposition':'Exact illustrative consequence; no actual report measured'},
 {'claim':'This arXiv wording is an exact implementable definition of selected code','support':'SOURCE_GAP_BLOCKER','anchor':'V p4 versus CustomConfig.rename and evaluate','disposition':'Mismatch; do not silently substitute distance/root conventions'},
 {'claim':'EDD improves target financial extraction by9.7 points','support':'SOURCE_GAP_BLOCKER','anchor':'VI.A–B','disposition':'No local/financial comparison; source-reported difference only'},
 {'claim':'Selected repository metric source is available','support':'IMPLEMENTATION_EVIDENCE','anchor':'pinned metric.py','disposition':'Read statically; dependency versions and runtime not checked'},
 {'claim':'EDD source code is globally unavailable','support':'SOURCE_GAP_BLOCKER','anchor':'captured root README only','disposition':'Not established; separate candidate repository must be investigated'}],
 'Current claims versus source statements, code observations and local deductions')
ledger('omitted-paper',[
 {'item':'Published ECCV edition','reason':'Six acquisition URLs used; v5 is exact inspected baseline','risk':'Printed defects may be corrected in final paper','next':'Verify independent official edition lead','status':'requires expansion'},
 {'item':'Separate EDD repository','reason':'New unverified candidate route; no budget hidden in this unit','risk':'Root README may be stale about code release','next':'Read repository identity/history before code availability conclusion','status':'requires expansion'},
 {'item':'APTED paper and dependency code','reason':'Only cited and imported, not downloaded','risk':'No general algorithm equivalence or range guarantee checked','next':'Inspect before adopting metric implementation','status':'blocked for general runtime claims'},
 {'item':'Current broad competitor/citation survey','reason':'This is one bounded original-method inquiry','risk':'Coverage is incomplete','next':'Continue distinct exact leads and retain missing metadata','status':'open'},
 {'item':'Original McCarthy, Imielinski/Lipski, Tamer, Caiani','reason':'Inherited blocked originals unchanged','risk':'Their dependent claims remain unsupported here','next':'Genuinely new primary route only','status':'blocked locally'}],
 'Explicit residuals; no comprehensive-survey claim')
spec=importlib.util.spec_from_file_location('local_checker',U/'compare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cases={'digit':m.witness(m.doc('100'),m.doc('900')),'bold_digit':m.witness(m.doc('<b>100</b>'),m.doc('<b>900</b>')),
       'sign':m.witness(m.doc('100'),m.doc('-100')),'external_unit':m.witness(m.doc('100','thousands'),m.doc('100','millions'))}
put('witnesses.json',{'witnesses':cases,'external_unit_amounts':{'thousands':100000,'millions':100000000},
 'distance_controls':6,'rejected_controls':['incorrect expected score: '+x for x in cases]+['changed topology','span outside contract','cost outside proof'],
 'upstream_metric_executed':False,'model_executed':False})
print(json.dumps({'records_written':8,'passages':len(passages),'witnesses':len(cases),'backward_entries':len(back)}))
