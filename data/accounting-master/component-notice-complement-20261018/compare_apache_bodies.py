"""Expose every differing line against the fully inspected Apache reference."""
from pathlib import Path
import difflib
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = OUT / 'sources'
REFERENCE = BASE / 'abseil.txt'
reference = REFERENCE.read_bytes().splitlines(keepends=True)
sha = lambda data: hashlib.sha256(data).hexdigest()
rows = []
for name in ['all_except_musl/llvm-libc.txt', 'android/cpu_features.txt', 'pdfium.txt', 'v8_xfa/highway.txt']:
    target = BASE / name
    lines = target.read_bytes().splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(a=reference, b=lines, autojunk=False)
    blocks = []
    covered = []
    print(name)
    for tag, a, z, b, y in matcher.get_opcodes():
        block = {'kind': tag, 'reference_slice_zero_based': [a, z], 'target_slice_zero_based': [b, y], 'reference_sha256': sha(b''.join(reference[a:z])), 'target_sha256': sha(b''.join(lines[b:y]))}
        if tag == 'equal':
            assert reference[a:z] == lines[b:y]
            if b < y:
                print(f'  target lines {b+1}-{y}: exact byte equality with inspected abseil lines {a+1}-{z}')
        else:
            for i in range(b, y):
                print(f'{i+1}: {lines[i].decode("utf-8").rstrip()}')
        blocks.append(block)
        covered.extend(range(b, y))
    assert covered == list(range(len(lines)))
    rows.append({'reference': str(REFERENCE.relative_to(ROOT)), 'reference_sha256': sha(REFERENCE.read_bytes()), 'target': str(target.relative_to(ROOT)), 'target_sha256': sha(target.read_bytes()), 'target_lines': len(lines), 'blocks': blocks, 'scope': 'Complete target coverage by exact byte-equal previously inspected lines and all differing target lines printed for inspection.'})
destination = OUT / 'apache-comparison.json'
with destination.open('x') as handle:
    json.dump({'scope': 'Exact byte/line comparison; full reference read and all displayed differences require actual inspection.', 'files': rows}, handle, indent=2)
    handle.write('\n')
