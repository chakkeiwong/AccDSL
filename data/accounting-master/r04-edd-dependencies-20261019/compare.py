"""Read-only documentary/AST comparison; never import acquired source."""
import ast
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
SOURCES = UNIT / "sources"


def check():
    assertions = 0

    def require(condition, label):
        nonlocal assertions
        assert condition, label
        assertions += 1

    def load(name):
        return json.loads((UNIT / name).read_text())

    def bound(item):
        return hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]

    ledger = load("source-ledger.json")
    require(len(ledger["acquisitions"]) == 6, "request budget")
    for row in ledger["acquisitions"]:
        require(bound(row["body"]) and bound(row["headers"]), "acquisition hashes")
        require((ROOT / row["body"]["path"]).stat().st_size == row["bytes"], "body bytes")
        require(row["status"] == 200 and row["redirects"] == 0 and row["effective_url"] == row["url"], "recorded curl receipt")
        statuses = re.findall(r"^HTTP/\S+ (\d+)", (ROOT / row["headers"]["path"]).read_text(), re.M)
        require(statuses and statuses[-1] == "200", "terminal response header")
    for row in ledger["passages"]:
        require(row["needle"] in (ROOT / row["path"]).read_text().splitlines()[row["first_line"] - 1], row["id"])
    for row in ledger["prior_bindings"] + ledger["rendered_read"]["images"]:
        require(bound(row), "prior/rendered binding")
    link = ledger["official_supplement_link"]
    index = (SOURCES / "05-index.body").read_text()
    require(index.index(link["relative_href"]) == link["character_offset"], "official link location")
    require("Image-based table recognition: data, model, and evaluation" in link["entry_excerpt"], "matching index title")
    require("Xu Zhong, Elaheh ShafieiBavani, Antonio Jimeno Yepes" in link["entry_excerpt"], "matching authors")
    for row in ledger["read_boundaries"]:
        require(row["lines"] == [1, len((ROOT / row["file"]).read_text().splitlines())], "exact reading boundary")
    require(ledger["acquired_code_executed"] is False, "no upstream execution")

    texts = {name: (SOURCES / name).read_text() for name in ("01-datasets.py", "02-utils.py", "03-metric.py")}
    trees = {name: ast.parse(text) for name, text in texts.items()}

    def definition(tree, name):
        return next(node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == name)

    metric = trees["03-metric.py"]
    prior_metric = ast.parse((ROOT / "data/accounting-master/r04-pubtabnet-20261019/sources/05-metric.py").read_text())
    same_config = ast.dump(definition(metric, "CustomConfig"), include_attributes=False) == ast.dump(definition(prior_metric, "CustomConfig"), include_attributes=False)
    require(same_config, "CustomConfig AST correspondence")
    require(texts["03-metric.py"] != (ROOT / "data/accounting-master/r04-pubtabnet-20261019/sources/05-metric.py").read_text(), "whole metrics differ")
    require("global __tokens__" in texts["03-metric.py"] and "self.__tokens__" not in texts["03-metric.py"], "global metric token accumulator")
    require("HTMLParser" not in texts["03-metric.py"] and "ignore_nodes" not in texts["03-metric.py"], "wrapper lacks earlier explicit parser settings/option")
    require('len(pred.xpath(".//*"))' in texts["03-metric.py"] and 'len(true.xpath(".//*"))' in texts["03-metric.py"], "raw descendant denominator")
    relation = definition(metric, "relation_metric")
    linspace = next(node for node in ast.walk(relation) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "linspace")
    require([ast.literal_eval(node) for node in linspace.args] == [0.6, 0.95, 8], "code adjacency thresholds")
    require("(0.5, 0.6, · · · , 0.9)" in (SOURCES / "06-supplement.txt").read_text(), "printed adjacency thresholds")
    require("zip(to_insert[::-1], cells[::-1])" in texts["03-metric.py"], "HTML reconstruction uses bounded zip")

    loader = definition(trees["01-datasets.py"], "TagCellDataset")
    initializer = definition(loader, "__init__")
    getitem = definition(loader, "__getitem__")
    iterator = definition(loader, "__next__")
    require(".hdf5" in ast.unparse(initializer), "loader hdf5 suffix")
    prep = (ROOT / "data/accounting-master/r04-edd-edition-20261019/sources/05-preparation.py").read_text()
    require("base_filename + '.hdf5'" in prep, "preparation hdf5 suffix")
    require("np.array(range(lack))" in ast.unparse(iterator), "raw index padding")
    require("self.imgsizes" in ast.unparse(getitem) and "self.imgsizes" not in ast.unparse(initializer), "getitem undefined initializer field")
    require("self.imgs[sample] / 255.0" in ast.unparse(iterator), "iterator scales image values")
    selected_model = (ROOT / "data/accounting-master/r04-edd-edition-20261019/sources/03-models.py").read_text().splitlines()[2317:2320]
    require("train_loader.shuffle()" in selected_model[0] and "enumerate(train_loader)" in selected_model[1], "selected training uses iterator")
    clip = definition(trees["02-utils.py"], "clip_gradient")
    require(".clamp_(-grad_clip, grad_clip)" in ast.unparse(clip), "elementwise clipping")
    checkpoint = definition(trees["02-utils.py"], "save_checkpoint_dual")
    state = next(node.value for node in checkpoint.body if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict))
    keys = [ast.literal_eval(key) for key in state.keys]
    require(keys == ["epoch", "encoder", "decoder", "encoder_optimizer", "tag_decoder_optimizer", "cell_decoder_optimizer", "cell_bbox_regressor_optimizer"], "checkpoint fields without RNG")
    requirements = [line for line in (SOURCES / "04-requirements.txt").read_text().splitlines() if line.strip()]
    require(len(requirements) == 9 and sum(">=" in line for line in requirements) == 4 and not any("==" in line for line in requirements), "unpinned environment")
    require(not any(line.lower().startswith("numpy") for line in requirements), "NumPy not directly declared; transitive status unknown")

    # Exact rational idealization of decimal endpoints, not IEEE NumPy output.
    supplement_grid = [str(Fraction(i, 10)) for i in range(5, 10)]
    default_grid = [str(Fraction(3, 5) + i * Fraction(1, 20)) for i in range(8)]

    def validate_witnesses(witnesses):
        assert witnesses["thresholds"] == {"supplement": supplement_grid, "code_default": default_grid}
        assert supplement_grid != default_grid
        assert len(witnesses["cases"]) == 2
        for case in witnesses["cases"]:
            n, batch, permutation = case["n"], case["batch_size"], case["permutation"]
            assert n > 0 and batch > 0 and sorted(permutation) == list(range(n))
            batches, pointer, padding = [], 0, []
            while pointer < n:
                step = min(batch, n - pointer)
                padding = list(range(batch - step))
                batches.append(permutation[pointer:pointer + step] + padding)
                pointer += step
            assert batches == case["batches"]
            assert padding == case["padding"]
            assert permutation[:len(padding)] == case["shuffled_prefix"]
            assert sorted({i for row in batches for i in row if i < 0 or i >= n}) == case["invalid_indices"]

    witnesses = load("witnesses.json")
    validate_witnesses(witnesses)
    require(True, "two source-derived finite index cases")
    rejected = 0
    for change in range(6):
        bad = deepcopy(witnesses)
        if change == 0:
            bad["cases"][0]["batches"][-1] = [0, 4, 3, 2]
        elif change == 1:
            bad["cases"][1]["invalid_indices"] = []
        elif change == 2:
            bad["cases"][0]["n"] = 6
        elif change == 3:
            bad["cases"][0]["permutation"][0] = 0
        elif change == 4:
            bad["thresholds"]["supplement"] = default_grid
        else:
            bad["thresholds"]["code_default"] = supplement_grid
        try:
            validate_witnesses(bad)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("invalid finite control accepted")
    require(rejected == 6, "six rejected altered illustrations")
    ledger_names = ["source-support", "citation-venue", "backward-snowball", "forward-snowball", "claim-support", "omission-risk"]
    for name in ledger_names:
        require(bool(load(name + "-ledger.json")), "additive literature ledger")
    return {"acquisitions": 6, "passage_anchors": len(ledger["passages"]), "assertions": assertions, "metric_config_ast_equal": same_config, "whole_metric_equivalence_admitted": False, "finite_index_cases": 2, "rejected_altered_controls": rejected, "literature_ledgers": 6, "runtime_admitted": False, "empirical_ranking_admitted": False, "manuscript_changed": False}
