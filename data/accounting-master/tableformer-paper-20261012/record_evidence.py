"""Assemble bounded documentary evidence; no network or model execution."""
import hashlib
import json
import re
import shutil
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DATE = '2026-10-12'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, v): (OUT / n).write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n')
assert not (OUT / 'completion.json').exists()

copies = []
for stem, title in [('paper', 'TableFormer Table Structure Understanding With Transformers Nassar (2022).pdf'),
                    ('supplement', 'TableFormer Table Structure Understanding With Transformers Supplement Nassar (2022).pdf')]:
    source = OUT / 'sources' / (stem + '.pdf')
    dest = ROOT / 'docs/papers' / title
    assert not dest.exists() or sha(source) == sha(dest)
    if not dest.exists(): shutil.copyfile(source, dest)
    copies.append({'source': str(source.relative_to(ROOT)), 'copy': str(dest.relative_to(ROOT)),
                   'sha256': sha(source), 'pages': len(fitz.open(source))})
save('paper-copies.json', copies)

receipts = []
for name in ['cvf-landing-sandbox', 'cvf-landing', 'paper', 'supplement', 'crossref']:
    transfer = json.loads((OUT / (name + '-transfer.json')).read_text())
    ext = {'cvf-landing': 'html', 'paper': 'pdf', 'supplement': 'pdf', 'crossref': 'json'}.get(name)
    body = OUT / 'sources' / (name + '.' + ext) if ext else None
    receipts.append({'attempt': name, 'access_date': DATE, 'url': transfer['url'],
        'effective_url': transfer['url_effective'], 'http_code': transfer['http_code'],
        'curl_exit_code': transfer['exitcode'], 'bytes': transfer['size_download'],
        'wall_seconds': transfer['time_total'], 'trusted': name != 'cvf-landing-sandbox',
        'limits': {'connect_seconds': 10, 'total_seconds': 30, 'bytes': 15000000},
        'body': str(body.relative_to(ROOT)) if body else None, 'sha256': sha(body) if body else None,
        'transfer_record': name + '-transfer.json', 'headers': 'sources/' + name + '.headers',
        'stderr': name + '-stderr.txt',
        'command_provenance': 'Raw curl write-out, headers and stderr retained. Original shell invocation is in the agent tool transcript; limits above are the recorded execution parameters, not a fabricated verbatim command.'})
save('access-receipts.json', {'distinct_resources': 4, 'attempts': receipts,
    'sandbox_failure': 'DNS failure is sandbox evidence; successful trusted retry retained separately.'})

crossref = json.loads((OUT / 'sources/crossref.json').read_text())['message']
save('source-support.json', {
 'title': 'TableFormer: Table Structure Understanding With Transformers',
 'authors': ['Ahmed Nassar', 'Nikolaos Livathinos', 'Maksym Lysak', 'Peter Staar'],
 'year': 2022, 'doi': '10.1109/CVPR52688.2022.00457', 'class': 'DIRECT_METHOD',
 'publication': 'CVPR 2022; official CVF open-access accepted copy and linked supplement',
 'copies': copies, 'full_text': 'All 10 main and all 6 supplement pages read; 12 selected renders inspected.',
 'anchors': ['main Sections 1–6, Tables 1–4, Equations 1–2, figures and references',
             'supplement Sections 1–2, matching/correction steps, intersection/PDF-cell-area equation, Figures 1–3'],
 'version_check': {'cvf_and_pdf_pages': '4614–4623', 'crossref_pages': crossref.get('page'),
    'disposition': 'Use inspected PDF/CVF pagination; conflicting Crossref page field excluded. No silent correction of retained metadata.',
    'arxiv': '2203.01017 linked by CVF; not retrieved or compared'},
 'correction_check': {'date': DATE, 'sources': ['CVF landing', 'Crossref DOI record'],
    'relations': crossref.get('relation'), 'update_to': crossref.get('update-to'), 'updated_by': crossref.get('updated-by'),
    'status': 'No notice located in bounded check; comprehensive correction clearance not established',
    'quarantine': 'No technical-source quarantine from inspected evidence; conflicting metadata page field excluded'},
 'allowed': ['Attributed mechanism, training choices and evaluation scope of this copy',
             'Conceptual comparison with separately pinned official inference methods'],
 'forbidden': ['4.0.2 checkpoint performance transfer', 'accounting semantic accuracy', 'local stochastic ranking',
               'exact training reproduction from ambiguous printed loss', 'complete survey or current model equivalence']})
