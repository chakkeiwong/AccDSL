"""One-shot layout-only successor; preserve the completed first build."""
import integrate as source
from pathlib import Path

H, T = source.H, source.T
TARGET = 'sections/temporal-statement-network.tex'
MARKER = r'\subsection{A second source representation supplies a reported value}'

def transform(n, text):
    text = source.transform(n, text)
    if n == TARGET:
        text = source.once(text, MARKER, '\\enlargethispage{\\baselineskip}\n' + MARKER)
    return text

if __name__ == '__main__':
    assert not (H / 'layout-lock.json').exists()
    p = T / TARGET
    before = p.read_text()
    assert before == source.transform(TARGET, (source.S / TARGET).read_text())
    (H / 'temporal-statement-network-before-layout.tex').write_text(before)
    p.write_text(transform(TARGET, (source.S / TARGET).read_text()))
    source.dump(H / 'layout-lock.json', dict(
        source_lock=source.sha(H / 'source-lock.json'),
        file=TARGET, before_sha256=source.sha(H / 'temporal-statement-network-before-layout.tex'),
        after_sha256=source.sha(p), repair_sha256=source.sha(Path(__file__)),
        reason='Physical page700 split the final line of the opening source citation onto701. Extend this page by one baseline, retaining all words and citations.',
        baseline_verification=source.sha(H / 'verification-02/verification.json'),
        expected_build='build-02-accounting-product-proposal', companion_build='build-01-simulation-foundations'))
    print('Applied one-baseline layout repair; original source and build preserved.')
