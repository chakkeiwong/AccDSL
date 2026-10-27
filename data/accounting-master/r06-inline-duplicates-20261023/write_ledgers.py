"""Record selected technical reading, scoped obligations and six ledgers once."""
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
U = Path(__file__).resolve().parent
R = U.parents[2]
d = json.loads((U / 'source-ledger.json').read_text())


def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


spans = {
 '01-primer2013': [[1,55],[244,322],[432,470],[645,687],[1003,1021]],
 '02-spec2013': [[1,42],[669,785],[2663,2794],[3343,3450],[4336,4495],
                 [5031,5292],[5333,5399],[5680,5722]],
 '03-primer2026': [[1,55],[187,334],[444,480],[665,698],[1003,1030]],
 '04-spec2026': [[1,45],[337,499],[535,789],[2174,5350],[5367,5442],[5615,5754]],
 '05-spechistory': [[1,44]],
 '06-primerhistory': [[1,47]],
}
reading = []
for ident, ranges in spans.items():
    n = len((U / 'sources' / (ident + '.visible.txt')).read_text().splitlines())
    assert all(1 <= a <= b <= n for a,b in ranges)
    structure = json.loads((U / 'sources' / (ident + '.structure.json')).read_text())
    assert structure['images'] == ([] if ident[0] != '0' or ident[1] not in '56' else
                                    [{'src':'css/assets/img/xbrl-logo.png','alt':'XBRL'}])
    reading.append({'source':ident, 'binding':d['sources'][ident], 'visible_lines':n,
                    'actually_read_spans':ranges,
                    'scope':'Complete history' if ident.endswith('history') else 'Selected technical/status/history passages only',
                    'images':structure['images'],
                    'image_disposition':'Navigation logo only; no technical figure' if ident.endswith('history') else 'No embedded image',
                    'remaining_text':'Not credited as read; matching source blocks in version-comparison.json are compared, not independently reread'})
write('reading-ledger.json', {'method':'Small complete retained-text spans; broad truncated output grants no reading credit',
                             'sources':reading,
                             'html_structure_inspection':'04-spec2026.body lines3105–3130 inspected; language paragraph inside div.nonNormativeNote',
                             'whole_specification_read':False,
                             'external_dependencies':'No Part2 schema, registry implementation or conformance suite read/executed in this unit'})

claims = []
def c(ident, target, support, verdict, actual, limit, support_class='PRIMARY_TECHNICAL_SUPPORT'):
    claims.append({'id':ident, 'claimed_target':target, 'support':support,
                   'verdict':verdict, 'actual_evidence':actual, 'limit':limit,
                   'support_class':support_class})
c('I01','Document authority', ['P2013-status','P2026-status','S2013-norm','S2026-norm'],
  'checked','Both Primers are non-normative; both Part1 editions declare normative status.',
  'Local non-normative content remains distinct within a normative document.')
c('I02','Target partition', ['S2013-target','S2026-target'], 'checked',
  'All required facts/relationships must be mapped for each unique target value; selected section3.2 text is unchanged.',
  'Different inputs/files and different targets are different partitions; no global merging rule follows.')
c('I03','Optional item de-duplication', ['P2013-option','P2026-option','S2026-exist'], 'qualified support',
  'Primer permits discretion. Per-input existential mapping does not itself demand pairwise distinct output nodes.',
  'One output can serve multiple inputs only if it satisfies every applicable mapping obligation; no sufficient algorithm or processor result established.',
  'PRIMARY_TECHNICAL_SUPPORT_AND_PROJECT_DERIVATION')
c('I04','Numeric output values', ['S2026-value','P2013-different','P2026-different'], 'checked',
  'Non-nil numeric mapping applies the declared format transformation, scale and sign; the Primer says differing values must both appear.',
  'Displayed lexical strings alone are not the mapped values. Nil exempts child-content rule; no registry transform executed.')
c('I05','Accuracy reduction during transformation', ['S2026-accuracy','S2026-precision'], 'checked',
  'Exact declared decimals/precision attributes and their prescribed absence must be preserved, not replaced with a highest-accuracy representative.',
  'This is transformation mapping, separate from a subsequent analytical de-duplication policy.')
