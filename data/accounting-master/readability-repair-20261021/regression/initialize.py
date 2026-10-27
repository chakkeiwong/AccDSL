"""Run the preserved review interface against the fixed Version 3.46 edition."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
SOURCE=OUT/'reading_inventory.py'
CANDIDATE=ROOT/'docs/design/proposal/manuscript-readability-20261021'
spec=spec_from_file_location('reading_inventory',SOURCE)
module=module_from_spec(spec);spec.loader.exec_module(module)
module.ROOT=ROOT;module.OUT=OUT;module.BASE=CANDIDATE
module.PDF=CANDIDATE/'accounting-product-proposal.pdf'
module.EXPECTED='4a516701b3105ea778807f7143eb4d457f6d18cd439d8fc7172e1d9506cd1be5'
module.LEDGER=OUT/'structure-ledger.json'
if __name__=='__main__':
    if len(sys.argv)==1:sys.argv.append('init')
    module.main()
    if sys.argv[1]=='init':
        ledger=json.loads(module.LEDGER.read_text())
        ledger['nodes'][0]['title']='AccDSL Version 3.46'
        module.write(module.LEDGER,ledger)
