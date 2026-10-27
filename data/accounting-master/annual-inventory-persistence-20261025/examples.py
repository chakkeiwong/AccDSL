from copy import deepcopy
from pathlib import Path
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import annual_inventory_store_v1 as m
s=importlib.util.spec_from_file_location('store_runtime_examples',ROOT/'data/accounting-master/annual-inventory-composition-20261025/examples.py')
inventory=importlib.util.module_from_spec(s);s.loader.exec_module(inventory)
def requests():
    names={'empty','partial','full','residual_carry_and_sale','refreshed_carry','unknown_findings','false_findings','oversale','wrong_method','retained_prefix','stale_measurement'}
    return [deepcopy(row) for row in inventory.cases() if row['case'] in names]
