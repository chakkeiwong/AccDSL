"""Exact-byte, single-writer evidence archive reference; no simulation admission."""
from copy import deepcopy
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
import json
import os
import re
import sqlite3
import tempfile
from contextlib import closing

import company_persistence_v1 as p07

PROFILE = 'SimulatorEvidenceBundle/1'
ARCHIVE = 'SimulatorEvidenceArchive/1'
RECEIPT = 'SimulatorEvidenceReceipt/1'
RECORD = 'SimulatorEvidenceBytes/1'
ROLES = {'definition', 'state', 'proposal', 'result', 'note'}
ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT/'data/accounting-master/simulator-evidence-archive-20261024/source-lock.json'
LIMIT_FIELDS = {'max_records', 'max_record_bytes', 'max_total_bytes'}
BOUNDARY = {'semantic_verified':False, 'source_admission':False,
            'accounting_admission':False, 'method_eligible':False,
            'simulation_executed':False, 'native_committed':False}


class ArchiveError(ValueError):
    def __init__(self, code, reason):
        self.code = code
        super().__init__(reason)


def need(condition, reason, code='Invalid'):
    if not condition:
        raise ArchiveError(code, reason)


def strict_object(text):
    """Validate JSON without converting or rewriting the retained original text."""
    need(type(text) is str, 'JSON text required')
    try:
        text.encode('utf-8', errors='strict')
        def pairs(items):
            result = {}
            for key, value in items:
                need(key not in result, 'duplicate JSON key')
                result[key] = value
            return result
        def constant(value):
            raise ArchiveError('Invalid', 'nonfinite JSON number')
        value = json.loads(text, object_pairs_hook=pairs, parse_int=Decimal,
                           parse_float=Decimal, parse_constant=constant)
        need(type(value) is dict, 'top-level JSON object required')
        def strings(x):
            if isinstance(x, str):
                x.encode('utf-8', errors='strict')
            elif isinstance(x, Decimal):
                need(x.is_finite(), 'nonfinite JSON number')
            elif isinstance(x, dict):
                for key, item in x.items():
                    strings(key); strings(item)
            elif isinstance(x, list):
                for item in x:
                    strings(item)
        strings(value)
        return value
    except ArchiveError:
        raise
    except (UnicodeError, ValueError, TypeError, RecursionError, ArithmeticError) as exc:
        raise ArchiveError('Invalid', 'invalid UTF-8 or JSON payload') from exc


def validate(bundle, limits):
    need(type(limits) is dict and set(limits)==LIMIT_FIELDS, 'closed explicit limits required')
    need(all(type(x) is int and x>0 for x in limits.values()), 'positive integer limits required')
    need(type(bundle) is dict and set(bundle)=={'profile','records'} and bundle['profile']==PROFILE, 'closed bundle profile required')
    rows = bundle['records']
    need(type(rows) is list and 0<len(rows)<=limits['max_records'], 'record count limit', 'Limit')
    seen = set(); total = 0
    for record in rows:
        need(type(record) is dict and set(record)=={'name','role','profile','json','dependencies'}, 'closed record fields')
        name = record['name']
        need(type(name) is str and re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,127}',name) is not None and name not in seen, 'unique ASCII record name required')
        need(type(record['role']) is str and record['role'] in ROLES, 'record role')
        need(type(record['profile']) is str and 0<len(record['profile'])<=200, 'declared profile label')
        try:
            record['profile'].encode('utf-8', errors='strict')
            raw = record['json'].encode('utf-8', errors='strict') if type(record['json']) is str else None
        except UnicodeError as exc:
            raise ArchiveError('Invalid','invalid UTF-8') from exc
        need(raw is not None, 'JSON text required')
        total += len(raw)
        need(len(raw)<=limits['max_record_bytes'] and total<=limits['max_total_bytes'], 'payload byte limit', 'Limit')
        value = strict_object(record['json'])
        if 'profile' in value:
            need(value['profile']==record['profile'], 'declared/payload profile mismatch')
        deps = record['dependencies']
        need(type(deps) is list and all(type(x) is str for x in deps), 'dependency names')
        need(len(deps)==len(set(deps)) and set(deps)<=seen, 'dependencies must be distinct prior records')
        seen.add(name)
    return total


def code_lock():
    locked = json.loads(LOCK_PATH.read_text())
    names = ['scripts/company_persistence_v1.py','scripts/company_execution_v1.py','scripts/context_chronology_v1.py']
    result = {name:locked[name] for name in names}
    for name, digest in result.items():
        need(sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'storage code changed: '+name, 'CodeMismatch')
    return result


