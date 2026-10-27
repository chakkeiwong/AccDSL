"""Create this unit's local completion helper once from the checked prior pattern."""
from pathlib import Path

out = Path(__file__).resolve().parent
prior = out.parent / "native-loader-source-20261018/complete.py"
text = prior.read_text().replace("native-loader-source-20261018", "native-occurrence-bytes-20261018")
text = text.replace("native-loader-source-supplement.json", "native-occurrence-bytes-supplement.json")
text = text.replace("controls-native-loader-before", "controls-native-occurrence-before")
text = text.replace("R06 pinned loader/parser/mapping source delta: ten retrievals, thirty inspected spans, 100 checks; no upstream execution",
                    "R06 twelve actual native facts, four contexts, two units, eighteen byte slices, 153 checks and nineteen rejected corruptions; no upstream execution")
with (out / "complete.py").open("x") as handle:
    handle.write(text)
