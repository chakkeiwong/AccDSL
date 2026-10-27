"""Check the bounded successor against its protected manuscript baseline."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected(text):
    return {
        'labels': Counter(re.findall(r'\\label\{([^}]+)\}', text)),
        'references': Counter(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}', text)),
        'citations': Counter(re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)),
        'bracket_displays': Counter(re.findall(r'\\\[(.*?)\\\]', text, re.S)),
        'environment_displays': Counter(re.findall(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}(.*?)\\end\{\1\}', text, re.S)),
    }


def main():
    started = datetime.now(timezone.utc).isoformat()
    timer = time.perf_counter()
    baseline = json.loads((OUT / 'baseline.json').read_text())
    source, target = (ROOT / baseline[k] for k in ('source_root', 'candidate_root'))
    issues, changes = [], []
    allowed = {'accounting-product-proposal.tex', 'chapters/06-language.tex',
               'chapters/07-execution.tex', 'chapters/17-portable-reference.tex'}
    # A sentinel prevents a broken pattern from vacuously passing.
    sample = r'\label{a} \ref{a} \citep{x} \[x+y\] \begin{equation}z\end{equation}'
    assert all(sum(v.values()) == 1 for v in protected(sample).values())
    totals = Counter()
    for name, expected in baseline['source_hashes'].items():
        old, new = source / name, target / name
        if sha(old) != expected:
            issues.append({'baseline_changed': name})
        if not new.exists():
            issues.append({'missing_successor_file': name})
            continue
        if sha(new) != expected:
            changes.append(name)
        if old.suffix == '.tex':
            old_units, new_units = protected(old.read_text()), protected(new.read_text())
            for kind, units in old_units.items():
                totals[kind] += sum(units.values())
                removed = units - new_units[kind]
                if removed:
                    issues.append({'file': name, 'removed_kind': kind, 'count': sum(removed.values())})
    if set(changes) != allowed:
        issues.append({'unexpected_source_delta': sorted(set(changes) ^ allowed)})
    if sha(source / 'accounting-product-proposal.pdf') != baseline['pdf_sha256']:
        issues.append({'baseline_pdf_changed': True})
    labels = Counter()
    for file in target.rglob('*.tex'):
        labels.update(protected(file.read_text())['labels'])
    duplicates = [k for k, n in labels.items() if n > 1]
    if duplicates:
        issues.append({'duplicate_labels': duplicates})
    log = (target / 'accounting-product-proposal.log').read_text(errors='replace')
    critical = [line for line in log.splitlines() if re.search(
        r'^!|Undefined control sequence|undefined references|Citation .* undefined|Reference .* undefined|Overfull', line)]
    if critical:
        issues.append({'critical_build_warnings': critical})
    pdf = target / 'accounting-product-proposal.pdf'
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M)[1])
    report = {'passed': not issues, 'baseline_sources': len(baseline['source_hashes']),
              'protected_occurrences': dict(totals), 'changed_files': sorted(changes),
              'new_section': 'sections/funded-year-authoring.tex',
              'candidate_version': '3.50', 'pages': pages, 'pdf_sha256': sha(pdf),
              'issues': issues, 'review_scope': 'Source preservation and build checks; no full-document readability or accounting acceptance.'}
    (OUT / 'verification.json').write_text(json.dumps(report, indent=2) + chr(10))
    manifest = {'git_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                'command': 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/funded-integration-20261023/verify.py',
                'environment': {'python': platform.python_version(), 'executable': sys.executable},
                'cpu_gpu': 'CPU only; GPU intentionally hidden; no ML framework imported',
                'cuda_visible_devices': os.environ.get('CUDA_VISIBLE_DEVICES'),
                'data_version': {'baseline_pdf': baseline['pdf_sha256'], 'candidate_pdf': sha(pdf)},
                'random_seeds': 'N/A: deterministic document checks', 'started_utc': started,
                'wall_seconds': time.perf_counter() - timer,
                'plan_file': 'docs/plans/accounting-funded-year-design-20261023.md',
                'result_file': str((OUT / 'result.md').relative_to(ROOT)),
                'build_record': 'build.json',
                'artifacts': {p.name: sha(p) for p in [Path(__file__), OUT/'baseline.json', OUT/'verification.json', OUT/'build.json']}}
    (OUT / 'run-manifest.json').write_text(json.dumps(manifest, indent=2) + chr(10))
    print(json.dumps(report))
    if issues:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
