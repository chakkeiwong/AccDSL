"""Read-only source checks and independent finite implications; stdlib only."""
from fractions import Fraction
import ast
import copy
import hashlib
from itertools import combinations
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
S = UNIT / 'sources'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text())

def tokenise(raw):
    # Independent boundary formulation: starts are byte zero and noncontinuations.
    if not raw:
        return []
    starts = [0] + [i for i in range(1, len(raw)) if not 128 <= raw[i] < 192]
    return [raw[a:b] for a, b in zip(starts, starts[1:] + [len(raw)])]

def oracle(a, b):
    # Exhaustive subsequence intersection, not the acquired dynamic program.
    sa = {tuple(a[i] for i in ix) for k in range(len(a)+1)
          for ix in combinations(range(len(a)), k)}
    sb = {tuple(b[i] for i in ix) for k in range(len(b)+1)
          for ix in combinations(range(len(b)), k)}
    return max(map(len, sa & sb))

def converted(x, version):
    if type(x) is str:
        try:
            return x.encode('utf-8', 'strict'), None
        except UnicodeEncodeError:
            return None, 'unicode_conversion_rejected'
    if type(x) is bytes:
        return x, None
    if type(x) is bytearray and version == 'v2.11.1':
        return bytes(x), None
    return None, 'input_type_rejected'

def describe(x):
    return {'type': type(x).__name__, 'repr': ascii(x), 'python_length': len(x)}

def finite_examples():
    inputs = ['ABC', '税', '\0', 'A\0Z', '\U0001f680', 'e\u0301',
              '\ud800', '\udfff', '\ud83d\ude00', b'\xc3\xa9', b'A\0Z',
              b'\xffA', b'\x80A', bytearray(b'\xc3\xa9'), bytearray(b'A\0Z')]
    converted_rows = []
    for x in inputs:
        row = describe(x)
        for v in ('v2.2.0', 'v2.11.1'):
            raw, error = converted(x, v)
            row[v] = {'error': error, 'hex': raw.hex() if raw is not None else None,
                      'tokens': [r.hex() for r in tokenise(raw)] if raw is not None else None}
        converted_rows.append(row)
    pairs = [
        ('unicode_nul', 'A\0D', 'B\0D'),
        ('bytes_nul', b'A\0D', b'B\0D'),
        ('nonascii_bytes', b'\xc3\xa9', b'a\xc3\xa9'),
        ('mixed_equal_text', 'é', b'\xc3\xa9'),
        ('invalid_bytes', b'\xffA', b'\xffB'),
        ('bytearray_difference', bytearray(b'\xc3\xa9'), bytearray(b'a\xc3\xa9')),
        ('equal_surrogate_shortcut', '\ud800', '\ud800'),
        ('unequal_surrogate', '\ud800', 'A'),
        ('equal_bytes_shortcut', b'\xc3\xa9', b'\xc3\xa9'),
        ('mixed_empty', '', b''),
        ('equal_bytearray_shortcut', bytearray(b'x'), bytearray(b'x')),
    ]
    rows = []
    for name, a, b in pairs:
        row = {'id': name, 'left': describe(a), 'right': describe(b)}
        for v in ('v2.2.0', 'v2.11.1'):
            if a == b:
                row[v] = {'outcome': 'equality_shortcut', 'score': '1'}
                continue
            ra, ea = converted(a, v)
            rb, eb = converted(b, v)
            if ea or eb:
                row[v] = {'outcome': ea or eb}
                continue
            lcs = oracle(tokenise(ra), tokenise(rb))
            denominator = len(a) + len(b)
            outcome = {'outcome': 'score' if denominator else 'zero_denominator',
                       'token_lcs': lcs, 'denominator': denominator}
            if denominator:
                outcome['score'] = str(Fraction(2*lcs, denominator))
            try:
                ua, ub = ra.decode('utf-8', 'strict'), rb.decode('utf-8', 'strict')
                l = oracle(ua, ub)
                outcome['decoded_codepoint_score'] = str(Fraction(2*l, len(ua)+len(ub))) if ua != ub else '1'
            except UnicodeDecodeError:
                outcome['decoded_codepoint_score'] = 'undefined_invalid_utf8'
            row[v] = outcome
        rows.append(row)
    return {'meaning': 'Conditional source implications for exact built-in inputs; no binding execution.',
            'conversions': converted_rows, 'pairs': rows}

EXPECTED_CLAIMS = {
    'versions_exhaust_dependency_range': False,
    'all_python_str_strictly_utf8_encodable': False,
    'unicode_nul_preserved': True,
    'bytes_validated_as_utf8': False,
    'v2_2_0_bytearray_accepted': False,
    'v2_11_1_bytearray_accepted': True,
    'surrogate_caster_load_succeeds': False,
    'equal_surrogate_wrapper_shortcut': True,
    'final_binding_exception_type_checked': False,
    'distribution_or_installed_identity_established': False,
}

def validate_claims(claims):
    assert claims == EXPECTED_CLAIMS, 'unsupported or changed source claim'

