"""Offline method-fragment diagnostics, not an installed Docling execution."""
import ast
import copy
from contextlib import nullcontext
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import logging
import os
from pathlib import Path
import sys
import time
import tomllib
from types import SimpleNamespace as NS

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PACKET = ROOT / 'docs/design/proposal/methods/preparation-20261005-v1/03-adapters'
PIN = 'eda5b5fc86d10b2b79a900ff3e69fc159d5f6014'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    started, timer = datetime.now(timezone.utc).isoformat(), time.monotonic()
    reg = read(PACKET / 'source-register.json')
    selected = ['docling/document_converter.py', 'docling/pipeline/standard_pdf_pipeline.py',
                'docling/datamodel/base_models.py', 'docling/datamodel/document.py',
                'docling/datamodel/pipeline_options.py', 'pyproject.toml', 'LICENSE']
    inputs, files = {}, {}
    for name in selected:
        row = next(r for r in reg['sources'] if r['repository'] == 'docling-project/docling' and r['upstream_path'] == name)
        path = PACKET / row['path']
        assert row['commit'] == PIN and sha(path) == row['sha256'], name
        inputs[rel(path)] = sha(path); files[name] = path
    base_path = OUT / 'sources/base-pipeline.py'
    files['base'] = base_path; inputs[rel(base_path)] = sha(base_path)
    inputs[rel(PACKET / 'source-register.json')] = sha(PACKET / 'source-register.json')
    save('acquisition-receipt.json', dict(url=f'https://raw.githubusercontent.com/docling-project/docling/{PIN}/docling/pipeline/base_pipeline.py',
        requested_commit=PIN, status=200, bytes=17334, curl_time_seconds=0.793686,
        body=dict(path=rel(base_path), sha256=sha(base_path)),
        headers=dict(path=rel(OUT / 'sources/base-pipeline.headers'), sha256=sha(OUT / 'sources/base-pipeline.headers')),
        permissions='ordinary sandbox request succeeded', retrieved_date='2026-10-10',
        retrieval_instant='not captured separately; HTTP headers and this post-retrieval receipt retained'))
    metadata = tomllib.loads(files['pyproject.toml'].read_text())
    save('declared-dependencies.json', dict(source=dict(path=rel(files['pyproject.toml']),sha256=sha(files['pyproject.toml'])),
        repository_pin=PIN, project=metadata['project']['name'], version=metadata['project']['version'],
        requires_python=metadata['project']['requires-python'], base=metadata['project']['dependencies'],
        optional=metadata['project']['optional-dependencies'], build=metadata['build-system'],
        source_licence=metadata['project']['license'], installed_lock=None, transitive_licence_lock=None,
        model_weights_lock=None, admission='declared source metadata only; no installation or compatibility result'))

    anchors = []
    scope = dict(__name__=__name__, Enum=Enum, dataclass=dataclass, field=field, sys=sys,
        ErrorItem=lambda **kw: NS(page_no=kw.pop('page_no', None), **kw),
        Size=lambda **kw: NS(**kw), PageItem=lambda **kw: NS(**kw),
        DocumentLimits=lambda **kw: NS(**kw), _DocumentConversionInput=lambda **kw: NS(**kw),
        DEFAULT_PAGE_RANGE=(1, sys.maxsize), ConversionError=RuntimeError,
        get_input_rejection_cause=lambda _: None, _log=logging.getLogger('docling-source-fragment'),
        TimeRecorder=lambda *a, **kw: nullcontext(), ProfilingScope=NS(DOCUMENT='document'))

    def extract(file_key, name, owner=None, compile_node=True):
        path = files[file_key]; text = path.read_text(); tree = ast.parse(text)
        parent = tree if owner is None else next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner)
        node = next(n for n in parent.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name == name)
        start = min([node.lineno] + [d.lineno for d in node.decorator_list])
        quote = '\n'.join(text.splitlines()[start-1:node.end_lineno]) + '\n'
        anchors.append(dict(id=(owner + '.' if owner else '') + name, path=rel(path), sha256=sha(path),
            first_line=start, last_line=node.end_lineno, quote_sha256=hashlib.sha256(quote.encode()).hexdigest(),
            executed_as_fragment=compile_node))
        if compile_node:
            detached = copy.deepcopy(node)
            # Remove only the Pydantic call decorator on the public generator.
            # Its method body stays byte/AST-identical; validation is not tested.
            if name == 'convert_all':
                detached.decorator_list = []
            original_body = ast.dump(ast.Module(body=node.body, type_ignores=[]), include_attributes=False)
            detached_body = ast.dump(ast.Module(body=detached.body, type_ignores=[]), include_attributes=False)
            assert original_body == detached_body
            module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), detached], type_ignores=[])
            exec(compile(ast.fix_missing_locations(module), rel(path), 'exec'), scope)
            return scope[name]

    base_models = 'docling/datamodel/base_models.py'
    for name in ['ConversionStatus', 'FailureCategory', 'DoclingComponentType']:
        extract(base_models, name)
    pipeline = 'docling/pipeline/standard_pdf_pipeline.py'
    extract(pipeline, 'ProcessingResult'); extract(pipeline, '_make_error_item')
    integrate = extract(pipeline, '_integrate_results', 'StandardPdfPipeline')
    add_missing = extract(pipeline, '_add_failed_pages_to_document', 'StandardPdfPipeline')
    determine = extract(pipeline, '_determine_status', 'StandardPdfPipeline')
    execute = extract('base', 'execute', 'BasePipeline')
    expected_pages = extract('base', 'get_expected_page_nos')
    convert = extract('docling/document_converter.py', 'convert_all', 'DocumentConverter')
    for file_key, name, owner in [
        (pipeline, '_build_document', 'StandardPdfPipeline'),
        (pipeline, '_assemble_document', 'StandardPdfPipeline'),
        (pipeline, 'stop', 'ThreadedPipelineStage'),
        ('base', '_enrich_document', 'BasePipeline'),
        ('docling/document_converter.py', '_convert', 'DocumentConverter'),
        ('docling/document_converter.py', '_process_document', 'DocumentConverter'),
        ('docling/document_converter.py', '_execute_pipeline', 'DocumentConverter')]:
        extract(file_key, name, owner, False)
    save('source-anchors.json', dict(pin=PIN, inputs=inputs, anchors=anchors,
        exact_method_bodies=True, excluded_decorator='Pydantic validate_call on convert_all; argument validation not tested'))
    run_cases(scope, inputs, anchors, integrate, add_missing, determine, execute, expected_pages, convert, started, timer)


