"""Pinned native source inventory; standard-library documentary checks only."""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from xml.parsers import expat

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = ROOT / 'data/accounting-master/taxonomy-reuse-20261007/archive/aapl-20240928_htm.xml'
PLAN = ROOT / 'docs/plans/accounting-native-shape-inventory-20261018.md'
XI, XD, LINK = '{http://www.xbrl.org/2003/instance}', '{http://xbrl.org/2006/xbrldi}', '{http://www.xbrl.org/2003/linkbase}'
XSI = '{http://www.w3.org/2001/XMLSchema-instance}'
EXPECTED_HASH = 'e92b4267ed5015cb6136aa00c48a73c00ac12e0cbfec18686811436cde898f2d'

def require(condition, code):
    if not condition: raise ValueError(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}

def write(path, value):
    with path.open('x') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')

def load(path):
    return json.loads(path.read_bytes())

def xml_tree(element):
    return {'name': element.tag, 'attributes': dict(element.attrib), 'text': element.text,
            'children': [xml_tree(child) | {'tail': child.tail} for child in element]}

def source_material():
    raw = SOURCE.read_bytes()
    require(sha(raw) == EXPECTED_HASH, 'SOURCE_HASH')
    require(raw.startswith(b'<?xml version="1.0" encoding="utf-8"?>\r\n'), 'ENCODING')
    raw.decode('utf-8', 'strict')
    require(not any(t in raw for t in [b'<!DOCTYPE', b'<!ENTITY', b'<![CDATA[']), 'UNSUPPORTED_XML_FORM')
    parser = expat.ParserCreate(namespace_separator='}')
    depth, rows, current, namespaces = 0, [], None, []
    root_open = None
    def tag_end(start):
        quote = None
        for i in range(start, len(raw)):
            char = raw[i]
            if quote is not None:
                if char == quote: quote = None
            elif char in (34, 39): quote = char
            elif char == 62: return i + 1
        raise ValueError('UNTERMINATED_TAG')
    def start_ns(prefix, uri):
        require(depth == 0, 'LOCAL_NAMESPACE_DECLARATION')
        namespaces.append({'prefix': prefix or '', 'namespace_uri': uri})
    def start(name, attrs):
        nonlocal depth, current, root_open
        depth += 1
        if depth == 1:
            root_open = raw[parser.CurrentByteIndex:tag_end(parser.CurrentByteIndex)]
        if depth == 2:
            begin = parser.CurrentByteIndex
            end = tag_end(begin)
            current = {'byte_start': begin, 'opening_end': end, 'self_closing': raw[end-2:end] == b'/>'}
    def end(name):
        nonlocal depth, current
        if depth == 2:
            stop = current['opening_end'] if current['self_closing'] else tag_end(parser.CurrentByteIndex)
            rows.append({'byte_start': current['byte_start'], 'byte_end': stop})
            current = None
        depth -= 1
    parser.StartNamespaceDeclHandler = start_ns
    parser.StartElementHandler, parser.EndElementHandler = start, end
    parser.Parse(raw, True)
    root = ET.fromstring(raw)
    require(len(rows) == len(root), 'PARSER_ELEMENT_COUNT')
    closing = b'</' + re.match(br'<([^\s>]+)', root_open).group(1) + b'>'
    for row, element in zip(rows, root):
        chunk = raw[row['byte_start']:row['byte_end']]
        fragment = ET.fromstring(root_open + chunk + closing)
        require(len(fragment) == 1 and xml_tree(fragment[0]) == xml_tree(element), 'INDEPENDENT_FRAGMENT')
        row['slice_sha256'] = sha(chunk)
    return raw, root, rows, namespaces

def lexical(element):
    text = ''.join(element.itertext())
    if element.get(XSI + 'nil') in ('true', '1'):
        return {'class': 'nil', 'rational_candidate': None}
    if len(element):
        return {'class': 'child_content', 'rational_candidate': None}
    token = text.strip()
    if re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)', token):
        value = Fraction(token)
        return {'class': 'decimal_lexical_candidate', 'rational_candidate': {'n': str(value.numerator), 'd': str(value.denominator)}}
    return {'class': 'empty' if not text else 'text', 'rational_candidate': None}

