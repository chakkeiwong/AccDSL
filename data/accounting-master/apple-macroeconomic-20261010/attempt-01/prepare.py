"""Prepare the annual-01 macroeconomic risk source unit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, shutil, subprocess, sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PLAN = ROOT / 'docs/plans/accounting-apple-macroeconomic-20261010.md'
FRONTIER = ROOT / 'data/accounting-master/apple-risk-coverage-20261010'
PRIOR = FRONTIER / 'run-manifest.json'
POINTERS = ['docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md',
            'docs/plans/accounting-continuation-requirements-20261007.md', 'docs/plans/accounting-master-current.md']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, value):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def baseline():
    assert not (OUT / 'baseline.json').exists()
    prior = read(PRIOR)
    assert sha(PRIOR) == read(PRIOR.with_name('completion.json'))['manifest_sha256']
    for name, digest in prior['artifact_hashes'].items():
        assert sha(ROOT / name) == digest, name
    relocations = []
    for name in POINTERS:
        dst = OUT / 'pointers-before' / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dst)
        relocations.append(dict(historical_path=name, preserved_path=rel(dst), sha256=sha(dst)))
    save('baseline.json', dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        prior_manifest=rel(PRIOR), prior_manifest_sha256=sha(PRIOR),
        prior_completion=rel(PRIOR.with_name('completion.json')),
        prior_completion_sha256=sha(PRIOR.with_name('completion.json')),
        prior_artifact_count=len(prior['artifact_hashes']), pointer_relocations=relocations,
        prior_result=rel(FRONTIER / 'result.md'), prior_checks=rel(FRONTIER / 'checks.json')))
    print(json.dumps(dict(prior_artifacts=len(prior['artifact_hashes']), pointers=len(relocations))))


SELECTED = [
    ('apple-perimeter-20261009', 'dependencies', 'annual.business_segments', 'region definitions and customer-location meaning'),
    ('apple-perimeter-20261009', 'dependencies', 'annual.distribution', 'direct and indirect distribution channels'),
    ('apple-segments-20261009', 'dependencies', 'annual.segment_mda', 'dated regional sales and currency explanations'),
    ('apple-segments-20261009', 'material_units', 'annual.note.13.definition', 'segment population and attribution basis'),
    ('apple-liquidity-20261009', 'material_units', 'annual.note.4.investment_2024', 'dated investment portfolio population'),
    ('apple-liquidity-20261009', 'material_units', 'annual.note.4.trade', 'trade-receivable concentration and credit support'),
    ('apple-liquidity-20261009', 'material_units', 'annual.note.4.vendor', 'vendor receivables and long-term prepayments'),
    ('apple-liquidity-20261009', 'dependencies', 'annual.liquidity', 'unrestricted resources and contractual cash requirements'),
    ('apple-liquidity-20261009', 'dependencies', 'annual.market_risk', 'hypothetical interest/foreign-exchange sensitivity'),
    ('apple-debt-20261009', 'dependencies', 'annual.hedging', 'hedge scope and residual financial exposure'),
    ('apple-debt-20261009', 'material_units', 'annual.note.9.commercial_terms', 'commercial-paper terms and dated balances'),
    ('apple-debt-20261009', 'material_units', 'annual.note.9.term_measurement', 'term-debt principal and carrying components'),
]


def sources():
    assert not (OUT / 'source-checks.json').exists()
    checks, refs = [], {}
    def ck(name, ok): checks.append(dict(id=name, passed=bool(ok)))
    prior_cov = read(FRONTIER / 'risk-coverage.json')
    rec = next(x for x in prior_cov['records'] if x['source'] == 'annual' and x['index'] == 1)
    annual = ROOT / 'docs/design/cases/apple/annual-2024.txt'
    interim = ROOT / 'docs/design/cases/apple/interim-2025q1.txt'
    annual_text, interim_text = annual.read_text(), interim.read_text()
    for p in [annual, interim, ROOT / 'docs/design/cases/apple/annual-2024.pdf',
              ROOT / 'docs/design/cases/apple/interim-2025q1.html', PLAN,
              FRONTIER / 'risk-coverage.json', FRONTIER / 'checks.json', FRONTIER / 'result.md',
              FRONTIER / 'next-source-frontier.md']:
        refs[rel(p)] = sha(p)
    inventory = ROOT / rec['body_path']
    ck('annual-01 exact inventory body', annual_text[rec['start']:rec['body_end']] == inventory.read_text())
    ck('annual-01 no prior overlap', rec['retention_status'] == 'no prior retained reading' and not rec['prior_overlaps'])
    footer = annual_text.find('Apple Inc. | 2024 Form 10-K | 5', rec['heading_end'], rec['body_end'])
    semantic_end = footer if footer >= 0 else rec['body_end']
    semantic = annual_text[rec['heading_end']:semantic_end]
    paragraphs = []
    for match in re.finditer(r'\S.*?(?=\n\s*\n|\Z)', semantic, flags=re.S):
        a, b = rec['heading_end'] + match.start(), rec['heading_end'] + match.end()
        q = annual_text[a:b]
        f = OUT / 'sources' / f'annual-01-paragraph-{len(paragraphs)+1:02}.txt'
        f.parent.mkdir(parents=True, exist_ok=True); f.write_text(q)
        paragraphs.append(dict(index=len(paragraphs)+1, start=a, end=b, quote=q,
                               sha256=hashlib.sha256(q.encode()).hexdigest(), path=rel(f), file_sha256=sha(f)))
        ck(f'annual-01 paragraph {len(paragraphs)} exact', annual_text[a:b] == q)
    ck('annual-01 known page furniture boundary', semantic_end == 33857 and rec['body_end'] == 33890)
    ck('annual-01 paragraph population is four', len(paragraphs) == 4)
    ck('annual-01 semantic partition is contiguous', ''.join(p['quote'] + '\n\n' for p in paragraphs).rstrip() == semantic.rstrip())
    selected = []
    for unit, kind, key, role in SELECTED:
        supplement = ROOT / 'data/accounting-master' / unit / 'source-claim-supplement.json'
        manifest = supplement.with_name('run-manifest.json')
        d, m = read(supplement), read(manifest)
        ck(f'{key} supplement manifest binding', m['artifact_hashes'][rel(supplement)] == sha(supplement))
        refs[rel(supplement)] = sha(supplement); refs[rel(manifest)] = sha(manifest)
        entry = d['dependencies'][key] if kind == 'dependencies' else next(x for x in d['material_units'] if x['id'] == key)
        source_id = entry.get('source_id', entry.get('source'))
        source_path = ROOT / ('docs/design/cases/apple/annual-2024.txt' if source_id == 'annual' else 'docs/design/cases/apple/interim-2025q1.txt')
        source_text = source_path.read_text()
        start, end, quote = entry['start'], entry['end'], entry['quote']
        expected = entry.get('span_sha256', entry.get('sha256'))
        ck(f'{key} exact interval', source_text[start:end] == quote)
        ck(f'{key} quote hash', hashlib.sha256(quote.encode()).hexdigest() == expected)
        ck(f'{key} extraction hash', sha(source_path) == entry['extraction_sha256'])
        selected.append(dict(unit=unit, supplement=rel(supplement), supplement_sha256=sha(supplement),
            manifest=rel(manifest), manifest_sha256=sha(manifest), kind=kind, id=key, role=role,
            source_id=source_id, start=start, end=end, quote=quote,
            quote_sha256=hashlib.sha256(quote.encode()).hexdigest(), source_path=rel(source_path),
            source_sha256=sha(source_path), interpretation=entry.get('interpretation', 'Prior bounded source reading; meaning remains scoped.')))
    preamble = FRONTIER / 'interim-preamble.txt'; scope = read(FRONTIER / 'interim-scope.json')
    ck('interim incorporation preamble exact', interim_text[scope['start']:scope['ranges'][0][1]] == preamble.read_text())
    refs[rel(preamble)] = sha(preamble); refs[rel(FRONTIER / 'interim-scope.json')] = sha(FRONTIER / 'interim-scope.json')
    save('source-claim-supplement.json', dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        body=dict(source='annual', heading=dict(start=rec['start'], end=rec['heading_end'], quote=annual_text[rec['start']:rec['heading_end']]),
            body_start=rec['heading_end'], semantic_end=semantic_end, body_end=rec['body_end'], source_path=rel(annual),
            source_sha256=sha(annual), inventory_body_path=rec['body_path'], inventory_body_sha256=rec['body_sha256'],
            paragraphs=paragraphs, page=8, page_furniture=annual_text[semantic_end:rec['body_end']]),
        interim_context=dict(path=rel(preamble), sha256=sha(preamble), quote=preamble.read_text(),
            meaning='FY2025 Q1 incorporates annual risk factors except stated changes; no annual-01 update inferred.'),
        selected_dependencies=selected, inputs=refs,
        limits=['No probability, elasticity, tariff/rate, geographic share, loss amount, journal or forecast is inferred.',
                'Annual segment regions and Note 4 populations are not legal-entity or supplier-route maps.',
                'Reported amounts remain dated observations, not macroeconomic shock parameters.']))
    report = dict(checker_sha256=sha(Path(__file__)), inputs=refs, checks=checks,
                  passed=sum(x['passed'] for x in checks), failed=sum(not x['passed'] for x in checks),
                  selected_dependencies=len(selected), annual_paragraphs=len(paragraphs))
    save('source-checks.json', report)
    assert report['failed'] == 0, [x for x in checks if not x['passed']]
    print(json.dumps({k: report[k] for k in ['passed', 'failed', 'selected_dependencies', 'annual_paragraphs']}))


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    action = sys.argv[1]
    if action == 'baseline': baseline()
    elif action == 'sources': sources()
    else: raise SystemExit('expected baseline or sources')
