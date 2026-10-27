"""Initialize the established scholarly inventory against exact Version 3.44."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "data/accounting-master/continuous-reading-20261017/reading_inventory.py"
CANDIDATE = ROOT / "docs/design/proposal/manuscript-early-conversion-20261018"
OUT = ROOT / "data/accounting-master/early-conversion-integration-20261018/regression"
spec = spec_from_file_location("reading_inventory", SOURCE)
module = module_from_spec(spec)
spec.loader.exec_module(module)
module.OUT = OUT
module.BASE = CANDIDATE
module.PDF = CANDIDATE / "accounting-product-proposal.pdf"
module.EXPECTED = hashlib.sha256(module.PDF.read_bytes()).hexdigest()
module.LEDGER = OUT / "structure-ledger.json"
module.initialize()
