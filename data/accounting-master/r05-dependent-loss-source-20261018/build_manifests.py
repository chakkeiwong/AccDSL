"""One-time documentary manifests from retained bytes and exact tool records."""
import hashlib
import json
import re
import shlex
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def write_new(name, data):
    if (UNIT / name).exists():
        assert json.loads((UNIT / name).read_text()) == data, name
        return
    with (UNIT / name).open("x") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def leaves(value):
    if isinstance(value, dict):
        for v in value.values():
            yield from leaves(v)
    elif isinstance(value, list):
        for v in value:
            yield from leaves(v)
    elif isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError:
            yield value
        else:
            yield from leaves(parsed)


def main():
    raw = json.loads((UNIT / "acquisition-tool-calls.json").read_text())
    routes = {}
    for call in raw["calls"]:
        s = call["exact_tool_input"]
        for name, url in re.findall(r'\{id:"([^"]+)",url:"([^"]+)"\}', s):
            assert name not in routes
            routes[name] = {"url": url, "call_id": call["call_id"],
                            "timestamp": call["timestamp"]}
        if not s.startswith("const base=") and 'cmd:"curl ' in s:
            start = s.index('cmd:') + 4
            command, _ = json.JSONDecoder().raw_decode(s[start:])
            name = re.search(r'/sources/([^ /]+)\.headers', command).group(1)
            url = shlex.split(command)[-1]
            routes[name] = {"url": url, "call_id": call["call_id"],
                            "timestamp": call["timestamp"], "exact_command": command}
    transfers = []
    for output in raw["outputs"] + raw["poll_outputs"]:
        for s in leaves(output["output"]):
            for match in re.finditer(
                r'http=(\d+) bytes=(\d+) seconds=([\d.]+)(?: url=([^\s]+))?', s
            ):
                code, size, seconds, url = match.groups()
                transfers.append({"http": int(code), "bytes": int(size),
                                  "seconds": float(seconds), "url": url,
                                  "output_call_id": output["call_id"]})
    entries = {}
    for path in sorted((UNIT / "sources").rglob("*")):
        if path.is_file():
            entries[str(path.relative_to(ROOT))] = {
                "sha256": sha(path), "bytes": path.stat().st_size}
    write_new("source-manifest.json", {
        "scope": "all retained raw acquisition, extracted code, text and rendered inspection files",
        "entries": entries})
    acquisitions = []
    for header in sorted((UNIT / "sources").glob("*.headers")):
        name = header.stem
        route = routes[name]
        body = header.with_suffix(".body")
        codes = [int(x) for x in re.findall(
            r'^HTTP/\S+\s+(\d+).*$', header.read_text(errors="replace"), re.M)]
        size = body.stat().st_size if body.exists() else None
        matches = [t for t in transfers if t["bytes"] == size and
                   (t["url"] == route["url"] or
                    (t["url"] is None and name == "forecomp-cran-archive"))]
        identities = {(m["http"], m["bytes"], m["seconds"], m["url"]) for m in matches}
        assert len(identities) == 1, (name, len(matches))
        transfer = {k: v for k, v in matches[0].items() if k != "output_call_id"}
        transfer["output_call_ids"] = sorted({m["output_call_id"] for m in matches})
        roles = {
            "forecomp-arxiv-v1": "matching primary text, technically inspected",
            "forecomp-cran-archive": "matching package mirror, selected code statically inspected",
            "dm2015-arxiv-route2": "REJECTED: unrelated incompressible-flow paper",
            "dm-title-discovery": "unusable Google discovery response",
            "hln-title-discovery": "unusable Google discovery response",
        }
        acquisitions.append({"id": name, **route, "http_chain": codes,
                             "header": str(header.relative_to(ROOT)),
                             "body": str(body.relative_to(ROOT)) if body.exists() else None,
                             "disposition": roles.get(name, "metadata/discovery or blocked route; no technical support"),
                             "transfer": transfer})
    assert len(acquisitions) == len(routes)
    write_new("acquisition-manifest.json", {
        "access_date": "2026-10-18", "trusted_network_execution": True,
        "exact_tool_calls": "acquisition-tool-calls.json",
        "command_note": "Batch tool inputs retain exact job URL/id and curl command construction; direct curl strings are also copied below.",
        "acquisitions": acquisitions,
        "transfer_seconds_sum": sum(a["transfer"]["seconds"] for a in acquisitions),
        "interpretation": "Sum of individual curl transfer wall times, not elapsed authoring time or a performance benchmark."})
    print(json.dumps({"source_files": len(entries), "acquisitions": len(acquisitions),
                      "exact_network_tool_calls": len(raw["calls"]),
                      "poll_calls": len(raw["poll_calls"])}))


if __name__ == "__main__":
    main()