def node_identity(kind, value, dependencies):
    return p07.identity('node', [kind,p07.identity(kind,value),sorted(dependencies)])


def marker_value():
    return {'profile':ARCHIVE, 'storage_code':code_lock(), 'boundary':deepcopy(BOUNDARY)}


class Archive:
    def __init__(self, path, limits, *, fault=None):
        # Validate limits independently, before creating or opening any database.
        need(type(limits) is dict and set(limits)==LIMIT_FIELDS, 'closed explicit limits required')
        need(all(type(x) is int and x>0 for x in limits.values()), 'positive integer limits required')
        self.limits = deepcopy(limits)
        self.path = Path(path).absolute()
        self.fault = fault
        self.marker = marker_value()
        self.marker_id = node_identity('archive_marker',self.marker,[])
        need(not self.path.is_symlink(), 'symlink archive path unsupported')
        if not self.path.exists():
            need(self.path.parent.is_dir(), 'archive parent missing')
            fd, stage = tempfile.mkstemp(prefix='.'+self.path.name+'.stage-',dir=self.path.parent)
            os.close(fd)
            stage = Path(stage)
            try:
                with p07.Store(stage) as db:
                    key = db.add_node('archive_marker',self.marker)
                    need(key==self.marker_id, 'marker identity mismatch', 'Integrity')
                self._fault('initial_before_publish')
                try:
                    os.link(stage,self.path)  # Never overwrite a concurrently created path.
                except FileExistsError:
                    pass
                self._fault('initial_after_publish')
            finally:
                stage.unlink(missing_ok=True)
        self._preflight()
        self.store = p07.Store(self.path)
        self._checked_node(self.marker_id,'archive_marker',[])

    def _fault(self, name):
        if self.fault:
            self.fault(name)

    def _preflight(self):
        """Refuse unrelated stores read-only, before P07 installs any triggers."""
        try:
            with closing(sqlite3.connect(self.path.as_uri()+'?mode=ro',uri=True)) as db:
                need(db.execute('PRAGMA user_version').fetchone()[0]==p07.VERSION,'unsupported storage version','Unsupported')
                row = db.execute('SELECT kind,payload,digest,canonical FROM nodes WHERE id=?',(self.marker_id,)).fetchone()
                need(row is not None,'archive marker missing or incompatible','Unsupported')
                value = p07.strict_loads(row[1])
                need(row[0]=='archive_marker' and value==self.marker and row[2]==p07.identity('archive_marker',value) and row[3]==p07.canonical(value),'invalid archive marker','Integrity')
                need(not db.execute('SELECT parent FROM edges WHERE child=?',(self.marker_id,)).fetchall(),'marker dependencies','Integrity')
        except ArchiveError:
            raise
        except (sqlite3.Error, p07.P07Error, ValueError, TypeError) as exc:
            raise ArchiveError('Unsupported','unrecognized or invalid archive') from exc

    def close(self):
        self.store.close()

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.close()

    def _checked_node(self, key, kind, dependencies):
        try:
            value = self.store.node(key)
            actual_kind = self.store.db.execute('SELECT kind FROM nodes WHERE id=?',(key,)).fetchone()[0]
            parents = [r[0] for r in self.store.db.execute('SELECT parent FROM edges WHERE child=? ORDER BY parent',(key,))]
            need(actual_kind==kind and parents==sorted(dependencies),'node kind or dependency mismatch','Integrity')
            need(key==node_identity(kind,value,dependencies),'node identity mismatch','Integrity')
            return value
        except p07.P07Error as exc:
            raise ArchiveError('Integrity',str(exc)) from exc

    def archive(self, bundle):
        total = validate(bundle,self.limits)
        code_lock()
        self._checked_node(self.marker_id,'archive_marker',[])
        nodes = {}; descriptors = []
        self.store.db.execute('BEGIN IMMEDIATE')
        try:
            for ordinal, record in enumerate(bundle['records']):
                raw = record['json'].encode('utf-8')
                # Hex-encode profile too: it is an exact declaration, not a normalized label.
                envelope = {'profile':RECORD,'name':record['name'],'role':record['role'],
                    'declared_profile_utf8_hex':record['profile'].encode('utf-8').hex(),
                    'sha256':sha256(raw).hexdigest(),'byte_count':len(raw),'bytes_hex':raw.hex(),
                    'ordered_parent_names':deepcopy(record['dependencies'])}
                parents = [self.marker_id, *(nodes[name] for name in record['dependencies'])]
                key = self.store.add_node('archive_record',envelope,parents)
                nodes[record['name']] = key
                descriptors.append({'name':record['name'],'node':key})
                self._fault('record_'+str(ordinal))
            value = {'profile':RECEIPT,'bundle_profile':PROFILE,'ordered_records':descriptors,
                     'total_bytes':total,'boundary':deepcopy(BOUNDARY)}
            key = self.store.add_node('archive_receipt',value,[self.marker_id,*nodes.values()])
            # An existing immutable identity is not a substitute for checking its bytes.
            need(self.read(key)['bundle']==bundle,'stored bundle differs from request','Integrity')
            self._fault('before_commit')
            self.store.db.commit()
            self._fault('after_commit')
        except BaseException:
            if self.store.db.in_transaction:
                self.store.db.rollback()
            raise
        return {'profile':RECEIPT,'receipt':key,'archived':True,**deepcopy(BOUNDARY)}

    def read(self, key):
        code_lock()
        self._checked_node(self.marker_id,'archive_marker',[])
        try:
            receipt = self.store.node(key)
            need(type(receipt) is dict and set(receipt)=={'profile','bundle_profile','ordered_records','total_bytes','boundary'},'closed receipt fields','Integrity')
            need(receipt['profile']==RECEIPT and receipt['bundle_profile']==PROFILE and receipt['boundary']==BOUNDARY,'receipt profile/boundary','Integrity')
            descriptors = receipt['ordered_records']
            need(type(descriptors) is list and 0<len(descriptors)<=self.limits['max_records'],'receipt count','Limit')
            need(all(type(x) is dict and set(x)=={'name','node'} and type(x['name']) is str and type(x['node']) is str for x in descriptors),'receipt descriptors','Integrity')
            self._checked_node(key,'archive_receipt',[self.marker_id,*[x['node'] for x in descriptors]])
            rows = []; nodes = {}; total = 0
            for descriptor in descriptors:
                name = descriptor['name']; node = descriptor['node']
                need(name not in nodes,'duplicate retained name','Integrity')
                value = self.store.node(node)
                need(type(value) is dict and set(value)=={'profile','name','role','declared_profile_utf8_hex','sha256','byte_count','bytes_hex','ordered_parent_names'},'closed record envelope','Integrity')
                need(value['profile']==RECORD and value['name']==name,'record profile/name','Integrity')
                deps = value['ordered_parent_names']
                need(type(deps) is list and all(type(x) is str and x in nodes for x in deps) and len(deps)==len(set(deps)),'record dependencies','Integrity')
                self._checked_node(node,'archive_record',[self.marker_id,*[nodes[x] for x in deps]])
                need(type(value['bytes_hex']) is str and len(value['bytes_hex'])<=2*self.limits['max_record_bytes'],'retained byte limit','Limit')
                raw = bytes.fromhex(value['bytes_hex'])
                need(raw.hex()==value['bytes_hex'] and type(value['byte_count']) is int and len(raw)==value['byte_count'] and sha256(raw).hexdigest()==value['sha256'],'byte hash/count mismatch','Integrity')
                need(total+len(raw)<=self.limits['max_total_bytes'],'retained total byte limit','Limit')
                declared = bytes.fromhex(value['declared_profile_utf8_hex']).decode('utf-8')
                need(declared.encode('utf-8').hex()==value['declared_profile_utf8_hex'],'profile bytes mismatch','Integrity')
                rows.append({'name':name,'role':value['role'],'profile':declared,'json':raw.decode('utf-8'),'dependencies':deepcopy(deps)})
                nodes[name] = node
                total += len(raw)
            bundle = {'profile':PROFILE,'records':rows}
            validate(bundle,self.limits)
            need(type(receipt['total_bytes']) is int and total==receipt['total_bytes'],'total bytes mismatch','Integrity')
            return {'profile':RECEIPT,'receipt':key,'bundle':bundle,'byte_integrity_verified':True,**deepcopy(BOUNDARY)}
        except ArchiveError:
            raise
        except (p07.P07Error, KeyError, TypeError, ValueError, UnicodeError, RecursionError) as exc:
            raise ArchiveError('Integrity','invalid retained evidence') from exc

    def integrity(self):
        code_lock()
        self._checked_node(self.marker_id,'archive_marker',[])
        result = self.store.integrity()
        need(result=={'integrity':'ok','foreign_keys':[]},'SQLite integrity failure','Integrity')
        receipts = [r[0] for r in self.store.db.execute("SELECT id FROM nodes WHERE kind='archive_receipt'")]
        for key in receipts:
            self.read(key)
        return {'byte_integrity_verified':True,'receipts':len(receipts),**deepcopy(BOUNDARY)}
