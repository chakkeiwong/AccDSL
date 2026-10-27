from pathlib import Path
import collections
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CANDIDATE = ROOT / 'docs/design/proposal/manuscript-release-prep-v552r1-20261027'
BS = chr(92)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def records(data):
    if isinstance(data, list): return [('/' + str(i), r) for i, r in enumerate(data)]
    if isinstance(data, dict):
        for key in ['records', 'sources', 'claims', 'authorities']:
            if isinstance(data.get(key), list):
                return [('/' + key + '/' + str(i), r) for i, r in enumerate(data[key])]
        return [('', data)]
    return []

excluded_parts = {'before', 'six-ledgers-before', 'inputs', 'bundle', '__pycache__'}
source_ledgers = []; claim_ledgers = []; other_ledgers = []; excluded = []
for root in [ROOT / 'docs/design/research', ROOT / 'data/accounting-master']:
    for p in root.rglob('*.json'):
        if HERE in p.parents: continue
        source = 'source-support' in p.name or p.name == 'supplemental-support.json'
        claim = 'claim-support' in p.name
        other = p.name in {'backward-snowball.json', 'forward-snowball.json', 'omissions.json', 'citation-venue-metadata.json', 'citation-metadata.json', 'citation-counts.json', 'venue-metadata.json', 'citation-venue.json'}
        if not (source or claim or other): continue
        if any(x in excluded_parts or x.startswith('attempt-') for x in p.parts):
            excluded.append(str(p.relative_to(ROOT))); continue
        (source_ledgers if source else claim_ledgers if claim else other_ledgers).append(p)
