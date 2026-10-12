"""Record versioned OTSL sources and bounded reading dispositions."""
import ast
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert not (OUT/'completion.json').exists()
paper=OUT/'sources/paper.pdf';copy=ROOT/'docs/papers/Optimized Table Tokenization for Table Structure Recognition Lysak (2023) arXiv v1.pdf'
assert not copy.exists() or sha(copy)==sha(paper)
if not copy.exists():shutil.copyfile(paper,copy)
save('paper-copy.json',{'source':str(paper.relative_to(ROOT)),'copy':str(copy.relative_to(ROOT)),'sha256':sha(paper),'pages':14})
resources={'publisher':'publisher.html','crossref':'crossref.json','published-pdf':'published-pdf.response',
 'arxiv-search':'arxiv-search.xml','arxiv-landing':'arxiv-landing.html','paper':'paper.pdf','otsl-code':'otsl.py'}
receipts=[]
for name,body in resources.items():
 d=json.loads((OUT/(name+'-transfer.json')).read_text());p=OUT/'sources'/body
 headers='otsl.py.headers' if name=='otsl-code' else name+'.headers'
 command=['curl','-L','--connect-timeout','10','--max-time','30','--max-filesize','15000000','-sS',
          '-D',str((OUT/'sources'/headers).relative_to(ROOT)),'-o',str(p.relative_to(ROOT)),'--write-out','%{json}',d['url']]
 receipts.append({'name':name,'date':'2026-10-12','command_argv':command,
  'stdout_file':str((OUT/(name+'-transfer.json')).relative_to(ROOT)),'stderr_file':str((OUT/(name+'-stderr.txt')).relative_to(ROOT)),
  'trusted':True,'http_code':d['http_code'],'exit_code':d['exitcode'],'effective_url':d['url_effective'],
  'bytes':p.stat().st_size,'sha256':sha(p),'body':str(p.relative_to(ROOT)),'wall_seconds':d['time_total'],
  'content_disposition':'HTML landing, not published PDF' if name=='published-pdf' else 'retained identified response'})
save('access-receipts.json',{'distinct_resources':7,'limit':8,'attempts':receipts})
cr=json.loads((OUT/'sources/crossref.json').read_text())['message']
save('source-support.json',{'title':'Optimized Table Tokenization for Table Structure Recognition',
 'authors':['Maksym Lysak','Ahmed Nassar','Nikolaos Livathinos','Christoph Auer','Peter Staar'],
 'class':'DIRECT_METHOD','doi':'10.1007/978-3-031-41679-8_3','published':'ICDAR 2023, pp. 37–50; first online 19 August 2023',
 'inspected_version':'arXiv:2305.03393v1, 5 May 2023','local_copy':str(copy.relative_to(ROOT)),'sha256':sha(copy),
 'full_text':'All fourteen pages read; no separate appendix in this copy; ten selected renders inspected',
 'technical_anchors':['Sections 3–4, pp. 5–8; six rules on p. 7','Section 4.3, p. 8: validity versus correct prediction and example heuristic',
 'Section 5 and Tables 1–2, pp. 8–10','Figures 1–6','Section 6 and all 23 reference entries, pp. 12–14'],
 'version_limits':['Publisher PDF route returned HTML','arXiv comment says 12 pages; inspected PDF contains 14 including continuing references',
 'No published-full-text equivalence established'],
 'correction_check':{'sources':['publisher landing','arXiv version history','Crossref record'],'date':'2026-10-12',
 'relation':cr.get('relation'),'update_to':cr.get('update-to'),'status':'No notice located in bounded records; comprehensive clearance not established'},
 'quarantine':'Claim-specific: six rules do not establish universal rectangular merged-cell geometry. Method is not wholly quarantined.',
 'allowed':['Exact representation and attributed experiment account','Finite local derivation with explicit target'],
 'forbidden':['Universal rectangular-cell guarantee from six rules','Local superiority/default claims','Exact checkpoint or training reproduction equivalence']})
save('citation-venue.json',{'date':'2026-10-12','venue':'ICDAR 2023 / LNCS 14188','venue_metric':'not available',
 'counts':[{'source':'Crossref','citing_works':cr.get('is-referenced-by-count')},{'source':'publisher landing','citations':33}],
 'limit':'Different live metadata counts; not reconciled as one universe and not evidence of validity'})
claims=[
 ('O1','PRIMARY_TECHNICAL_SUPPORT','Five-token atomic-grid representation and six rules','Sections 4.1–4.2, pp. 6–7','Exact arXiv v1, not later token set'),
 ('O2','PRIMARY_TECHNICAL_SUPPORT','Syntax validity differs from correct prediction; ranked-token replacement is an example heuristic','Section 4.3, p. 8','Not proof of actual 4.0.2 enforcement'),
 ('O3','PROJECT_DERIVATION','C L / U C passes six rules but forms an L-shaped merged cell','technical-review.md; finite-diagnostic.json','Counterexample to rectangular-cell sufficiency only; no frequency claim'),
 ('O4','IMPLEMENTATION_EVIDENCE','Later helper checks row widths/pads and expands right/down without complete geometry validation','otsl.py 35–77 and 95–241','Static source trace; no upstream execution'),
 ('O5','IMPLEMENTATION_EVIDENCE','line_num remains zero; first-line correction applies on every iteration','TableModel04_rs.predict 110–328, assignment 170 and guard 200','Wrong relative to stated first-line scope; occurrence not measured'),
 ('O6','PRIMARY_TECHNICAL_SUPPORT','Reported HPO/data/metric/timing outcomes have specified source scope','Section 5, Tables 1–2, pp. 8–10','No statistical ranking or direct comparison with 2022 content score'),
 ('O7','PRIMARY_TECHNICAL_SUPPORT','Across-the-board improvement language overstates individual table entries','Tables 1–2: equal PubTabNet overall and lower simple OTSL; 4/4 and 2/4 lower overall','Attribute exact descriptive entries; do not replace with opposite universal ranking')]