def run_cases(scope, inputs, anchors, integrate, add_missing, determine, execute, expected_pages, convert, started, timer):
    status, category = scope['ConversionStatus'], scope['FailureCategory']
    scope['ConversionResult'] = lambda **kw: NS(**kw, pages=[], errors=[], status=status.PENDING,
                                                document=NS(pages={}))
    cases = [
        dict(id='all_requested_complete', success=[1, 2, 3], failed=[], timeout=False,
             page_range=[1, 3], expected_status='success', expected_exception=False),
        dict(id='two_pages_failed', success=[1], failed=[2, 3], timeout=False,
             page_range=[1, 3], expected_status='partial_success', expected_exception=False),
        dict(id='timeout_before_first_page', success=[], failed=[1, 2, 3], timeout=True,
             page_range=[1, 3], expected_status='partial_success', expected_exception=False),
        dict(id='complete_failure_without_timeout', success=[], failed=[1, 2, 3], timeout=False,
             page_range=[1, 3], expected_status='failure', expected_exception=True),
        dict(id='requested_subset_complete', success=[2], failed=[], timeout=False,
             page_range=[2, 2], expected_status='success', expected_exception=False),
    ]
    outcomes, checks = [], []
    for c in cases:
        source = NS(file=Path('synthetic-three-page.pdf'), page_count=3,
                    limits=NS(page_range=tuple(c['page_range'])))
        class StageFixture:
            keep_images = True
            keep_backend = True
            pipeline_options = NS(generate_parsed_pages=True)
            _page_sizes_by_no = {n: NS(width=612.0, height=792.0) for n in [1, 2, 3]}

            def _build_document(self, res):
                requested = expected_pages(res)
                res.pages = [NS(page_no=n) for n in requested]
                failures = [(n, RuntimeError('synthetic timeout' if c['timeout'] else 'synthetic page failure'),
                    scope['ErrorItem'](component_type=scope['DoclingComponentType'].PIPELINE,
                        module_name='synthetic_stage', error_message='synthetic page outcome',
                        category=category.TIMEOUT if c['timeout'] else category.INFERENCE_FAILURE,
                        page_no=n)) for n in c['failed']]
                proc = scope['ProcessingResult'](pages=[NS(page_no=n) for n in c['success']],
                                                failed_pages=failures, total_expected=len(requested))
                integrate(self, res, proc, timeout_exceeded=c['timeout'])
                return res

            def _assemble_document(self, res):
                # Supply the successful model outputs; no actual layout/model runs.
                res.document.pages = {n: NS(page_no=n, content='synthetic successful page') for n in c['success']}
                add_missing(self, res, expected_page_nos=expected_pages(res))
                return res

            def _enrich_document(self, res):
                return res  # No enrichments in the diagnostic fixture.

            def _determine_status(self, res):
                return determine(self, res)

            def _unload(self, res):
                self.unload_called = True  # No backend/worker exists to unload.

        fixture = StageFixture()
        result = execute(fixture, source, raises_on_error=True)
        requested = expected_pages(result)
        emitted, exception = [], None
        converter_fixture = NS(_convert=lambda *a, **kw: iter([result]))
        try:
            emitted = list(convert(converter_fixture, ['synthetic-three-page.pdf'], raises_on_error=True))
        except RuntimeError as e:
            exception = str(e)
        processed = [p.page_no for p in result.pages]
        missing = sorted(set(requested) - set(processed))
        placeholders = [n for n, p in result.document.pages.items() if getattr(p, 'content', None) is None]
        errors = [dict(category=e.category.value, page_no=e.page_no, message=e.error_message) for e in result.errors]
        expected_error_pages = c['failed']
        assertions = {
            'declared_status': result.status.value == c['expected_status'],
            'declared_exception_behavior': bool(exception) == c['expected_exception'],
            'successful_pages_exact': processed == c['success'],
            'structured_page_errors_retained': sorted(e['page_no'] for e in errors if e['page_no'] is not None) == expected_error_pages,
            'numbering_restored_without_content': sorted(result.document.pages) == requested and sorted(placeholders) == missing,
            'timeout_document_error': any(e['category'] == 'timeout' and e['page_no'] is None for e in errors) == c['timeout'],
            'result_yielded_iff_return_filter_allows': len(emitted) == (0 if c['expected_exception'] else 1),
        }
        checks.extend(dict(id=c['id'] + ':' + name, passed=value) for name, value in assertions.items())
        outcomes.append(dict(case=c, evidence_class='observed exact-method fragment under synthetic stage outcomes',
            upstream_status=result.status.value, raises_on_error=True, converter_exception=exception,
            yielded_results=len(emitted), source_pages=[1, 2, 3], requested_pages=requested,
            processed_pages=processed, document_page_keys=sorted(result.document.pages), placeholder_pages=sorted(placeholders),
            structured_errors=errors, proposed_exchange=dict(
                requested_processing='complete' if not missing and not errors else 'incomplete',
                missing_requested_pages=missing, unrequested_pages=sorted({1, 2, 3} - set(requested)),
                semantic_acceptance='pending', original_source_preserved='required by proposed contract; no actual source conversion here'),
            cleanup_observation='source finally called a no-op diagnostic unload; no real worker termination tested'))
    save('fragment-results.json', dict(pin=PIN, cases=outcomes,
        injected_objects=['SimpleNamespace page/result/input/error/size records replace library data classes',
                          'synthetic builder outcomes replace threads, OCR, PDF backend and timing',
                          'synthetic assembly result plus exact missing-page helper replaces layout/reading-order models',
                          'identity enrichment and no-op unload replace downstream stages and cleanup',
                          'precomputed result iterator replaces converter scheduling',
                          'null timer and disabled logger replace profiling; API argument validator omitted'],
        non_claim='Not an installed Docling run, extraction ranking or end-to-end reachability demonstration'))
    for name in ['source-anchors.json', 'fragment-results.json', 'declared-dependencies.json',
                 'source-review.md', 'acquisition-receipt.json']:
        inputs[rel(OUT / name)] = sha(OUT / name)
    report = dict(checker_sha256=sha(Path(__file__)), inputs=inputs, checks=checks,
        passed=sum(c['passed'] for c in checks), failed=sum(not c['passed'] for c in checks),
        started_at=started, wall_seconds=time.monotonic() - timer,
        command='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 ' + rel(Path(__file__)),
        python_executable=sys.executable, python_version=sys.version, CUDA_VISIBLE_DEVICES='-1',
        cpu_gpu_status='CPU only; GPU devices intentionally hidden', runtime_library_imported=False)
    save('checks.json', report)
    print(json.dumps(dict(cases=len(cases), passed=report['passed'], failed=report['failed'],
                          outcomes={c['case']['id']:c['upstream_status'] for c in outcomes})))
    assert not report['failed']


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'completion.json').exists()
    main()
