#!/usr/bin/env python3
"""Separate P12 preparation and evaluation invocations; synchronous children only."""
import argparse
import json
import os
from pathlib import Path
import sys
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from accounting_benchmark_v1 import (OUTPUT, preparation, repair_preparation, file_hash,
                                     require, read, evaluate, render_result, execute_workload)


def main(argv=None):
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--evaluate', action='store_true')
    modes.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--repair-archive', type=Path,
                        help='With --prepare, preserve a verified prior benchmark/report/source archive')
    args = parser.parse_args(argv)
    if args.repair_archive and not args.prepare:
        parser.error('--repair-archive requires --prepare')
    if args.child:
        print(json.dumps(execute_workload(json.load(sys.stdin))))
        return 0
    path = OUTPUT / 'benchmark.json'
    if args.prepare:
        if path.exists():
            if not args.repair_archive:
                raise ValueError('preparation already exists; do not overwrite frozen evidence')
            archive = read(args.repair_archive)
            require(file_hash(path) == archive['benchmark_sha256'], 'archive benchmark does not match disk')
            require(file_hash(OUTPUT / 'result.md') == archive['result_sha256'], 'archive result does not match disk')
            document = repair_preparation(read(path), archive)
        else:
            require(not args.repair_archive, 'repair requires an existing benchmark')
            document = preparation()
        OUTPUT.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n')
        print(json.dumps({'status': document['status'], 'preparation_sha256': document['preparation_sha256']}))
        return 0
    document = evaluate(read(path))
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + '\n')
    (OUTPUT / 'result.md').write_text(render_result(document))
    print(json.dumps({'status': document['status'], 'chronology_passed': document['runs'][-1]['chronology_score']['passed'],
                      'workload_runs_passed': document['runs'][-1]['workload_runs_passed']}))
    return 0 if document['status'] == 'finite_conformance_pass' else 1


if __name__ == '__main__':
    sys.exit(main())