save('claim-support.json',[{'id':i,'class':c,'claim':t,'anchor':a,'limit':l} for i,c,t,a,l in claims])
text=(OUT/'sources/paper.txt').read_text();refs=text[text.rfind('References'):]
entries={int(m.group(1)):' '.join(m.group(2).split()) for m in re.finditer(r'(?m)^\s*(\d{1,2})\.\s+(.*?)(?=^\s*\d{1,2}\.\s+|\Z)',refs,re.S)}
assert set(entries)==set(range(1,24)),sorted(entries)
back=[]
for n,citation in entries.items():
 cl='COMPETITOR';action='defer to broader competitor review; no technical claim imported'
 if n in [1,8,15]:cl='IMPLEMENTATION_OR_SOFTWARE';action='inspect if expanding upstream PDF-conversion claims'
 elif n in [7,10,14,23]:cl='EMPIRICAL_EXAMPLE';action='dataset context; preserve existing project disposition; not reread here'
 elif n==9:cl='DIRECT_METHOD';action='complete main/supplement read preserved in tableformer-paper-20261012'
 elif n==16:cl='FOUNDATIONAL';action='historical table abstraction lead; no formal claim imported'
 elif n in [21,22]:cl='DIRECT_METHOD';action='retain exact data/metric predecessor lead; broader evaluation coverage remains open'
 back.append({'reference':n,'citation_as_extracted':citation,'class':cl,'action':action,'full_text_this_unit':False})
save('backward-snowball.json',{'all_printed_reference_entries':23,'candidates':back,'limit':'Consideration is not full-text reading'})
save('forward-snowball.json',{'date':'2026-10-12','checked_citing_work':'Docling Technical Report Auer (2024), PDF 3–4 and reference 9 on PDF 6',
 'relation':'Explicit token-language refinement cites this paper','source':'docs/papers/Docling Technical Report Auer (2024).pdf',
 'sha256':sha(ROOT/'docs/papers/Docling Technical Report Auer (2024).pdf'),
 'coverage':'Concrete retained forward relation only; no systematic citing-work search or highly-cited/recent/negative-result coverage established'})
save('omission-supplement.json',{'historical_ledgers':'preserved unchanged','updated_work':'OTSL 2023 author copy now technically inspected',
 'open':['Published full text and version equivalence','Systematic forward/competitor coverage','Original training/checkpoint identity',
 'Four previously blocked foundational papers and broader mission obligations'],
 'claim_disposition':'Universal geometry guarantee from printed six rules excluded; compact representation remains viable with added validation'})
defaults=[
 ('version','Exact arXiv query/landing/PDF','Title/authors and version-specific locators','Assume published equivalence','Preserve HTML response and explicit v1','reviewed version only'),
 ('merge target','Section 4.1 plus stated HTML exchange','Requires rectangular nonoverlapping cells for rowspan/colspan','Treat local admissibility as cell geometry','2×2 finite rule/merge check','explicit target, not universal table model'),
 ('HPO depth','Table 1/Section 5.2','Historical PubTabNet selection','Transfer across financial datasets without local tuning','Record chosen 6/6/8 and mixed table entries','source choice, not local default'),
 ('metric/timing','Tables 1–2 and single-core machine','Attribute reported measurements','Compare mismatched content targets or hardware','Keep 2022 Table 4 separate and no local speed claim','descriptive source result'),
 ('inference source','Pinned 4.0.2 and tree blob','Exact bounded comparison','Assume partial corrections implement six-rule search','Read complete predict and relevant helpers, static store check','candidate source only'),
 ('resource bound','Audited eight-resource plan','Bound access and preserve attempt bodies','Mistake limited check for complete literature clearance','Count seven URLs and record coverage limits','convenience bound')]
save('default-assumption-audit.json',[{'choice':a,'provenance':b,'justification':c,'failure_mode':d,'early_diagnostic':e,'status':f} for a,b,c,d,e,f in defaults])
code=OUT/'sources/otsl.py';tree=ast.parse(code.read_text());ranges=[{'name':n.name,'first':n.lineno,'last':n.end_lineno} for n in tree.body if isinstance(n,ast.FunctionDef) and n.end_lineno<=241]
save('code-anchors.json',{'commit':'d1569fdffee1d09cb3111d6d5490991cb59d59fd','path':str(code.relative_to(ROOT)),'sha256':sha(code),
 'git_blob':'60b9151ef419aa3e8f45a640fd6a0c9839105736','read_ranges':ranges,'module_context':'lines 1–24 read',
 'not_read':'html_to_otsl, 244–550; no claim of roundtrip or full-module correctness',
 'retained_predict_method':'data/accounting-master/tableformer-loader-20261010/sources/docling_ibm_models__tableformer__models__table04_rs__tablemodel04_rs.py:110–328',
 'predictor_local_width_checker':'data/accounting-master/tableformer-loader-20261010/sources/docling_ibm_models__tableformer__data_management__tf_predictor.py:52–86'})
save('reading-review.json',{'text_pages':list(range(1,15)),'renders':json.loads((OUT/'render-manifest.json').read_text()),
 'scope':'All ten renders visually inspected, including six-rule list, token figures, complete benchmark tables and selected qualitative examples',
 'independent_reader':'pending','human_acceptance':'pending'})
print({'resources':len(receipts),'backward_entries':len(back),'claims':len(claims),'copies':1})
