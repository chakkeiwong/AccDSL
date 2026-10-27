"""Source-only integrity/claim-anchor checks; no upstream import or execution."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = OUT / "sources"
COMMIT = "01f6a4656c2c6551d2f05f31c9d74366d133ee7e"
UPSTREAM = ROOT / "docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/arelle"
PRIOR = ROOT / "data/accounting-master/taxonomy-reuse-20261007"
INTEGRATION = ROOT / "data/accounting-master/early-conversion-integration-20261018"
PLAN = ROOT / "docs/plans/accounting-native-loader-source-20261018.md"
DELTA = ROOT / "docs/design/proposal/architecture/native-loader-source-delta-v1.md"
MODULES = [
    ("FileSource", "arelle/FileSource.py"), ("ModelObjectFactory", "arelle/ModelObjectFactory.py"),
    ("UrlUtil", "arelle/UrlUtil.py"), ("PackageManager", "arelle/PackageManager.py"),
    ("PluginManager", "arelle/PluginManager.py"), ("package_manager", "arelle/packages/_package_manager.py"),
    ("plugin_manager", "arelle/plugin_system/_plugin_manager.py"),
    ("package_registry", "arelle/packages/package_registry.py"),
    ("plugin_provider", "arelle/plugin_system/plugin_provider.py"), ("DisclosureSystem", "arelle/DisclosureSystem.py")]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())}


def load(path):
    return json.loads(path.read_bytes())


def require(value, code):
    if not value:
        raise ValueError(code)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    names = ["source-manifest.json", "source-anchors.json", "checks.json", "run-manifest.json"]
    if args.record:
        for name in names:
            require(not (OUT / name).exists(), "OUTPUT_EXISTS:" + name)
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    checks, sources, trees = [], [], {}
    def check(label, condition):
        require(condition, label)
        checks.append(label)
    for i, (name, upstream_path) in enumerate(MODULES):
        raw_path, headers_path, response_path = SOURCE / (name + ".py"), SOURCE / (name + ".headers"), SOURCE / ("fetch-result-" + str(i) + ".json")
        response = load(response_path)
        curl = json.loads(response["output"])
        url = "https://raw.githubusercontent.com/Arelle/Arelle/" + COMMIT + "/" + upstream_path
        check("fetch_success:" + name, response["exit_code"] == curl["exitcode"] == 0 and curl["http_code"] == 200)
        check("exact_commit_url:" + name, curl["url"] == curl["url_effective"] == url and curl["num_redirects"] == 0)
        raw = raw_path.read_bytes()
        check("response_size:" + name, len(raw) == curl["size_download"] and 0 < len(raw) <= 2000000)
        check("recorded_target:" + name, curl["filename_effective"] == str(raw_path.relative_to(ROOT)))
        check("headers_preserved:" + name, b"200" in headers_path.read_bytes().splitlines()[0])
        text = raw.decode("utf-8")
        trees[name] = ast.parse(text)
        check("python_source_syntax_only:" + name, bool(trees[name].body))
        command = ["curl", "--silent", "--show-error", "--location", "--max-time", "45", "--max-filesize", "2000000",
                   "--dump-header", str(headers_path.relative_to(ROOT)), "--output", str(raw_path.relative_to(ROOT)),
                   "--write-out", "%{json}", url]
        sources.append({"upstream_path": upstream_path, "commit": COMMIT, "command_arguments": command,
                        "permission_context": "trusted curl with existing approved prefix",
                        "body": binding(raw_path), "headers": binding(headers_path), "transport_result": binding(response_path),
                        "bytes": len(raw), "lines": len(text.splitlines()), "http_status": 200,
                        "curl_wall_seconds": curl["time_total"], "runtime_imported": False})
    specs = [
        (SOURCE / "FileSource.py", 494, 511, "source-first-prefix-plus-disclosure"),
        (SOURCE / "FileSource.py", 544, 588, "archive-bytes-to-text"),
        (SOURCE / "FileSource.py", 652, 662, "file-hook"),
        (SOURCE / "FileSource.py", 856, 878, "hook-and-member-separator"),
        (SOURCE / "FileSource.py", 880, 929, "second-mapping-and-server-cache-open"),
        (SOURCE / "FileSource.py", 931, 980, "decode-and-declaration"),
        (SOURCE / "ModelObjectFactory.py", 44, 62, "explicit-parser-options"),
        (SOURCE / "ModelObjectFactory.py", 171, 202, "parse-time-schema-discovery"),
        (SOURCE / "UrlUtil.py", 58, 62, "fragment-decode"),
        (SOURCE / "PackageManager.py", 10, 30, "package-wrapper"),
        (SOURCE / "PluginManager.py", 12, 35, "plugin-wrapper"),
        (SOURCE / "package_manager.py", 381, 404, "package-config-load-reset"),
        (SOURCE / "package_manager.py", 447, 448, "package-close"),
        (SOURCE / "package_manager.py", 675, 729, "package-remapping"),
        (SOURCE / "plugin_manager.py", 57, 100, "plugin-config-load-reset"),
        (SOURCE / "plugin_manager.py", 138, 148, "plugin-close"),
        (SOURCE / "plugin_manager.py", 675, 698, "enabled-hooks"),
        (SOURCE / "package_registry.py", 29, 52, "registry-forwarding"),
        (SOURCE / "plugin_provider.py", 39, 46, "provider-forwarding"),
        (SOURCE / "DisclosureSystem.py", 493, 529, "disclosure-map-and-xinclude"),
        (UPSTREAM / "arelle__XmlUtil.py", 29, 29, "declaration-pattern"),
        (UPSTREAM / "arelle__XmlUtil.py", 146, 170, "encoding-branch-order"),
        (UPSTREAM / "arelle__ModelDocument.py", 185, 208, "parser-stream-and-errors"),
        (UPSTREAM / "arelle__ModelDocument.py", 457, 469, "schemalocated-load"),
        (UPSTREAM / "arelle__api__Session.py", 141, 161, "session-new-controller"),
        (PRIOR / "sources/arelle-cntlr-trusted.body", 280, 322, "persistent-versus-gui-config"),
        (PRIOR / "sources/arelle-cntlrcmdline-trusted.body", 1471, 1488, "preload-construction"),
        (PRIOR / "sources/arelle-cntlrcmdline-trusted.body", 1599, 1611, "non-gui-controller"),
        (PRIOR / "sources/arelle-cntlrcmdline-trusted.body", 1718, 1730, "empty-plugin-option"),
        (PRIOR / "sources/arelle-cntlrcmdline-trusted.body", 1785, 1792, "empty-package-option")]
    anchors = []
    for path, first, last, role in specs:
        lines = path.read_bytes().splitlines(keepends=True)
        check("anchor_range:" + role, 1 <= first <= last <= len(lines))
        excerpt = b"".join(lines[first - 1:last])
        anchors.append({**binding(path), "start_line": first, "end_line": last, "purpose": role,
                        "excerpt_utf8": excerpt.decode(), "excerpt_sha256": sha(excerpt)})
    function = next(n for n in trees["ModelObjectFactory"].body if isinstance(n, ast.FunctionDef) and n.name == "parser")
    calls = [n for n in ast.walk(function) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "XMLParser"]
    options = {k.arg: k.value.value for k in calls[0].keywords if isinstance(k.value, ast.Constant)}
    check("explicit_parser_flags", len(calls) == 1 and options == {"recover": True, "huge_tree": True, "resolve_entities": False})
    check("no_explicit_network_option_in_constructor", all(k.arg != "no_network" for k in calls[0].keywords))
    xmlutil = (UPSTREAM / "arelle__XmlUtil.py").read_text()
    encoding = next(n for n in ast.parse(xmlutil).body if isinstance(n, ast.FunctionDef) and n.name == "encoding")
    starts = sorted((n.lineno, n.args[0].value) for n in ast.walk(encoding) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "startswith" and n.args and isinstance(n.args[0], ast.Constant))
    short = next(line for line, value in starts if value == bytes([255, 254]))
    long = next(line for line, value in starts if value == bytes([255, 254, 0, 0]))
    check("encoding_prefix_order_source_only", short < long)
    register_path = UPSTREAM.parents[2] / "source-register.json"
    register = load(register_path)
    prior_paths = {path for path, _, _, _ in specs if path.parent == UPSTREAM}
    register_hits = []
    for row in register["sources"]:
        path = register_path.parent / row["path"]
        if path in prior_paths:
            check("prior_source_pin:" + path.name, row["commit"] == COMMIT and sha(path.read_bytes()) == row["sha256"])
            register_hits.append(path)
    check("prior_pin_coverage", set(register_hits) == prior_paths)
    receipt_paths = []
    for name in ["arelle-cntlr-trusted", "arelle-cntlrcmdline-trusted"]:
        receipt_path = PRIOR / "sources" / (name + ".receipt.json")
        receipt = load(receipt_path)
        check("controller_source_pin:" + name, receipt["http_status"] == 200 and receipt["request"]["commit"] == COMMIT and sha((ROOT / receipt["body"]).read_bytes()) == receipt["sha256"])
        receipt_paths.append(receipt_path)
    duties = load(ROOT / "data/accounting-master/native-offline-resolution-20261018/dependency-prerequisites.json")
    check("twelve_runtime_duties_remain", len(duties["pending"]) == 12 and all(r["value"] is None for r in duties["pending"]) and duties["runtime_admission"] == "held")
    evidence = {"all_passed": True, "checks": checks, "check_count": len(checks), "retrieved_sources": len(sources),
                "source_spans": len(anchors), "execution_class": "static_source_inspection_and_binding_only",
                "upstream_imported_or_executed": False, "runtime_duties_unresolved": 12}
    values = {"source-manifest.json": sources, "source-anchors.json": anchors, "checks.json": evidence}
    if args.record:
        protected = [path for path, _, _, _ in specs if path.parent != SOURCE] + receipt_paths + [register_path]
        protected += [ROOT / "data/accounting-master/native-offline-resolution-20261018" / name for name in ["run-manifest.json", "completion.json", "dependency-prerequisites.json"]]
        protected += [INTEGRATION / name for name in ["assessment-successor.json", "integration-bindings.json", "operation-successor.json", "native-offline-resolution-supplement.json", "native-xbrl-translation-supplement.json"]]
        protected += [ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf",
                      ROOT / "docs/design/proposal/architecture/native-offline-resolution-proposed-v1.md"]
        for name, value in values.items():
            with (OUT / name).open("x") as handle:
                json.dump(value, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
        manifest = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "wall_seconds": time.monotonic() - tick,
                    "command": "python3 data/accounting-master/native-loader-source-20261018/check.py --record",
                    "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                    "index_sha256": sha((ROOT / ".git/index").read_bytes()),
                    "tracked_dirty": subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True).splitlines(),
                    "environment": {"executable": sys.executable, "python": platform.python_version(), "conda_env": os.environ.get("CONDA_DEFAULT_ENV"),
                                    "cpu_gpu_status": "CPU standard-library AST/file/hash checks only; no upstream/numerical framework import or GPU use"},
                    "seeds": "N/A", "data_version": COMMIT, "plan": binding(PLAN), "delta": binding(DELTA), "verifier": binding(Path(__file__).resolve()),
                    "protected_inputs": [binding(p) for p in sorted(set(protected))], "outputs": [binding(OUT / n) for n in values],
                    "result_path": str((OUT / "result.md").relative_to(ROOT)),
                    "time_limits": "Retrieval times are in saved curl responses; source-reading time was not measured"}
        with (OUT / "run-manifest.json").open("x") as handle:
            json.dump(manifest, handle, indent=2)
            handle.write("\n")
    else:
        for name, value in values.items():
            require(load(OUT / name) == value, "REPLAY:" + name)
        manifest = load(OUT / "run-manifest.json")
        for row in manifest["protected_inputs"] + manifest["outputs"] + [manifest[k] for k in ["plan", "delta", "verifier"]]:
            require(binding(ROOT / row["path"]) == row, "BINDING:" + row["path"])
        require(sha((ROOT / ".git/index").read_bytes()) == manifest["index_sha256"], "INDEX_CHANGED")
        require(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True).splitlines() == manifest["tracked_dirty"], "DIRTY_ENTRIES_CHANGED")
    print(json.dumps({"status": "recorded" if args.record else "read-only replay passed", "checks": len(checks),
                      "sources": len(sources), "spans": len(anchors), "runtime_executed": False}))


if __name__ == "__main__":
    main()
