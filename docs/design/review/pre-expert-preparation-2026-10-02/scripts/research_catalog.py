#!/usr/bin/env python3
"""Local catalogue operations; network retrieval is recorded separately."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/design/research'

def read(path):
    return json.loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def initialize():
    records = []
    for candidate in read(BASE / 'candidates.json'):
        key = candidate['id']
        results = read(BASE / 'raw' / f'{key}-search.json').get('results', [])
        if key == 'jensen1999':
            continue  # Search result is not the requested paper.
        index = 1 if key == 'vandeMeent2018' else 0
        r = results[index]
        authors = [a['author']['display_name'] for a in r.get('authorships', [])]
        records.append(dict(id=key, title=r['title'], authors=authors,
                            year=r['publication_year'], doi=r.get('doi'),
                            openalex_id=r['id'], selected_search_result=index,
                            cited_by_count=r.get('cited_by_count', 'not available'),
                            venue=(r.get('primary_location') or {}).get('raw_source_name'),
                            is_retracted=r.get('is_retracted'),
                            urls=[x['pdf_url'] for x in r.get('locations', []) if x.get('pdf_url')],
                            status='nominated; full text not yet inspected'))
    write(BASE / 'catalog.json', records)

def index_files():
    records = read(BASE / 'catalog.json')
    for r in records:
        if not r.get('local_path'):
            continue
        p = ROOT / r['local_path']
        if not p.exists():
            continue
        if not p.read_bytes().startswith(b'%PDF-'):
            print(r['id'], 'INVALID_PDF')
            continue
        r['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
        target = BASE / 'text' / (r['id'] + '.txt')
        subprocess.run(['pdftotext', '-layout', str(p), str(target)], check=True)
        r['text_path'] = str(target.relative_to(ROOT))
        info = subprocess.run(['pdfinfo', str(p)], capture_output=True, text=True, check=True).stdout
        m = re.search(r'^Pages:\s+(\d+)', info, re.M)
        r['pages'] = int(m.group(1)) if m else None
        print(r['id'], r['pages'], 'pages', len(target.read_text()), 'characters')
    write(BASE / 'catalog.json', records)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['initialize', 'index'])
    args = parser.parse_args()
    initialize() if args.action == 'initialize' else index_files()
