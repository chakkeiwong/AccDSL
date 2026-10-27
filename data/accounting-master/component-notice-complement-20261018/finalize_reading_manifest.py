"""Bind completed author readings; preserve the earlier pending-reading record."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


# These are author dispositions of the inspected texts, not build selections.
# Each range is inclusive and refers to the exact raw text's numbered lines.
READINGS = {
    "abseil.txt": (
        "Apache terms; NOTICE retention is conditional; no general trademark grant.",
        "Covered files, contributor identities, changes and any applicable NOTICE.",
        [(8, 65, "Definitions"), (67, 88, "Copyright and limited patent grants"),
         (90, 129, "Redistribution and conditional NOTICE"),
         (131, 175, "Contributions, trademarks, warranty and liability"),
         (177, 203, "Application appendix")]),
    "agg23.txt": (
        "Copyright in all copies; permission and disclaimer have the stated scope.",
        "Actual files/version and retention destination.", [(1, 14, "Complete notice")]),
    "all_except_musl/llvm-libc.txt": (
        "Apache, limited LLVM exceptions, third-party qualification and legacy NCSA; do not assign every regime to every file.",
        "Actual revision/files; applicable current/legacy regime; file-specific third-party notices.",
        [(1, 206, "Apache body and inspected differences"),
         (208, 222, "Two limited LLVM exceptions"),
         (224, 234, "Third-party file/directory notices"),
         (237, 278, "Legacy NCSA terms")]),
    "android/catapult.txt": (
        "Source/binary retention, named non-endorsement and disclaimer.",
        "Actual Android inclusion/files and notice destination.", [(1, 27, "Complete notice")]),
    "android/cpu_features.txt": (
        "Apache body and separately scoped two-condition BSD ndk_compat text.",
        "Actual included files/subdirectories, changes and any applicable NOTICE.",
        [(1, 203, "Apache body"), (204, 230, "ndk_compat terms")]),
    "android/libunwind.txt": (
        "Apache/LLVM terms plus a legacy NCSA-or-MIT choice; do not require both alternatives.",
        "Actual revision/files/regime and incorporated CREDITS.TXT.",
        [(1, 234, "Apache, LLVM exceptions and third-party qualification"),
         (239, 245, "Legacy licence choice"),
         (249, 289, "NCSA and credits"), (293, 311, "MIT and credits")]),
    "cibw_musl/libgcc_and_libstdc++.txt": (
        "Runtime Exception 3.1 is file- and eligible-compilation-dependent; full GPLv3 remains distinct.",
        "Covered holder notices, runtime versions/files, compiler provenance, changes, distribution form, Corresponding Source and conditional installation information; any actual AGPL combination needs its own text.",
        [(1, 20, "Exception identity and file applicability"),
         (22, 57, "Exception definitions and eligible compilation"),
         (59, 72, "Conditional grant and no weakening of GCC copyleft"),
         (76, 146, "GPLv3 identity and preamble"),
         (148, 227, "Definitions and Corresponding Source"),
         (229, 268, "Basic permissions and anti-circumvention"),
         (270, 318, "Verbatim/modified source and aggregate"),
         (320, 416, "Object code, source provision and installation information"),
         (418, 480, "Additional terms and permissions"),
         (482, 544, "Termination, acceptance and downstream recipients"),
         (546, 613, "Patent provisions"),
         (615, 662, "Conflicts, conditional AGPL combination and versions"),
         (664, 696, "Warranty, liability and interpretation")]),
    "fast_float.txt": (
        "MIT-style retention in copies/substantial portions and disclaimer.",
        "Covered files/version and notice destination.", [(1, 27, "Complete notice")]),
    "icu.txt": (
        "Separate Unicode, historical ICU, dictionary, data and build-file conditions; exceptions do not establish a repackaging's facts.",
        "Actual versions/files/data, incorporated per-file notices and modification/distribution facts; full GPLv2 if that unexcepted regime becomes relevant.",
        [(1, 39, "Unicode V3 copies-or-documentation condition"),
         (43, 84, "Third parties and historical ICU copies-and-documentation condition"),
         (88, 139, "Google dictionary terms and composition"),
         (141, 214, "Libtabe/TaBE, Academia Sinica and Chih-Hao attribution"),
         (217, 290, "IPADIC and ICOT conditions"),
         (294, 332, "Lao dictionary"), (336, 374, "Burmese dictionary"),
         (378, 399, "Time-zone statement and court-order qualification"),
         (403, 430, "Double-conversion"),
         (434, 465, "pkg.m4 GPLv2-or-later and conditional exception"),
         (469, 495, "config.guess GPLv3-or-later and conditional exception"),
         (499, 512, "install-sh notices and name-use condition")]),
    "lcms.txt": (
        "Copyright/permission retention and disclaimer; version label is notice metadata.",
        "Actual included version/files and notice destination.", [(1, 27, "Complete notice")]),
    "libopenjpeg.txt": (
        "Source/binary retention; no inferred third-party/contributor/patent grant.",
        "Actual files/version, third-party rights and notice destination.",
        [(1, 5, "Express third-party and patent boundary"), (7, 32, "Retention and disclaimer")]),
    "libtiff.txt": (
        "Notices in software/related documentation; advertising/publicity name-use condition.",
        "Actual files, changes, documentation and retention destination.", [(1, 21, "Complete notice")]),
    "pdfium-binaries.txt": (
        "MIT-style text plus an explicit third-party licences reference; no payload identity.",
        "Actual binary payload and all incorporated licences.", [(1, 9, "Complete notice and licences reference")]),
    "pdfium-binaries_musl/musl.txt": (
        "MIT author notice, third-party/file-specific qualifications and limited header/crt attribution exception.",
        "Actual version/files, TRE/math/ARM/AArch64/DES/Blowfish/smoothsort notices, port file/authorship mapping and listed-path exception applicability.",
        [(1, 109, "General notice and authors"), (111, 146, "Third-party/per-file sources"),
         (148, 169, "Standard MIT ports and original-file authorship"),
         (171, 186, "Limited header/crt exception"), (188, 193, "Clarification")]),
    "pdfium.txt": (
        "Preserve both BSD-style prefix and Apache body; file-specific assignment remains unknown.",
        "Actual revision/covered files, applicable regimes, changes, NOTICE and third-party terms.",
        [(1, 27, "BSD-style prefix"), (29, 230, "Byte-equal Apache body")]),
    "v8_xfa/bigint.txt": (
        "Author's original-work copyright waiver/public-domain and warranty statement; context is not universal rights clearance.",
        "Actual code identity and third-party additions.",
        [(1, 64, "Technical context"), (65, 71, "Original-work waiver and warranty")]),
    "v8_xfa/fdlibm.txt": (
        "Sun permission requires the notice to be preserved.",
        "Actual included files/version and notice destination.", [(1, 6, "Complete notice")]),
    "v8_xfa/fp16.txt": (
        "MIT-style retention and disclaimer.",
        "Actual included files/version and notices.", [(1, 12, "Complete notice")]),
    "v8_xfa/highway.txt": (
        "Apache body with inspected differences; inclusion is not proved by the directory name.",
        "Actual files/flags/version, changes and any NOTICE.", [(1, 201, "Complete Apache text")]),
    "v8_xfa/inspector_protocol.txt": (
        "Source/binary retention, Google/contributor non-endorsement and disclaimer.",
        "Actual enabled components/files and notices.", [(1, 27, "Complete notice")]),
    "v8_xfa/simdutf.txt": (
        "MIT-style retention and disclaimer.",
        "Actual included files/version and notices.", [(1, 18, "Complete notice")]),
    "v8_xfa/strongtalk.txt": (
        "Source/binary retention, Sun/contributor non-endorsement and disclaimer.",
        "Actual included files/version and notices.", [(1, 29, "Complete notice")]),
    "v8_xfa/v8.txt": (
        "Source/binary retention, Google/contributor non-endorsement and disclaimer.",
        "Actual V8 flags/version/files and notices.", [(1, 26, "Complete notice")]),
}


def main():
    path = OUT / "source-manifest.json"
    raw = path.read_bytes()
    manifest = json.loads(raw)
    assert manifest["status"] == "extracted_reading_pending", "Already finalised; do not rerun."
    assert not manifest["anchors"]
    assert all(r["reading_status"] == "pending" for r in manifest["selected_texts"])
    prefix = "pypdfium2-5.9.0/BUILD_LICENSES/"
    assert {r["archive_member"].removeprefix(prefix) for r in manifest["selected_texts"]} == READINGS.keys()
    for row in manifest["protected_inputs"] + [manifest["archive"], manifest["plan"]]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
    comparison = json.loads((OUT / "apache-comparison.json").read_text())
    compared = {r["target"] for r in comparison["files"]}
    anchors = []
    for row in manifest["selected_texts"]:
        source = ROOT / row["path"]
        assert sha(source) == row["sha256"]
        lines = source.read_bytes().splitlines(keepends=True)
        assert len(lines) == row["lines"]
        finding, missing, spans = READINGS[row["archive_member"].removeprefix(prefix)]
        row.update(reading_status="complete_author_inspection",
                   reading_method=("reference_comparison_and_all_differences" if row["path"] in compared else "direct_complete_text"),
                   inspected_lines=[[1, len(lines)]], conditional_disposition=finding,
                   missing_applicability_facts=missing)
        for start, end, purpose in spans:
            assert 1 <= start <= end <= len(lines)
            anchors.append({"path": row["path"], "start_line": start, "end_line": end,
                            "sha256": hashlib.sha256(b"".join(lines[start - 1:end])).hexdigest(),
                            "purpose": purpose})
    snapshot = OUT / "source-manifest-extracted-reading-pending.json"
    with snapshot.open("xb") as handle:
        handle.write(raw)
    manifest.update(
        status="complete_author_reading_actual_build_pending",
        completed_binding_utc=datetime.now(timezone.utc).isoformat(),
        pending_reading_snapshot=ref(snapshot), anchors=anchors,
        author_observation_record=ref(OUT / "source-reading.md"),
        artifacts=[ref(OUT / name) for name in ["source-reading.md", "result.md", "extraction-manifest.json",
                   "apache-comparison.json", "extract_notices.py", "compare_apache_bodies.py",
                   "finalize_reading_manifest.py", "verify_bindings.py"]],
        scope="Complete author reading of this retained archive's 23-text complement; all 28 archive notices accounted for with earlier five. Actual inclusion, incorporated file notices, compatibility and rights decisions remain pending.")
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"author_readings": len(READINGS), "comparison_methods": len(compared),
                      "clause_anchors": len(anchors), "protected_inputs": len(manifest["protected_inputs"])}))


if __name__ == "__main__":
    main()
