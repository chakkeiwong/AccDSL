"""Extract one retained document once; this supplies no reading credit."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
U = Path(__file__).resolve().parent
R = U.parents[2]
P = R / 'data/accounting-master/r06-duplicates-guidance-20261023/extract.py'


def main():
    ident = sys.argv[1]
    assert ident in ('01-primer2013', '02-spec2013', '03-primer2026',
                     '04-spec2026', '05-spechistory', '06-primerhistory')
    body = U / 'sources' / (ident + '.body')
    visible = U / 'sources' / (ident + '.visible.txt')
    structure = U / 'sources' / (ident + '.structure.json')
    assert not visible.exists() and not structure.exists()
    receipt = json.loads((U / 'sources' / (ident + '.receipt.json')).read_text())
    assert receipt['exit_code'] == 0 and receipt['metrics']['http_code'] == 200
    spec = importlib.util.spec_from_file_location('prior_authored_text_parser', P)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parser = module.Text()
    parser.feed(body.read_text())
    with visible.open('x') as stream:
        stream.write('\n'.join(parser.parts) + '\n')
    value = {'body_sha256': hashlib.sha256(body.read_bytes()).hexdigest(),
             'visible_sha256': hashlib.sha256(visible.read_bytes()).hexdigest(),
             'parser_path': str(P.relative_to(R)),
             'parser_sha256': hashlib.sha256(P.read_bytes()).hexdigest(),
             'links': parser.links, 'images': parser.images,
             'headings': parser.headings, 'table_count': parser.table_count,
             'reading_credit': 'none from extraction'}
    with structure.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'id': ident, 'lines': len(parser.parts),
                      'images': len(parser.images), 'tables': parser.table_count}))


if __name__ == '__main__':
    main()
