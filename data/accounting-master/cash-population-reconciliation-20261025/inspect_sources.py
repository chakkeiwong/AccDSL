"""Replay retained bytes and selected cash facts; no source admission."""
from pathlib import Path
from hashlib import sha256
from collections import defaultdict
import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDFS = {
    '2024': 'docs/design/cases/apple/annual-2024.pdf',
    '2023': 'data/financial-report-benchmark/documents/apple/apple-2023-annual/original.pdf',
}
ARCHIVE = 'docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.zip'
HTML = 'docs/design/cases/apple/p02-v1/annual-2024-official.html'
NS = {'x': 'http://www.xbrl.org/2003/instance',
      'd': 'http://xbrl.org/2006/xbrldi',
      'l': 'http://www.xbrl.org/2003/linkbase',
      'a': 'http://www.w3.org/1999/xlink'}
CONCEPTS = {'CashAndCashEquivalentsAtCarryingValue',
    'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',
    'RestrictedCashAndCashEquivalents', 'DebtSecuritiesAvailableForSaleRestricted'}

def digest(data): return sha256(data).hexdigest()
def local(tag): return tag.rsplit('}', 1)[-1]
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def inspect():
    sources = {name: digest((ROOT / name).read_bytes())
               for name in [*PDFS.values(), ARCHIVE, HTML]}
    pages, searches = {}, {}
    for year, path in PDFS.items():
        doc = fitz.open(ROOT / path)
        selected = [33, 35, 39, 45] if year == '2023' else [34, 36, 40, 46]
        pages[year] = [{'pdf_page': p, 'text': doc[p-1].get_text(),
                        'page_text_sha256': digest(doc[p-1].get_text().encode())}
                       for p in selected]
        hits = []
        for n, page in enumerate(doc, 1):
            text = ' '.join(page.get_text().split())
            for match in re.finditer(r'restricted|reconcil|(?<!\d)772(?!\d)', text, re.I):
                hits.append({'pdf_page': n, 'term': match[0],
                    'start': match.start(), 'end': match.end(),
                    'excerpt': text[max(0,match.start()-130):match.end()+220]})
        searches[year] = {'scope': 'all extracted PDF page text; no OCR or external search',
                          'pattern': r'restricted|reconcil|(?<!\d)772(?!\d)', 'hits': hits}
    with zipfile.ZipFile(ROOT / ARCHIVE) as archive:
        members = {name: digest(archive.read(name)) for name in archive.namelist()}
        instance_name = next(n for n in members if n.endswith('_htm.xml'))
        calc_name = next(n for n in members if n.endswith('_cal.xml'))
        instance = ET.fromstring(archive.read(instance_name))
        calc = ET.fromstring(archive.read(calc_name))
    contexts = {}
    for c in instance.findall('x:context', NS):
        identifier = c.find('x:entity/x:identifier', NS)
        period = c.find('x:period', NS)
        contexts[c.attrib['id']] = {'entity': identifier.text,
            'scheme': identifier.attrib['scheme'],
            'period': {local(e.tag): e.text for e in period},
            'dimensions': [{'dimension': e.attrib['dimension'], 'member': e.text}
                           for e in c.findall('.//d:explicitMember', NS)],
            'raw_xml': ET.tostring(c, encoding='unicode')}
    units = {u.attrib['id']: ET.tostring(u,encoding='unicode')
             for u in instance.findall('x:unit', NS)}
    facts = []
    residuals = []
    for node in instance:
        if 'contextRef' not in node.attrib: continue
        if node.text and node.text.strip() in {'772', '772000000', '-772000000'}:
            residuals.append({'concept': node.tag, **node.attrib, 'literal': node.text})
        if local(node.tag) not in CONCEPTS: continue
        ctx = contexts[node.attrib['contextRef']]
        facts.append({'concept': node.tag, **node.attrib, 'literal': node.text,
            'context': ctx, 'unit_xml': units[node.attrib['unitRef']]})
    grouped = defaultdict(list)
    for f in facts:
        semantic = {k: f[k] for k in ['concept','literal','decimals','context','unit_xml']}
        grouped[digest(json.dumps(semantic,sort_keys=True).encode())].append(f['id'])
    arcs = []
    for link in calc.findall('l:calculationLink', NS):
        locs = {e.attrib['{'+NS['a']+'}label']: e.attrib['{'+NS['a']+'}href']
                for e in link.findall('l:loc', NS)}
        for arc in link.findall('l:calculationArc', NS):
            src, dst = (locs[arc.attrib['{'+NS['a']+'}'+k]] for k in ['from','to'])
            if 'RestrictedCash' in src + dst:
                arcs.append({'role': link.attrib['{'+NS['a']+'}role'],
                    'from': src, 'to': dst, 'weight': arc.attrib['weight']})
    return {'schema': 'accdsl.retained-cash-source-inspection.v1',
        'source_sha256': sources, 'archive_member_sha256': members,
        'selected_pages': pages, 'pdf_searches': searches,
        'cash_facts': facts, 'duplicate_representation_groups': list(grouped.values()),
        'exact_772_numeric_facts': residuals, 'restricted_cash_calculation_arcs': arcs,
        'derived_display_arithmetic_usd_million': {'2023': '30737 - 29965 = 772',
                                                  '2024': '29943 - 29943 = 0'},
        'source_admission': False, 'accounting_admission': False,
        'population_membership': 'unresolved',
        'boundary': 'Displayed subtraction is not an account, flow, or exact unrounded difference.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--record',action='store_true')
    args = parser.parse_args(); result = inspect(); target = HERE / 'source-ledger.json'
    if args.record:
        assert not target.exists(), 'Frozen source ledger already exists'
        dump(target,result)
    else:
        assert result == json.loads(target.read_text()), 'Source replay mismatch'
    print(json.dumps({'passed': True, 'source_files':len(result['source_sha256']),
        'tagged_occurrences':len(result['cash_facts']),
        'representation_groups':len(result['duplicate_representation_groups']),
        'restricted_cash_arcs':len(result['restricted_cash_calculation_arcs']),
        'exact_772_facts':len(result['exact_772_numeric_facts']),
        'search_hit_counts':{k:len(v['hits']) for k,v in result['pdf_searches'].items()}}))
