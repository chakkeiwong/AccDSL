"""Index inspected source and declared dependencies without importing Docling."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import re
import time
import tomllib

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/docling'
PIN = 'eda5b5fc86d10b2b79a900ff3e69fc159d5f6014'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(ROOT))


def save(name, value):
    with (OUT / name).open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def source(upstream):
    filename = upstream.replace('/', '__')
    p = OUT / 'sources' / filename
    return p if p.exists() else OLD / filename


def anchor(key, upstream, qualname, meaning):
    p = source(upstream)
    raw = p.read_text()
    node = ast.parse(raw)
    for name in qualname.split('.'):
        node = next(n for n in node.body if getattr(n, 'name', None) == name or
                    isinstance(n, ast.Assign) and any(getattr(x, 'id', None) == name for x in n.targets))
    excerpt = ''.join(raw.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
    return dict(id=key, path=rel(p), sha256=sha(p), start_line=node.lineno,
                end_line=node.end_lineno, qualified_name=qualname,
                excerpt_sha256=hashlib.sha256(excerpt.encode()).hexdigest(),
                meaning=meaning, evidence='source inspection; no upstream execution')


def main():
    tick = time.monotonic()
    selections = [
        ('converter', 'docling/document_converter.py', 'PdfFormatOption', 'Default pipeline and backend classes.'),
        ('backend', 'docling/backend/docling_parse_backend.py', 'ThreadedDoclingParseDocumentBackend.__init__', 'Guarded parser import; separate parser thread default.'),
        ('pdf_options', 'docling/datamodel/pipeline_options.py', 'PdfPipelineOptions', 'Requested stages and bounded-worker settings.'),
        ('ocr_docs', 'docling/datamodel/pipeline_options.py', 'OcrAutoOptions', 'Descriptive example is not the actual priority algorithm.'),
        ('stage_init', 'docling/pipeline/standard_pdf_pipeline.py', 'StandardPdfPipeline._init_models', 'Stage constructors and enabled flags.'),
        ('ocr_factory_call', 'docling/pipeline/standard_pdf_pipeline.py', 'StandardPdfPipeline._make_ocr_model', 'Only KServe OCR receives the remote-service flag.'),
        ('factory', 'docling/models/factories/base_factory.py', 'BaseFactory.create_instance', 'Select registered class by exact option type.'),
        ('plugins', 'docling/models/factories/base_factory.py', 'BaseFactory.load_from_plugins', 'External plugin filter examines module prefix; not a network sandbox.'),
        ('layout_stage', 'docling/models/stages/layout/layout_object_detection_model.py', 'LayoutObjectDetectionModel.__init__', 'Constructs and initializes configured engine.'),
        ('layout_preset', 'docling/datamodel/stage_model_specs.py', 'OBJECT_DETECTION_LAYOUT_HERON', 'Heron default main revision; ONNX has a different repository.'),
        ('layout_engine', 'docling/models/inference_engines/object_detection/factory.py', 'create_object_detection_engine', 'Local engines are not guarded by enable_remote_services.'),
        ('layout_init', 'docling/models/inference_engines/object_detection/transformers_engine.py', 'TransformersObjectDetectionEngine.initialize', 'Processor, label map, weights, dtype and optional compilation.'),
        ('layout_folder', 'docling/models/inference_engines/common/hf_vision_base.py', 'HfVisionModelMixin._resolve_model_folder', 'Delegates local path or download choice.'),
        ('path_resolution', 'docling/models/inference_engines/vlm/_utils.py', 'resolve_model_artifacts_path', 'No supplied root downloads; supplied root with missing repo folder raises.'),
        ('hf_download', 'docling/models/utils/hf_model_download.py', 'download_hf_model', 'snapshot_download with repo/revision, no local_files_only argument.'),
        ('table_init', 'docling/models/stages/table_structure/table_structure_model.py', 'TableStructureModel.__init__', 'Enabled gate; accurate/fast paths; tm_config and TFPredictor.'),
        ('table_download', 'docling/models/stages/table_structure/table_structure_model.py', 'TableStructureModel.download_models', 'docling-models tag v2.3.0; no file filter in helper.'),
        ('auto_init', 'docling/models/stages/ocr/auto_ocr_model.py', 'OcrAutoModel.__init__', 'Platform/package/language/runtime choices; no-engine warning path.'),
        ('auto_call', 'docling/models/stages/ocr/auto_ocr_model.py', 'OcrAutoModel.__call__', 'Disabled or absent engine yields unchanged page objects.'),
        ('easy_init', 'docling/models/stages/ocr/easyocr_model.py', 'EasyOcrModel.__init__', 'Root suppresses downloads only when explicit model_storage_directory is absent.'),
        ('easy_download', 'docling/models/stages/ocr/easyocr_model.py', 'EasyOcrModel.download_models', 'URLs and filenames come from installed EasyOCR config; cached file existence is not a hash check here.'),
        ('rapid_init', 'docling/models/stages/ocr/rapid_ocr_model.py', 'RapidOcrModel.__init__', 'Local-file checks precede caller rapidocr_params overrides.'),
        ('rapid_download', 'docling/models/stages/ocr/rapid_ocr_model.py', 'RapidOcrModel.download_models', 'Model URLs depend on resolved backend/language/version/model size.'),
        ('accelerator', 'docling/datamodel/accelerator_options.py', 'AcceleratorOptions', 'Device/threads use settings and environment unless supplied.'),
        ('compile_default', 'docling/datamodel/settings.py', 'default_compile_model', 'Settings-derived compilation default.'),
    ]
    anchors = [anchor(*args) for args in selections]
    save('source-anchors.json', anchors)
    defaults = []
    for upstream, classes in [
        ('docling/datamodel/pipeline_options.py', ['PipelineOptions','ConvertPipelineOptions','PaginatedPipelineOptions','PdfPipelineOptions','BaseLayoutOptions','LayoutObjectDetectionOptions','TableStructureOptions','OcrOptions','EasyOcrOptions','RapidOcrOptions']),
        ('docling/datamodel/backend_options.py', ['PdfBackendOptions','ThreadedDoclingParseBackendOptions']),
        ('docling/datamodel/object_detection_engine_options.py', ['TransformersObjectDetectionEngineOptions']),
        ('docling/models/inference_engines/object_detection/base.py', ['BaseObjectDetectionEngineOptions']),
        ('docling/datamodel/accelerator_options.py', ['AcceleratorOptions'])]:
        p = source(upstream)
        for n in ast.parse(p.read_text()).body:
            if isinstance(n, ast.ClassDef) and n.name in classes:
                for a in n.body:
                    if isinstance(a, ast.AnnAssign) and a.value is not None:
                        defaults.append(dict(path=rel(p), sha256=sha(p), class_name=n.name,
                            field=ast.unparse(a.target), expression=ast.unparse(a.value), line=a.lineno,
                            status='upstream expression; not evaluated or adopted'))
    save('default-expressions.json', defaults)
    p = OLD / 'pyproject.toml'; metadata = tomllib.loads(p.read_text())['project']
    extras = metadata['optional-dependencies']; packages = {}
    for label, roots in [('native_text',['convert-core','format-pdf-docling','models-local']),
                         ('english_ocr',['convert-core','format-pdf-docling','models-local','feat-ocr-easyocr'])]:
        seen, pending, deps = set(), list(roots), set(metadata['dependencies'])
        while pending:
            key = pending.pop()
            if key in seen: continue
            seen.add(key)
            for dep in extras[key]:
                match = re.fullmatch(r'docling-slim\[([^]]+)\]', dep)
                if match: pending.extend(match.group(1).split(','))
                else: deps.add(dep)
        packages[label] = dict(requested_extras=roots, visited_extras=sorted(seen),
                              declared_requirements=sorted(deps),
                              exact_lock=None, markers_evaluated=False,
                              import_sufficiency='not checked; eager plugin imports and transitive packages remain open')
    save('dependency-proposals.json', dict(project=metadata['name'], version=metadata['version'],
        source=rel(p), sha256=sha(p), base_count=len(metadata['dependencies']), proposals=packages,
        limitation='Declared extras only. No resolver, installation, transitive metadata or distribution permission.'))
    inputs = {a['path']: a['sha256'] for a in anchors}
    inputs.update({d['path']: d['sha256'] for d in defaults});inputs[rel(p)] = sha(p)
    save('preparation-receipt.json', dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        anchors=len(anchors), default_expressions=len(defaults), inputs=inputs,
        script_sha256=sha(Path(__file__)), wall_seconds=time.monotonic()-tick,
        execution='standard library AST/TOML; no Docling/model imports or runtime'))
    print(json.dumps(dict(anchors=len(anchors), default_expressions=len(defaults),
        declared_dependencies={k:len(v['declared_requirements']) for k,v in packages.items()})))


if __name__ == '__main__': main()
