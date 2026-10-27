"""Document inventory and page rendering only; no automatic reading verdicts."""
import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "docs/design/proposal/manuscript-origin-matched-cessation-20261017"
PDF = BASE / "accounting-product-proposal.pdf"
EXPECTED = "efceea6d417fb00108985cd43ca57844258a90eb1b809186be6a1b797c953407"
LEDGER = OUT / "structure-ledger.json"
RANKS = {"part": 0, "chapter": 1, "section": 2, "subsection": 3,
         "subsubsection": 4, "paragraph": 5, "subparagraph": 6}
TOKEN = re.compile(r"\\(?P<heading>part|chapter|section|subsection|subsubsection|paragraph|subparagraph)\*?\s*(?:\[[^\]]*\]\s*)?\{|\\(?:input|include)\s*\{(?P<input>[^}]+)\}|(?P<bracket>\\\[)|(?P<dollars>\$\$)|\\begin\{(?P<math>equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|flalign\*?|displaymath)\}")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")

def relative(path):
    return str(path.relative_to(ROOT))

def source_body(path):
    text = path.read_text()
    text = re.sub(r"(?<!\\)%[^\n]*", lambda m: " " * len(m[0]), text)
    return re.sub(r"\\begin\{(lstlisting|verbatim|Verbatim)\}.*?\\end\{\1\}",
                  lambda m: re.sub(r"[^\n]", " ", m[0]), text, flags=re.S)

def braces(text, start):
    depth = 1
    for index in range(start, len(text)):
        if text[index] in "{}" and (index == 0 or text[index - 1] != "\\"):
            depth += 1 if text[index] == "{" else -1
            if depth == 0:
                return text[start:index], index + 1
    raise ValueError("Unclosed heading braces")

