"""Author-entered annotation preparation; not a product extractor or gold oracle."""
from pathlib import Path
import hashlib
import json
import platform
import re
import sys
from datetime import datetime, timezone

import fitz
from lxml import html, etree

ROOT = Path(__file__).resolve().parent
SELECTION = json.loads((ROOT / 'selection.json').read_text())
DOCS = {r['document_id']: r for r in SELECTION['records']}
LABELS, OCCURRENCES = [], []
FIELDS = ['entity', 'perimeter', 'concept', 'period', 'currency', 'unit',
          'scale', 'sign', 'precision', 'basis']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make(ident, docid, section, literal, locator, meaning=None, context=None,
         value=None, support=(), questions=(), kind='context_support'):
    record = DOCS[docid]
    ctx = {k: None for k in FIELDS}
    ctx.update(context or {})
    LABELS.append({
        'annotation_id': ident, 'document_id': docid,
        'original_sha256': record['sha256'],
        'source': {'format': locator['format'], 'section': section,
                   'locator': locator['description'], 'incorporated_document_ids': []},
        'literal': literal,
        'readings': [] if meaning is None else [{
            'reading_id': ident + ':reading-v1', 'evidence_kind': 'source_assertion',
            'meaning': meaning, 'value_exact': value, 'context': ctx,
            'status': 'proposed', 'supporting_annotation_ids': list(support)}],
        'review_status': 'provisional', 'open_questions': list(questions)})
    field_support = {}
    for field in FIELDS:
        field_support[field] = {
            'state': 'unknown' if ctx[field] is None else 'proposed_supported',
            'value': ctx[field], 'support_occurrence_ids': list(support) + [ident]
            if ctx[field] is not None else []}
    OCCURRENCES.append({
        'occurrence_id': ident, 'source_version_id': 'sha256:' + record['sha256'],
        'kind': kind, 'locator': locator, 'field_support': field_support,
        'location_status': 'resolves_checked',
        'semantic_review': 'author_provisional_not_independently_adjudicated',
        'dimensions_status': 'not_completely_annotated',
        'publication_evidence': {
            'date': record['metadata'].get('publication_date'),
            'status': record['metadata']['publication_date_status'],
            'retained_evidence': record['packet_landing'],
            'historical_retained_byte_availability': 'not_established'},
        'acquisition_record_attempted_at': record['acquisition_record_attempted_at']})


def pdf(ident, docid, number, box, section, literal=None, **kwargs):
    doc = fitz.open(ROOT / DOCS[docid]['packet_source'])
    p = doc[number - 1]
    clip = fitz.Rect(box)
    extracted = p.get_textbox(clip).strip()
    assert extracted, (ident, box)
    render = ROOT / 'rendered' / f'{docid}-p{number}.png'
    if not render.exists():
        p.get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(render)
    literal = extracted if literal is None else literal
    locator = {'format': 'pdf', 'physical_page_1based': number,
               'printed_page_label': str(number - (1 if docid.startswith('midea') else 2)),
               'bbox_points': list(box), 'origin': 'top_left',
               'page_dimensions_points': [p.rect.width, p.rect.height],
               'extracted_text': extracted, 'render_path': str(render.relative_to(ROOT)),
               'render_sha256': digest(render),
               'description': f'physical PDF page {number}; bbox {box} points, top-left; {section}',
               'literal_basis': 'author_read_render' if literal != extracted else 'text_and_render'}
    make(ident, docid, section, literal, locator, **kwargs)


APPLE_BYTES = (ROOT / DOCS['apple-2025-q1']['packet_source']).read_bytes()
APPLE = html.fromstring(APPLE_BYTES)


def raw_html_element(element_id):
    pattern = rb'<(?P<tag>[A-Za-z0-9_:.-]+)\b[^>]*\bid="' + re.escape(element_id.encode()) + rb'"[^>]*>'
    matches = list(re.finditer(pattern, APPLE_BYTES))
    assert len(matches) == 1, element_id
    found = matches[0]
    close = b'</' + found.group('tag') + b'>'
    end = APPLE_BYTES.index(close, found.end()) + len(close)
    data = APPLE_BYTES[found.start():end]
    attrs = {m.group(1).decode(): m.group(2).decode() for m in
             re.finditer(rb'([A-Za-z_:][A-Za-z0-9_:.-]*)="([^"]*)"', found.group())}
    return data, {'start_byte':found.start(),'end_byte_exclusive':end,
                  'sha256':hashlib.sha256(data).hexdigest(),
                  'opening_tag_utf8':found.group().decode()}, attrs


