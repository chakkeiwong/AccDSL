"""One recorded successor build; never rebuild a completed numerical attempt."""
from datetime import datetime, timezone
import json
import subprocess
import time
from integrate_manuscript import NEXT, OUT


def main():
    record = OUT / 'build-manifest.json'
    assert not record.exists(), 'Preserve completed build'
    command = ['latexmk', '-lualatex', '-silent', '-g', '-interaction=nonstopmode',
               '-halt-on-error', 'accounting-product-proposal.tex']
    started = time.monotonic()
    with (OUT / 'build-console.log').open('w') as log:
        run = subprocess.run(command, cwd=NEXT, stdout=log, stderr=subprocess.STDOUT)
    record.write_text(json.dumps(dict(command=command, directory=str(NEXT),
        recorded_utc=datetime.now(timezone.utc).isoformat(), exit_code=run.returncode,
        wall_seconds=time.monotonic()-started), indent=2)+'\n')
    print(json.dumps(dict(exit_code=run.returncode, wall_seconds=time.monotonic()-started)))
    raise SystemExit(run.returncode)


if __name__ == '__main__':
    main()