save('citation-venue.json', {'source': 'Crossref DOI record', 'date': DATE,
    'citing_works': crossref.get('is-referenced-by-count'), 'venue': 'CVPR 2022',
    'venue_metric': 'not available', 'meaning': 'Dated visibility metadata only; neither correctness nor coverage evidence'})

claims = [
 ('C1', 'PRIMARY_TECHNICAL_SUPPORT', 'Cropped image predicts HTML structure and synchronized cell boxes; text supplied separately', 'main Sections 4–5, PDF 4–7', 'Not an end-to-end accounting interpretation'),
 ('C2', 'PRIMARY_TECHNICAL_SUPPORT', '95.4/90.1/93.6 is PubTabNet simple/complex/all structure WITH content from cropped PDF tables', 'Table 4, PDF 7/printed 4620; retained model-card row', 'Not structure-only or measured release 4.0.2 performance'),
 ('C3', 'PRIMARY_TECHNICAL_SUPPORT', 'Structure-only scores are in a different table/population', 'Table 2, PDF 7/printed 4620', 'Not a comparable replacement for Table 4'),
 ('C4', 'PRIMARY_TECHNICAL_SUPPORT', 'Text matching and repair can deduplicate columns and create cells', 'supplement Section 2, pp. 2–3', 'Selected figures are not an accuracy sample'),
 ('C5', 'IMPLEMENTATION_EVIDENCE', 'Later retained model uses OTSL, argmax and cached step bound; wrapper merges PDF text', 'code-anchors.json', 'No paper beam-search mismatch established; helper equivalence incomplete'),
 ('C6', 'PRIMARY_TECHNICAL_SUPPORT', 'Training defaults/filtering and large-table downsampling constrain interpretation', 'main Sections 3, 5.1, 5.4; supplement Section 1', 'Source-reported choices are not AccDSL defaults; evaluation filtering kept distinct'),
 ('C7', 'PRIMARY_TECHNICAL_SUPPORT', 'Printed Equation 1 omits explicit l1 factor suggested by prose', 'main PDF 6/printed 4619, rendered equation and adjacent prose', 'Training-source clarification needed; no silent formula repair'),
 ('C8', 'PRIMARY_TECHNICAL_SUPPORT', 'Docling report states later token-language refinement and supplies exact follow-up', 'archived Docling report PDF 3–4 and reference 9 on PDF 6', 'OTSL paper not read in this unit'),
 ('C9', 'IMPLEMENTATION_EVIDENCE', 'Retained accurate/fast depth/head/dropout settings differ from paper', 'retained tm_config.json files; main Section 5.1', 'No checkpoint identity or runtime compatibility established')]
save('claim-support.json', [{'id': i, 'support_class': c, 'claim': t, 'anchor': a, 'limit': l} for i,c,t,a,l in claims])

prior = ROOT / 'data/accounting-master/tableformer-loader-20261010/sources'
code_rows = []
for suffix, ranges in [
 ('models__table04_rs__tablemodel04_rs.py', [(26,84,'constructor settings'),(110,328,'complete predict')]),
 ('data_management__tf_predictor.py', [(379,436,'complete _merge_tf_output'),(714,853,'complete predict')]),
 ('data_management__matching_post_processor.py', [(1265,1515,'complete process; called helpers not fully audited')])]:
    p = prior / ('docling_ibm_models__tableformer__' + suffix)
    lines = p.read_text().splitlines()
    code_rows.append({'path': str(p.relative_to(ROOT)), 'sha256': sha(p),
       'ranges': [{'first': a, 'last': b, 'scope': scope, 'first_line': lines[a-1], 'last_line': lines[b-1]} for a,b,scope in ranges]})