def construct(material):
    raw, root, spans, namespaces = material
    entries = []
    ns = {r['prefix']: r['namespace_uri'] for r in namespaces}
    def measure(element):
        token = (element.text or '').strip()
        prefix, local = token.split(':', 1) if ':' in token else ('', token)
        return {'token': element.text, 'namespace_uri': ns.get(prefix), 'local_name': local}
    for position, (element, span) in enumerate(zip(root, spans), 1):
        category = 'context' if element.tag == XI + 'context' else 'unit' if element.tag == XI + 'unit' else 'link' if element.tag.startswith(LINK) else 'fact'
        entry = {'position': position, 'element_path': '/1/' + str(position), 'id': element.get('id'),
                 'name': element.tag, 'attributes': dict(element.attrib), 'category': category, 'span': span}
        if category == 'fact':
            entry.update(context_id=element.get('contextRef'), unit_id=element.get('unitRef'),
                         decoded_text=''.join(element.itertext()), child_count=len(element), lexical=lexical(element),
                         taxonomy_type='Unknown', financial_admission='Unknown')
        elif category == 'context':
            entry['source_tree'] = xml_tree(element)
            entry['period_children'] = [child.tag for child in element.find(XI + 'period')]
            entry['qualifiers'] = [{'container': container.tag.split('}')[-1], 'reading': xml_tree(child)}
                                   for container in element.iter() if container.tag in (XI + 'segment', XI + 'scenario') for child in container]
        elif category == 'unit':
            entry['source_tree'] = xml_tree(element)
            entry['numerator'] = [measure(e) for e in element.findall(XI + 'measure')] + [measure(e) for e in element.findall(XI + 'divide/' + XI + 'unitNumerator/' + XI + 'measure')]
            entry['denominator'] = [measure(e) for e in element.findall(XI + 'divide/' + XI + 'unitDenominator/' + XI + 'measure')]
        else:
            entry['source_tree'] = xml_tree(element)
        entries.append(entry)
    facts = [r for r in entries if r['category'] == 'fact']
    contexts = [r for r in entries if r['category'] == 'context']
    units = [r for r in entries if r['category'] == 'unit']
    ids = Counter(r['id'] for r in entries if r['id'] is not None)
    cids, uids = {r['id'] for r in contexts}, {r['id'] for r in units}
    repeats = defaultdict(list)
    for fact in facts:
        sig = json.dumps([fact[k] for k in ['name', 'context_id', 'unit_id', 'decoded_text']] +
                         [fact['attributes'].get(k) for k in ['decimals', 'precision', XSI + 'nil']], sort_keys=True)
        repeats[sig].append(fact['id'])
    summary = {'categories': dict(Counter(r['category'] for r in entries)),
        'lexical_classes': dict(Counter(f['lexical']['class'] for f in facts)),
        'unitless_decimal_candidates': [f['id'] for f in facts if not f['unit_id'] and f['lexical']['class'] == 'decimal_lexical_candidate'],
        'unit_bearing_nondecimal': [f['id'] for f in facts if f['unit_id'] and f['lexical']['class'] not in ('decimal_lexical_candidate', 'nil')],
        'missing_ids': [r['position'] for r in entries if r['id'] is None],
        'duplicate_ids': {k: v for k, v in ids.items() if v > 1},
        'missing_context_joins': [f['id'] for f in facts if f['context_id'] not in cids],
        'missing_unit_joins': [f['id'] for f in facts if f['unit_id'] is not None and f['unit_id'] not in uids],
        'repeated_signatures': [v for v in repeats.values() if len(v) > 1],
        'qualifier_names': dict(Counter(q['reading']['name'] for c in contexts for q in c['qualifiers'])),
        'period_shapes': dict(Counter(','.join(x.split('}')[-1] for x in c['period_children']) for c in contexts)),
        'link_elements': [{'position': r['position'], 'name': r['name']} for r in entries if r['category'] == 'link'],
        'child_content_facts': [f['id'] for f in facts if f['child_count']],
        'text_with_markup_characters': [f['id'] for f in facts if f['lexical']['class'] == 'text' and '<' in f['decoded_text'] and '>' in f['decoded_text']]}
    return {'evidence_mode': 'retained_source_structural_inventory', 'upstream_executed': False,
            'source': binding(SOURCE) | {'byte_length': len(raw)}, 'namespace_bindings': namespaces,
            'root_attributes': dict(root.attrib), 'entries': entries, 'summary': summary}

