"""P07 local transactional adapter for the actual deterministic P05 Engine.

One writer, immutable records, versioned evidence views. No stochastic execution.
Errors at authoring boundaries are P07Error; execution failures are typed results.
"""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
from datetime import datetime
from pathlib import Path
import hashlib
import json
import os
import sqlite3
import unicodedata

from company_execution_v1 import Engine, exact, serial, event, period_events, statements, ROOT
from context_chronology_v1 import select_evidence

VERSION = 2
SET_FIELDS = {'dependencies', 'source_ids', 'constraints', 'depends'}
FAULT_POINTS = ('state', 'journal', 'measurement', 'lineage', 'receipt', 'before_commit', 'after_commit')


class P07Error(ValueError):
    def __init__(self, code, detail):
        self.code = code
        super().__init__(detail)


def fail(code, detail):
    raise P07Error(code, detail)


def strict_loads(text):
    def pairs(rows):
        out = {}
        for k, v in rows:
            key = unicodedata.normalize('NFC', k)
            if key in out:
                fail('CanonicalError', 'duplicate or normalized duplicate key')
            out[key] = v
        if set(out) == {'$rational'}:
            try:
                n, d = out['$rational']
                if not isinstance(n, str) or not isinstance(d, str): raise ValueError('rational strings required')
                return Fraction(int(n), int(d))
            except (TypeError, ValueError, ZeroDivisionError) as exc:
                fail('CanonicalError', str(exc))
        return out
    def integer(value):
        if value == '-0': fail('CanonicalError', 'negative zero')
        return int(value)
    def floating(value):
        fail('CanonicalError', 'floating JSON numbers unsupported')
    return json.loads(text, object_pairs_hook=pairs, parse_int=integer,
                      parse_float=floating, parse_constant=floating)


