"""Single-writer annual checkpoints with full-state replay on reopening."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sqlite3

import annual_inventory_authoring_v1 as author

runtime = author.runtime
annual = runtime.annual
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/annual-inventory-persistence-20261025'
LOCK = '2f7fe2b686dc67a7cced5982e87bcceffd663ab7ffc44795ff7d2a4911a02666'
PROFILE = 'AnnualInventoryStore/1'
VERSION = 1
MAX_BUDGET = 4096
SCHEMA = """
CREATE TABLE metadata(singleton INTEGER PRIMARY KEY CHECK(singleton=1), payload TEXT NOT NULL);
CREATE TABLE checkpoints(seq INTEGER PRIMARY KEY CHECK(seq>=0), payload TEXT NOT NULL,
 result_sha256 TEXT NOT NULL, previous_sha256 TEXT);
CREATE TRIGGER metadata_no_update BEFORE UPDATE ON metadata BEGIN SELECT RAISE(ABORT,'immutable metadata'); END;
CREATE TRIGGER metadata_no_delete BEFORE DELETE ON metadata BEGIN SELECT RAISE(ABORT,'immutable metadata'); END;
CREATE TRIGGER checkpoints_no_update BEFORE UPDATE ON checkpoints BEGIN SELECT RAISE(ABORT,'immutable checkpoint'); END;
CREATE TRIGGER checkpoints_no_delete BEFORE DELETE ON checkpoints BEGIN SELECT RAISE(ABORT,'immutable checkpoint'); END;
"""


class Invalid(ValueError):
    pass


def need(value, reason):
    if not value:
        raise Invalid(reason)


def canonical(value):
    return annual.caller.canonical(value).decode('utf-8')


def digest(value):
    return sha256(canonical(value).encode('utf-8')).hexdigest()


def strict_loads(text):
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'duplicate_json_key')
            result[key] = value
        return result
    def reject(value):
        raise Invalid('nonportable_json_number')
    result = json.loads(text, object_pairs_hook=pairs, parse_float=reject, parse_constant=reject)
    need(canonical(result) == text, 'noncanonical_json')
    return result


def binding():
    raw = (HERE/'source-lock.json').read_bytes()
    need(sha256(raw).hexdigest() == LOCK, 'source_lock_changed')
    for name, expected in json.loads(raw).items():
        need(sha256((ROOT/name).read_bytes()).hexdigest() == expected, 'protected_source_changed:' + name)
    author.protected()
    return {'profile': PROFILE, 'version': VERSION, 'source_lock_sha256': LOCK,
            'store_implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
            'runtime_implementation_sha256': sha256(Path(runtime.__file__).read_bytes()).hexdigest()}


def validated_request(body):
    program = author.from_request(body)
    result = author.compile_program(program, {body['root_sha256']: body['root_request']})['request']
    need(result == body, 'request_lowering')
    return result


def prefix_result(body, attempts):
    prefix = runtime.request(body['root_request'], body['operations'][:attempts])
    result = runtime.run(prefix)
    if 'request_sha256' in result:
        result['request_sha256'] = digest(body)
    if 'trace' in result:
        result['remaining_operations'] = deepcopy(body['operations'][len(result['trace']):])
        if result['status'] == 'complete_provisional' and attempts < len(body['operations']):
            result['status'] = 'paused_provisional'
    return result


def next_result(body, previous, index):
    need(previous['status'] == 'paused_provisional', 'terminal_result')
    need(index == len(previous['trace']) and index < len(body['operations']), 'attempt_cursor')
    result = deepcopy(previous)
    current = result['period_book']
    stop = None
    try:
        step = runtime.transition(current, body['operations'][index])
        result['trace'].append({'operation': deepcopy(body['operations'][index]), 'result': step})
        current = step['after']
    except (annual.native.Refused, annual.native.lease.Refused, annual.losses.Refused,
            runtime.partial.book.Refused, runtime.partial.book.lease.Refused) as exc:
        stop = {'index': index, 'status': exc.status, 'reason': exc.reason}
    except (ValueError, TypeError, KeyError, AttributeError, AssertionError, OverflowError, RecursionError) as exc:
        stop = {'index': index, 'status': 'invalid', 'reason': str(exc)[:350]}
    report = annual.root.carry.statements(current['opening'], current['after'], current['account_classes'])
    report.update(scope='Finite reusable period book under selected conditional models', unresolved=deepcopy(annual.UNRESOLVED))
    status = 'stopped_provisional' if stop else 'complete_provisional' if index + 1 == len(body['operations']) else 'paused_provisional'
    result.update(status=status, period_book=current, stop=stop,
                  conditional_current_assessed=current['current_period_tax'] == 'conditionally_assessed',
                  conditional_deferred_assessed=current['current_period_deferred_tax'] == 'conditionally_assessed',
                  deferred_asset_recognized=current['current_period_deferred_tax'] == 'conditionally_assessed' and Fraction(current['after']['balances']['dta']) > 0,
                  remaining_operations=deepcopy(body['operations'][len(result['trace']):]),
                  recorded_statements=report, unresolved=deepcopy(annual.UNRESOLVED))
    return result


def schema_rows(db):
    return [tuple(row) for row in db.execute(
        "SELECT type,name,tbl_name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name")]


def expected_schema():
    with sqlite3.connect(':memory:') as db:
        db.executescript(SCHEMA)
        return schema_rows(db)


class Store:
    def __init__(self, path, body=None, *, fault=None):
        self.path = Path(path)
        self.fault = fault
        exists = self.path.exists()
        need(exists or body is not None, 'new_store_requires_request')
        supplied = validated_request(body) if body is not None else None
        expected = binding()
        self.db = sqlite3.connect(str(self.path), timeout=5, isolation_level=None)
        try:
            version = self.db.execute('PRAGMA user_version').fetchone()[0]
            objects = schema_rows(self.db)
            # A crash before the initial transaction commits leaves an empty
            # SQLite target. Its request is not yet durable and must be supplied.
            uninitialized = version == 0 and not objects
            if uninitialized:
                need(supplied is not None, 'uninitialized_store_requires_request')
                self.body = supplied
            elif exists:
                need(self.db.execute('PRAGMA user_version').fetchone()[0] == VERSION, 'schema_version')
                need(schema_rows(self.db) == expected_schema(), 'schema_mismatch')
                rows = self.db.execute('SELECT singleton,payload FROM metadata').fetchall()
                need(len(rows) == 1 and rows[0][0] == 1, 'metadata_population')
                metadata = strict_loads(rows[0][1])
                need(set(metadata) == {'binding', 'request', 'request_sha256'}, 'metadata_fields')
                need(metadata['binding'] == expected, 'source_binding')
                self.body = validated_request(metadata['request'])
                need(metadata['request_sha256'] == digest(self.body), 'request_digest')
                need(supplied is None or supplied == self.body, 'request_mismatch')
            self.db.execute('PRAGMA foreign_keys=ON')
            self.db.execute('PRAGMA synchronous=FULL')
            self.db.execute('PRAGMA journal_mode=DELETE')
            if uninitialized:
                self.db.executescript('BEGIN IMMEDIATE;\n' + SCHEMA)
                self.db.execute('PRAGMA user_version=1')
                metadata = {'binding': expected, 'request': self.body, 'request_sha256': digest(self.body)}
                self.db.execute('INSERT INTO metadata VALUES(1,?)', (canonical(metadata),))
                result = prefix_result(self.body, 0)
                self.db.execute('INSERT INTO checkpoints VALUES(0,?,?,NULL)', (canonical(result), digest(result)))
                self._fault('initial_before_commit')
                self.db.commit()
                self._fault('initial_after_commit')
            self._validate()
        except BaseException:
            if self.db.in_transaction:
                self.db.rollback()
            self.db.close()
            raise

    def _fault(self, point):
        if self.fault is not None:
            self.fault(point)

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _validate(self):
        rows = self.db.execute('SELECT seq,payload,result_sha256,previous_sha256 FROM checkpoints ORDER BY seq').fetchall()
        need(bool(rows), 'missing_initial_checkpoint')
        previous = None
        for index, (seq, raw, saved_hash, prior_hash) in enumerate(rows):
            need(seq == index and seq <= len(self.body['operations']), 'checkpoint_sequence')
            need(prior_hash == (digest(previous) if previous is not None else None), 'checkpoint_chain')
            result = strict_loads(raw)
            need(saved_hash == digest(result), 'checkpoint_digest')
            if previous is not None:
                need(previous['status'] == 'paused_provisional', 'checkpoint_after_terminal')
            need(result == prefix_result(self.body, seq), 'checkpoint_replay')
            previous = result
        self.cursor = rows[-1][0]
        self.current = previous

    def inspect(self):
        return {'profile': PROFILE, 'cursor': self.cursor, 'request_sha256': digest(self.body),
                'result_sha256': digest(self.current), 'result': deepcopy(self.current)}

    def advance(self, max_operations, *, expected_cursor=None):
        need(type(max_operations) is int and 0 <= max_operations <= MAX_BUDGET, 'operation_budget')
        if expected_cursor is not None:
            need(type(expected_cursor) is int and 0 <= expected_cursor <= self.cursor, 'expected_cursor')
            if expected_cursor < self.cursor:
                return self.inspect()
        for _ in range(max_operations):
            if self.current['status'] != 'paused_provisional':
                break
            self.db.execute('BEGIN IMMEDIATE')
            committed = False
            try:
                row = self.db.execute('SELECT seq,result_sha256 FROM checkpoints ORDER BY seq DESC LIMIT 1').fetchone()
                need(tuple(row) == (self.cursor, digest(self.current)), 'external_writer_changed')
                result = next_result(self.body, self.current, self.cursor)
                self.db.execute('INSERT INTO checkpoints VALUES(?,?,?,?)',
                                (self.cursor + 1, canonical(result), digest(result), digest(self.current)))
                self._fault('before_commit')
                self.db.commit(); committed = True
                self.cursor += 1; self.current = result
                self._fault('after_commit')
            except BaseException:
                if self.db.in_transaction:
                    self.db.rollback()
                if committed:
                    self._validate()
                raise
        return self.inspect()
