"""Read retained builds; repair only the failed text-needle check."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import difflib
import json
import re
import time
import fitz
import integrate as original

H, R, S, T = original.H, original.R, original.S, original.T
sha, read, dump = original.sha, original.read, original.dump


def verify():
    out = H / 'verification-02'
    out.mkdir(exist_ok=False)
    checks, documents = [], []
    started = time.monotonic()
    lock = read(H / 'source-lock.json')

    def check(ok, name):
        checks.append(dict(name=name, passed=bool(ok)))
        if not ok:
            dump(out / 'failure.json', dict(checks=checks, failed=name))
            raise AssertionError(name)

    for n, h in lock['sources'].items():
        check(sha(S / n) == h, 'baseline:' + n)
        if (S / n).suffix in ['.tex', '.md']:
            check((T / n).read_text() == original.transform(n, (S / n).read_text()), 'exact_transform:' + n)
        else:
            check(sha(T / n) == h, 'copied_bytes:' + n)
        if n.endswith('.tex'):
            a, b = (S / n).read_text(), (T / n).read_text()
            pat = r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}'
            check(Counter(m.group(0) for m in re.finditer(pat, a, re.S)) <= Counter(m.group(0) for m in re.finditer(pat, b, re.S)), 'display_preserved:' + n)
            pat = r'\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{[^}]*\}'
            check(Counter(re.findall(pat, a)) <= Counter(re.findall(pat, b)), 'citations_preserved:' + n)
    for category, root in [('pdfs', S), ('evidence', R), ('inputs', H)]:
        for n, h in lock[category].items():
            check(sha(root / n) == h, category + ':' + n)
    check(sha(S / 'package-manifest.json') == lock['package_manifest'], 'baseline_package_manifest')

    def warnings(p):
        return Counter(re.sub(r' on input line \d+', '', s) for s in p.read_text().splitlines()
                       if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined', s))

    needles = ['A second source representation supplies a reported value', 'Occurrence f-325',
               'network under the PDF-only', 'Two annual calculations cannot be completed under the PDF-only',
               'original PDF-only full network', 'separately checks a numerical reading']
    for name in original.NAMES:
        build = H / ('build-01-' + name)
        check(read(build / 'manifest.json')['exit_code'] == 0, name + ':successful_build')
        check(sha(build / (name + '.pdf')) == sha(T / (name + '.pdf')), name + ':retained_build_identity')
        log = (T / (name + '.log')).read_text()
        check(not re.search(r'undefined|multiply defined', log, re.I), name + ':references')
        extra = warnings(T / (name + '.log')) - warnings(S / (name + '.log'))
        check(not extra, name + ':no_new_warning:' + str(dict(extra)))
        pdf = fitz.open(T / (name + '.pdf'))
        texts = [' '.join(p.get_text().split()) for p in pdf]
        check('Version 5.53' in texts[0], name + ':cover')
        pages, anchors = {1}, {}
        if name == original.NAMES[0]:
            for needle in needles:
                hits = [i + 1 for i, t in enumerate(texts) if needle in t]
                check(bool(hits), 'found:' + needle)
                anchors[needle] = hits
                for n in hits:
                    pages.update(range(max(1, n - 1), min(len(pdf), n + 2) + 1))
            pages.update([702, 703])
        else:
            baseline = fitz.open(S / (name + '.pdf'))
            check(len(pdf) == len(baseline), 'companion_pages')
            check(all(texts[i] == ' '.join(baseline[i].get_text().split()) for i in range(1, len(pdf))), 'companion_body_unchanged')
        clipped = [i + 1 for i, p in enumerate(pdf) if any(min(b[0], b[1]) < -1 or b[2] > p.rect.width + 1 or b[3] > p.rect.height + 1 for b in p.get_text('blocks'))]
        check(not clipped, name + ':clipping')
        render = out / ('render-' + name)
        render.mkdir()
        for n in sorted(pages):
            pdf[n - 1].get_pixmap(matrix=fitz.Matrix(1, 1)).save(render / f'page-{n}.png')
        documents.append(dict(document=name, pages=len(pdf), sha256=sha(T / (name + '.pdf')),
                              rendered_pages=sorted(pages), anchors=anchors))
    dump(out / 'verification.json', dict(passed=True, checks=checks, documents=documents,
          author_review='pending', independent_acceptance=False))
    dump(out / 'manifest.json', dict(command='python3 data/accounting-master/debt-reading-integration-20261027/verify_v2.py',
         verifier_sha256=sha(Path(__file__)), source_lock_sha256=sha(H / 'source-lock.json'),
         git_commit='unavailable: unusable repository marker', environment='Python / PyMuPDF; CPU document verification',
         gpu='not used; no numerical framework imported', random_seeds='N/A deterministic document verification',
         wall_seconds=time.monotonic()-started, timestamp_utc=datetime.now(timezone.utc).isoformat(),
         plan=lock['plan'], result=str((out / 'verification.json').relative_to(R))))
    print(json.dumps(dict(passed=True, checks=len(checks), documents=documents)))


if __name__ == '__main__':
    verify()