def apple(ident, element_id, section, relative=None, markup=False, **kwargs):
    node = APPLE.get_element_by_id(element_id)
    raw, source_span, attrs = raw_html_element(element_id)
    if relative:
        node = node.xpath(relative)[0]
    literal = raw.decode() if markup else ''.join(node.itertext()).strip()
    locator = {'format': 'html', 'element_id': element_id, 'relative_xpath': relative,
               'capture': 'original_element_bytes' if markup else 'parsed_visible_itertext',
               'description': f'original HTML id={element_id}' + (f'; relative XPath {relative}' if relative else ''),
               'anchor_original_attributes': attrs, 'parser_attributes':dict(node.attrib),
               'original_anchor_bytes':source_span,
               'parser':'lxml.html; parsed names may be lowercase; original anchor preserved separately'}
    make(ident, 'apple-2025-q1', section, literal, locator, **kwargs)


apple('A-context', 'c-1', 'Inline duration context', markup=True,
      meaning='Source context c-1 identifies CIK 0000320193, start 2024-09-29 and end 2024-12-28; no explicit segment members in this context.')
apple('A-instant', 'c-17', 'Inline instant context', markup=True,
      meaning='Source instant is 2024-12-28. A library exclusive datetime boundary on 2024-12-29 is a different representation, not the reported date.')
apple('A-unit', 'usd', 'Inline currency unit', markup=True,
      meaning='The unit references iso4217:USD.')
apple('A-policy', 'f-265', 'Note 1 basis and incorporated annual report', relative='./div[2]/span',
      meaning='The Company describes Apple Inc. and wholly owned subsidiaries, US GAAP, recurring adjustments and management estimates; it incorporates FY2024 annual statements and notes.',
      questions=['FY2024 annual report is retained in the corpus, but this packet has not closed or semantically annotated the incorporated notes.'])
apple('A-heading', 'f-58', 'Statement heading and scale',
      relative='ancestor::table/../preceding-sibling::div[2]',
      meaning='Statement heading gives millions except share and per-share amounts; retain exceptions.')
a_ctx = dict(entity='Apple Inc.', perimeter='Apple Inc. and wholly owned subsidiaries',
             concept='us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (reported Total net sales)',
             period='duration 2024-09-29 through 2024-12-28; fiscal FY2025 Q1, not calendar Q1',
             currency='USD', unit='currency', scale='1000000', sign='positive',
             precision='inline decimals=-6; scale=6; reported numeral is not an unrounded economic amount',
             basis='US GAAP as stated by issuer')
for ident, fact, section in [('A-sales-statement','f-58','Condensed consolidated statements of operations'),
                             ('A-sales-note','f-279','Note 2 disaggregated products and services')]:
    apple(ident, fact, section, value='124300', context=a_ctx,
          meaning='Reported total net sales of USD 124,300 million for the source fiscal quarter.',
          support=('A-context','A-unit','A-policy','A-heading'), kind='reported_amount')
apple('A-assets', 'f-134', 'Consolidated balance sheet, Total assets', value='344085',
      meaning='Reported total assets at the source instant 2024-12-28.',
      context={**a_ctx, 'concept':'us-gaap:Assets (reported Total assets)',
               'period':'instant 2024-12-28'},
      support=('A-instant','A-unit','A-policy'), kind='reported_amount')

hsbc='hsbc-2024-annual'
pdf('H-heading',hsbc,343,[40,80,555,220],'Consolidated statement title, year headers, units and interest rows',
    meaning='The first numeric column is 2024; $m applies to these interest rows; consolidated annual results.')
pdf('H-basis',hsbc,355,[40,400,554,506],'Note 1.1(a) basis',
    meaning='Issuer states UK-adopted standards, EU-adopted standards and IASB IFRS compliance with no applicable differences for the periods presented.')