c('I06','IDs/custom-attribute collapse', ['S2026-id','S2026-other','P2013-custom','P2026-custom'], 'local necessary condition proved',
  'An output cannot have id=a and id=b for unequal non-absent input IDs. Nor can a single mapped attribute with one expanded name have two unequal required values.',
  'No claim that every custom-attribute difference prevents merging: different names or absent constraints may be compatible; no sufficiency proof.',
  'PROJECT_DERIVATION')
c('I07','Non-numeric and nil mapping', ['S2026-other','S2026-lang','S2026-lang-root'], 'checked within selected text',
  'Section11.2 requires the input concept/context/ID/other attributes and transformed content; its child-content obligation excludes nil facts.',
  'No DTS/datatype, schema or transformation validation was executed; value-space equality is not assumed to settle every mapping condition.')
c('I08','Language inheritance', ['P2013-ancestor','P2026-ancestor','S2026-lang','S2026-lang-root'], 'source tension preserved',
  'Both Primers mention ancestor language propagation; the corrected Part1 adds a nonNormativeNote distinguishing explicit item language and target-root language from arbitrary Inline ancestor inheritance.',
  'Addition is not independently dated by AppendixE and is not a new normative MUST. No installed behavior or global errata claim.')
c('I09','Tuple duplicates', ['P2013-tuple','P2026-tuple','S2026-tuple-unique','S2026-tuple-equality','S2026-tuple-literal','S2026-tuple-map'],
  'checked','Tuple content has unique order, must satisfy same-order whitespace-normalized equality, and is emitted in order; duplicate-child reduction is described as necessary.',
  'Literal equality includes attributes. Preserve the exact set/validation wording; no independent schema or algorithm conformance established.')
c('I10','Relationship mapping', ['S2013-relation','S2026-relation'], 'edition difference checked',
  'Corrected13.2 requires the two mapped facts to satisfy the rules for F and N respectively; original says f and F. Required relationships remain part of target obligations.',
  'The 2013 expression is retained as written. No footnote-subtree/schema conformance, deletion or rewriting permission inferred.')
c('I11','2018 complete-duplicate shorthand', ['N2018-complete','N2018-processing','S2026-other','S2026-accuracy'],
  'requires qualification','Note complete equality ignores custom attributes/footnotes; it cannot be used as a sufficient input/output collapsing predicate for the inspected mapping rules.',
  'The note remains guidance. Its formula/calculation recommendations are separate inquiries.',
  'PRIMARY_TECHNICAL_SUPPORT_AND_PROJECT_DERIVATION')
c('I12','Edition and history comparison', ['H-primer-date','H-spec-current','P2026-revision','S2026-validation','S2026-registry'],
  'checked with provenance limit','Retained index exposes July2026 corrected sources. Primer revision entry17Nov2015 differs from publication index9Dec2015; validation and registry text visibly changed.',
  'Revision/publication dates need not match. No latest-worldwide or exhaustive correction-coverage inference.')
c('I13','Processor/suite conformance', ['S2013-dts','S2026-dts','S2013-norm','S2026-norm'], 'not evaluated',
  'DTS access is optional; source inspection establishes text obligations only.',
  'Part2 schema, acquired code, conformance pairs and installed behavior were not executed or admitted.')
c('I14','Occurrence/provenance retention', ['P2026-option','N2018-complete','S2026-target','S2026-relation'], 'engineering consequence only',
  'Target-document mapping can omit some duplicate occurrences while still differing from archival source-preservation needs.',
  'Retain raw IXDS, occurrence links and unresolved conflicts; no issuer, policy, vintage, manuscript or whole-row promotion.',
  'PROJECT_DERIVATION')
known = {a['id'] for a in d['anchors']}
assert all(set(x['support']) <= known for x in claims)
write('claim-support-ledger.json', {'claims':claims})
write('obligation-comparison.json', {'rows':[
 {'id':x['id'],'question':x['claimed_target'],'status':x['verdict'],
  'required_or_permitted':x['actual_evidence'],'boundary':x['limit'],'support':x['support']}
 for x in claims]})

