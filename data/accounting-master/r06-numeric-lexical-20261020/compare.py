"""Local documentary checks; no schema processor or acquired code executes."""
from collections import Counter
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'data/accounting-master'
COVERAGE = B / 'native-concept-type-coverage-20261018/coverage.json'
INSTANCE = B / 'taxonomy-reuse-20261007/archive/aapl-20240928_htm.xml'
XS = '{http://www.w3.org/2001/XMLSchema}'
XSI = '{http://www.w3.org/2001/XMLSchema-instance}'
DECIMAL = re.compile(r'[+-]?(?:[0-9]+(?:[.][0-9]*)?|[.][0-9]+)')
INTEGER = re.compile(r'[+-]?[0-9]+')

def load(p):
    return json.loads(p.read_text())

def digest(b):
    return hashlib.sha256(b).hexdigest()

@lru_cache(None)
def raw(path):
    return (R / path).read_bytes()

def bind(p):
    return {'path': str(p.relative_to(R)), 'sha256': digest(p.read_bytes())}

def collapse(s):
    replaced = s.translate({9: 32, 10: 32, 13: 32})
    return ' '.join(x for x in replaced.split(' ') if x)

def digits(s):
    n = 0
    for c in s:
        assert '0' <= c <= '9'
        n = 10 * n + ord(c) - 48
    return n

def rational(q):
    return {'n': str(q.numerator), 'd': str(q.denominator)}

def lexical(s, terminal):
    if not isinstance(s, str):
        return {'status': 'not_text', 'collapsed': None, 'rational': None}
    assert terminal in ('decimal', 'integer')
    t = collapse(s)
    grammar = DECIMAL if terminal == 'decimal' else INTEGER
    if grammar.fullmatch(t) is None:
        return {'status': 'outside_lexical_space', 'collapsed': t, 'rational': None}
    body = t[1:] if t[0] in '+-' else t
    left, dot, right = body.partition('.')
    q = Fraction(digits(left + right), 10 ** len(right))
    if t[0] == '-':
        q = -q
    sign, ds, exponent = Decimal(t).as_tuple()
    coefficient = sum(d * 10 ** i for i, d in enumerate(reversed(ds)))
    independent = Fraction((-1) ** sign * coefficient) * Fraction(10) ** exponent
    assert q == independent, 'independent Decimal tuple mismatch'
    return {'status': 'member', 'collapsed': t, 'rational': rational(q),
            'negative_zero_spelling': q == 0 and t.startswith('-'),
            'fractional_spelling_digits': len(right), 'independent_value_match': True}

def checked_anchor(a):
    data = raw(a['source_path'])
    assert digest(data) == a['source_sha256']
    piece = data[a['byte_start']:a['byte_end']]
    assert digest(piece) == a['slice_sha256']
    assert piece.decode() == a['text']

@lru_cache(None)
def schema(path):
    scopes, stack, pending = {}, [], []
    root = None
    for event, item in ET.iterparse(R / path, events=('start-ns', 'start', 'end')):
        if event == 'start-ns':
            pending.append(item)
        elif event == 'start':
            if root is None: root = item
            scope = dict(stack[-1]) if stack else {}
            scope.update(pending)
            pending.clear()
            scopes[id(item)] = scope
            stack.append(scope)
        else: stack.pop()
    return root, scopes

def expanded(token, ns):
    if ':' in token:
        prefix, local = token.split(':', 1)
        return '{' + ns[prefix] + '}' + local
    return '{' + ns.get('', '') + '}' + token

def type_audit(d, concepts):
    visited, paths = {}, {}
    def visit(name, trail):
        assert name not in trail, 'cycle'
        n = d['type_nodes'][name]
        if n['status'] == 'builtin_reference_only':
            assert name in (XS + 'decimal', XS + 'integer')
            visited[name] = {'type': name, 'terminal': True,
                             'additional_value_facets': [], 'basis': 'retained_2004_specification'}
            return [name]
        checked_anchor(n['anchor'])
        root, scopes = schema(n['anchor']['source_path'])
        matches = [e for e in root if e.get('name') == name.split('}')[-1]
                   and e.tag in (XS + 'simpleType', XS + 'complexType')]
        assert len(matches) == 1
        derivations = [e for e in matches[0].iter() if e.tag in (XS+'extension', XS+'restriction')]
        assert len(derivations) == 1
        e = derivations[0]
        assert n['derivation'] == e.tag.split('}')[-1]
        children = [{'tag': c.tag, 'attributes': dict(c.attrib)} for c in e]
        assert children == n['derivation_children']
        assert all(c['tag'] == XS + 'attributeGroup' for c in children), 'unhandled value facet'
        assert len(n['edges']) == 1 and n['edges'][0]['role'] == 'base'
        target = expanded(e.attrib['base'], scopes[id(e)])
        assert target == n['edges'][0]['target']
        visited[name] = {'type': name, 'terminal': False, 'derivation': n['derivation'],
                         'base': target, 'additional_value_facets': [], 'attribute_children': children,
                         'anchor': n['anchor']}
        return [name] + visit(target, trail | {name})
    for name in sorted(concepts):
        c = d['concepts'][name]
        checked_anchor(c['declaration_anchor'])
        root, scopes = schema(c['declaration_anchor']['source_path'])
        elements = [e for e in root if e.tag == XS+'element' and e.get('name') == name.split('}')[-1]]
        assert len(elements) == 1
        assert dict(elements[0].attrib) == c['source_attributes']
        assert expanded(elements[0].attrib['type'], scopes[id(elements[0])]) == c['declared_type']
        path = visit(c['declared_type'], set())
        assert c['type_path']['terminal_references'] == [path[-1]]
        paths[name] = path
    return {'concept_paths': paths, 'nodes': [visited[k] for k in sorted(visited)],
            'concepts': len(paths), 'type_nodes': len(visited),
            'full_schema_validation': 'not_run', 'unit_attribute_semantics': 'not_checked_here'}