source_records = []; claim_records = []; manifests = []
for kind, paths, target in [('source', source_ledgers, source_records), ('claim', claim_ledgers, claim_records), ('other', other_ledgers, None)]:
    for path in sorted(paths):
        data = json.loads(path.read_text()); recs = records(data)
        manifests.append({'kind': kind, 'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'record_count': len(recs), 'top_level_fields': list(data) if isinstance(data, dict) else None})
        if target is None: continue
        for pointer, rec in recs:
            target.append({'ledger': str(path.relative_to(ROOT)), 'pointer': pointer, 'record': rec, 'record_sha256': hashlib.sha256(json.dumps(rec, sort_keys=True, ensure_ascii=False).encode()).hexdigest(), 'ledger_context': {k: v for k, v in data.items() if k not in {'records', 'sources', 'claims', 'authorities'}} if isinstance(data, dict) and pointer else {}})

bib = (CANDIDATE / 'references.bib').read_text()
entries = {}
for match in re.finditer('@[A-Za-z]+[{]([^,]+),', bib):
    start = match.start(); depth = 1; pos = match.end()
    while pos < len(bib) and depth:
        if bib[pos] == '{' and (pos == 0 or bib[pos-1] != BS): depth += 1
        elif bib[pos] == '}' and (pos == 0 or bib[pos-1] != BS): depth -= 1
        pos += 1
    key = match.group(1).strip()
    if key in entries: raise ValueError('Duplicate bibliography key ' + key)
    entries[key] = bib[start:pos]

pattern = re.compile(re.escape(BS) + 'cite[A-Za-z]*[*]?(?:' + re.escape('[') + '[^]]*' + re.escape(']') + ')*[{]([^}]+)[}]')
occurrences = collections.defaultdict(list)
for path in sorted(CANDIDATE.rglob('*.tex')):
    if 'companions' in path.parts: continue
    content = path.read_text()
    for match in pattern.finditer(content):
        for key in match.group(1).split(','):
            occurrences[key.strip()].append({'file': str(path.relative_to(CANDIDATE)), 'line': content[:match.start()].count(chr(10)) + 1, 'citation': match.group(0)})
aux_keys = set()
for name in ['accounting-product-proposal', 'simulation-foundations']:
    for part in (CANDIDATE / (name + '.aux')).read_text().split(BS + 'citation{')[1:]:
        aux_keys.update(part.split('}', 1)[0].split(','))

aliases = {'litcloseestimation': 'adapted-estimation', 'litclosehartmoore': 'hart-moore', 'litclosekerneltop': 'kernel-topology', 'litclosepichlershapiro': 'pichler-shapiro-foundations', 'litcloseprobview': 'probabilistic-adapted', 'litcloseseaman': 'seaman', 'litcloseshapiro': 'shapiro-rectangular', 'litclosesuijs': 'disclosure-tilburg', 'litclosetcvae': 'time-causal-vae', 'litclosexingoldberg': 'xin-goldberg-time', 'litcloseadapted': 'adapted', 'litclosebenzoni': 'debt-fixed-costs', 'litclosedewat': 'capital-dynamics', 'litcloselambrecht': 'investment-payout-debt', 'litclosemccarthy': 'mccarthy', 'litclosepflug': 'pflug', 'litclosesmc2': 'smc2', 'litclosekara': 'kara-robustness'}
identity_checks = []
for item in source_records:
    rec = item['record']
    if not isinstance(rec, dict): continue
    path = next((rec.get(k) for k in ['local_path', 'path', 'local_copy', 'source_pdf', 'pdf', 'source'] if isinstance(rec.get(k), str) and (ROOT / rec[k]).is_file()), None)
    declared = next((rec.get(k) for k in ['sha256', 'source_sha256', 'pdf_sha256', 'local_sha256_verified'] if isinstance(rec.get(k), str) and len(rec[k]) == 64), None)
    if path:
        actual = sha(ROOT / path)
        item['local_identity'] = {'path': path, 'actual_sha256': actual, 'declared_sha256': declared, 'matches': actual == declared if declared else None}
        identity_checks.append(item['local_identity'] | {'ledger': item['ledger'], 'pointer': item['pointer']})

rows = []
for key, locations in sorted(occurrences.items()):
    ids = {key, aliases.get(key, key)}
    matched = [r for r in source_records if isinstance(r['record'], dict) and r['record'].get('id') in ids]
    claims = []
    for r in claim_records:
        rec = r['record']
        if not isinstance(rec, dict): continue
        sources = rec.get('sources', [])
        if not isinstance(sources, list): sources = [sources]
        if isinstance(rec.get('source'), str): sources = sources + [rec['source']]
        if any(isinstance(s, str) and s in ids for s in sources): claims.append({'ledger': r['ledger'], 'pointer': r['pointer']})
    routes = []
    if not matched:
        command = ['rg', '-l', '-F', '--glob', '*.json', '--glob', '*.md', '--glob', '!**/before/**', '--glob', '!**/six-ledgers-before/**', '--glob', '!**/inputs/**', '--glob', '!**/bundle/**', '--glob', '!**/release-plan-execution-20261027/**', key, 'docs/design/research', 'data/accounting-master']
        r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if r.returncode not in {0, 1}: raise RuntimeError(r.stderr)
        routes = r.stdout.splitlines()
    rows.append({'key': key, 'bibliography_entry': entries.get(key), 'occurrences': locations, 'source_ids': sorted(ids), 'alias_basis': 'Manually inspected bibliography title and source ledger title; navigation only, editions and source limits preserved' if key in aliases else 'Exact record ID only', 'source_records': [{'ledger': r['ledger'], 'pointer': r['pointer']} for r in matched], 'linked_claim_records': claims, 'additional_local_routes': routes, 'status': 'retained_source_records_found_not_claim_acceptance' if matched else 'local_evidence_routes_require_inspection' if routes else 'no_route_in_bounded_scan_requires_targeted_search', 'remaining': 'Check the exact current sentence/derivation against the retained technical anchor, edition, limitations and applicable source authority; citation identity alone does not close this.'})

checks = {'all_cited_keys_have_bibliography': set(occurrences) <= set(entries), 'source_scan_matches_built_aux_keys': set(occurrences) == aux_keys, 'ledger_inputs_unchanged': all(sha(ROOT / x['path']) == x['sha256'] for x in manifests), 'declared_source_hash_mismatches': [r for r in identity_checks if r['matches'] is False]}
result = {'date': '2026-10-27', 'candidate': str(CANDIDATE.relative_to(ROOT)), 'bibliography_sha256': sha(CANDIDATE / 'references.bib'), 'bibliography_entries': len(entries), 'citation_keys': len(rows), 'citation_occurrences': sum(len(v) for v in occurrences.values()), 'checks': checks, 'ledger_manifests': manifests, 'source_records': source_records, 'claim_records': claim_records, 'citation_routes': rows, 'excluded_copy_paths': sorted(excluded), 'scope': 'Current citation navigation plus preserved source/claim records and six-ledger routes. No new paper reading, whole-literature completeness, technical implication check, edition equivalence or release acceptance.'}
(HERE / 'citation-source-index.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + chr(10))
summary = collections.Counter(r['status'] for r in rows)
lines = ['# Current citation and technical-source routes', '', '27 October 2026. The candidate has ' + str(len(rows)) + ' distinct cited keys and ' + str(result['citation_occurrences']) + ' source citation occurrences. The index retains ' + str(len(source_records)) + ' source records and ' + str(len(claim_records)) + ' claim records without merging away their scope or version qualifications.', '', 'This is navigation and identity reconciliation. Every exact current claim still needs an implication/authority review. Unmatched IDs do not establish missing literature: local evidence routes are listed. Old section numbers stay attached to their original supplement.', '', '| Citation | Locations | Source records | Claim links | Current task |', '|---|---:|---:|---:|---|']
for r in rows:
    lines.append('| ' + r['key'] + ' | ' + str(len(r['occurrences'])) + ' | ' + str(len(r['source_records'])) + ' | ' + str(len(r['linked_claim_records'])) + ' | ' + r['status'] + ' |')
lines += ['', '## Verification and remaining work', '', json.dumps(checks, indent=2), '', 'Review source hash mismatches before using dependent support. The source index preserves complete original records; counts do not establish claim coverage. Continue with current-sentence/anchor mappings for consequential financing, information and compression claims, then remaining source and authority routes.']
(HERE / 'citation-source-index.md').write_text(chr(10).join(lines) + chr(10))
print(json.dumps({'citation_keys': len(rows), 'occurrences': result['citation_occurrences'], 'source_records': len(source_records), 'claim_records': len(claim_records), 'ledgers': len(manifests), 'route_statuses': dict(summary), 'checks': checks}, indent=2))