write('source-support-ledger.json', {'scope':'Dated official documentary comparator; selected reading only', 'sources':[
 {'id':k,'title':(U/'sources'/(k+'.visible.txt')).read_text().splitlines()[0],
  'authors_editors':'Philip Allen; listed contributors preserved in retained headers' if 'history' not in k else 'XBRL International official index',
  'doi_arxiv':'N/A official standard/guidance',
  'url':json.loads((U/'sources'/(k+'.receipt.json')).read_text())['url'],
  'local':d['new_documents'][k],
  'classification':'PRIMARY_OFFICIAL_TECHNICAL_SOURCE' if 'history' not in k else 'OFFICIAL_EDITION_METADATA',
  'publication_status':'See retained exact title/header; Primer non-normative, Part1 normative, histories metadata',
  'correction_status':'Actual selected text compared with2013/2026; histories and AppendixD/E read; language clarification not separately listed in AppendixE',
  'retraction_quarantine':'No notice in inspected status/history; no global search',
  'full_text_status':'Retained complete, selected reading spans in reading-ledger.json; not full conformance review',
  'technical_anchors':[x['id'] for x in d['anchors'] if x['source']==k],
  'allowed':'Scoped source/version obligations and explicit local logical deductions',
  'forbidden':'Installed conformance, archival/semantic completeness, policy adoption or latest-worldwide claim'}
 for k in spans]})
write('citation-venue-ledger.json', {'sources':[
 {'id':k,'access_local_date':'2026-10-23 Asia/Shanghai; UTC bounds in receipt',
  'citation_count':'not available; not a promotion criterion',
  'citation_source':'No citation-metadata service queried',
  'venue':'XBRL International technical publication',
  'venue_ranking':'N/A standards and guidance; no journal ranking inference',
  'caveat':'Publication/revision/status dates remain separate'} for k in spans]})
refs = [
 ('Inline XBRL Schema','DIRECT_METHOD','Not acquired/read in this unit; required for full conformance.'),
 ('Inline XBRL Transformations','DIRECT_METHOD','Only selected contract read; no exact transform invocation or registry certification.'),
 ('XBRL2.1','FOUNDATIONAL','Earlier retained source work provides context; no new whole-standard review.'),
 ('XML/XML Names/XML Base/XML Infoset/XML Schema Structures/Datatypes/XPath1.0','FOUNDATIONAL','Technical terms delegated by specification; elementary incompatible-single-attribute argument only, no full XML validation.'),
 ('XLink','FOUNDATIONAL','Selected13.2 read, no full linkbase validation.'),
 ('XBRL Registry/Function Definitions','DIRECT_METHOD','16.2 version condition read, no full registry/function audit.'),
 ('RFC2119/TECH-WG-PROCESSES','BACKGROUND','Requirement wording/status context; no independent process-certification claim.'),
 ('Report Packages','DIRECT_METHOD','2026 Primer2.2.1 read; discovery remains a separate dependency.'),
 ('Duplicate Facts WGN','DIRECT_METHOD','Complete exact2018 note already frozen; reused by anchors, not reread as a new completed unit.'),
 ('Formula1.0','DIRECT_METHOD','2018note5.2 claim remains a separate ready source inquiry; no inference from Inline mapping.'),
]
write('backward-snowball-ledger.json', {'scope':'Relevant dependencies screened from selected sections and complete current Part1 AppendixA; not a scholarly citation survey',
                                      'rows':[{'work':a,'classification':b,'disposition':c} for a,b,c in refs]})
write('forward-snowball-ledger.json', {'query':'Retained official Part1/Primer release histories and prior index, accessed23October2026 local',
                                     'sources':['05-spechistory','06-primerhistory'],
                                     'result':'Exact July2026 corrected Part1 and Working Group Note Primer compared with exact2013 pair.',
                                     'scope':'Official edition lineage only; no citation-network coverage or latest-global claim',
                                     'next':'Formula claim in the already retained2018note; inspect exact cited source before using it.'})
write('omission-risk-ledger.json', {'rows':[
 {'topic':a,'reason':c,'support_status':'Not promoted beyond selected checked text',
  'reviewer_objection':'Does the omitted dependency change the stronger conformance/policy inference?',
  'disposition':'Separate dependency; blocks stronger claim, not this bounded documentary comparison'} for a,b,c in refs if a!='Duplicate Facts WGN'],
 'additional_risks':['No full2013/2026 specification reading claim',
                     'No arbitrary ancestor language inheritance or correction-date inference',
                     'No equivalence between value-space duplicate classes and sufficient mapping predicates',
                     'No running processor, suite, issuer compliance, source completeness or vintage admission']})
print(json.dumps({'research_ledgers':6,'claims':len(claims),'obligation_rows':len(claims),
                  'selected_reading_sources':len(reading),'whole_specification_read':False}))
