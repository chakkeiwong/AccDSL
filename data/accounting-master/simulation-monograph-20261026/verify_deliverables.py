"""Bounded document verification; no engine or forecast validation."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, json, re
import fitz

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CAND = REPO / 'docs/design/proposal/manuscript-simulation-foundations-20261026'
BS = re.escape(chr(92))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + chr(10))

def cite_locations(paths):
    found = defaultdict(list)
    pattern = BS + r'cite[a-zA-Z]*[*]?(?:\[[^\]]*\])*[{]([^}]+)[}]'
    for path in paths:
        for number, line in enumerate(path.read_text().splitlines(), 1):
            for match in re.finditer(pattern, line):
                for key in match.group(1).split(','):
                    found[key.strip()].append({'file': str(path.relative_to(CAND)), 'line': number})
    return dict(sorted(found.items()))

baseline_checks = []
for name in ['baseline-manifest.json', 'integration-v448-baseline-manifest.json', 'integration-v449-baseline-manifest.json', 'integration-baseline-manifest.json']:
    manifest = json.loads((OUT / name).read_text())
    root = REPO / manifest['root']
    failures = [row['relative'] for row in manifest['sources'] if digest(root / row['relative']) != row['sha256']]
    pdf_ok = digest(root / 'accounting-product-proposal.pdf') == manifest['pdf_sha256']
    baseline_checks.append({'manifest': name, 'sources': len(manifest['sources']), 'changed_sources': failures, 'pdf_unchanged': pdf_ok})
    assert not failures and pdf_ok, (name, failures)
base_manifest = json.loads((OUT / 'integration-baseline-manifest.json').read_text())
base = REPO / base_manifest['root']
inherited = [row for row in base_manifest['sources'] if Path(row['relative']).parts[0] in ('chapters','sections','spec')]
changed = [row['relative'] for row in inherited if digest(CAND / row['relative']) != row['sha256']]
assert not changed, changed
prefix = (CAND / 'references.bib').read_bytes().startswith((base / 'references.bib').read_bytes())
assert prefix
archive = REPO / 'docs/archive/accounting-product-design-v1.2-20261026'
archive_rows = json.loads((archive / 'archive-manifest.json').read_text())
archive_failures = [row['archive'] for row in archive_rows if digest(REPO / row['archive']) != row['sha256']]
old_roots = [row['old'] for row in archive_rows if row['operation'] == 'move' and (REPO / row['old']).exists()]
archive_deps = []
for file in archive.rglob('*.tex'):
    for cmd, target in re.findall(BS + r'(input|include|bibliography|lstinputlisting)(?:\[[^\]]*\])*[{]([^}]+)[}]', file.read_text()):
        for item in target.split(','):
            target_path = archive / item
            if cmd in ('input', 'include') and not target_path.suffix:
                target_path = target_path.with_suffix('.tex')
            if cmd == 'bibliography':
                target_path = target_path.with_suffix('.bib')
            if not target_path.exists():
                archive_deps.append({'file': str(file.relative_to(archive)), 'target': str(target_path)})
assert not archive_failures and not old_roots and not archive_deps
save('preservation-check.json', {'baselines': baseline_checks, 'inherited_sources_identical': len(inherited), 'changed_inherited_sources': changed, 'bibliography_prefix_preserved': prefix, 'archive_hashes': len(archive_rows), 'archive_hash_failures': archive_failures, 'old_roots_remaining': old_roots, 'archive_static_dependencies_missing': archive_deps})

new_cites = cite_locations(sorted((CAND / 'simulation').glob('*.tex')))
all_cites = cite_locations(sorted(CAND.rglob('*.tex')))
entries = re.findall(r'^@[A-Za-z]+[{]([^,]+),', (CAND / 'references.bib').read_text(), re.M)
base_entries = re.findall(r'^@[A-Za-z]+[{]([^,]+),', (base / 'references.bib').read_text(), re.M)
missing = sorted(set(all_cites) - set(entries))
duplicates = sorted(key for key, n in Counter(entries).items() if n > 1)
assert not missing and not duplicates
save('citation-locations.json', new_cites)
save('all-citation-locations.json', all_cites)
save('bibliography-check.json', {'baseline_byte_prefix_preserved': prefix, 'baseline_entries': len(base_entries), 'candidate_entries': len(entries), 'new_part_cited_sources': len(new_cites), 'all_cited_keys': len(all_cites), 'missing_keys': missing, 'duplicate_keys': duplicates, 'uncited_bibliography_keys': sorted(set(entries)-set(all_cites))})

support = json.loads((OUT / 'source-support.json').read_text())
records = {row['id']: row for row in support['records']}
source = json.loads((OUT / 'scenario-reduction-source.json').read_text())
source.update({'title': 'Scenario Reduction in Stochastic Programming: An Approach Using Probability Metrics', 'authors': ['Jitka Dupačová', 'Nicole Gröwe-Kuska', 'Werner Römisch'], 'year': 2000, 'classification': 'DIRECT_METHOD', 'publication_status': '2000 institutional preprint; later publication correspondence not checked', 'inspected_technical_anchors': source['inspection'], 'evidence_record': 'data/accounting-master/simulation-monograph-20261026/source-reading.md', 'allowed_scope': 'Fixed-subset probability redistribution and qualified stochastic-program stability; local expected-output and regret derivations are separately identified', 'claims_forbidden': ['Universal preservation of default probabilities or actor information', 'Global optimality of forward or backward greedy subset choice', 'Validated general company simulation or official-code reproduction'], 'correction_status': 'Retained repository metadata and copy identify version; no separate publisher-wide erratum clearance or later-version equivalence established', 'citation_count': 'not available', 'venue_metric': 'not available'})
records[source['id']] = source
for key, locations in new_cites.items():
    assert key in records, key
    row = records[key]
    path = REPO / (row.get('local_path') or row.get('path'))
    assert path.is_file(), path
    row['local_sha256_verified'] = digest(path)
    row['citation_locations'] = locations
    row.setdefault('review_scope', 'Specified technical passages; not exhaustive clearance of every result or version.')
records['givan2003']['inspected_technical_anchors'] = 'Sections 3.1–3.3 and 4.1–4.3; appendix Theorems 4–7, including full proof of Theorem 7 and supporting lemmas, in retained 62-page author-hosted manuscript.'
support['records'] = [records[key] for key in sorted(new_cites)]
support['cited_sources'] = len(new_cites)
support['unresolved_leads'] = ['Scenario-reduction guarantees for adaptive company policies, threshold payoffs and actor information', 'Francis–Rowell 1978 technical full text', 'Gentry 1974 derivation appendix and 1979 version correspondence', 'Current publisher erratum status for Strebulaev–Whited', 'Matched ACTUS specification, dictionary and runtime', 'Official learned-solver code audits and target-specific numerical evidence']
save('source-support.json', support)

builds = {}
for stem in ['accounting-product-proposal', 'simulation-foundations']:
    log = (CAND / (stem + '.log')).read_text(errors='replace')
    blg = (CAND / (stem + '.blg')).read_text(errors='replace')
    categories = {'overfull': r'Overfull', 'undefined': r'(?:Citation|Reference).*undefined|There were undefined', 'missing_character': r'Missing character', 'duplicate_label': r'multiply defined|duplicate ignored|destination.*already', 'bibtex_warning': r'Warning--'}
    counts = {name: len(re.findall(pattern, blg if name == 'bibtex_warning' else log, re.I)) for name, pattern in categories.items()}
    assert not any(counts.values()), counts
    pdf = fitz.open(CAND / (stem + '.pdf'))
    outside = []
    for number, page in enumerate(pdf, 1):
        for block in page.get_text('blocks'):
            x0,y0,x1,y1 = block[:4]
            if x0 < -0.5 or y0 < -0.5 or x1 > page.rect.width+0.5 or y1 > page.rect.height+0.5:
                outside.append({'page': number, 'bbox': list(block[:4])})
    assert not outside, (stem, outside)
    aux = (CAND / (stem + '.aux')).read_text()
    end = re.search(BS+r'newlabel[{]sim:body-end[}][{][{][^}]*[}][{]([0-9]+)[}]', aux)
    assert end
    body_pages = int(end.group(1)) - (1 if stem == 'simulation-foundations' else 2)
    builds[stem] = {'pdf_pages': len(pdf), 'new_chapter_body_pages': body_pages, 'warnings': counts, 'out_of_page_text_blocks': outside, 'pdf_sha256': digest(CAND / (stem+'.pdf')), 'root_tex_sha256': digest(CAND / (stem+'.tex')), 'engine': 'LuaHBTeX 1.24.0 / TeX Live 2026', 'bibliography': 'BibTeX via latexmk'}
    save('visual/'+stem+'-geometry.json', {'pdf_sha256': builds[stem]['pdf_sha256'], 'pages': len(pdf), 'out_of_page_blocks': outside, 'scope': 'Automated physical-page bounds only; no readability certification.'})
assert 150 <= builds['simulation-foundations']['new_chapter_body_pages'] <= 300
assert len(list((CAND/'simulation').glob('*.tex'))) == 26
save('build-check.json', builds)
save('candidate-source-manifest.json', {'root': str(CAND.relative_to(REPO)), 'version': '5.0', 'sources': [{'relative': str(path.relative_to(CAND)), 'sha256': digest(path)} for path in sorted(CAND.rglob('*')) if path.is_file() and path.suffix in ('.tex','.bib','.lark')]})
print(json.dumps({'builds': builds, 'new_sources': len(new_cites), 'bibliography_entries': len(entries), 'inherited_identical': len(inherited), 'archive_hashes': len(archive_rows)}, indent=2))
