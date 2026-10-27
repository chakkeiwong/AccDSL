#!/usr/bin/env python3
"""Build the current AccDSL PDFs without modifying the protected source package."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = {
    'main': ROOT / 'docs/AccDSL-latest.tex',
    'simulation': ROOT / 'docs/AccDSL-simulation-foundations.tex',
}


def build(requested, output, force=False):
    # LaTeX Workshop's %DOC% omits the .tex suffix. Keep the alias's job name
    # so its PDF viewer finds the expected file, but resolve the source cwd.
    if requested.suffix != '.tex':
        requested = Path(str(requested) + '.tex')
    source = requested.resolve(strict=True)
    if source.suffix != '.tex' or not source.is_relative_to(ROOT / 'docs'):
        raise ValueError('Expected a TeX root within this repository docs directory')
    for protected in [source.parent, ROOT / 'docs/design/proposal', ROOT / 'docs/archive']:
        if output == protected or output.is_relative_to(protected):
            raise ValueError('Build outputs must be outside protected source packages')
    job = requested.stem
    output.mkdir(parents=True, exist_ok=True)
    cache = output / '.tex-cache'
    cache.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.update(TEXMFVAR=str(cache), TEXMFCACHE=str(cache))
    command = [
        'latexmk', '-norc', '-lualatex', '-interaction=nonstopmode',
        '-halt-on-error', '-file-line-error', '-synctex=1', '-no-shell-escape',
        '-outdir=' + str(output), '-jobname=' + job,
    ]
    if force:
        command.append('-g')
    command.append(source.name)
    log_path = output / (job + '.build.log')
    pdf_path = output / (job + '.pdf')
    for path in output.glob(job + '.*'):
        if path.is_symlink():
            raise ValueError('Refusing symlinked build output: ' + str(path))
    print('Source: ' + str(source), flush=True)
    print('Output: ' + str(pdf_path), flush=True)
    start = time.monotonic()
    with log_path.open('w') as log:
        process = subprocess.Popen(
            command, cwd=source.parent, env=env, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, errors='replace',
        )
        try:
            for line in process.stdout:
                log.write(line)
                print(line, end='', flush=True)
            code = process.wait()
        except KeyboardInterrupt:
            process.terminate()
            process.wait()
            raise
    if code == 0 and not pdf_path.is_file():
        code = 1
    result = {
        'command': command, 'cwd': str(source.parent),
        'requested_tex': str(requested), 'resolved_tex': str(source),
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'returncode': code, 'seconds': time.monotonic() - start,
        'environment': {key: env[key] for key in ['TEXMFVAR', 'TEXMFCACHE']},
        'pdf': str(pdf_path), 'log': str(log_path),
        'pdf_sha256': hashlib.sha256(pdf_path.read_bytes()).hexdigest()
        if code == 0 else None,
        'scope': 'Local build only; no change to canonical PDFs or release acceptance',
    }
    (output / (job + '.build.json')).write_text(json.dumps(result, indent=2) + '\n')
    if code:
        print('Build failed; see ' + str(log_path), file=sys.stderr)
    else:
        print('Built ' + str(pdf_path), flush=True)
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('volume', nargs='?', choices=['main', 'simulation', 'all'], default='all')
    parser.add_argument('--tex', type=Path, help='Explicit root or symlink, with or without .tex')
    parser.add_argument('--output-dir', type=Path, default=ROOT / '.build/pdf')
    parser.add_argument('--force', action='store_true', help='Ask latexmk to rerun all rules')
    args = parser.parse_args()
    missing = [tool for tool in ['latexmk', 'lualatex', 'bibtex'] if not shutil.which(tool)]
    if missing:
        parser.error('Missing required TeX tools on PATH: ' + ', '.join(missing))
    if args.tex and args.volume != 'all':
        parser.error('Use either --tex or a volume selection')
    requested = [args.tex.expanduser()] if args.tex else (
        list(DOCUMENTS.values()) if args.volume == 'all' else [DOCUMENTS[args.volume]])
    try:
        for path in requested:
            code = build(path, args.output_dir.expanduser().resolve(), args.force)
            if code:
                return code
    except (OSError, ValueError) as error:
        print('PDF build: ' + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
