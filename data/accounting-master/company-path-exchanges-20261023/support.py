"""Local trusted dependencies; packet content never selects executable code."""
from pathlib import Path
import hashlib
import json
from exchanges import load, validate

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=HERE.parent/'company-path-admission-20261023'
JOIN=HERE.parent/'company-operation-path-20261023'
OLD=HERE.parent/'corporate-portable-20261015'


def context():
    previous=load('exchange_baseline_verifier',BASE/'verify.py')
    engine=previous.load_local_engine()
    schema_bytes=(OLD/'record-schemas.json').read_bytes()
    path_schema=(JOIN/'schema.json').read_bytes()
    lock=json.loads((BASE/'reference-locks.json').read_text())
    baseline_hash=hashlib.sha256((BASE/'packet.json').read_bytes()).hexdigest()
    def baseline_admitter(packet,raw):
        return previous.admit_packet(packet,raw,schema_bytes,path_schema,
                                     lock['engine'],lock['methods'],engine.verify_chain)
    def check(packet,raw,replay=True):
        return validate(packet,raw,json.loads(schema_bytes),baseline_hash,
                        baseline_admitter,engine,replay)
    return previous,engine,check