pdf('H-currency',hsbc,356,[40,180,554,239],'Note 1.1(d) presentation currency',
    meaning='HSBC consolidated statements are presented in US dollars.')
pdf('H-footnotes',hsbc,343,[40,580,555,775],'Interest and other statement footnotes',
    questions=['Footnotes 1–3 qualify interest amounts; their components are retained here but not fully decomposed into assertion records.'])
h_ctx=dict(entity='HSBC Holdings plc',perimeter='HSBC consolidated group',
           concept='Net interest income',period='year ended 2024-12-31',currency='USD',
           unit='currency',scale='1000000',sign='positive',
           precision='reported integer millions; rounding rule not established',
           basis='UK/EU adopted and IASB IFRS as stated in Note 1.1(a)')
pdf('H-net-interest',hsbc,343,[436,183,460,192],'Net interest income, 2024 column',literal='32,733',
    meaning='Reported consolidated net interest income.',value='32733',context=h_ctx,
    support=('H-heading','H-basis','H-currency','H-footnotes'),kind='reported_amount')
pdf('H-interest-expense',hsbc,343,[434,202,462,212],'Interest expense, 2024 column',literal='(75,898)',
    meaning='Reported interest expense is shown as a deduction in parentheses; debit/credit convention is not inferred.',
    value='-75898',context={**h_ctx,'concept':'Interest expense','sign':'negative presentation (parentheses)'},
    support=('H-heading','H-basis','H-currency','H-footnotes'),kind='reported_amount')

munich='munich_re-2024-annual'
pdf('R-heading',munich,206,[49,76,548,141],'Consolidated income statement title and headers',
    meaning='Consolidated results for financial year 2024; first value column is EUR millions. Note numbers are separate from amounts.')
pdf('R-basis',munich,211,[50,185,292,245],'Basis of preparation, Application of IFRS Accounting Standards',
    meaning='Issuer states IFRS as adopted by the EU and additional German HGB requirements; this is not silently replaced by an IASB-only claim.')
pdf('R-rounding',munich,211,[50,275,292,347],'Presentation of figures',
    meaning='Amounts are rounded to million euros and totals may deviate; bracket references concern comparatives and signs depend on presentation context.')
pdf('R-row-labels',munich,206,[50,144.6,353,259],'Rows 1–6, insurance/reinsurance labels and note references; amounts located separately',
    meaning='Issued insurance revenue, ceded revenue, reinsurance income and the reinsurance service result are different measures.')
r_ctx=dict(entity='Munich Re',perimeter='Munich Re consolidated group',
           concept='Insurance revenue from insurance contracts issued',period='financial year 2024',
           currency='EUR',unit='currency',scale='1000000',sign='positive',
           precision='rounded million EUR; tie-breaking rule not stated',
           basis='EU-adopted IFRS plus German HGB Section 315e(1) as stated')
for ident,box,literal,value,concept in [
    ('R-revenue',[373.7,144.6,397,154.45],'60,830','60830','Insurance revenue from insurance contracts issued'),
    ('R-ceded',[374.1,228.2,397,238.0],'–1,666','-1666','Insurance revenue ceded from reinsurance contracts held'),
    ('R-reinsurance-income',[384.2,238.65,397,248.45],'486','486','Income from reinsurance contracts held'),
    ('R-reinsurance-result',[374.1,248.9,397,258.96],'–1,181','-1181','Insurance service result from reinsurance contracts held')]:
    pdf(ident,munich,206,box,concept+', 2024 column',literal=literal,value=value,
        meaning='Reported consolidated '+concept.lower()+'.',
        context={**r_ctx,'concept':concept,'sign':'negative presentation' if value.startswith('-') else 'positive'},
        support=('R-heading','R-basis','R-rounding','R-row-labels'),kind='reported_amount',
        questions=['Extracted PDF text replaces the visible thousands comma with U+FFFD in this clip; sorted text may present a space. Visible comma transcribed from render.' ] if ',' in literal else ())