def initialize():
    if LEDGER.exists():
        raise SystemExit("Inventory exists; preserve it and use validate/render")
    assert sha(PDF) == EXPECTED, "Wrong baseline PDF"
    nodes = [{"id": "document", "kind": "document", "parent": None,
              "title": "AccDSL Version3.41", "judgment": None,
              "reading_status": "pending"}]
    stack, counters, visited = [], {}, []

    def expand(path, ancestors=()):
        if path in ancestors:
            raise ValueError("Recursive input")
        visited.append(relative(path))
        text = source_body(path)
        pos = 0
        while match := TOKEN.search(text, pos):
            pos = match.end()
            if match["input"]:
                target = (BASE / match["input"]).with_suffix(".tex")
                if not target.exists():
                    target = (path.parent / match["input"]).with_suffix(".tex")
                if not target.is_relative_to(BASE):
                    raise ValueError("Input escapes protected source tree")
                expand(target, ancestors + (path,))
                continue
            kind = match["heading"] or "equation"
            line = text[:match.start()].count("\n") + 1
            key = (relative(path), kind)
            counters[key] = counters.get(key, 0) + 1
            node_id = f"{path.relative_to(BASE)}:{kind}:{counters[key]}"
            if match["heading"]:
                title, pos = braces(text, pos)
                rank = RANKS[kind]
                while stack and stack[-1][0] >= rank:
                    stack.pop()
                parent = stack[-1][1] if stack else "document"
            else:
                ending = "\\]" if match["bracket"] else "$$" if match["dollars"] else "\\end{" + match["math"] + "}"
                end = text.find(ending, pos)
                if end < 0:
                    raise ValueError(f"Unclosed display in {path}:{line}")
                title = text[match.start():end + len(ending)].strip()
                pos = end + len(ending)
                parent = stack[-1][1] if stack else "document"
            argument = (node_id if match["heading"] and rank <= 2 else
                        next((n for r, n in reversed(stack) if r <= 2), "document"))
            node = {"id": node_id, "kind": kind, "parent": parent,
                    "argument_ancestor": argument, "path": relative(path),
                    "line": line, "title_or_display": title,
                    "reading_status": "pending", "judgment": None}
            if kind == "equation":
                node["exposition_role"] = None
            nodes.append(node)
            if match["heading"]:
                stack.append((rank, node_id))

    expand(BASE / "accounting-product-proposal.tex")
    sources = []
    for path in sorted(BASE.rglob("*")):
        if path.is_file() and path.suffix in (".tex", ".bib", ".ebnf", ".bnf"):
            target = OUT / "protected-baseline" / path.relative_to(BASE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            sources.append({"path": relative(path), "sha256": sha(path),
                            "protected_copy": relative(target)})
    pages = []
    (OUT / "extracted-text").mkdir(exist_ok=True)
    with fitz.open(PDF) as document:
        for index, page in enumerate(document):
            target = OUT / "extracted-text" / f"page-{index + 1:03}.txt"
            target.write_text(page.get_text())
            pages.append({"page": index + 1, "printed_label": page.get_label(),
                          "text_path": relative(target), "text_sha256": sha(target),
                          "render": None, "reading_status": "pending"})
        bookmarks = document.get_toc()
    write(LEDGER, {"created_utc": datetime.now(timezone.utc).isoformat(),
          "baseline_pdf": relative(PDF), "pdf_sha256": EXPECTED,
          "page_count": len(pages), "sources": sources, "nodes": nodes,
          "expanded_inputs": visited, "bookmarks": bookmarks, "pages": pages,
          "ordered_segments": [], "diagnosis_status": "in_progress",
          "independent_reader": "pending", "human_acceptance": "pending"})
    print(f"Protected {len(sources)} sources; inventoried {len(nodes)} nodes and {len(pages)} pages; all reading judgments pending")

def render(start, end):
    ledger = json.loads(LEDGER.read_text())
    assert sha(PDF) == ledger["pdf_sha256"] == EXPECTED
    assert 1 <= start <= end <= ledger["page_count"] and end - start < 6
    target_dir = OUT / "rendered"
    target_dir.mkdir(exist_ok=True)
    with fitz.open(PDF) as document:
        for number in range(start, end + 1):
            row = ledger["pages"][number - 1]
            target = target_dir / f"page-{number:03}.png"
            if row["render"]:
                assert sha(target) == row["render"]["sha256"]
                continue
            assert not target.exists(), "Refusing unrecorded render overwrite"
            page = document[number - 1]
            page.get_pixmap(matrix=fitz.Matrix(110 / 72, 110 / 72), alpha=False).save(target)
            row["render"] = {"path": relative(target), "sha256": sha(target), "dpi": 110}
    write(LEDGER, ledger)
    print(f"Bound normal-resolution renders for physical pages {start}–{end}; reading remains pending")

def validate():
    ledger = json.loads(LEDGER.read_text())
    assert sha(PDF) == ledger["pdf_sha256"] == EXPECTED
    assert len(ledger["pages"]) == ledger["page_count"] == 396
    by_id = {node["id"]: node for node in ledger["nodes"]}
    assert len(by_id) == len(ledger["nodes"]), "Duplicate stable ID"
    for node in ledger["nodes"][1:]:
        assert node["parent"] in by_id
        current = by_id[node["parent"]]
        chain = []
        while current["id"] != "document":
            assert current["id"] not in chain, "Hierarchy cycle"
            chain.append(current["id"])
            current = by_id[current["parent"]]
        if node["kind"] in RANKS:
            assert all(RANKS[by_id[p]["kind"]] < RANKS[node["kind"]] for p in chain)
        expected = (node["id"] if node["kind"] in ("part", "chapter", "section") else
                    next((p for p in chain if by_id[p]["kind"] in ("part", "chapter", "section")), "document"))
        assert node["argument_ancestor"] == expected, "Wrong argument ancestor"
    for row in ledger["sources"]:
        assert sha(ROOT / row["path"]) == row["sha256"]
        assert sha(ROOT / row["protected_copy"]) == row["sha256"]
    for row in ledger["pages"]:
        assert sha(ROOT / row["text_path"]) == row["text_sha256"]
        if row["render"]:
            assert sha(ROOT / row["render"]["path"]) == row["render"]["sha256"]
    previous, exit_state = 0, None
    for filename in ledger["ordered_segments"]:
        if filename in ledger.get("segment_sha256", {}):
            assert sha(ROOT / filename) == ledger["segment_sha256"][filename]
        segment = json.loads((ROOT / filename).read_text())
        start, end = segment["physical_pages"]
        assert start == previous + 1 and start <= end < start + 6
        if exit_state is not None:
            assert segment["entry_state"] == exit_state, "Broken continuous reading chain"
        assert segment["exit_state"].strip() and segment["findings"]
        assert all(ledger["pages"][p - 1]["render"] for p in range(start, end + 1))
        assert all(ledger["pages"][p - 1]["reading_status"] == "author_read" for p in range(start, end + 1))
        previous, exit_state = end, segment["exit_state"]
    assert all(p["reading_status"] == "pending" for p in ledger["pages"][previous:])
    for node in ledger["nodes"]:
        if node["reading_status"] == "author_read":
            assert node["judgment"], "Read node lacks a specific judgment"
            assert node["physical_pages"][1] <= previous
    # Completion is a separate, stricter assertion than an intact page chain.
    if ledger["diagnosis_status"] == "author_diagnosis_complete":
        assert previous == ledger["page_count"]
        authored = {}
        for filename in ledger["ordered_segments"]:
            authored.update(json.loads((ROOT / filename).read_text()).get("node_judgments", {}))
        for supplement in ledger.get("supplemental_judgments", []):
            path = ROOT / supplement["path"]
            assert sha(path) == supplement["sha256"], "Changed supplemental judgments"
            authored.update(json.loads(path.read_text())["node_judgments"])
        required = ("entry_belief", "open_question", "parent_contribution",
                    "belief_update", "exit_question", "removal_verdict",
                    "swap_verdict", "entry_verdict", "exit_verdict",
                    "promise_verdict", "distinct_contribution_verdict")
        equation_fields = ("exposition_role", "symbols_units_domain",
                           "assumptions_timing", "source_and_equality",
                           "interpretation", "transition")
        later_equation_fields = ("exposition_role", "role", "symbols_and_units",
                                 "assumptions_and_domain", "derivation_and_status",
                                 "interpretation_and_transition", "source_and_code_boundary")
        texts = {}
        for node in ledger["nodes"]:
            assert node["reading_status"] == "author_read", node["id"]
            judgment = node["judgment"]
            assert authored.get(node["id"]) == judgment, "Unbound judgment: " + node["id"]
            assert judgment["physical_pages"] == node["physical_pages"]
            for field in required:
                value = judgment.get(field)
                assert isinstance(value, str) and value.strip(), (node["id"], field)
                texts.setdefault(value.strip(), set()).add(node["id"])
            if node["kind"] == "equation":
                equation = judgment.get("equation", {})
                fields = later_equation_fields if "symbols_and_units" in equation else equation_fields
                for field in fields:
                    assert equation.get(field, "").strip(), (node["id"], field)
            if node["parent"]:
                first, last = by_id[node["parent"]]["physical_pages"]
                assert first <= node["physical_pages"][0] <= node["physical_pages"][1] <= last, ("Page containment", node["id"])
        assert not any(len(ids) > 2 for ids in texts.values()), "Repeated judgment across unrelated units"
        assert ledger["independent_reader"] == ledger["human_acceptance"] == "pending"
    print(f"Integrity/hierarchy valid: {len(by_id)} nodes, {len(ledger['sources'])} sources, {ledger['page_count']} bound pages; continuous author reading covers {previous}; acceptance pending")

def record(segment_path):
    """Append one completed ordered reading segment and mark its pages read."""
    ledger = json.loads(LEDGER.read_text())
    assert sha(PDF) == ledger["pdf_sha256"] == EXPECTED
    segment_file = Path(segment_path)
    if not segment_file.is_absolute():
        segment_file = (ROOT / segment_file).resolve()
    if not segment_file.is_relative_to(ROOT):
        raise ValueError("Segment escapes repository")
    segment = json.loads(segment_file.read_text())
    start, end = segment["physical_pages"]
    if not (1 <= start <= end <= ledger["page_count"] and end - start < 6):
        raise ValueError("Segment must contain at most six physical pages")
    rel = str(segment_file.relative_to(ROOT))
    if rel in ledger["ordered_segments"]:
        raise ValueError("Segment already recorded")
    if ledger["ordered_segments"]:
        previous = json.loads((ROOT / ledger["ordered_segments"][-1]).read_text())
        if segment["entry_state"] != previous["exit_state"]:
            raise ValueError("Entry state does not continue the previous segment")
        if start != previous["physical_pages"][1] + 1:
            raise ValueError("Segment is not contiguous")
    elif start != 1:
        raise ValueError("First segment must begin with page 1")
    if not segment.get("exit_state", "").strip() or not segment.get("findings"):
        raise ValueError("Segment needs an exit state and findings")
    for number in range(start, end + 1):
        row = ledger["pages"][number - 1]
        if not row["render"]:
            raise ValueError(f"Page {number} has no bound render")
        if row["reading_status"] not in ("pending", "author_read"):
            raise ValueError(f"Page {number} has an incompatible reading status")
        row["reading_status"] = "author_read"
    for node_id, judgment in segment.get("node_judgments", {}).items():
        matches = [node for node in ledger["nodes"] if node["id"] == node_id]
        if len(matches) != 1:
            raise ValueError(f"Unknown node: {node_id}")
        if not judgment or not (1 <= judgment["physical_pages"][0] <= judgment["physical_pages"][1] <= end):
            raise ValueError(f"Missing judgment or unread pages for {node_id}")
        matches[0]["reading_status"] = "author_read"
        matches[0]["judgment"] = judgment
        matches[0]["physical_pages"] = judgment["physical_pages"]
        if matches[0]["kind"] == "equation":
            matches[0]["exposition_role"] = judgment["equation"]["exposition_role"]
    ledger.setdefault("defects", []).extend(segment.get("defects", []))
    ledger["ordered_segments"].append(rel)
    hashes = ledger.setdefault("segment_sha256", {})
    for filename in ledger["ordered_segments"]:
        if filename not in hashes:
            hashes[filename] = sha(ROOT / filename)
    write(LEDGER, ledger)
    print(f"Recorded ordered reading segment {start}–{end}; author reading covers through {end}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "render", "record", "validate"])
    parser.add_argument("pages", nargs="*", type=int)
    parser.add_argument("--segment-path")
    args = parser.parse_args()
    if args.action == "init":
        initialize()
    elif args.action == "render":
        render(*args.pages)
    elif args.action == "record":
        if not args.segment_path or args.pages:
            raise SystemExit("record requires --segment-path FILE and no page arguments")
        record(args.segment_path)
    else:
        validate()

if __name__ == "__main__":
    main()
