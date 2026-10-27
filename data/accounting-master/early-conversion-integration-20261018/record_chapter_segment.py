"""Bind actual local chapter reading; never mark the whole-document chain read."""
import argparse
import hashlib
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
EXPECTED = 'afbbdbe73d6ac25a9e59ea6f39e25b2e579ebd1e5fcad0ac9959e87cc6ab5d80'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('segment', type=Path)
    parser.add_argument('--unit', choices=('chapter10', 'appendixA'), required=True)
    args = parser.parse_args()
    bounds = (177, 243) if args.unit == 'chapter10' else (364, 374)
    ledger_path = OUT / f'{args.unit}-ordered-review.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else dict(
        candidate_version='3.44', pdf_sha256=EXPECTED, physical_pages=list(bounds),
        segments=[], status='in_progress', independent_reader='pending', human_acceptance='pending',
        whole_document_credit=False,
        scope='Local ordered chapter reading only; full-document chain and structural/equation judgments remain separate.')
    path = args.segment.resolve()
    assert path.is_relative_to(OUT) and path.exists()
    segment = json.loads(path.read_text())
    start, end = segment['physical_pages']
    assert segment['pdf_sha256'] == ledger['pdf_sha256'] == EXPECTED
    assert bounds[0] <= start <= end <= bounds[1] and end - start < 6
    if ledger['segments']:
        previous = ledger['segments'][-1]
        previous_path = ROOT / previous['path']
        assert sha(previous_path) == previous['sha256']
        previous_segment = json.loads(previous_path.read_text())
        assert start == previous_segment['physical_pages'][1] + 1
        assert segment['entry_state'] == previous_segment['exit_state']
    else:
        assert start == bounds[0]
    assert segment['entry_state'].strip() and segment['exit_state'].strip()
    assert segment['findings'] and segment['source_limit'].strip()
    assert segment['actual_view_order'] == list(range(start, end + 1))
    structure = json.loads((OUT / 'regression/structure-ledger.json').read_text())
    assert structure['pdf_sha256'] == EXPECTED
    assert sha(ROOT / structure['baseline_pdf']) == EXPECTED
    renders = []
    for number in range(start, end + 1):
        row = structure['pages'][number - 1]
        assert row['render'] and sha(ROOT / row['render']['path']) == row['render']['sha256']
        renders.append(dict(page=number, **row['render']))
    assert 'render_bindings' not in segment
    segment['render_bindings'] = renders
    path.write_text(json.dumps(segment, indent=2, ensure_ascii=False) + '\n')
    ledger['segments'].append(dict(path=str(path.relative_to(ROOT)), sha256=sha(path), physical_pages=[start, end]))
    ledger['through_physical_page'] = end
    ledger['status'] = 'ordered_pages_read_chapter_synthesis_pending' if end == bounds[1] else 'in_progress'
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
    print(f'{args.unit}: ordered pages {bounds[0]}–{end}; whole-document credit false; acceptance pending')


if __name__ == '__main__':
    main()