def validate(inventory, material):
    raw, root, spans, namespaces = material
    expected = construct(material)
    checks = []
    def check(label, condition):
        require(condition, label); checks.append(label)
    check('SOURCE_METADATA', {k: v for k, v in inventory.items() if k not in ('entries', 'summary')} == {k: v for k, v in expected.items() if k not in ('entries', 'summary')})
    check('ALL_ROOT_ELEMENTS', len(inventory['entries']) == len(root))
    previous_end = 0
    for row, reference in zip(inventory['entries'], expected['entries']):
        key = str(reference['position'])
        span = row['span']
        check('ORDERED_SPAN:' + key, previous_end <= span['byte_start'] < span['byte_end'] <= len(raw))
        previous_end = span['byte_end']
        check('SPAN_HASH:' + key, sha(raw[span['byte_start']:span['byte_end']]) == span['slice_sha256'])
        check('SOURCE_ENTRY:' + key, row == reference)
    check('SUMMARY_RECONCILES', inventory['summary'] == expected['summary'])
    counts = inventory['summary']['categories']
    check('BASELINE_TOTALS', counts.get('fact') == 1127 and counts.get('context') == 193 and counts.get('unit') == 7)
    return checks

def negatives(inventory, material):
    cases = []
    def run(name, edit, prefix):
        value = deepcopy(inventory); edit(value)
        try: validate(value, material)
        except ValueError as error:
            require(str(error).startswith(prefix), 'UNEXPECTED_NEGATIVE:' + name + ':' + str(error))
            cases.append({'case': name, 'rejected': str(error)})
        else: raise ValueError('ACCEPTED_CORRUPTION:' + name)
    run('drop-top-level-link', lambda d: d['entries'].pop(0), 'ALL_ROOT_ELEMENTS')
    run('alter-summary', lambda d: d['summary']['categories'].__setitem__('fact', 1126), 'SUMMARY_RECONCILES')
    run('shift-byte-span', lambda d: d['entries'][0]['span'].__setitem__('byte_start', d['entries'][0]['span']['byte_start'] + 1), 'SPAN_HASH:')
    fact_index = next(i for i,r in enumerate(inventory['entries']) if r['id'] == 'f-105')
    run('lose-context-join', lambda d: d['entries'][fact_index].__setitem__('context_id', 'missing'), 'SOURCE_ENTRY:')
    run('promote-taxonomy-type', lambda d: d['entries'][fact_index].__setitem__('taxonomy_type', 'monetary'), 'SOURCE_ENTRY:')
    run('lose-unit-denominator', lambda d: next(r for r in d['entries'] if r['id'] == 'usdPerShare').__setitem__('denominator', []), 'SOURCE_ENTRY:')
    run('merge-repeated-occurrence', lambda d: d['entries'].remove(next(r for r in d['entries'] if r['id'] == 'f-256')), 'ALL_ROOT_ELEMENTS')
    run('drop-dimensional-qualifiers', lambda d: next(r for r in d['entries'] if r['id'] == 'c-13').__setitem__('qualifiers', []), 'SOURCE_ENTRY:')
    run('declare-upstream-execution', lambda d: d.__setitem__('upstream_executed', True), 'SOURCE_METADATA')
    run('typed-domain-content-lost', lambda d: next(r for r in d['entries'] if r['id'] == 'c-58')['qualifiers'][0]['reading'].__setitem__('children', []), 'SOURCE_ENTRY:')
    run('numeric-looking-identifier-normalized', lambda d: next(r for r in d['entries'] if r['id'] == 'f-59').__setitem__('decoded_text', '320193'), 'SOURCE_ENTRY:')
    run('schema-reference-invented-id', lambda d: d['entries'][0].__setitem__('id', 'invented'), 'SOURCE_ENTRY:')
    return cases

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--record', action='store_true'); mode.add_argument('--check-only', action='store_true')
    args = parser.parse_args(); tick = time.monotonic()
    material = source_material()
    inventory = construct(material) if args.record or args.check_only else load(OUT / 'inventory.json')
    checks = validate(inventory, material); corruptions = negatives(inventory, material)
    findings = {'checks': checks, 'negative_cases': corruptions, 'summary': inventory['summary']}
    if args.record:
        for name in ['inventory.json', 'checks.json', 'run-manifest.json']:
            require(not (OUT / name).exists(), 'ALREADY_RECORDED:' + name)
        write(OUT / 'inventory.json', inventory); write(OUT / 'checks.json', findings)
        predecessor = ROOT / 'data/accounting-master/native-selected-portable-20261018'
        protected = [SOURCE, PLAN, predecessor / 'completion.json', predecessor / 'checks.json', predecessor / 'portable-records.json', predecessor / 'run-manifest.json']
        inherited = load(predecessor / 'protected-inputs.json')
        manifest = {'recorded_utc': datetime.now(timezone.utc).isoformat(),
            'command': 'python3 data/accounting-master/native-shape-inventory-20261018/check.py --record',
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'environment': {'executable': sys.executable, 'python': platform.python_version(), 'conda_env': 'tfgpu', 'cpu_gpu': 'CPU standard-library XML/file checks only; no numerical framework or GPU'},
            'data_version': binding(SOURCE), 'random_seeds': 'N/A: deterministic', 'wall_seconds': time.monotonic() - tick,
            'plan_file': str(PLAN.relative_to(ROOT)), 'result_file': str((OUT / 'result.md').relative_to(ROOT)),
            'protected_inputs': inherited + [binding(p) for p in protected],
            'artifacts': [binding(OUT / n) for n in ['check.py', 'inventory.json', 'checks.json']]}
        write(OUT / 'run-manifest.json', manifest)
    elif not args.check_only:
        require(findings == load(OUT / 'checks.json'), 'REPLAY_CHANGED')
        manifest = load(OUT / 'run-manifest.json')
        for row in manifest['protected_inputs'] + manifest['artifacts']:
            require(binding(ROOT / row['path']) == row, 'PROTECTED:' + row['path'])
    summary = inventory['summary']
    print(json.dumps({'mode': 'check_only' if args.check_only else 'record' if args.record else 'read_only_replay',
        'checks': len(checks), 'corruptions_rejected': len(corruptions), 'categories': summary['categories'],
        'lexical_classes': summary['lexical_classes'], 'unitless_decimal_candidates': summary['unitless_decimal_candidates'],
        'unit_bearing_nondecimal': summary['unit_bearing_nondecimal'], 'missing_ids': summary['missing_ids'],
        'duplicate_ids': summary['duplicate_ids'], 'missing_context_joins': summary['missing_context_joins'],
        'missing_unit_joins': summary['missing_unit_joins'], 'repeated_groups': len(summary['repeated_signatures']),
        'qualifiers': summary['qualifier_names'], 'period_shapes': summary['period_shapes'], 'links': summary['link_elements'],
        'child_content_facts': summary['child_content_facts'], 'markup_text_count': len(summary['text_with_markup_characters'])}))

if __name__ == '__main__': main()
