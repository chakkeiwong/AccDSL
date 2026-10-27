"""Construct authoring requests from immutable, previously recorded evidence."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import receivable_term_text_v1 as text


def retained():
    folder = ROOT / 'data/accounting-master/receivable-term-history-20261025'
    locks = json.loads((folder / 'source-lock.json').read_text())
    for name, expected in locks.items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    return json.loads((folder / 'evidence.json').read_text())['cases']


def program(case, chart):
    commands = []
    for i, row in enumerate(case['steps']):
        if i == 7:
            request = case['carry_request']
            report = request['report_request']
            commands.append({'kind': 'carry', 'id': request['close_id'],
                             'cutoff': case['carry_before']['book']['date'],
                             'equity_movements': deepcopy(report['equity_movements']),
                             'notes': deepcopy(report['notes']),
                             'retained_account': request['retained_account'],
                             'next_end_exclusive': request['next_end_exclusive']})
        commands.append({'kind': 'event', 'method_key': row['request']['operation'],
                         'event': deepcopy(row['request']['event'])})
    report = case['carry_request']['report_request']
    return {'profile': text.PROGRAM, 'name': 'term-history-' + chart,
            'state': deepcopy(case['migration']['state']),
            'report_context': {'opening': deepcopy(report['opening']), 'mapping': deepcopy(report['mapping'])},
            'commands': commands}


def expected_trace(case):
    result = []
    for i, row in enumerate(case['steps']):
        if i == 7:
            result.append({'request': case['carry_request'], 'result': case['carry']})
        result.append({'request': row['request'], 'result': row['result']})
    return result


def check(case, chart):
    body = program(case, chart)
    source, imports = text.from_program(body)
    compiled = text.compile_text(source, imports)
    assert compiled['status'] == 'compiled', compiled
    assert compiled['program'] == body
    result = text.execute_text(source, imports)
    assert result['status'] == 'complete_provisional', result.get('stop')
    assert result['successful_commands'] == 10
    expected = expected_trace(case)
    for actual, original in zip(result['trace'], expected, strict=True):
        assert actual['request'] == original['request']
        assert actual['result'] == original['result']
    assert result['current'] == case['final']
    assert all(result[flag] is False for flag in text.terms.FLAGS)
    return {'program': body, 'source': source, 'imports': imports, 'compiled': compiled, 'result': result}
