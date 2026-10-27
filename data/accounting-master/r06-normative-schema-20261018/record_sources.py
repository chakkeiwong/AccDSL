"""One-time transcription of acquired source receipts and exact comparison."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]

def bind(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

def write(name, obj):
    with (UNIT/name).open('x') as f:
        json.dump(obj, f, indent=2); f.write(chr(10))

prefix = 'https://specifications.xbrl.org/'
old = 'https://www.xbrl.org/Specification/XBRL-RECOMMENDATION-2003-12-31+Corrected-Errata-2008-07-02.'
rows = [
    ('01-navigation', prefix, 6, 0, 0, 0.000136, None, 'sandbox DNS failure; no body'),
    ('01-navigation-trusted', prefix, 0, 200, 11073, 1.812884, 'text/html', 'trusted retry'),
    ('02-index', prefix+'specifications-full-index.html', 0, 200, 118473, 2.981023, 'text/html', 'home page href'),
    ('03-history', prefix+'release-history-base-spec-xbrl-2.1.html', 0, 200, 9305, 3.435616, 'text/html', 'full index href'),
    ('04-specification', old+'htm', 0, 200, 1593764, 2.682604, 'text/html; charset=UTF-8', 'release history exact dated href'),
    ('05-normative', old+'rtf', 0, 200, 6643279, 6.198365, 'application/rtf', 'HTML explicitly names this normative filename; resolve sibling URL'),
]
acquisitions = []
for stem,url,exitcode,status,size,seconds,ctype,lead in rows:
    headers = UNIT/'sources'/f'{stem}.headers'
    body = UNIT/'sources'/f'{stem}.body'
    assert headers.is_file()
    assert (body.stat().st_size if body.exists() else 0) == size
    command = ['curl']
    if stem not in ('01-navigation', '01-navigation-trusted'):
        command += ['--silent', '--show-error']
    command += ['--location', '--connect-timeout', '10', '--max-time', '35', '--max-filesize', '12582912',
                '--proto', '=https', '--proto-redir', '=https', '--dump-header', str(headers.relative_to(ROOT)),
                '--output', str(body.relative_to(ROOT)), '--write-out', '%{json}'+chr(92)+'n', url]
    acquisitions.append({'id':stem, 'url':url, 'effective_url':url, 'lead':lead,
                         'exitcode':exitcode, 'http_status':status, 'bytes':size, 'curl_seconds':seconds,
                         'content_type':ctype, 'redirects':0, 'trusted':stem!='01-navigation',
                         'command_argv':command, 'headers':bind(headers), 'body':bind(body) if body.exists() else None,
                         'receipt_provenance':'transcribed from completed tool curl JSON; original response headers/body retained'})
write('source-ledger.json', {'scope':'finite source-copy inquiry, five URLs and one sandbox retry; no further acquisition',
                           'acquisitions':acquisitions,
                           'web_search':'Two server search queries for exact edition returned no source entries; not evidentiary.',
                           'inspected_sources':'Official links, edition/status/Appendix A boundaries, complete extracted instance schema; no claim of whole-specification reading.'})
sp=importlib.util.spec_from_file_location('comparison', UNIT/'compare.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
n,h,r,meta=m.extraction()
n1=m.remove_header_comment(n);r1=m.remove_header_comment(r)
assert n1+chr(10) == r1
write('exact-correspondence.json', {
    'retained':bind(m.RETAINED),'normative_rtf':bind(UNIT/'sources/05-normative.body'),
    'normative_extracted':bind(UNIT/'normative-instance.xsd'),
    'normalizations':['retained CRLF to LF', 'remove exactly the first XML comment after the prolog in each text',
                      'append one LF to the extracted RTF XML ending at the closing schema tag'],
    'exact_equal_after_these_only':True, 'normalised_length':len(r1),
    'normalised_sha256':hashlib.sha256(r1.encode()).hexdigest(),
    'remaining_differences':[],
    'claim':'exact source text correspondence under the three listed presentation/notice adjustments; not byte identity or schema validation',
    'extraction_failures':['Initial decoder rejected its starred-destination regex; corrected to explicit literal marker before successful extraction.',
                           'One attempted source correction had Python quoting syntax error; no source data or successful extraction was changed.'],
    'normalization_interpretation':'The line diff has zero lines because splitlines ignores the final newline; the separate exact comparison makes that difference explicit.'})
print(json.dumps({'acquisitions':len(acquisitions),'exact_correspondence':True,'normalised_characters':len(r1)}))
