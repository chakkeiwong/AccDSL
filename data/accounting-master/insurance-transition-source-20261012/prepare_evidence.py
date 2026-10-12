"""Bind the inspected transition excerpts and four bounded access responses."""
import datetime
import hashlib
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
assert not (OUT / 'completion.json').exists()
started = time.monotonic()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda s: ' '.join(s.split())
def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

specs = [
    ('edition', 1, 'annual periods beginning on or after 1 January 2023 but before 1 July 2026.'),
    ('comparison', 5, 'Australian-specific paragraphs (which are not included in IFRS 17) are identified with the prefix'),
    ('C2', 57, 'the transition date is the beginning of the annual reporting period immediately preceding the date of initial application.'),
    ('C3', 57, 'Unless it is impracticable to do so, or paragraph C5A applies, an entity shall apply AASB 17 retrospectively'),
    ('C4', 57, 'recognise any resulting net difference in equity.'),
    ('C5', 57, 'If, and only if, it is impracticable for an entity to apply paragraph C3 for a group of insurance contracts'),
    ('C5A', 57, 'for a group of insurance contracts with direct participation features to which it could apply AASB 17 retrospectively if, and only if:'),
    ('C5A-b', 58, 'as specified in paragraph B115, before the transition date.'),
    ('C6', 58, 'If the entity cannot obtain reasonable and supportable information necessary to apply the modified retrospective approach, it shall apply the fair value approach.'),
    ('C8', 58, 'only to the extent that an entity does not have reasonable and supportable information to apply a retrospective approach.'),
    ('C12', 59, 'The cash flows that are known to have occurred include cash flows resulting from contracts that ceased to exist before the transition date.'),
    ('C13', 59, 'That spread shall be an average over at least three years immediately before the transition date.'),
    ('C14D', 59, 'If an entity does not have reasonable and supportable information to apply paragraph C14B, the entity shall determine the following amounts to be nil at the transition date:'),
    ('C16C', 60, 'If an entity does not have reasonable and supportable information to apply paragraph C16A, the entity shall not identify a loss-recovery component for the group of reinsurance contracts held.'),
    ('C17-e', 60, 'adjust the loss component to nil and increase the liability for remaining coverage excluding the loss component by the same amount.'),
    ('C20', 61, 'as the difference between the fair value of a group of insurance contracts at that date and the fulfilment cash flows measured at that date.'),
    ('C20-demand', 61, 'an entity shall not apply paragraph 47 of AASB 13 Fair Value Measurement (relating to demand features).'),
    ('C20A', 61, 'without the need to meet the condition set out in paragraph B119C'),
    ('C22', 62, 'reasonable and supportable information available at the transition date.'),
    ('C24', 62, 'as nil – unless (c) applies;'),
    ('C24B', 62, 'exclude from the measurement of any groups of insurance contracts the amount of any asset for insurance acquisition cash flows.'),
    ('C25', 63, 'the beginning of the earliest adjusted comparative period presented'),
    ('C27', 63, 'clearly identify the information that has not been adjusted, disclose that it has been prepared on a different basis, and explain that basis.'),
    ('C28E', 63, 'only apply those paragraphs to comparative information for reporting periods between the transition date to AASB 17 and the date of initial application of AASB 17'),
    ('C31', 64, 'The entity may restate prior periods only if it is possible without the use of hindsight.'),
]
anchors = []
for label, page, excerpt in specs:
    p = OUT / 'text' / f'page-{page}.txt'
    text = norm(p.read_text()); excerpt = norm(excerpt)
    assert text.count(excerpt) == 1, label
    anchors.append({'provision': label, 'pdf_page': page, 'text_path': str(p.relative_to(ROOT)),
                    'normalized_start': text.index(excerpt), 'exact_normalized_excerpt': excerpt})
save('source-anchors.json', anchors)

requests = [
    ('aasb-index', 'https://www.aasb.gov.au/pronouncements/accounting-standards/', 'aasb-index.html', 200, 'official index links to standards portal'),
    ('standards-portal', 'https://standards.aasb.gov.au/accounting-standards', 'standards-portal.html', 200, 'paginated official index; initial page does not provide the two dependencies'),
    ('aasb108', 'https://www.aasb.gov.au/admin/file/content105/c9/AASB108_08-15_COMPdec22_01-23.pdf', 'aasb108-response.pdf', 404, 'constructed edition URL; HTML error body, not a PDF'),
    ('aasb13', 'https://www.aasb.gov.au/admin/file/content105/c9/AASB13_08-15_COMPdec22_01-23.pdf', 'aasb13-response.pdf', 404, 'constructed edition URL; HTML error body, not a PDF'),
]
access = []
for label, url, filename, status, disposition in requests:
    header = OUT / 'acquisition' / f'{label}.headers'; body = OUT / 'acquisition' / filename
    found = re.findall(r'^HTTP/\S+\s+(\d+)', header.read_text(), re.M)
    assert int(found[-1]) == status
    assert not body.read_bytes().startswith(b'%PDF'), filename
    access.append({'url': url, 'status': status, 'body': str(body.relative_to(ROOT)),
        'body_sha256': sha(body), 'bytes': body.stat().st_size, 'disposition': disposition,
        'command': ['curl', '--location', '--silent', '--show-error', '--max-time', '40',
                    '--max-filesize', '12000000', '--dump-header', str(header.relative_to(ROOT)),
                    '--output', str(body.relative_to(ROOT)), '--write-out',
                    'http=%{http_code} bytes=%{size_download} url=%{url_effective}\n', url]})
save('acquisition.json', access)
source = ROOT / 'docs/design/research/standards/aasb17.pdf'
save('source-evidence.json', {
    'source': str(source.relative_to(ROOT)), 'source_sha256': sha(source),
    'selected_read_pages': [1, 5, 57, 58, 59, 60, 61, 62, 63, 64],
    'text_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sorted((OUT / 'text').glob('*.txt'))},
    'renders': [{'pdf_page': int(p.stem.split('-')[-1]), 'path': str(p.relative_to(ROOT)),
                 'sha256': sha(p), 'source_sha256': sha(source), 'author_inspected': True}
                for p in sorted((OUT / 'rendered').glob('*.png'))],
    'source_anchors': len(anchors), 'requests': len(access),
    'dependency_text_acquired': False, 'wall_seconds': time.monotonic() - started,
    'scope': 'selected transition provisions; no complete AASB 108/13/9 dependency review'})
print(json.dumps({'anchors': len(anchors), 'requests': len(access), 'source_pages': 10, 'renders': 6}))
