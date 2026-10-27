"""Build source records from explicitly inspected public documents, once."""
from fractions import Fraction as F
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re

U = Path(__file__).resolve().parent
R = U.parents[2]
OLD = R / 'data/accounting-master/r06-calculations11-source-20261020/sources'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(R))
load = lambda p: json.loads(p.read_text())


def write(name, value):
    with (U / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.links, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'a':
            self.links.append(dict(attrs).get('href', ''))

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1

    def handle_data(self, text):
        if not self.skip and text.strip():
            self.parts.append(' '.join(text.split()))


sources, normalized = [], {}
for ident, scope in [
    ('01-product', 'Complete visible index and actual links'),
    ('02-requirements', 'Complete requirements: sections 1–4 and Appendices A–B'),
    ('03-history', 'Complete visible requirements release history and actual links')]:
    p = U / 'sources' / (ident + '.body')
    parser = Text()
    parser.feed(p.read_text())
    normalized[ident] = ' '.join(parser.parts)
    visible = U / 'sources' / (ident + '.visible.txt')
    with visible.open('x') as stream:
        stream.write('\n'.join(parser.parts) + '\n')
    receipt = load(U / 'sources' / (ident + '.receipt.json'))
    assert receipt['exit_code'] == 0 and receipt['metrics']['http_code'] == 200
    assert p.stat().st_size == receipt['metrics']['size_download']
    sources.append({'id': ident, 'url': receipt['url'], 'scope_read': scope,
                    'body': {'path': rel(p), 'sha256': sha(p)},
                    'visible': {'path': rel(visible), 'sha256': sha(visible)},
                    'links': parser.links, 'receipt': rel(U / 'sources' / (ident + '.receipt.json'))})

prior = OLD / '02-calc11.visible.txt'
normalized['prior-recommendation'] = ' '.join(prior.read_text().split())
quotes = [
    ('A01','01-product','Access heading','Additional Resources (members-only)'),
    ('A02','01-product','Conformance suite label','Calculations 1.1 Conformance Suite'),
    ('A03','02-requirements','Title date','Requirements Document 25 May 2022'),
    ('A04','03-history','Displayed release date/status','2022-05-22 Supports Candidate Recommendation'),
    ('A05','02-requirements','1 Introduction','which share the same period, dimensions and other contextual information.'),
    ('A06','02-requirements','2.3 Syntactic dependencies','This effectively requires that all facts have the same dimensions, including both built-in and taxonomy-defined dimensions, and the same units.'),
    ('A07','02-requirements','2.3 Syntactic dependencies','QNames that make use of different prefixes bound to the same namespace URI should be considered equivalent, but will not be unless the comparison is type-aware.'),
    ('A08','02-requirements','3.1 Calculation consistency','Reported values should be deemed to be consistent with a calculation if there is a set of actual values from which the reported values could have been rounded which conform to the specified calculation.'),
    ('A09','02-requirements','3.2 Rounding methods','The solution should support both "round to nearest" and truncation methods.'),
    ('A10','02-requirements','3.2 Ties','Where the consistency of a calculation cannot be established without knowing which variation has been used, it should be treated as consistent.'),
    ('A11','02-requirements','3.3 Duplicate facts','Where multiple consistent facts are present, the calculation should be checked using the most precise fact available.'),
    ('A12','02-requirements','3.4 Syntax independence','The solution should be defined in terms of the report model defined in the Open Information Model and should not depend on the XML syntax defined in XBRL v2.1'),
    ('A13','02-requirements','4.1 Out of scope','It should not attempt to introduce any new functionality, such as the ability to check cross-period or other cross-dimensional calculations.'),
    ('A14','02-requirements','Appendix B','9 November 2021 Paul Warren Initial draft'),
    ('A15','prior-recommendation','5.1 Binding','Two reported data points, a and b, are dimensionally aligned if for every dimension other than the concept core dimension in the {dimensions} property of a, the same dimension is present in b with an equal dimension value.'),
    ('A16','prior-recommendation','5.4 Duplicates','Two facts are calculation 1.1 consistent duplicates if they meet the specification for OIM duplicate facts, with the modification that the interval used to establish numeric value consistency is the fact value interval, as defined in this specification.'),
    ('A17','prior-recommendation','5.5 Intersection','Where consistent duplicates are present, the calculation is performed using the intersection of fact value intervals for all facts within the set.'),
    ('A18','prior-recommendation','5.5 Example','These facts are consistent with having been rounded from a value in the range [5450, 5500], so this is the interval used for the calculation.')]
anchors = []
for ident, source, section, quote in quotes:
    text = normalized[source]
    assert quote in text, (ident, quote)
    offset = text.index(quote)
    anchors.append({'id': ident, 'source': source, 'section': section, 'quote': quote,
                    'normalized_character_span': [offset, offset + len(quote)]})
write('source-ledger.json', {'sources': sources, 'prior_recommendation': {
    'path': rel(prior), 'sha256': sha(prior), 'scope_revisited': 'Sections 4.1, 5.1–5.7'},
    'anchors': anchors, 'suite': {'status': 'not_requested_members_only_listing',
    'url': 'https://base-spec.ci.xbrl.org/calculations/1-1-0-rec1-calc11-2024-02-14/conformance/calculation-1.1-conformance-2024-02-14.zip',
    'basis': ['A01','A02'], 'not_concluded': 'No HTTP denial or global inaccessibility was observed'}})

def arithmetic():
    assert 12141123 + 45441321 == 57582444
    rounded_sum = F('12.1') + F('45.4')
    assert rounded_sum == F('57.5') != F('57.6')
    component = (F('12.05') + F('45.35'), F('12.15') + F('45.45'))
    total = (F('57.55'), F('57.65'))
    overlap = (max(component[0],total[0]), min(component[1],total[1]))
    assert component == (F('57.4'), F('57.6')) and overlap == (F('57.55'),F('57.6'))
    coarse, fine = (F(4500),F(5500)), (F(5450),F(5550))
    intersection = (max(coarse[0],fine[0]),min(coarse[1],fine[1]))
    assert intersection == (F(5450),F(5500)) and intersection != fine
    assert fine[0] <= 5525 <= fine[1] and not intersection[0] <= 5525 <= intersection[1]
    return {'actual_sum':57582444, 'rounded_sum_millions':str(rounded_sum),
            'source_reported_total_millions':'288/5',
            'calculated_interval_millions':list(map(str,component)),
            'overlap_millions':list(map(str,overlap)),
            'finer_interval':list(map(str,fine)), 'intersection':list(map(str,intersection)),
            'authored_exact_total':5525, 'finest_only_accepts':True, 'intersection_accepts':False}

write('exact-examples.json', arithmetic())
claims = [
    {'id':'C01','claim':'The official index places the suite in a members-only resource category; no suite was requested or read.', 'support':['A01','A02'], 'class':'PRIMARY_DOCUMENTARY_SUPPORT'},
    {'id':'C02','claim':'The 2022 requirements support preserving common contextual dimensions and exclude new cross-dimensional functionality.', 'support':['A05','A06','A07','A12','A13'], 'class':'PRIMARY_TECHNICAL_SUPPORT'},
    {'id':'C03','claim':'That design intent supports the prior contextual equality reading but does not amend the literal 5.1 definition.', 'support':['A06','A13','A15'], 'class':'LOCAL_INTERPRETATION_NOT_NORMATIVE_CORRECTION'},
    {'id':'C04','claim':'The early most-precise duplicate requirement differs from the final intersection rule; the final example demonstrates the distinction.', 'support':['A11','A17','A18'], 'class':'SOURCE_COMPARISON_AND_EXACT_DERIVATION'},
    {'id':'C05','claim':'The index/history date is 22 May, while the linked document title and URL say 25 May 2022.', 'support':['A03','A04'], 'class':'PRIMARY_DOCUMENTARY_SUPPORT'},
    {'id':'C06','claim':'Neither the broad duplicate requirement nor the unread suite resolves the section 5.4 OIM reference mismatch.', 'support':['A11','A16'], 'class':'BOUNDED_UNRESOLVED_SOURCE_QUESTION'}]
write('claim-support-ledger.json', {'claims':claims,'manuscript_change':False,'normative_correction':False})
write('source-support-ledger.json', {'sources':[
    {'id':s['id'],'classification':'PRIMARY_STANDARDS_DOCUMENT' if s['id']=='02-requirements' else 'OFFICIAL_DISCOVERY_METADATA',
     'local':s['body'],'technical_read':s['scope_read'],
     'status':'Requirements; supports candidate recommendation' if s['id']=='02-requirements' else 'Publisher index',
     'correction_status':'Linked release history inspected; index/date discrepancy retained; no global absence-of-correction claim'} for s in sources],
    'suite_status':'advertised members-only; not acquired; no test cases inspected'})
write('citation-venue-ledger.json', {'scope':'Standards and official indexes, not an academic-paper survey',
    'citation_counts':'not available and not used','venue_ranking':'not applicable',
    'source_dates':{'product_index_display':'2022-05-22','requirements_title':'2022-05-25','history_display':'2022-05-22'}})
write('backward-snowball-ledger.json', {'references':[
    {'source':'XBRL 2.1 corrected 2013 specification','disposition':'Retained and technically inspected in predecessor; no re-download'},
    {'source':'OIM work-product index','disposition':'Existing normative OIM dependency retained; no index request needed'},
    {'source':'Calculations 2.0 requirements 2019-02-06','disposition':'New explicit related-source lead; outside this 1.1 source inquiry'},
    {'source':'XBRL legal page','disposition':'Legal-policy navigation; no rights clearance inferred; original Appendix A preserved'}]})
write('forward-snowball-ledger.json', {'scope':'Official release progression, not citation search',
    'checked':'2022 requirements release history and already retained corrected 2024 Recommendation',
    'disposition':'Recommendation supersedes the requirements as operational comparator; no exhaustive correction search claim'})
write('omission-risk-ledger.json', {'risks':[
    {'source':'Dated official conformance suite','status':'not acquired','reason':'members-only resource listing','impact':'Expected test results and coverage remain unknown'},
    {'source':'Normative clarification of sections 5.1/5.4','status':'not obtained','reason':'Requirements give intent but no authoritative correction','impact':'Conditional interpretation remains labelled'},
    {'source':'Calculations 2.0 requirements','status':'new lead not yet read','reason':'Different proposed scope','impact':'No transfer of broader functionality to 1.1'},
    {'source':'Installed processor and actual report policy','status':'unadmitted','reason':'Runtime and policy selection outside preparation','impact':'No conformance or issuer-error claim'}]})
print(json.dumps({'sources':len(sources),'anchors':len(anchors),'claims':len(claims),'suite_tests_read':0,'exact_examples':'passed'}))