save('code-anchors.json', {'release': '4.0.2', 'commit': 'd1569fdffee1d09cb3111d6d5490991cb59d59fd',
    'prior_git_blob_verification': 'data/accounting-master/tableformer-loader-20261010', 'sources': code_rows,
    'not_checked': ['complete helper algorithms', 'training code', 'installed wiring', 'numerical equivalence']})

maintext = (OUT / 'sources/paper.txt').read_text()
refs_text = maintext[maintext.rfind('References'):]
refs = {int(m.group(1)): ' '.join(m.group(2).split()) for m in re.finditer(r'\[(\d+)\]\s+(.*?)(?=\n\[\d+\]|\Z)', refs_text, re.S)}
assert set(refs) == set(range(1,40)), sorted(refs)
classes = {1:'FOUNDATIONAL',3:'SURVEY_OR_TUTORIAL',9:'FOUNDATIONAL',16:'FOUNDATIONAL',17:'BACKGROUND',
           18:'EMPIRICAL_EXAMPLE',20:'IMPLEMENTATION_OR_SOFTWARE',23:'IMPLEMENTATION_OR_SOFTWARE',
           26:'FOUNDATIONAL',31:'IMPLEMENTATION_OR_SOFTWARE',32:'FOUNDATIONAL',33:'BACKGROUND',
           36:'BACKGROUND',37:'DIRECT_METHOD',38:'DIRECT_METHOD',39:'EMPIRICAL_EXAMPLE'}
special = {
 1:('inspect if training reproduction is proposed','DETR detector ancestry is method context, not locally reproduced'),
 18:('retain existing project source disposition','TableBank is already discussed; this unit did not reread its full text'),
 19:('inspect in later competing-method review','GFTE is a financial-table alternative; title/citation only here'),
 20:('inspect before expanding upstream text-backend claims','PDF text source is a concrete dependency'),
 21:('inspect in later competing-method review','Comparison context; no competitor ranking from this unit'),
 26:('inspect if implementing box loss','GIoU theory does not resolve the printed l1-factor ambiguity'),
 27:('retain as candidate competitor','Reference 28 repeats the same DeepDeSRT paper'),
 28:('duplicate of reference 27','Count once as a work; preserve both printed reference numbers'),
 32:('inspect if implementing architecture','Foundational attention source; this source reading does not reproduce its results'),
 37:('retain existing project source disposition','GTE/FinTabNet already discussed; target-specific validity not established here'),
 38:('inspect in later metric/competitor review','EDD/PubTabNet and TEDS are direct evaluation dependencies')}
back = []
for n, citation in sorted(refs.items()):
    cl = classes.get(n,'COMPETITOR')
    action, reason = special.get(n, ('defer with explicit scope', 'Method/benchmark context; this bounded unit compares TableFormer to its retained consumer, not all table-recognition methods. No technical support imported.'))
    back.append({'reference': n, 'citation_as_extracted': citation, 'class': cl, 'action': action,
                 'reason': reason, 'full_text_this_unit': False})
save('backward-snowball.json', {'seed': 'TableFormer 2022', 'scope': 'All 39 printed reference entries considered, including duplicate 27/28; consideration is not full-text reading', 'candidates': back})
docling = ROOT / 'docs/papers/Docling Technical Report Auer (2024).pdf'
save('forward-snowball.json', {'date': DATE, 'source': str(docling.relative_to(ROOT)), 'sha256': sha(docling),
 'inspected': ['PDF 3–4 TableFormer paragraphs', 'PDF 6 references 9 and 12'],
 'citing_work': 'Docling Technical Report (archived Auer-first version)',
 'follow_up': {'title': 'Optimized Table Tokenization for Table Structure Recognition',
     'authors': ['Maksym Lysak','Ahmed Nassar','Nikolaos Livathinos','Christoph Auer','Peter Staar'],
     'year': 2023, 'doi': '10.1007/978-3-031-41679-8_3', 'pages': '37–50',
     'class': 'DIRECT_METHOD', 'action': 'inspect next', 'full_text': 'not read'},
 'query_limit': 'Inspected retained citing work and exact references; no systematic citing-work search performed. Crossref count supplies no list.',
 'coverage': 'Concrete forward relation only; high-citation/recent/negative-result coverage remains open'})
