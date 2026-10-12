"""Documentary exchange and expected queries; this is not a product adapter."""
import json
from prepare import OUT, ROOT, PDF, EXPECTED, sha, save

assert not (OUT / 'annotation.json').exists(), 'Preserve existing evidence'
context = dict.fromkeys(['entity','perimeter','concept','period','currency','unit','scale','sign','precision','basis'])
context.update(entity='HSBC Holdings plc', concept='cover_title')
raw = (OUT / 'pymupdf-page1.txt').read_text()
readings = [
    {'reading_id':'hsbc-cover-raw-text','evidence_kind':'extraction_reading',
     'meaning':'PyMuPDF returns both Accounts 2024 and Accounts 2023 in the cover text.',
     'value_exact':None,'context':context,'status':'proposed',
     'reason':'Faithful record of the raw output, not a decision about the visible report year.',
     'supporting_annotation_ids':[]},
    {'reading_id':'hsbc-cover-visible-2023','evidence_kind':'extraction_reading',
     'meaning':'The inspected rendered title reads HSBC Holdings plc, Annual Report and Accounts 2023.',
     'value_exact':'2023','context':context | {'concept':'visible_cover_report_year'},'status':'proposed',
     'reason':'Author inspection of the same PDF page, supported by later opaque painting over the earlier 2024 text.',
     'supporting_annotation_ids':[]},
    {'reading_id':'hsbc-cover-report-year-2024','evidence_kind':'extraction_reading',
     'meaning':'Interpret the earlier Accounts 2024 characters as the visible cover report year.',
     'value_exact':'2024','context':context | {'concept':'visible_cover_report_year'},'status':'rejected_with_reason',
     'reason':'Wrong for the visible cover: the earlier text is covered by a later opaque rectangle. Its characters remain in the raw extraction.',
     'supporting_annotation_ids':[]}
]
save('annotation.json',{'annotation_id':'hsbc-2023-annual-cover-visibility-20261012',
    'document_id':'hsbc-2023-annual','original_sha256':EXPECTED,
    'source':{'format':'pdf','section':'Cover','locator':'Physical PDF page 1, upper-left title; complete page-1 text extraction, characters 0 through '+str(len(raw))+' (end exclusive).',
        'extracted_text_sha256':sha(OUT/'pymupdf-page1.txt'),'incorporated_document_ids':[]},
    'literal':raw,'readings':readings,'review_status':'internally_checked',
    'review_evidence':['author-review.md; author inspection on 2026-10-12, source cover and baseline manuscript slice',
        'initial-renders.json; same PDF/page render binding','paint-evidence.json; selected rendering-order records'],
    'open_questions':['Independent adjudication pending.',
        'Historical availability of the selected annual-report bytes is unverified.',
        'No general PDF visibility classifier or document-wide extraction validation is established.']})
save('query-examples.json',{'kind':'Proposed expected behavior; not an executed engine or API',
    'examples':[
        {'query':'Search the raw page extraction for 2024','expected':'hit',
         'reason':'Raw extracted characters are preserved even when later covered.'},
        {'query':'Read the visible cover report year','expected':'2023',
         'status':'author-supported proposed reading; independent acceptance pending',
         'reason':'The selected render and paint sequence support the visible title.'},
        {'query':'Automatically admit 2024 as this report year from the raw hit','expected':'reject interpretation; retain raw occurrence',
         'reason':'Text presence alone does not establish visibility or report identity.'},
        {'query':'Admit this selected annual PDF to a historical evidence view using only its cover year','expected':'unresolved availability',
         'reason':'Report year does not supply an availability timestamp for these bytes.'},
        {'query':'Replace a hypothetical previously accepted 2024 report-year reading','expected':'create corrected reading; explicit Supersede after layer-specific review',
         'reason':'Invalidate dependent results in the new view; preserve frozen old runs and their original decisions. No actual accepted 2024 reading is asserted.'},
        {'query':'Treat the two extracted years as contradictory issuer accounting assertions','expected':'unsupported conflict classification',
         'reason':'This case concerns covered characters, not two inspected incompatible accounting assertions.'}
    ]})
schema = ROOT/'data/financial-report-benchmark/annotation-record.schema.json'
import jsonschema
jsonschema.Draft202012Validator(json.loads(schema.read_text())).validate(json.loads((OUT/'annotation.json').read_text()))
print(json.dumps({'schema_valid':True,'readings':len(readings),'query_examples':6,'product_execution':False}))
