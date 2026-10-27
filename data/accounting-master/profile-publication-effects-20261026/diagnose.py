"""Bounded debugging inventory; does not publish acceptance results."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from descriptor import Descriptor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
lock = json.loads((HERE / 'source-lock.json').read_text())
for entry in lock['profiles']:
    for path, digest in entry['files'].items():
        assert sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    packet = json.loads((ROOT / entry['packet']).read_text())
    try:
        reader = Descriptor(packet, entry)
    except Exception as exc:
        print(json.dumps({'profile': entry['name'], 'constructor': type(exc).__name__ + ':' + str(exc)}))
        continue
    counts, samples = Counter(), {}
    for exchange in packet['exchanges']:
        try:
            result = reader.describe(exchange)
            counts['pass:' + result['disposition']] += 1
        except Exception as exc:
            key = type(exc).__name__ + ':' + str(exc)
            counts[key] += 1
            samples.setdefault(key, exchange['id'])
    print(json.dumps({'profile': entry['name'], 'counts': counts, 'first_failure': samples}, sort_keys=True))