save('omission-supplement.json', {'historical_ledgers_preserved': ['docs/design/research/omissions.json','docs/design/research/backward-snowball.json'],
 'changes': [
  {'work':'TableFormer 2022','previous':'deferred until component dependency','now':'identified main/supplement technically inspected','remaining':'training formula, checkpoint transfer, broader evaluation'},
  {'work':'Optimized Table Tokenization 2023','previous':'not assessed in this unit','now':'concrete next source lead from Docling reference 9','remaining':'method, grammar, evaluation, decoder/paper correspondence'},
  {'work':'upstream PDF conversion and TEDS/EDD comparison sources','now':'specific backward leads recorded','remaining':'targeted technical reading before stronger claims'},
  {'work':'McCarthy 1982; Caiani 2016; Imielinski/Lipski 1984; Tamer 2010','now':'existing source blockers unchanged','remaining':'new routes needed; no unchanged retries'}],
 'survey_readiness':'not_ready; this is a supplemental bounded read, not survey completion'})

defaults = [
 ('source version','official CVF accepted copy','exact title/authors and checked pages make statements locatable','metadata pagination conflict or later revision mistaken for this copy','PDF/landing identity check','reviewed source, not current-release equivalence'),
 ('training architecture and optimizer','main Section 5.1','record historical method faithfully','transfer to later release or local financial corpus without tuning','compare retained config depths/heads/dropout','source fact, not local default'),
 ('image size and training filters','main Sections 3/5; supplement 1','identify experiment population and preprocessing','downsampling or discarded ambiguous tables distorts target transfer','read Section 5.4 and separate evaluation population','historical source choice'),
 ('paper score','Table 4 and model card','identify advertised simple/complex/all figures','confuse structure-only, whole-page, semantic or deployed performance','compare Table 2 and input/text description','attributed descriptive result'),
 ('4.0.2/config selection','prior pinned loader and model metadata','concrete previously inspected comparator','assume label beam_size or version bound is operative/locked','read complete predict and text merge','baseline candidate only'),
 ('printed box loss','Equation 1 and adjacent prose','preserve source without inventing missing term','implement a wrong training objective','visually inspect formula, then require training-source clarification','unresolved; no implementation'),
 ('resource and reading bounds','audited eight-resource plan','limits acquisition while inspecting material appendix','bounded query mistaken for full correction/forward clearance','retain all attempts and explicit coverage limits','convenience bound, not acceptance threshold')]
save('default-assumption-audit.json', [{'choice':a,'provenance':b,'justification':c,'failure_mode':d,'early_diagnostic':e,'status':f} for a,b,c,d,e,f in defaults])
save('reading-review.json', {'text_read': {'main':list(range(1,11)), 'supplement':list(range(1,7))},
 'renders': json.loads((OUT / 'render-manifest.json').read_text()),
 'inspection': 'All twelve listed images inspected before this record. Main method/training/score pages and supplement correction figures were read at page resolution.',
 'render_findings': ['Equation 1 lacks explicit l1 factor expected from adjacent prose','HTML/span drawings and matching diagrams require visible geometry','Supplement correction examples are selected illustrations'],
 'reviewer': 'author/source reader', 'independent_reader':'pending', 'human_acceptance':'pending'})
print(json.dumps({'copies':len(copies),'attempts':len(receipts),'claims':len(claims),'references_considered':len(back)}))
