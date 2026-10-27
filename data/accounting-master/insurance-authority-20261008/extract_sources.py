"""Extract the retained ASBE text without confusing article references with headings."""
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = OUT / "sources/asbe25-http.body"


def chinese_number(text):
    digits = dict(zip("零一二三四五六七八九", range(10)))
    result = current = 0
    for char in text:
        if char in digits:
            current = digits[char]
        else:
            result += (current or 1) * {"十": 10, "百": 100}[char]
            current = 0
    return result + current


soup = BeautifulSoup(SOURCE.read_bytes(), "html.parser")
body = soup.select_one(".TRS_Editor")
assert body is not None
articles = {}
current = None
for node in body.select("p"):
    text = re.sub(r"\s+", "", node.get_text("", strip=True))
    if re.match(r"^第[零一二三四五六七八九十百]+[章节]", text):
        continue
    match = re.match(r"^第([零一二三四五六七八九十百]+)条", text)
    if match:
        number = chinese_number(match[1])
        assert number == len(articles) + 1, (number, len(articles))
        current = str(number)
        articles[current] = {"heading": match[0], "paragraphs": []}
    if text and current:
        articles[current]["paragraphs"].append(text)
assert list(articles) == [str(n) for n in range(1, 121)]
for article in articles.values():
    article["text"] = "\n".join(article["paragraphs"])

extraction = {
    "source": str(SOURCE.relative_to(ROOT)),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "extractor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "normalization": "HTML .TRS_Editor p elements; remove whitespace within each paragraph; preserve paragraph boundaries; exclude chapter/section headings; require article headings 1 through 120 in order",
    "articles": articles,
    "inspection_scope": "Extraction covers all headings; technical inspection is limited to the articles named in source-note.md and source-claim-supplement.json",
}
(OUT / "source-extract.json").write_text(json.dumps(extraction, ensure_ascii=False, indent=2) + "\n")
(OUT / "sources/asbe25-articles.txt").write_text("\n\n".join(a["text"] for a in articles.values()) + "\n")
print(json.dumps({"articles": len(articles), "source_sha256": extraction["source_sha256"]}))