def interpret(row, declaration, path):
    base = {k: row[k] for k in ('fact_id', 'source_concept', 'source_context_id',
            'source_unit_id', 'source_attributes', 'decoded_text', 'source_span', 'portable_candidate_value')}
    base.update(type_path=path, validation_status='not_run', portable_value_mutated=False,
                processor_value_admitted=False, financial_admission=False)
    if row['portable_candidate_value']['tag'] == 'Nil':
        conditions = {'nil_true': row['source_attributes'].get(XSI+'nil') in ('true', '1'),
            'declaration_nillable': declaration['source_attributes'].get('nillable') in ('true', '1'),
            'no_fixed_value_constraint': 'fixed' not in declaration['source_attributes'],
            'empty_raw_content': row['source_span']['content_utf8'] == '',
            'no_decoded_text': row['decoded_text'] is None}
        base.update(status='nil_conditions_observed' if all(conditions.values()) else 'nil_condition_failed',
                    conditions=conditions, lexical=None, candidate_value_match=None)
        return base
    terminal = path[-1].split('}')[-1]
    parsed = lexical(row['decoded_text'], terminal)
    match = parsed['rational'] == row['portable_candidate_value'].get('rational')
    base.update(status='narrow_lexical_value_agreement' if parsed['status']=='member' and match else 'requires_repair',
                lexical=parsed, candidate_value_match=match)
    return base

def derive():
    d = load(COVERAGE)
    selected = [r for r in d['occurrences'] if r['portable_candidate_value']['tag'] in ('Decimal','Nil')]
    audit = type_audit(d, {r['source_concept'] for r in selected})
    instance_raw = INSTANCE.read_bytes()
    elements = {e.get('id'): e for e in ET.fromstring(instance_raw) if e.get('contextRef') is not None}
    rows = []
    for r in selected:
        a = r['source_span']
        piece = instance_raw[a['byte_start']:a['byte_end']]
        assert digest(piece) == a['slice_sha256'] and piece.decode() == a['raw_utf8']
        e = elements[r['fact_id']]
        assert e.tag == r['source_concept'] and dict(e.attrib) == r['source_attributes']
        assert e.text == r['decoded_text'] and len(e) == 0
        assert r['packet_candidate_value'] == r['portable_candidate_value']
        assert r['validation_status'] == 'not_run' and not r['portable_value_mutated']
        rows.append(interpret(r, d['concepts'][r['source_concept']], audit['concept_paths'][r['source_concept']]))
    return audit, rows

def check():
    audit, rows = derive()
    assert audit == load(U/'type-audit.json')
    assert rows == load(U/'occurrences.json')
    assertions = 2
    def require(condition):
        nonlocal assertions
        assert condition
        assertions += 1
    require(len(rows) == 963 and audit['concepts'] == 263 and audit['type_nodes'] == 13)
    numeric = [r for r in rows if r['lexical'] is not None]
    nil = [r for r in rows if r['lexical'] is None]
    require(len(numeric)==961 and len(nil)==2)
    for r in numeric: require(r['status']=='narrow_lexical_value_agreement')
    for r in nil: require(r['status']=='nil_conditions_observed' and r['portable_candidate_value']=={'tag':'Nil'})
    fixtures = load(U/'fixtures.json')
    for f in fixtures:
        out = lexical(f['raw'], f['terminal'])
        require(out['status'] == f['expected_status'])
        require(out['rational'] == f['expected_rational'])
    require(lexical('-00.00','decimal')['negative_zero_spelling'])
    require(lexical('2.00','decimal')['fractional_spelling_digits']==2)
    require(lexical('2.0','decimal')['rational']==lexical('2.00','decimal')['rational'])
    for a in load(U/'source-ledger.json')['anchors']:
        p = R/a['source']['path']
        require(bind(p)==a['source'])
        excerpt = b''.join(p.read_bytes().splitlines(keepends=True)[a['first_line']-1:a['last_line']])
        require(digest(excerpt)==a['raw_excerpt_sha256'])
        require(bind(R/a['readable']['path'])==a['readable'])
    for b in load(U/'source-ledger.json')['bindings']: require(bind(R/b['path'])==b)
    controls = load(U/'altered-controls.json')
    d = load(COVERAGE)
    originals = {r['fact_id']: r for r in d['occurrences']}
    for c in controls:
        r = json.loads(json.dumps(originals[c['fact_id']]))
        decl = json.loads(json.dumps(d['concepts'][r['source_concept']]))
        for key, value in c.get('row_changes', {}).items(): r[key] = value
        for key, value in c.get('declaration_changes', {}).items(): decl['source_attributes'][key] = value
        result = interpret(r, decl, audit['concept_paths'][r['source_concept']])
        require(result['status'] == c['expected_status'])
    counts = Counter(r['type_path'][-1].split('}')[-1] for r in numeric)
    require(dict(counts)=={'decimal':958,'integer':3})
    require(all(r['validation_status']=='not_run' and not r['processor_value_admitted'] for r in rows))
    return {'status':'passed','assertions':assertions,'numeric_occurrences':len(numeric),
            'nil_occurrences':len(nil),'terminal_counts':dict(counts),'concepts':audit['concepts'],
            'type_nodes':audit['type_nodes'],'fixtures':len(fixtures),'altered_controls':len(controls),
            'all_exact_value_matches':True,'upstream_executed':False,'schema_validation':'not_run',
            'new_acquisitions':0,'whole_rows_closed':0}
