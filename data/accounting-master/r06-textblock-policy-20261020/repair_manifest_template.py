"""Repair unfinished-unit provenance only, preserving the prepared originals."""
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
path = U / 'verify.py'
protection = U / 'protection.json'
assert not (U / 'completion.json').exists()
before = path.read_bytes()
baseline_bytes = protection.read_bytes()
baseline = json.loads(baseline_bytes)
key = str(path.relative_to(R))
assert baseline['protected'][key] == hashlib.sha256(before).hexdigest()
old = '"acquisition_commands": "None; exact retained primary documents reused", "environment": sys.executable,'
new = '''"acquisition_commands": [load(UNIT / "sources" / (name + "-receipt.json"))["cmd"]
                                 for name in ("DTR", "ValidateFilingText", "edbody.dtd", "xhtml1-strict-ix.dtd")],
        "execution_audit": bind(UNIT / "execution-audit.md"),
        "environment": sys.executable,'''
assert before.decode().count(old) == 1
after = before.decode().replace(old, new).encode()
archive = U / 'recovery'
archive.mkdir(exist_ok=False)
(archive / 'verify-pre-repair.py').write_bytes(before)
(archive / 'protection-pre-repair.json').write_bytes(baseline_bytes)
path.write_bytes(after)
baseline['protected'][key] = hashlib.sha256(after).hexdigest()
protection.write_text(json.dumps(baseline, indent=2) + '\n')
original = json.loads(baseline_bytes)
original['protected'][key] = baseline['protected'][key]
assert original == baseline
record = {
    'reason': 'Copied manifest template falsely stated no acquisitions; four exact receipts exist.',
    'scope': 'Unfinished unit only; no completed predecessor or source/result binding changed.',
    'old_verifier_sha256': hashlib.sha256(before).hexdigest(),
    'new_verifier_sha256': hashlib.sha256(after).hexdigest(),
    'old_protection_sha256': hashlib.sha256(baseline_bytes).hexdigest(),
    'protection_delta': 'Exactly the local verifier self-binding; original bytes archived.',
    'scientific_check_delta': 'None; compare.py and checks.json unchanged.',
}
(archive / 'repair.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record))
