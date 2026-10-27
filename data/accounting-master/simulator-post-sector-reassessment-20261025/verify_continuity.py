"""Read frozen coverage links and compare the preserved original records."""
from pathlib import Path
from hashlib import sha256
import json
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CURRENT = 'data/accounting-master/credit-linked-book-integration-20261025/coverage.json'
OLD = 'data/accounting-master/simulator-gap-reassessment-20261025/original-obligations.json'
PDF = 'docs/design/proposal/manuscript-credit-linked-book-20261025/accounting-product-proposal.pdf'
EXPECTED_PDF = '8b37990bbc97416916ae9874156ecdb4e2a286ba6d6d7cfe70e26c3fd221a878'
def digest(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
def main():
    hashes, cache = {}, {}
    def read(name):
        if name not in cache:
            path = (ROOT/name).resolve()
            assert path.is_relative_to(ROOT), name
            raw = path.read_bytes(); hashes[name] = sha256(raw).hexdigest()
            cache[name] = json.loads(raw)
        return cache[name]
    old, current = read(OLD), read(CURRENT)
    for name, value in old['source_hashes'].items():
        read(name); assert hashes[name] == value, name
    result = {}
    for group, expected_count in [('obligations',53),('interactions',6),('operations',46)]:
        expected = {r['id']:r for r in old['groups'][group]}
        rows = current[group]
        assert len(rows) == len(expected) == expected_count
        assert {r['id'] for r in rows} == set(expected)
        resolved = []
        for row in rows:
            seen = set(); path = CURRENT; links = 0
            while 'prior_ref' in row:
                ref = row['prior_ref']; token = (ref['path'],ref['collection'],ref['id'])
                assert token not in seen, token
                seen.add(token); parent = read(ref['path'])
                matches = [r for r in parent[ref['collection']] if r['id']==ref['id']]
                assert len(matches)==1 and digest(matches[0])==ref['sha256'], token
                path, row = ref['path'], matches[0]; links += 1
                assert links <= 256
            prior = expected[row['id']]
            assert path == prior['resolved_file'], (row['id'],path)
            # Older records embed earlier assessments; compare the exact retained record.
            target = prior['original_record']
            def contains(value):
                if value == target: return True
                if isinstance(value,dict): return any(contains(v) for v in value.values())
                if isinstance(value,list): return any(contains(v) for v in value)
                return False
            assert contains(row), row['id']
            resolved.append({'id':row['id'],'resolved_file':path,'reference_links':links,'original_record_sha256':digest(target)})
        result[group] = resolved
    pdf_hash = sha256((ROOT/PDF).read_bytes()).hexdigest()
    assert pdf_hash == EXPECTED_PDF
    output = {'candidate':'4.32','pdf':PDF,'pdf_sha256':pdf_hash,'groups':result,
              'source_hashes':hashes,'counts':{k:len(v) for k,v in result.items()},
              'interpretation':'ID and evidence continuity only; no requirement completion inferred.'}
    text = json.dumps(output,indent=2,ensure_ascii=False)+'\n'
    path = HERE/'continuity.json'
    if path.exists(): assert path.read_text()==text, 'continuity result changed'
    else: path.write_text(text)
    print(json.dumps({'counts':output['counts'],'coverage_files':len(cache)-1,'pdf_verified':True}))
if __name__ == '__main__': main()
