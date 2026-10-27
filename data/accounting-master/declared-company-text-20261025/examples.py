"""Full command-text comparisons, including an independently authored small case."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / 'scripts'))
import declared_company_text_v1 as frontend
spec = importlib.util.spec_from_file_location('text_compare_program', ROOT / 'data/accounting-master/declared-company-program-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


def independent_source():
    body = ex.fixture(); body['commands'] = [body['commands'][0], body['commands'][1]]
    imports = {frontend.runner.digest(body[k]): deepcopy(body[k]) for k in frontend.IMPORTS}
    header = 'company_program "DeclaredCompanyText/1" "two-period-alpha";\n'
    header += ''.join('import_' + k + ' "' + frontend.runner.digest(body[k]) + '";\n' for k in frontend.IMPORTS)
    # Written from the command grammar, without using frontend.render.
    source = header + '''event "sale.2027" method "sell" on "2027-02-01";
input "approved" known true because "Authored synthetic event";
input "cost" known "15/1" because "Authored synthetic event";
input "proceeds" known "40/1" because "Authored synthetic event";
end_event;
report "interim.2027" at "2027-06-30";
note "debt_terms" label "Debt terms and maturity" status "missing" because "Synthetic loan has no source disclosure package";
end_report;
end_program;
'''
    return body, imports, source


def cases():
    out = [('complete.alpha', ex.fixture()), ('complete.beta', ex.fixture('beta'))]
    for name in ['unknown', 'false', 'missing_policy', 'reset', 'duplicate', 'date_order', 'equity_refusal']:
        body = ex.fixture()
        if name == 'unknown':body['commands'][2]['event']['inputs']['approved']['value'] = {'status': 'unknown', 'reason': 'Actual approval finding absent'}
        elif name == 'false':body['commands'][2]['event']['inputs']['approved']['value']['value'] = False
        elif name == 'missing_policy':del body['commands'][4]['memory_policies']['/loan/paid']
        elif name == 'reset':
            body['commands'][4]['memory_policies']['/loan/paid'] = {'kind': 'reset',
                'type': deepcopy(body['opening']['memory_types']['/loan/paid']), 'value': '0/1', 'provenance': 'Explicit counter reset'}
        elif name == 'duplicate':body['commands'][2]['event']['id'] = 'sale.2027'
        elif name == 'date_order':body['commands'][2]['event']['date'] = '2027-01-01'
        else:
            body['commands'][1]['equity_movements'] = [{'id': 'explanation', 'event_id': 'sale.2027', 'date': '2027-02-01',
                'account': 'capital.alpha', 'amount': '1/1', 'description': 'Explicit but unreconciled equity explanation'}]
        out.append((name, body))
    return out


def compare():
    rows = []
    for name, body in cases():
        original = deepcopy(body); author, imports = frontend.from_program(body)
        source = frontend.render(author); before_imports = deepcopy(imports)
        compiled = frontend.compile_text(source, imports)
        expected = ex.program.run(body); actual = frontend.execute_text(source, imports)
        checks = {'program_exact': compiled['program'] == body, 'author_roundtrip': frontend.lower(source) == author,
                  'canonical_render': frontend.render(frontend.lower(source)) == source,
                  'result_exact': actual == expected, 'input_unchanged': body == original,
                  'imports_unchanged': imports == before_imports, 'engine_replay': ex.program.verify(body, actual),
                  'source_identity': compiled['source_text_sha256'] == frontend.sha256(source.encode()).hexdigest(),
                  'source_commands': len(compiled['source_spans']['commands']) == len(body['commands']),
                  'no_execution_on_compile': compiled['executed'] is False,
                  'no_admission': all(compiled[k] is False and actual[k] is False for k in ex.program.FLAGS)}
        rows.append({'case': name, 'source': source, 'imports': imports, 'compiled': compiled,
                     'result': actual, 'expected_result_sha256': frontend.runner.digest(expected), 'checks': checks})
    body, imports, source = independent_source(); compiled = frontend.compile_text(source, imports)
    actual = frontend.execute_text(source, imports); expected = ex.program.run(body)
    rows.append({'case': 'independent_source', 'source': source, 'imports': imports, 'compiled': compiled,
                 'result': actual, 'expected_result_sha256': frontend.runner.digest(expected),
                 'checks': {'program_exact': compiled['program'] == body, 'result_exact': actual == expected,
                            'cash': actual['trace'][1]['result']['cash_flows']['closing_cash'] == '140/1',
                            'profit': actual['trace'][1]['result']['income']['profit'] == '25/1',
                            'equity': actual['trace'][1]['result']['equity']['closing'] == '125/1'}})
    return {'cases': rows, 'checks': [{'name': row['case'] + ':' + name, 'passed': bool(value)}
                                    for row in rows for name, value in row['checks'].items()]}


if __name__ == '__main__':
    import json
    result = compare(); failed = [c['name'] for c in result['checks'] if not c['passed']]
    print(json.dumps({'cases': len(result['cases']), 'checks': len(result['checks']), 'failures': failed}))
    raise SystemExit(bool(failed))
