"""Read-only documentary checks; no upstream code or external dependency runs."""
from pathlib import Path
from fractions import Fraction
import ast
import hashlib
import json
import xml.etree.ElementTree as ET

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lev(a, b):
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        current = [i]
        for j, y in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (x != y)))
        previous = current
    return previous[-1]


def tokens(node):
    out = ['<' + node.tag + '>'] + list(node.text or '')
    for child in node:
        out.extend(tokens(child))
    if node.tag != 'unk':
        out.append('</' + node.tag + '>')
    if node.tag != 'td':
        out.extend(list(node.tail or ''))
    return out


def witness(pred, true):
    """Exact closed form only for the proved single-cell same-topology subset."""
    a, b = ET.fromstring(pred), ET.fromstring(true)
    assert a.tag == b.tag == 'html'
    a, b = a.find('./body/table'), b.find('./body/table')
    assert a is not None and b is not None
    assert len(list(a)) == len(list(b)) == 1
    assert a[0].tag == b[0].tag == 'tbody'
    assert len(a[0]) == len(b[0]) == 1
    assert a[0][0].tag == b[0][0].tag == 'tr'
    assert len(a[0][0]) == len(b[0][0]) == 1
    ca, cb = a[0][0][0], b[0][0][0]
    assert ca.tag == cb.tag == 'td'
    assert len(list(a.iter('td'))) == len(list(b.iter('td'))) == 1
    assert ca.attrib == cb.attrib == {}
    ta, tb = tokens(ca)[1:-1], tokens(cb)[1:-1]
    d = Fraction(lev(ta, tb), max(len(ta), len(tb))) if ta or tb else Fraction(0)
    assert d < 1, 'the closed-form proof deliberately excludes d >= 1'
    denominator = max(len(list(a.iter())) - 1, len(list(b.iter())) - 1)
    return {'cell_distance': str(d), 'raw_descendant_denominator': denominator,
            'closed_form_score': str(1 - d / denominator),
            'changed_cell_tokens': [ta, tb], 'execution': 'local closed form, not upstream metric'}


def doc(cell, unit=None):
    context = '' if unit is None else '<p>Amounts in ' + unit + '</p>'
    return '<html><body>' + context + '<table><tbody><tr><td>' + cell + '</td></tr></tbody></table></body></html>'


def check():
    ledger = json.loads((UNIT / 'source-ledger.json').read_text())
    assert len(ledger['acquisitions']) == 6
    assert len({x['url'] for x in ledger['acquisitions']}) == 6
    for row in ledger['acquisitions']:
        for kind in ('body', 'headers'):
            p = ROOT / row[kind]['path']
            assert sha(p) == row[kind]['sha256'], str(p)
        assert row['status'] == 200 and row['redirects'] == 0
        assert (ROOT / row['body']['path']).stat().st_size == row['bytes']
        assert '200' in (ROOT / row['headers']['path']).read_text().splitlines()[0]
    for row in ledger['bindings']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    for row in ledger['passages']:
        text = (ROOT / row['path']).read_text()
        assert row['needle'] in text, row['id']
    paper = (UNIT / 'sources/02-paper.txt').read_text()
    assert len([p for p in paper.split('\f') if p.strip()]) == 11
    code = (UNIT / 'sources/05-metric.py').read_text()
    tree = ast.parse(code)
    classes = {c.name: c for c in tree.body if isinstance(c, ast.ClassDef)}
    assert {'TableTree', 'CustomConfig', 'TEDS'} <= classes.keys()
    methods = {c.name: c for c in classes['TEDS'].body if isinstance(c, ast.FunctionDef)}
    assert {'tokenize', 'load_html_tree', 'evaluate', 'batch_evaluate'} <= methods.keys()
    readme = (UNIT / 'sources/03-readme.txt').read_text()
    assert 'source code of the model will not be released' in readme
    assert '21/July/2020' in readme and 'only non-empty cells' in readme
    controls = [("", "", 0), ("100", "100", 0), ("100", "900", 1),
                ("100", "-100", 1), ("-100", "100", 1), ("abc", "xyz", 3)]
    for a,b,n in controls:
        assert lev(a,b) == n
    cases = {
        'digit': witness(doc('100'), doc('900')),
        'bold_digit': witness(doc('<b>100</b>'), doc('<b>900</b>')),
        'sign': witness(doc('100'), doc('-100')),
        'external_unit': witness(doc('100','thousands'), doc('100','millions')),
    }
    expected = {'digit': ('1/3',3,'8/9'), 'bold_digit':('1/5',4,'19/20'),
                'sign':('1/4',3,'11/12'), 'external_unit':('0',3,'1')}
    for key,(dist,denom,score) in expected.items():
        assert (cases[key]['cell_distance'],cases[key]['raw_descendant_denominator'],
                cases[key]['closed_form_score']) == (dist,denom,score)
    assert Fraction(cases['bold_digit']['closed_form_score']) > Fraction(cases['digit']['closed_form_score'])
    amounts = {'thousands':100*1000, 'millions':100*1000000}
    assert Fraction(amounts['millions'],amounts['thousands']) == 1000
    # Finite altered outcomes and out-of-domain witnesses must not be accepted.
    rejections=[]
    for name,wrong in [('digit','1'),('bold_digit','8/9'),('sign','1'),('external_unit','0')]:
        try:
            assert cases[name]['closed_form_score'] == wrong
        except AssertionError:
            rejections.append('incorrect expected score: '+name)
        else:
            raise AssertionError('bad expected result accepted')
    for name,invalid in [('changed topology',doc('100').replace('</tr>','<td>1</td></tr>')),
                         ('span outside contract',doc('100').replace('<td>','<td colspan="2">')),
                         ('cost outside proof',doc('xyz'))]:
        try:
            witness(invalid,doc('100'))
        except AssertionError:
            rejections.append(name)
        else:
            raise AssertionError('unsupported witness accepted')
    data={'witnesses':cases,'external_unit_amounts':amounts,
          'distance_controls':len(controls),'rejected_controls':rejections,
          'upstream_metric_executed':False,'model_executed':False}
    assert json.loads((UNIT / 'witnesses.json').read_text()) == data
    for name in ('source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omitted-paper'):
        value=json.loads((UNIT / (name+'-ledger.json')).read_text())
        assert value['scope'] and value['entries']
    return {'official_acquisitions':6,'paper_pages':11,'rendered_pages':[3,4],
            'source_passages':len(ledger['passages']),'source_bindings':len(ledger['bindings']),
            'official_code_files_read':1,'finite_witnesses':len(cases),
            'distance_controls':len(controls),'rejected_controls':len(rejections),
            'six_literature_ledgers':True,'upstream_execution':False,
            'model_code_read':False,'separate_edd_repository_lead':True,
            'financial_correctness_admitted':False}