midea='midea-2024-annual'
pdf('M-heading',midea,158,[84,70,525,184],'Company name, statement title and four year/perimeter headers',
    meaning='人民币千元; consolidated 2024, consolidated 2023 (restated), parent 2024, parent 2023 are distinct columns.')
pdf('M-basis',midea,166,[85,172,526,375],'Notes II(1)–(2), preparation and compliance',
    meaning='Issuer states ASBE basic/specific standards and CSRC reporting requirements; preserve the claim as issuer evidence.')
pdf('M-calendar-currency',midea,166,[85,413,526,519],'Notes II(3)–(4), calendar and presentation currency',
    meaning='Calendar year is 1 January–31 December; presentation currency is RMB, while subsidiaries may use other functional currencies.')
pdf('M-revenue-rows',midea,158,[106,209,525,260],'营业收入, 利息收入 and 手续费及佣金收入 rows',
    meaning='Preserve revenue versus interest/fee rows and group versus parent columns separately.')
m_ctx=dict(entity='美的集团股份有限公司',perimeter='合并 (consolidated group)',concept='营业收入',
           period='2024-01-01 through 2024-12-31',currency='CNY (人民币)',unit='currency',scale='1000',
           sign='positive',precision='reported integer RMB thousands; rounding rule not established',
           basis='ASBE and CSRC reporting requirements as stated by issuer')
for ident,box,literal,value,overrides in [
    ('M-group-revenue',[273,222,330,235],'407,149,600','407149600',{}),
    ('M-parent-revenue',[419,222,458,235],'946,607','946607',{'perimeter':'公司 (parent only)'}),
    ('M-restated-revenue',[336,222,394,235],'372,037,280','372037280',
     {'period':'2023-01-01 through 2023-12-31 comparative, 经重列 (restated)'})]:
    pdf(ident,midea,158,box,'营业收入, specific year/perimeter column',literal=literal,
        meaning='Reported 营业收入; retain perimeter and comparative-version qualifications.',
        value=value,context={**m_ctx,**overrides},support=('M-heading','M-basis','M-calendar-currency','M-revenue-rows'),kind='reported_amount',
        questions=['Reason and scope of 2023 restatement are outside this selected span.'] if 'restated' in ident else ())
pdf('M-parent-interest-dash',midea,158,[452,235,458,248],'利息收入, parent 2024 column',literal='-',
    questions=['Dash is visibly present. Zero, inapplicability or another convention is not resolved here; value remains unknown.'],kind='unresolved_symbol')
pdf('M-revenue-note-reference',midea,158,[231,209,267,234],'营业收入 note references 四(49), 十八(3)',
    questions=['References identify group and parent revenue notes; target sections exist in the report but their scope and content are not annotated in this pilot.'],kind='reference_frontier')

def write(name, value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

write('labels-v1.json',LABELS)
write('occurrence-index-v1.json',{'schema_version':1,'status':'proposed sidecar, not a selected product API',
      'occurrences':OCCURRENCES,'relations':[
      {'from':'A-sales-statement','to':'A-sales-note','relation':'candidate_same_assertion',
       'basis':'same source concept, c-1, USD, value, decimals; repeated source locations remain separate',
       'independent_evidence_count':1,'adjudication':'pending'},
      {'from':'M-group-revenue','to':'M-parent-revenue','relation':'different_perimeter_not_alias'},
      {'from':'M-restated-revenue','relation':'comparative_revision_without_prior_version_comparison'}]})
write('build-manifest.json',{'created_at':datetime.now(timezone.utc).isoformat(),
      'command':'python3 build_pilot.py','python':sys.version,'platform':platform.platform(),
      'pymupdf':fitz.VersionBind,'lxml':etree.LXML_VERSION,'git_commit':'N/A: source inputs pinned by SHA256; no usable Git history asserted',
      'random_seeds':'N/A: author-entered deterministic annotation','CPU_GPU':'CPU-only PDF/XML operations; no GPU framework imported',
      'plan':'PLAN.md','result':'RESULT.md','implementation_status':'proposal preparation only',
      'labels':len(LABELS),'source_hashes':{k:v['sha256'] for k,v in DOCS.items()}})
print('Wrote',len(LABELS),'provisional located records')
