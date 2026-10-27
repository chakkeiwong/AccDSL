"""One-time receipts and inspected-source bindings; no network or model calls."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

U = Path(__file__).resolve().parent
R = U.parents[2]
S = U / 'sources'
PAPER = R / 'docs/papers/Tests of conditional predictive ability Giacomini (2003).pdf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p), 'bytes': p.stat().st_size}


def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def main():
    assert all(not (U / n).exists() for n in ('request-receipts.json', 'source-record.json'))
    requests = [
        ('crossref', 'https://api.crossref.org/works/10.1111/j.1468-0262.2006.00718.x', 200, 6452, '1.148412', 0, 'Matching bibliographic metadata'),
        ('cemmap-index', 'https://www.cemmap.ac.uk/publication/tests-of-conditional-predictive-ability/', 404, 45768, '6.454127', 0, 'No matching publication page'),
        ('openalex', 'https://api.openalex.org/works/https://doi.org/10.1111/j.1468-0262.2006.00718.x', 200, 25506, '4.036863', 0, 'Matching metadata and institutional locations'),
        ('bc-working-paper', 'https://fmwww.bc.edu/EC-P/wp572.pdf', 0, 0, '10.001548', 28, 'Connection timeout; no body'),
        ('uc-record', 'https://escholarship.org/uc/item/5jk0j5jh', 202, 0, '1.181631', 0, 'Empty body; no technical text'),
        ('munich-working-paper', 'https://econwpa.ub.uni-muenchen.de/econ-wp/em/papers/0308/0308001.pdf', 200, 657408, '2.738107', 0, 'Matching April2003 working paper,38 pages'),
        ('publisher-record', 'https://onlinelibrary.wiley.com/doi/10.1111/j.1468-0262.2006.00718.x', 403, 5553, '4.655613', 0, 'Publisher page inaccessible; final edition/notice unverified'),
        ('forward-metadata', 'https://api.openalex.org/works?filter=cites:W2135150595&sort=cited_by_count:desc&per-page=8&select=id,doi,title,publication_year,cited_by_count,is_retracted', 200, 2895, '1.820176', 0, 'Eight metadata-only citing works')]
    rows = []
    for key, url, status, size, seconds, code, finding in requests:
        body, headers = S / (key + '.body'), S / (key + '.headers')
        assert headers.is_file()
        if body.exists():
            assert body.stat().st_size == size
        else:
            assert key == 'bc-working-paper' and size == 0
        observed = re.findall(r'^HTTP/\S+\s+(\d+)', headers.read_text(), re.M)
        if status:
            assert observed and int(observed[-1]) == status
        command = ['curl', '--location', '--silent', '--show-error', '--connect-timeout', '10',
                   '--max-time', '45', '--max-filesize', '15000000', '--dump-header', rel(headers),
                   '--output', rel(body), '--write-out', '%{http_code} %{size_download} %{time_total} %{url_effective}\\n', url]
        rows.append({'id': key, 'requested_url': url,
                     'effective_url': url.replace('https://www.cemmap.ac.uk/', 'https://cemmap.ac.uk/'),
                     'command_argv': command, 'http_status': status, 'curl_exit': code,
                     'download_bytes': size, 'curl_seconds': seconds,
                     'body': bind(body) if body.exists() else None, 'headers': bind(headers),
                     'finding': finding, 'request_started_utc': None,
                     'time_provenance': 'Curl elapsed value from executed tool output; request start not recorded. Header dates remain distinct observations.',
                     'permissions': 'trusted/elevated curl; public unauthenticated read'})
    receipts = {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'requests': rows,
        'http_requests': 8, 'budget_exhausted': True,
        'local_invocation_failure': {'before': 'openalex', 'option': '--connect-timeoutout',
             'exit_code': 2, 'http_request_sent': False,
             'message': 'curl rejected misspelled option before networking; corrected call retained above'},
        'route_limits': 'No challenge bypass, credentials, registration, outreach, fees or acquired-code execution',
        'provenance_limit': 'Exact request start times were not captured; file times and response dates are not substituted'}
    assert PAPER.read_bytes() == (S / 'munich-working-paper.body').read_bytes()
    text = (S / 'munich-working-paper.txt').read_text()
    pages = text.split('\f')
    assert len(pages) == 39 and not pages[-1].strip()
    anchors = [
        (1, 'This version: April 2003', 'Edition'),
        (4, 'The central idea of this paper', 'Conditional versus population-parameter target'),
        (5, 'We call a test of the hypothesis (2)', 'Actual estimated method'),
        (6, 'it seems appropriate in a time-varying environment', 'Finite-memory motivation'),
        (9, 'The only requirement here', 'Finite maximum window'),
        (10, 'For a given loss function', 'Equation3 conditional null'),
        (10, 'Let us restrict attention', 'Finite test functions'),
        (11, 'Theorem 1 (Conditional predictive accuracy test)', 'Theorem1 conditions'),
        (11, 'requirement of finite estimation window rules out', 'Expanding-window exclusion'),
        (12, 'Corollary 2 Under', 'Uncentered regression identity'),
        (12, 'Corollary 3 Let', 'Missing assumption(iv) reference'),
        (13, 'H0 and HA,h are not necessarily exhaustive', 'Power/alternative boundary'),
        (14, 'For a forecast horizon', 'Null-implied lag structure'),
        (14, 'Theorem 5 (Multi-step conditional predictive accuracy test)', 'Multistep theorem and literal t+1'),
        (15, 'user-specified threshold', 'Selection point rule'),
        (16, 'The results are collected in Table 1.', 'Simulation scope'),
        (20, 'maximum estimation window', 'Application refitting choice'),
        (21, 'The number within parentheses', 'Fitted selection percentages'),
        (23, 'Much work remains to be done', 'Multiplicity/bootstrap extensions'),
        (24, 'The variable', 'Literal product-measurability issue'),
        (25, 'Proof of Theorem 5.', 'Multistep proof'),
        (27, 'Appendix B.', 'Selection algorithm'),
        (33, 'Table 1.', 'Source size table'),
        (34, 'Figure 2:', 'Fitted loss differences'),
        (35, 'Table 2.', 'Source application table meaning')]
    bound_anchors = []
    offset = 0
    offsets = []
    for page in pages[:-1]:
        offsets.append(offset)
        offset += len(page) + 1
    for i, (page, needle, role) in enumerate(anchors, 1):
        matches = list(re.finditer(re.escape(needle).replace(r'\ ', r'\s+'), pages[page-1]))
        assert len(matches) == 1, (page, needle)
        first = offsets[page-1] + matches[0].start()
        last = min(first + max(250, len(needle)), offsets[page-1] + len(pages[page-1]))
        bound_anchors.append({'id': f'GW-A{i:02}', 'page': page, 'role': role,
            'character_span': [first, last], 'quote': text[first:last],
            'lines_by_newline': [text[:first].count('\n')+1, text[:last].count('\n')+1]})
    images = [S / f'theory-{p}.png' for p in (11,12,14)] + [S / 'proof-24.png'] + [S / f'figures-{p}.png' for p in (33,34)]
    source = {'id': 'GW03', 'paper': bind(PAPER), 'download': bind(S / 'munich-working-paper.body'),
        'text': bind(S / 'munich-working-paper.txt'), 'edition': 'Cover: This version: April2003',
        'physical_pages': 38, 'text_pages_inspected': list(range(1,39)),
        'rendered_pages_inspected': [11,12,14,24,33,34], 'rendered_bindings': [bind(p) for p in images],
        'generated_not_viewed': [bind(S / 'theory-13.png')], 'anchors': bound_anchors,
        'source_description_only': True, 'final_edition_equality': 'not_verified',
        'original_author_code': 'not_acquired_or_inspected', 'inference_admitted': False,
        'precedents': [bind(R / p) for p in (
            'data/accounting-master/r05-dependent-loss-source-20261018/backward-snowball-ledger.md',
            'data/accounting-master/r05-repeated-origins-20261023/choice.json',
            'data/accounting-master/r05-forecast-accountability-20261023/completion.json',
            'data/accounting-master/r05-target-overlap-20261018/target-sheets.json')]}
    write('request-receipts.json', receipts)
    write('source-record.json', source)
    print(json.dumps({'requests': len(rows), 'technical_papers': 1, 'pages': 38,
                      'anchors': len(bound_anchors), 'viewed_pages': 6, 'inference_admitted': False}))


if __name__ == '__main__':
    main()
