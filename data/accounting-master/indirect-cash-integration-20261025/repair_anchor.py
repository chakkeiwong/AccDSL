"""Preserve the first verifier and use an end anchor on the final added page."""
from pathlib import Path
from hashlib import sha256
import json
HERE = Path(__file__).resolve().parent
source = HERE / 'integrate.py'
text = source.read_text()
old = 'Algebraically consistent decompositions can nevertheless'
assert old in text
target = HERE / 'integrate_v2.py'
assert not target.exists()
attempt = HERE / 'attempt-01-page-anchor'
attempt.mkdir()
(attempt / 'verification.log').write_bytes(Path('/tmp/accdsl-indirect-integration-verification.log').read_bytes())
(attempt / 'verifier.py').write_bytes(source.read_bytes())
target.write_text(text.replace(old, 'that the full note package is complete.'))
(HERE / 'verification-repair.md').write_text('''# PDF text anchor repair

The manuscript builds successfully and preserves content. Verification failed
because an exact search phrase straddled PDF398/399. The successor verifier
uses the final qualification as the end anchor, ensuring the review includes
page399. Original verifier and failed log remain preserved. The manuscript
and locked evidence are unchanged. This repairs navigation, not the claims.
''')
print(json.dumps({'repair': 'cross-page search anchor', 'successor': str(target),
                  'sha256': sha256(target.read_bytes()).hexdigest()}))