def canonical(value):
    def norm(x, field=None):
        if x is None or isinstance(x, bool): return x
        if isinstance(x, (int, Fraction)):
            q = Fraction(x)
            return {'$rational': [str(q.numerator), str(q.denominator)]}
        if isinstance(x, str): return unicodedata.normalize('NFC', x)
        if isinstance(x, float): fail('CanonicalError', 'floats forbidden')
        if isinstance(x, dict):
            if set(x) == {'$rational'}:
                n, d = x['$rational']
                if not isinstance(n, str) or not isinstance(d, str): fail('CanonicalError', 'rational strings required')
                return norm(Fraction(int(n), int(d)))
            out = {}
            for k, v in x.items():
                if not isinstance(k, str): fail('CanonicalError', 'string keys required')
                key = unicodedata.normalize('NFC', k)
                if not key.isascii() or key in out: fail('CanonicalError', 'ASCII unique keys required')
                out[key] = norm(v, key)
            return out
        if isinstance(x, (list, tuple)):
            out = [norm(v) for v in x]
            if field in SET_FIELDS:
                out.sort(key=lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False))
                if len({json.dumps(v, sort_keys=True) for v in out}) != len(out):
                    fail('CanonicalError', 'duplicate set member')
            return out
        fail('CanonicalError', 'unsupported canonical type')
    return json.dumps(norm(value), sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def identity(domain, value):
    return hashlib.sha256(('accdsl.p07.' + domain + '.v1\0' + canonical(value)).encode()).hexdigest()


def dump(value):
    canonical(value)  # Reject unsafe/noncanonical input before storing lossless P05 JSON.
    def numeric(x):
        if isinstance(x, Fraction): return {'$rational': [str(x.numerator), str(x.denominator)]}
        raise TypeError('unsupported stored type')
    return json.dumps(value, default=numeric, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def event_identity(owner, schedule_version, e, occurrence=0):
    return identity('event', [owner, schedule_version, e['date'], e.get('phase', 'P05-period-step'), e['op'], occurrence])


def branch_identity(hypothesis, scenario):
    return identity('branch', [hypothesis, scenario])


def reference_uniform(seed, coupling_group, entity, cohort, economic_date, shock_kind, draw_index):
    # Exactly the normative reference tuple; a primitive, not an assessed generator.
    key = ['stream-v1', seed, coupling_group, entity, cohort, economic_date, shock_kind, draw_index]
    word = int.from_bytes(hashlib.sha256(canonical(key).encode()).digest()[:8], 'big')
    return Fraction(2 * word + 1, 2 ** 65)


def make_schedule(spec):
    rows = []
    for p in spec['periods']:
        for e in period_events(spec, p):
            dynamic = None
            if e['op'] == 'interest_pay': dynamic = 'interest_payable'
            if e['op'] == 'tax_pay' and 'tax_payment' not in p: dynamic = 'tax_payable'
            rows.append({'event': e, 'dynamic': dynamic})
    return rows


def order_schedule(rows):
    rows = deepcopy(rows)
    aliases = [x['event']['id'] for x in rows]
    if len(set(aliases)) != len(aliases): fail('Conflict', 'duplicate schedule IDs')
    pending = {x['event']['id']: x for x in rows}
    known = set(); ordered = []
    while pending:
        ready = [x for x in pending.values() if set(x['event']['depends']) <= known]
        if not ready: fail('Rejected', 'dependency cycle or missing reference')
        earliest = min(x['event']['date'] for x in ready)
        tied = [x for x in ready if x['event']['date'] == earliest]
        if len(tied) != 1: fail('Unsupported', 'ambiguous overlapping same-date events')
        row = tied[0]; key = row['event']['id']
        if ordered and earliest < ordered[-1]['event']['date']: fail('Rejected', 'date inversion')
        ordered.append(row); known.add(key); del pending[key]
    counts = {}
    for row in ordered:
        e = row['event']; group = (e['date'], e.get('phase', 'P05-period-step'), e['op'])
        ordinal = counts.get(group, 0); counts[group] = ordinal + 1
        row['event_id'] = event_identity(e['context']['entity'], 'P05-schedule-v1', e, ordinal)
    return ordered


SCHEMA = """
CREATE TABLE nodes(id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL,
 digest TEXT NOT NULL, canonical TEXT NOT NULL);
CREATE TABLE edges(parent TEXT REFERENCES nodes(id), child TEXT REFERENCES nodes(id),
 PRIMARY KEY(parent,child), CHECK(parent<>child));
CREATE TABLE head(singleton INTEGER PRIMARY KEY CHECK(singleton=1), view_id TEXT REFERENCES nodes(id));
CREATE TABLE requests(id TEXT PRIMARY KEY, digest TEXT NOT NULL, result TEXT NOT NULL);
CREATE TABLE runs(id TEXT PRIMARY KEY REFERENCES nodes(id), lock_payload TEXT NOT NULL);
CREATE TABLE commits(run_id TEXT REFERENCES runs(id), seq INTEGER NOT NULL, event_id TEXT NOT NULL,
 payload TEXT NOT NULL, receipt TEXT NOT NULL, state_id TEXT REFERENCES nodes(id),
 journal_id TEXT REFERENCES nodes(id), measurement_id TEXT REFERENCES nodes(id),
 event_node TEXT REFERENCES nodes(id), PRIMARY KEY(run_id,seq), UNIQUE(run_id,event_id));
CREATE TABLE migrations(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
"""


def install_triggers(db):
    for table in ('nodes', 'edges', 'requests', 'runs', 'commits', 'migrations'):
        for action in ('UPDATE', 'DELETE'):
            db.execute(f'CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,"immutable record"); END')


class Store:
    def __init__(self, path, *, fault=None):
        self.path = str(path); self.fault = fault
        self.db = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA journal_mode=DELETE')
        version = self.db.execute('PRAGMA user_version').fetchone()[0]
        tables = self.db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        if version == 0 and not tables:
            try:
                self.db.executescript('BEGIN IMMEDIATE;\n' + SCHEMA)
                self._fault('initial_schema')
                self.db.execute('PRAGMA user_version=2')
                install_triggers(self.db)
                view = self.add_node('view', {'parent': None, 'states': {}, 'stale': []})
                self.db.execute('INSERT INTO head VALUES(1,?)', (view,))
                self._fault('initial_view')
                self._fault('initial_before_commit')
                self.db.commit()
            except BaseException:
                self.db.rollback(); self.db.close(); raise
        elif version != VERSION:
            self.db.close(); fail('MigrationRequired' if version == 1 else 'Unsupported', f'schema {version}')
        install_triggers(self.db)

    def close(self): self.db.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

    @property
    def view(self): return self.db.execute('SELECT view_id FROM head').fetchone()[0]

    def _fault(self, point):
        if self.fault: self.fault(point)

    def node(self, key):
        row = self.db.execute('SELECT * FROM nodes WHERE id=?', (key,)).fetchone()
        if row is None: fail('MissingReference', key)
        value = strict_loads(row['payload'])
        if identity(row['kind'], value) != row['digest'] or canonical(value) != row['canonical']:
            fail('IntegrityFailure', 'node content hash mismatch: ' + key)
        return value

    def kind(self, key):
        self.node(key)
        return self.db.execute('SELECT kind FROM nodes WHERE id=?', (key,)).fetchone()[0]

    def add_node(self, kind, value, dependencies=(), identifier=None):
        dependencies = sorted(dependencies)
        if len(set(dependencies)) != len(dependencies): fail('Rejected', 'duplicate dependencies')
        digest = identity(kind, value)
        key = identifier or identity('node', [kind, digest, dependencies])
        prior = self.db.execute('SELECT digest,kind FROM nodes WHERE id=?', (key,)).fetchone()
        if prior:
            parents = [r[0] for r in self.db.execute('SELECT parent FROM edges WHERE child=? ORDER BY parent', (key,))]
            if prior['digest'] != digest or prior['kind'] != kind or parents != dependencies:
                fail('Conflict', 'immutable node replacement or cycle')
            return key
        for dep in dependencies: self.node(dep)
        if key in dependencies: fail('Rejected', 'dependency cycle')
        own = not self.db.in_transaction
        if own: self.db.execute('BEGIN IMMEDIATE')
        try:
            self.db.execute('INSERT INTO nodes VALUES(?,?,?,?,?)', (key, kind, dump(value), digest, canonical(value)))
            for dep in dependencies: self.db.execute('INSERT INTO edges VALUES(?,?)', (dep, key))
            if own: self.db.commit()
        except BaseException:
            if own: self.db.rollback()
            raise
        return key

    def descendants(self, roots):
        seen = set(); todo = list(roots)
        while todo:
            parent = todo.pop()
            for row in self.db.execute('SELECT child FROM edges WHERE parent=?', (parent,)):
                if row[0] not in seen: seen.add(row[0]); todo.append(row[0])
        return sorted(seen)

    def ancestors(self, roots):
        seen = set(); todo = list(roots)
        while todo:
            key = todo.pop()
            if key in seen: continue
            self.node(key); seen.add(key)
            todo.extend(r[0] for r in self.db.execute('SELECT parent FROM edges WHERE child=?', (key,)))
        return seen

    def require_usable(self, roots, view):
        if self.kind(view) != 'view': fail('Rejected', 'evidence view required')
        evidence = self.node(view); stale = set(evidence['stale'])
        for key in self.ancestors(roots):
            if key in stale: fail('StaleResult', 'recompute under corrected view')
            if self.kind(key) == 'reading':
                state = evidence['states'].get(key, {}).get('state', 'Proposed')
                if state not in ('Accepted', 'AcceptedAlternative'):
                    fail('StaleResult' if state in ('Rejected', 'Superseded') else 'Rejected',
                         'reading is not accepted in requested view: ' + key)

    def add_source(self, path):
        path = Path(path).resolve()
        raw = path.read_bytes()
        return self.add_node('source', {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes_hex': raw.hex()})

    def verify_sources(self, roots=None):
        keys = self.ancestors(roots) if roots is not None else [r[0] for r in self.db.execute("SELECT id FROM nodes WHERE kind='source'")]
        for key in keys:
            if self.kind(key) != 'source': continue
            source = self.node(key)
            try: current_hash = file_hash(source['path'])
            except OSError: fail('IntegrityFailure', 'referenced source unavailable')
            if current_hash != source['sha256'] or hashlib.sha256(bytes.fromhex(source['bytes_hex'])).hexdigest() != source['sha256']:
                fail('IntegrityFailure', 'source bytes changed')

    def propose(self, reading, identifier=None):
        for key in ('source', 'start', 'end', 'literal', 'context', 'concept', 'period', 'lineage', 'layer', 'value'):
            if key not in reading: fail('Rejected', 'missing reading ' + key)
        if self.kind(reading['source']) != 'source': fail('Rejected', 'source node required')
        if reading['layer'] not in ('extraction', 'interpretation'): fail('Rejected', 'unknown review layer')
        if reading.get('correction_of'):
            old = self.node(reading['correction_of'])
            if any(old[k] != reading[k] for k in ('context','concept','period','lineage','layer')):
                fail('Rejected', 'correction scope mismatch')
        return self.add_node('reading', reading, [reading['source']], identifier)

    def _validate_acceptance(self, reading, evidence):
        for key in ('reviewer', 'time', 'rationale', 'applicability', 'reconciliation'):
            if not evidence.get(key): fail('Rejected', 'missing review evidence ' + key)
        stamp = datetime.fromisoformat(evidence['time'])
        if stamp.tzinfo is None: fail('Rejected', 'review time requires timezone')
        source = self.node(reading['source']); raw = bytes.fromhex(source['bytes_hex']).decode('utf-8')
        if raw[reading['start']:reading['end']] != reading['literal']:
            fail('Rejected', 'locator/literal mismatch')
        if not reading['context']: fail('Rejected', 'context required')
        if reading['layer'] == 'extraction' and exact(reading['literal']) != exact(reading['value']):
            fail('Rejected', 'extraction value differs from literal')
        if reading['layer'] == 'interpretation' and not evidence.get('interpretation_support'):
            fail('Rejected', 'interpretation support required separately')
        self.verify_sources([reading['source']])

    def review(self, reading_id, action, evidence, *, prior_view, request_id, replacement=None, choice_group=None):
        request = [reading_id, action, evidence, prior_view, replacement, choice_group]
        digest = identity('request', request)
        existing = self.db.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone()
        if existing:
            if existing['digest'] != digest: fail('Conflict', 'request payload changed')
            return strict_loads(existing['result'])
        if prior_view != self.view: fail('Conflict', 'stale prior evidence view')
        reading = self.node(reading_id)
        if self.kind(reading_id) != 'reading': fail('Rejected', 'reading required')
        previous = self.node(prior_view); states = deepcopy(previous['states'])
        old = states.get(reading_id, {}).get('state', 'Proposed')
        allowed = {'Proposed': {'Accepted', 'AcceptedAlternative', 'Rejected'},
                   'Accepted': {'Superseded'}, 'AcceptedAlternative': {'Superseded'}}
        if action not in allowed.get(old, set()): fail('Rejected', 'invalid review transition')
        for key in ('reviewer', 'time', 'rationale'):
            if not evidence.get(key): fail('Rejected', 'missing decision attribution')
        try:
            if datetime.fromisoformat(evidence['time']).tzinfo is None: raise ValueError('timezone required')
        except (ValueError, TypeError) as exc:
            fail('Rejected', 'invalid review time: ' + str(exc))
        if action in ('Accepted', 'AcceptedAlternative'): self._validate_acceptance(reading, evidence)
        if action == 'AcceptedAlternative' and not choice_group: fail('Rejected', 'choice group required')
        if action == 'Superseded':
            if replacement == reading_id:
                fail('Rejected', 'supersession requires a distinct accepted replacement')
            new = self.node(replacement)
            if states.get(replacement, {}).get('state') not in ('Accepted', 'AcceptedAlternative'):
                fail('Rejected', 'accepted replacement required')
            if any(reading[k] != new[k] for k in ('context', 'concept', 'period', 'lineage', 'layer')):
                fail('Rejected', 'supersession scope mismatch')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            states[reading_id] = {'state': action, 'replacement': replacement, 'choice_group': choice_group}
            affected = self.descendants([reading_id])
            stale = sorted(set(previous['stale']) | set(affected))
            decision = self.add_node('review', {'reading': reading_id, 'action': action, 'evidence': evidence,
                'prior_view': prior_view, 'replacement': replacement, 'request_id': request_id}, [reading_id])
            # View links are metadata, not economic dependency edges.
            view = self.add_node('view', {'parent': prior_view, 'states': states, 'stale': stale, 'decision': decision})
            result = {'status': 'Reviewed', 'view': view, 'decision': decision, 'invalidated': affected}
            self.db.execute('INSERT INTO requests VALUES(?,?,?)', (request_id, digest, dump(result)))
            self.db.execute('UPDATE head SET view_id=? WHERE singleton=1', (view,))
            self.db.commit()
            return result
        except BaseException:
            self.db.rollback(); raise

    def select(self, view, cutoff, **kwargs):
        states = self.node(view)['states']; rows = []
        for key, state in states.items():
            if state['state'] not in ('Accepted', 'AcceptedAlternative', 'Superseded'): continue
            r = deepcopy(self.node(key)); r['id'] = key; r['supersedes'] = []
            for old, s in states.items():
                if s.get('replacement') == key: r['supersedes'].append(old)
            rows.append(r)
        result = select_evidence(rows, cutoff, **kwargs)
        groups = {}
        for r in result['selected']:
            group = canonical([r['context'], r['period'], r['concept'], r['layer']])
            groups.setdefault(group, []).append(r)
        result['conflicts'] = [sorted(x['id'] for x in rs) for rs in groups.values() if len({canonical(r['value']) for r in rs}) > 1]
        result['choice_groups'] = {k: v['choice_group'] for k, v in states.items() if v.get('choice_group')}
        return result

    def bind_reading(self, reading_id, view, spec, period_id, field='sales_consideration'):
        if field != 'sales_consideration': fail('Unsupported', 'only explicit revenue binding supported')
        state = self.node(view)['states'].get(reading_id, {}).get('state')
        if state not in ('Accepted', 'AcceptedAlternative'): fail('Rejected', 'accepted reading required')
        r = self.node(reading_id)
        if r['context'] != spec['context'] or r['period'] != period_id or r['concept'] != 'revenue':
            fail('Rejected', 'binding context mismatch')
        out = deepcopy(spec)
        matches = [p for p in out['periods'] if p['id'] == period_id]
        if len(matches) != 1: fail('Rejected', 'period missing or ambiguous')
        matches[0][field] = str(exact(r['value']))
        mapping = self.add_node('mapping', {'reading': reading_id, 'field': field, 'period': period_id, 'view': view}, [reading_id])
        calculation = self.add_node('calculation', {'spec': out, 'binding': mapping}, [mapping])
        return out, calculation

    def create_run(self, spec, *, view=None, schedule=None, dependencies=(), scenario='historical',
                   stream='deterministic', package='DemoCorporate/1', environment='python-rational-v1'):
        if stream != 'deterministic': return {'status': 'Unsupported', 'reason': 'production stochastic execution unsupported'}
        view = view or self.view
        if self.kind(view) != 'view': fail('Rejected', 'evidence view required')
        self.require_usable(dependencies, view)
        ordered = order_schedule(make_schedule(spec) if schedule is None else schedule)
        source = self.add_source(ROOT / spec['source'])
        lock = {'spec': deepcopy(spec), 'schedule': ordered, 'view': view, 'scenario': scenario,
            'package': package, 'environment': environment, 'numeric': 'exact-rational', 'calendar': spec['context']['calendar'],
            'horizon': [e['event']['date'] for e in ordered], 'outputs': ['state','journals','statements'],
            'initial_state': Engine(spec).snapshot(), 'stream': stream,
            'code': {name: file_hash(ROOT / 'scripts' / name) for name in ('company_execution_v1.py','company_persistence_v1.py','context_chronology_v1.py')},
            'sources': [source], 'dependencies': sorted(dependencies)}
        key = identity('run', lock)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            self.add_node('run', lock, [source, *dependencies], key)
            self.db.execute('INSERT OR IGNORE INTO runs VALUES(?,?)', (key, dump(lock)))
            self.db.commit()
        except BaseException:
            self.db.rollback(); raise
        return {'status': 'Created', 'run_id': key}

    def _lock(self, run_id):
        row = self.db.execute('SELECT lock_payload FROM runs WHERE id=?', (run_id,)).fetchone()
        if not row: fail('MissingReference', run_id)
        lock = strict_loads(row[0])
        if identity('run', lock) != run_id or self.node(run_id) != lock: fail('IntegrityFailure', 'run lock changed')
        for name, digest in lock['code'].items():
            if file_hash(ROOT / 'scripts' / name) != digest: fail('Conflict', 'code lock changed')
        self.verify_sources([run_id])
        return lock

    def _replay(self, run_id, lock):
        en = Engine(lock['spec'])
        rows = self.db.execute('SELECT * FROM commits WHERE run_id=? ORDER BY seq', (run_id,)).fetchall()
        for i, row in enumerate(rows):
            if row['seq'] != i or row['event_id'] != lock['schedule'][i]['event_id']: fail('IntegrityFailure', 'cursor mismatch')
            e = strict_loads(row['payload'])
            expected_event = deepcopy(lock['schedule'][i]['event'])
            dynamic = lock['schedule'][i]['dynamic']
            if dynamic: expected_event['params']['amount'] = str(-en.balances[dynamic])
            if dump(e) != dump(expected_event): fail('IntegrityFailure', 'committed payload differs from locked schedule')
            receipt = en.apply(e)
            if receipt['status'] != 'Applied' or receipt != strict_loads(row['receipt']): fail('IntegrityFailure', 'receipt replay mismatch')
            if en.snapshot() != self.node(row['state_id']): fail('IntegrityFailure', 'snapshot replay mismatch')
            if serial(en.journals[-1]) != self.node(row['journal_id']): fail('IntegrityFailure', 'journal replay mismatch')
            if statements(lock['spec']['opening'], en.journals) != self.node(row['measurement_id']): fail('IntegrityFailure', 'measurement mismatch')
            expected = self._event_dependencies(run_id, e, rows[:i])
            for key in ('event_node', 'state_id', 'journal_id', 'measurement_id'):
                parents = sorted(r[0] for r in self.db.execute('SELECT parent FROM edges WHERE child=?', (row[key],)))
                if parents != expected: fail('IntegrityFailure', key + ' lineage mismatch')
            self.node(row['event_node'])
        return en, rows

    def _event_dependencies(self, run_id, e, rows):
        aliases = {strict_loads(r['payload'])['id']: r['event_node'] for r in rows}
        return sorted({run_id, *(aliases[a] for a in e['depends']), *([rows[-1]['event_node']] if rows else [])})

    def resume_run(self, run_id, *, expected_lock=None):
        lock = self._lock(run_id)
        if expected_lock is not None and canonical(expected_lock) != canonical(lock): fail('Conflict', 'changed run lock')
        engine, rows = self._replay(run_id, lock)
        return {'status': 'Resumed', 'run_id': run_id, 'cursor': len(rows), 'state': engine.snapshot(), 'lock': lock}

    def apply_event(self, run_id, event_id=None, payload=None):
        try:
            lock = self._lock(run_id)
            existing = self.db.execute('SELECT * FROM commits WHERE run_id=? AND event_id=?', (run_id, event_id)).fetchone() if event_id else None
            if existing:
                if payload is not None and dump(payload) != existing['payload']: fail('Conflict', 'event payload changed')
                return {'status': 'Duplicate', 'receipt': strict_loads(existing['receipt']), 'event_id': event_id}
            self.db.execute('BEGIN IMMEDIATE')
            engine, rows = self._replay(run_id, lock); i = len(rows)
            if i == len(lock['schedule']):
                self.db.rollback(); return {'status': 'Complete'}
            item = lock['schedule'][i]
            if event_id is not None and item['event_id'] != event_id: fail('Rejected', 'event is not next committed cursor')
            e = deepcopy(item['event'])
            if item['dynamic']: e['params']['amount'] = str(-engine.balances[item['dynamic']])
            if payload is not None and dump(payload) != dump(e): fail('Conflict', 'payload differs from locked schedule')
            receipt = engine.apply(e)
            if receipt['status'] != 'Applied':
                self.db.rollback(); return {**receipt, 'outputs_available': False}
            dependencies = self._event_dependencies(run_id, e, rows)
            state = self.add_node('state', engine.snapshot(), dependencies); self._fault('state')
            journal = self.add_node('journal', serial(engine.journals[-1]), dependencies); self._fault('journal')
            measurement = self.add_node('measurement', statements(lock['spec']['opening'], engine.journals), dependencies); self._fault('measurement')
            node = self.add_node('event', {'run': run_id, 'event_id': item['event_id'], 'payload': e,
                'state': state, 'journal': journal, 'measurement': measurement}, self._event_dependencies(run_id, e, rows))
            self._fault('lineage')
            self.db.execute('INSERT INTO commits VALUES(?,?,?,?,?,?,?,?,?)',
                (run_id, i, item['event_id'], dump(e), dump(receipt), state, journal, measurement, node))
            self._fault('receipt'); self._fault('before_commit'); self.db.commit(); self._fault('after_commit')
            return {'status': 'Applied', 'receipt': receipt, 'event_id': item['event_id']}
        except P07Error as exc:
            if self.db.in_transaction: self.db.rollback()
            return {'status': exc.code, 'reason': str(exc), 'outputs_available': False}
        except Exception as exc:
            if self.db.in_transaction: self.db.rollback()
            return {'status': 'InternalFailure', 'reason': str(exc), 'outputs_available': False}
        except BaseException:
            if self.db.in_transaction: self.db.rollback()
            raise

    def execute_period(self, run_id, period_id):
        lock = self._lock(run_id)
        ids = [e['event']['period'] for e in lock['schedule']]
        if period_id not in ids: fail('Rejected', 'unknown period')
        target = max(i for i, p in enumerate(ids) if p == period_id)
        while self.db.execute('SELECT count(*) FROM commits WHERE run_id=?', (run_id,)).fetchone()[0] <= target:
            r = self.apply_event(run_id)
            if r['status'] != 'Applied': return r
        return self.period_result(run_id, period_id)

    def period_result(self, run_id, period_id):
        lock = self._lock(run_id); engine, rows = self._replay(run_id, lock)
        opening = Engine(lock['spec']); inputs = []; journals = []; receipts = []
        for row in rows:
            e = strict_loads(row['payload'])
            if e['period'] == period_id:
                inputs.append(e); journals.append(self.node(row['journal_id'])); receipts.append(strict_loads(row['receipt']))
            elif not inputs: opening.apply(e)
        required = sum(e['event']['period'] == period_id for e in lock['schedule'])
        complete = len(inputs) == required and required > 0
        return {'status': 'Complete' if complete else 'Incomplete', 'inputs': inputs, 'events': receipts,
                'opening': serial(opening.balances), 'journals': journals,
                'statements': statements(opening.balances, journals) if complete else None}

    def freeze_result(self, run_id):
        lock = self._lock(run_id); engine, rows = self._replay(run_id, lock)
        if len(rows) != len(lock['schedule']): fail('Rejected', 'incomplete run cannot freeze')
        data = {'run': run_id, 'view': lock['view'], 'state': engine.snapshot(),
                'periods': {p: self.period_result(run_id, p) for p in dict.fromkeys(e['event']['period'] for e in lock['schedule'])}}
        return self.add_node('report', data, [run_id, *(r['event_node'] for r in rows)])

    def result(self, report_id, view=None):
        view = view or self.view
        self.require_usable([report_id], view)
        if self.kind(report_id) != 'report': fail('Rejected', 'report required')
        return self.node(report_id)

    def export(self, report_id, path, *, view=None):
        data = self.result(report_id, view); path = Path(path); temporary = path.with_name(path.name + '.partial')
        try:
            with temporary.open('w') as f:
                f.write(dump(data)); f.flush(); os.fsync(f.fileno())
            self._fault('export'); os.replace(temporary, path)
        finally:
            if temporary.exists(): temporary.unlink()

    def integrity(self):
        nodes = self.db.execute('SELECT id FROM nodes').fetchall()
        for row in nodes: self.node(row[0])
        return {'integrity': self.db.execute('PRAGMA integrity_check').fetchone()[0],
                'foreign_keys': [tuple(r) for r in self.db.execute('PRAGMA foreign_key_check')]}


def migrate(path, *, fault=None, transform=None):
    """Schema 1→2 representation migration; legacy text and all original IDs retained."""
    db = sqlite3.connect(str(path), isolation_level=None)
    db.row_factory = sqlite3.Row
    try:
        db.execute('PRAGMA foreign_keys=ON'); db.execute('PRAGMA synchronous=FULL')
        version = db.execute('PRAGMA user_version').fetchone()[0]
        if version == 2: return {'status': 'AlreadyCurrent'}
        if version != 1: fail('Unsupported', 'unknown migration source schema')
        db.execute('BEGIN IMMEDIATE')
        # DDL and trigger restoration participate in the same migration transaction.
        db.execute('DROP TRIGGER IF EXISTS immutable_nodes_UPDATE')
        db.execute('ALTER TABLE nodes ADD COLUMN canonical TEXT')
        mappings = []
        for key, kind, payload, digest in db.execute('SELECT id,kind,payload,digest FROM nodes').fetchall():
            value = strict_loads(payload); converted = deepcopy(value) if transform is None else transform(deepcopy(value))
            if converted != value or identity(kind, value) != digest: fail('SemanticChange', 'migration changes meaning or legacy hash invalid')
            content = canonical(converted)
            db.execute('UPDATE nodes SET canonical=? WHERE id=?', (content, key))
            mappings.append({'old_id': key, 'new_id': key, 'original_payload': payload,
                             'new_payload': content, 'before_digest': digest, 'after_digest': identity(kind, converted)})
        record = {'from': 1, 'to': 2, 'mappings': mappings}
        db.execute('INSERT INTO migrations VALUES(?,?)', (identity('migration', record), dump(record)))
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            fail('IntegrityFailure', 'invalid legacy database')
        validator = object.__new__(Store)
        validator.db = db
        for row in db.execute('SELECT id FROM runs').fetchall():
            validator._replay(row[0], validator._lock(row[0]))
        if fault: fault('before_commit')
        db.execute('PRAGMA user_version=2'); install_triggers(db); db.commit()
        return {'status': 'Migrated', **record}
    except BaseException:
        db.rollback(); raise
    finally: db.close()