def check():
    count = 0
    def need(test, label):
        nonlocal count
        assert test, label
        count += 1
    ledger = load(UNIT / 'source-ledger.json')
    need(len(ledger['acquisitions']) == 14, 'bounded requests')
    for row in ledger['acquisitions']:
        for item in row['files']:
            need(digest(ROOT / item['path']) == item['sha256'], item['path'])
        receipt = load(S / (row['stem'] + '.receipt.json'))
        invocation = load(S / (row['stem'] + '.invocation.json'))
        need(receipt['http_code'] == 200 and invocation['returncode'] == 0, 'HTTP source success')
        need((S / (row['stem'] + '.body')).stat().st_size == receipt['size_download'], 'actual size')
    for row in ledger['blobs']:
        raw = (S / (row['stem'] + '.body')).read_bytes()
        tree = load(S / f"{row['version_index']}-tree.body")
        identity = load(S / f"{row['version_index']}-commit.body")
        need(tree['sha'] == identity['commit']['tree']['sha'] and not tree['truncated'], 'tree identity')
        e = next(x for x in tree['tree'] if x['path'] == row['source_path'])
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == e['sha'] == row['git_blob'], 'git blob')
    for a in ledger['anchors']:
        raw = ROOT / a['path']
        need(digest(raw) == a['sha256'], 'anchor source identity')
        excerpt = '\n'.join(raw.read_text().splitlines()[a['first_line']-1:a['last_line']])
        need(excerpt == a['excerpt'], 'anchor content')
    old = (S/'s00.body').read_text().splitlines()[1098:1203]
    new = (S/'s03.body').read_text().splitlines()[363:507]
    old, new = '\n'.join(old), '\n'.join(new)
    for text in (old, new):
        need('PyUnicode_Check(load_src.ptr())' in text, 'Unicode branch')
        need('PyErr_Clear();' in text and 'return false;' in text, 'conversion rejection')
        need('StringType(bytes, (size_t) PYBIND11_BYTES_SIZE(src.ptr()))' in text, 'bytes explicit length')
    need('PyUnicode_AsEncodedString(' in old and '"utf-8"' in old, 'old UTF8 path')
    need('StringType(buffer, length)' in old, 'old UTF8 explicit length')
    need('PyUnicode_AsUTF8AndSize(load_src.ptr(), &size)' in new, 'new UTF8 path')
    need('StringType(buffer, static_cast<size_t>(size))' in new, 'new explicit length')
    need('PyByteArray_Check' not in old and 'PyByteArray_Check' in new, 'version-dependent bytearray')
    need('StringType(bytearray, (size_t) PyByteArray_Size(src.ptr()))' in new, 'bytearray explicit length')
    for name in ('helper0','helper1'):
        text=(S/(name+'.body')).read_text()
        for macro,api in [('CHECK','PyBytes_Check'),('AS_STRING','PyBytes_AsString'),('SIZE','PyBytes_Size')]:
            need(f'#define PYBIND11_BYTES_{macro} {api}' in text,'bytes API mapping')
    for name in ('s01','s04'):
        need('All Python ``str`` can be encoded in UTF-8' in (S/(name+'.body')).read_text(),'universal documentary claim retained')
    wrapper = ROOT/'data/accounting-master/r04-pubtablesv2-20261019/sources/05-metric.py'
    fn = next(n for n in ast.parse(wrapper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='lcs_similarity')
    need([type(n).__name__ for n in fn.body]==['Expr','If','Assign','Return'],'wrapper no extra type validation')
    need(ast.unparse(fn.body[1].test)=='string1 == string2','shortcut condition')
    need(ast.unparse(fn.body[2].value)=='pylcs.lcs_sequence_length(string1, string2)','dependency call')
    examples = finite_examples()
    need(load(UNIT/'witnesses.json') == examples,'finite result binding')
    r = {x['id']:x for x in examples['pairs']}
    for name, expected in [('unicode_nul','2/3'),('bytes_nul','2/3'),('nonascii_bytes','2/5'),('mixed_equal_text','2/3'),('invalid_bytes','1/2')]:
        for v in ('v2.2.0','v2.11.1'):
            need(r[name][v]['score']==expected, name)
    need(r['nonascii_bytes']['v2.11.1']['decoded_codepoint_score']=='2/3','byte denominator difference')
    need(r['mixed_equal_text']['v2.11.1']['decoded_codepoint_score']=='1','mixed equality difference')
    need(r['bytearray_difference']['v2.2.0']['outcome']=='input_type_rejected','old bytearray rejection')
    need(r['bytearray_difference']['v2.11.1']['score']=='2/5','new bytearray path')
    for v in ('v2.2.0','v2.11.1'):
        need(r['equal_surrogate_shortcut'][v]['score']=='1','shortcut bypasses conversion')
        need(r['unequal_surrogate'][v]['outcome']=='unicode_conversion_rejected','unequal surrogate rejected')
        need(r['mixed_empty'][v]['outcome']=='zero_denominator','mixed-empty failure')
    validate_claims(load(UNIT/'claim-support-ledger.json')['summary'])
    rejected = []
    for name in EXPECTED_CLAIMS:
        changed=copy.deepcopy(EXPECTED_CLAIMS); changed[name]=not changed[name]
        try:
            validate_claims(changed)
        except AssertionError:
            rejected.append(name)
    need(len(rejected)==len(EXPECTED_CLAIMS),'altered claim controls')
    need(len(ledger['blobs'])==8,'pinned selected blobs')
    for name in ('source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omission-risk'):
        need((UNIT/(name+'-ledger.json')).is_file(),'additive ledger')
    return {'assertions':count,'acquisitions':14,'pinned_blobs':8,'anchors':len(ledger['anchors']),
            'input_examples':len(examples['conversions']),'wrapper_pairs':len(examples['pairs']),
            'altered_claim_controls_rejected':len(rejected),'runtime_executed':False,'whole_rows_closed':0}
