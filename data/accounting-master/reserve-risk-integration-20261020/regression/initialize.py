"""Run the preserved review interface against the fixed Version 3.45 edition."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
SOURCE=OUT/'reading_inventory.py'
CANDIDATE=ROOT/'docs/design/proposal/manuscript-reserve-risk-20261020'
spec=spec_from_file_location('reading_inventory',SOURCE)
module=module_from_spec(spec);spec.loader.exec_module(module)
module.ROOT=ROOT;module.OUT=OUT;module.BASE=CANDIDATE
module.PDF=CANDIDATE/'accounting-product-proposal.pdf'
module.EXPECTED='92b1ab24970cb301ba96d409edcadd3679fc778917c81e82b1c82da592e3dd0d'
module.LEDGER=OUT/'structure-ledger.json'
if __name__=='__main__':
    if len(sys.argv)==1:sys.argv.append('init')
    module.main()
    if sys.argv[1]=='init':
        ledger=json.loads(module.LEDGER.read_text())
        ledger['nodes'][0]['title']='AccDSL Version 3.45'
        module.write(module.LEDGER,ledger)
