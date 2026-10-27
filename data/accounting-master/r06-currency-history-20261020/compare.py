"""Static currency-source adequacy; no processor, workbook calculation or admission."""
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'data/accounting-master'
FACTS = B / 'r06-unit-measures-20261020/facts.json'
UNITS = B / 'r06-unit-measures-20261020/units.json'
CONTEXTS = B / 'r06-context-periods-20261020/contexts.json'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

def load(path):
    return json.loads(path.read_text())

def bind(path):
    return {'path': str(path.relative_to(R)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def source(name):
    return U / 'sources' / (name + '-sandbox.body')

def xml(data):
    text = data.decode('utf-8-sig') if isinstance(data, bytes) else data
    assert '<!DOCTYPE' not in text and '<!ENTITY' not in text
    return ET.fromstring(text)

def currency_list(name):
    root = xml(source(name).read_bytes())
    assert root.tag == 'ISO_4217' and len(root) == 1
    rows = [{c.tag: c.text for c in e} for e in root[0]]
    assert all(len(row) == len(e) for row, e in zip(rows, root[0])), 'duplicate field'
    return {'source': bind(source(name)), 'published': root.attrib['Pblshd'],
            'row_count': len(rows), 'fields': sorted({k for row in rows for k in row}),
            'selected_rows': [row for row in rows if row.get('Ccy') in ('USD', 'EUR')],
            'effective_start_field_present': False,
            'date_scope': 'publication of this list; not code inception or uninterrupted validity'}

def amendment_index():
    path = source('amendments-index')
    with zipfile.ZipFile(path) as archive:
        assert sum(x.file_size for x in archive.infolist()) < 2000000
        strings = [''.join(x.itertext()) for x in xml(archive.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        sheet = xml(archive.read('xl/worksheets/sheet1.xml'))
        relations = {x.attrib['Id']: dict(x.attrib) for x in xml(archive.read('xl/worksheets/_rels/sheet1.xml.rels'))}
        links = {x.attrib['ref']: relations[x.attrib[RID]] for x in sheet.findall('.//s:hyperlink', NS)}
        rows = []
        for row in sheet.findall('.//s:sheetData/s:row', NS):
            values = {}
            for cell in row.findall('s:c', NS):
                assert cell.find('s:f', NS) is None, 'formula needs separate inspection'
                value = cell.findtext('s:v', default='', namespaces=NS)
                if cell.get('t') == 's' and value:
                    value = strings[int(value)]
                if value:
                    values[cell.attrib['r']] = {'value': value, 'type': cell.get('t', 'n'),
                                               'style': cell.get('s'), 'link': links.get(cell.attrib['r'])}
            rows.append({'row': int(row.attrib['r']), 'cells': values})
        styles = xml(archive.read('xl/styles.xml'))
        formats = {x.attrib['numFmtId']: x.attrib['formatCode'] for x in styles.findall('s:numFmts/s:numFmt', NS)}
        date_style = styles.findall('s:cellXfs/s:xf', NS)[11]
        selected = [row for row in rows if row['row'] in (102, 108, 267)]
        numbered = [int(c['value']) for row in rows for key, c in row['cells'].items()
                    if re.fullmatch(r'B[0-9]+', key) and c['value'].isdigit()]
        assert len(selected) == 3
        return {'source': bind(path), 'rows': rows, 'row_count': len(rows),
                'hyperlink_relationships': len(relations), 'selected': selected,
                'maximum_number_listed': max(numbered),
                'date_style': dict(date_style.attrib), 'date_format': formats[date_style.attrib['numFmtId']],
                'workbook_properties': dict(xml(archive.read('xl/workbook.xml')).find('s:workbookPr', NS).attrib),
                'date_interpretation': 'raw numeric cells preserved; dates read from the actual PDF text',
                'completeness': 'index lists through179 while live page names180; no complete chronology inferred'}

def join_facts(facts, units, contexts):
    by_unit = {r['unit_id']: r for r in units}
    by_context = {r['context_id']: r for r in contexts}
    assert len(by_unit) == len(units) and len(by_context) == len(contexts)
    out = []
    for row in facts:
        if row['unit_compatibility']['status'] != 'partial_currency_history_unverified':
            continue
        uid, cid = row['source_unit_id'], row['source_context_id']
        assert uid in by_unit and cid in by_context, 'missing source join'
        unit, context = by_unit[uid]['interpretation'], by_context[cid]
        assert unit['status'] == 'supported' and context['interpretation']['status'] == 'supported'
        assert len(unit['numerator']) == 1
        name = unit['numerator'][0]['expanded_name']
        assert name.startswith('{http://www.xbrl.org/2003/iso4217}'), 'currency namespace'
        code = name.split('}', 1)[1]
        assert code in ('USD', 'EUR'), 'unreviewed code'
        assert unit['denominator'] == [] or (uid == 'usdPerShare' and len(unit['denominator']) == 1
            and unit['denominator'][0]['expanded_name'] == '{http://www.xbrl.org/2003/instance}shares')
        out.append({'fact_id': row['fact_id'], 'context_id': cid, 'unit_id': uid, 'currency': code,
                    'source_nil': row['source_nil'], 'raw_period': context['raw_period'],
                    'period_interpretation': context['interpretation'],
                    'current_code_membership': 'supported_at_list_publication',
                    'historical_designation': 'partial_currency_history_unverified',
                    'source_value_unchanged': True})
    assert len({r['fact_id'] for r in out}) == len(out), 'duplicate fact'
    return out

def source_findings():
    page = (U / 'sources/SIX-index.visible.txt').read_text()
    a94 = ' '.join((U / 'sources/amendment-94.txt').read_text().split())
    a158 = ' '.join((U / 'sources/amendment-158.txt').read_text().split())
    a160 = ' '.join((U / 'sources/amendment-160.txt').read_text().split())
    checks = {
        'index_states_maintenance_role': 'is the official Maintenance Agency of these currency codes under ISO 4217' in page,
        'index_distinguishes_current_and_historical': 'Current Currency & Funds' in page and 'Historical (Currencies & Funds)' in page,
        'live_page_names_2026_bulgaria_effect': 'Effective from 1st of January 2026' in page,
        'eur_issued_in_1997': 'Date : 21/04/97' in a94 and 'EUR* 978 2' in a94,
        'eur_adoption_distinct_from_advance_issue': 'On 1 January 1999' in a94 and 'This code has been issued now so that technical preparations can be started.' in a94,
        'eur_notice_announces_further_amendments': 'Further amendments regarding this currency will be made' in a94,
        'amendment158_is_uss_not_usd': 'USS 998 2' in a158 and not re.search(r'\bUSD\b', a158),
        'uss_removed_with_immediate_effect_20140328': '28 March 2014' in a158 and 'With immediate effect' in a158 and 'will be removed from the ISO 4217 lists' in a158,
        'amendment160_corrects_country_names': '19 June 2015' in a160 and 'UNITED STATES to UNITED STATES OF AMERICA (THE)' in a160,
        'amendment160_does_not_name_usd': not re.search(r'\bUSD\b', a160),
        'amendment160_corrects_a_different_currency_date': '1st January 1994 and not 25th August 1994' in a160,
    }
    assert all(checks.values()), [key for key,value in checks.items() if not value]
    return list(checks)

def controls():
    facts, units, contexts = load(FACTS), load(UNITS), load(CONTEXTS)
    selected = [r for r in facts if r['unit_compatibility']['status'] == 'partial_currency_history_unverified']
    bad = []
    one = deepcopy(selected[:1]); one[0]['source_context_id'] = 'absent'; bad.append((one,units,contexts))
    one = deepcopy(selected[:1]); one[0]['source_unit_id'] = 'absent'; bad.append((one,units,contexts))
    us = deepcopy(units); us[0]['interpretation']['numerator'][0]['expanded_name'] = '{urn:other}USD'; bad.append((selected[:1],us,contexts))
    us = deepcopy(units); us[0]['interpretation']['numerator'][0]['expanded_name'] = '{http://www.xbrl.org/2003/iso4217}USS'; bad.append((selected[:1],us,contexts))
    bad.append((selected[:1]*2,units,contexts))
    bad.append((selected[:1],units+[units[0]],contexts))
    bad.append((selected[:1],units,contexts+[contexts[0]]))
    for args in bad:
        try:
            join_facts(*args)
        except AssertionError:
            pass
        else:
            raise AssertionError('altered input accepted')
    for raw in ('<!DOCTYPE x><x/>', '<!ENTITY x "y"><x/>'):
        try:
            xml(raw)
        except AssertionError:
            pass
        else:
            raise AssertionError('DTD input accepted')
    return {'rejected_join_controls': len(bad), 'rejected_external_declaration_controls': 2}

def derive():
    facts = join_facts(load(FACTS), load(UNITS), load(CONTEXTS))
    current, historic = currency_list('list-one'), currency_list('list-three')
    assert current['fields'] == ['Ccy', 'CcyMnrUnts', 'CcyNbr', 'CcyNm', 'CtryNm']
    assert historic['fields'] == ['Ccy', 'CcyNbr', 'CcyNm', 'CtryNm', 'WthdrwlDt']
    assert current['row_count'] == 280 and historic['row_count'] == 169
    assert {r['Ccy'] for r in current['selected_rows']} == {'USD','EUR'}
    assert historic['selected_rows'] == [{'CtryNm':'SERBIA AND MONTENEGRO','CcyNm':'Euro', 'Ccy':'EUR','CcyNbr':'978','WthdrwlDt':'2006-10'}]
    codes = {code:{'facts':sum(r['currency']==code for r in facts),
                  'current_entries':sum(r['Ccy']==code for r in current['selected_rows']),
                  'dated_interval_evidence':'not_established'} for code in ('USD','EUR')}
    periods = sorted({tuple(tuple(x) for x in r['raw_period']) for r in facts})
    return {'fact_count':len(facts), 'context_count':len({r['context_id'] for r in facts}),
            'unit_counts':dict(Counter(r['unit_id'] for r in facts)), 'codes':codes,
            'raw_periods':[[list(x) for x in p] for p in periods], 'facts':facts,
            'current':current, 'historic':historic, 'amendments':amendment_index(),
            'source_findings':source_findings(), 'controls':controls(),
            'historical_admissions':0, 'runtime_admitted':False, 'whole_rows_closed':0}

def check():
    ledger = load(U / 'source-ledger.json')
    count = 0
    for row in ledger['bindings']:
        assert bind(R / row['path']) == row; count += 1
    for row in ledger['anchors']:
        path = R / row['source']['path']
        assert bind(path) == row['source']; count += 1
        assert '\n'.join(path.read_text().splitlines()[row['first_line']-1:row['last_line']]) == row['excerpt']; count += 1
    actual = derive()
    assert actual == load(U / 'history.json'); count += 1
    assert (actual['fact_count'],actual['context_count'],len(actual['raw_periods'])) == (873,143,10); count += 1
    for row in actual['facts']:
        assert row['historical_designation'] == 'partial_currency_history_unverified' and row['source_value_unchanged']; count += 1
    spec=importlib.util.spec_from_file_location('source_view', U/'source_view.py')
    view=importlib.util.module_from_spec(spec);spec.loader.exec_module(view)
    for name in ('SIX-index','SIX-currency'):
        fresh=view.derive(source(name))
        assert '\n'.join(fresh.parts)+'\n' == (U/'sources'/(name+'.visible.txt')).read_text(); count += 1
        assert fresh.links == load(U/'sources'/(name+'.links.json')); count += 1
    receipts=sorted((U/'sources').glob('*-receipt.json'))
    for path in receipts:
        receipt=load(path); result=receipt.get('final_result',receipt['result']); meta=json.loads(result['output'])
        assert result['exit_code']==0 and meta['http_code']==200; count += 1
        assert (R/meta['filename_effective']).stat().st_size==meta['size_download']; count += 1
    count += len(actual['source_findings'])+sum(actual['controls'].values())
    return {'checks':count, 'fact_joins':873, 'contexts':143, 'raw_periods':10,
            'source_anchors':len(ledger['anchors']), 'input_bindings':len(ledger['bindings']),
            'acquisitions':len(receipts), 'source_findings':len(actual['source_findings']),
            'archive_rows':actual['amendments']['row_count'], 'controls':actual['controls'],
            'historical_admissions':0, 'upstream_executed':False, 'whole_rows_closed':0}
