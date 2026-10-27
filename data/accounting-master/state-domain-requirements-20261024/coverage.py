"""Explicit disposition for every native invariant need call; not proof by count."""
import ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'company-return-execution-20261024/native_returns.py'
DISPOSITIONS={
 'closed state fields':('residual_structure',[]),
 'state profile':('residual_structure',[]),
 'closed account registry':('selected',['missing_account','extra_zero_account']),
 'account classification coverage':('pinned_implementation_constants',[]),
 'account classification overlap':('pinned_implementation_constants',[]),
 'book balance':('selected',['book_imbalance']),
 'cash shortfall':('selected',['balanced_cash_shortfall','funding_and_duplicate_seen']),
 'negative other inventory':('selected',['negative_other_inventory']),
 'inventory allocation':('selected',['inventory_allocation']),
 'refund allocation':('selected',['refund_component']),
 'recovery allocation':('selected',['recovery_component']),
 'unknown settlement memory':('selected',['unknown_settlement']),
 'settled rights remain':('selected',['settled_outstanding_rights']),
 'lot identity':('selected',['lot_stored_identity','lot_component_identity']),
 'lot amount domain':('selected',['negative_units','negative_lot_carrying']),
 'lot tax method':('selected',['lot_tax_basis']),
 'lot disposition type':('explicit_unknown_extension',['unknown_disposition']),
 'disposed stock remains':('selected',['disposed_stock_remains']),
 'empty live lot':('selected',['empty_live_lot']),
 'duplicate lifetime event':('selected',['duplicate_seen']),
 'tax adjustment identity':('selected',['duplicate_adjustment','adjustment_unseen'])}


def coverage(rows,native):
    tree=ast.parse(SOURCE.read_text())
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='invariant')
    result=[];cases={r['case']:r for r in rows}
    for node in ast.walk(function):
        if not (isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='need'):
            continue
        reason=ast.literal_eval(node.args[1]);status,names=DISPOSITIONS[reason]
        assert all(name in cases and cases[name]['passed'] for name in names),reason
        if status=='selected':assert names,reason
        result.append({'line':node.lineno,'condition':ast.unparse(node.args[0]),'reason':reason,
                       'native_category':ast.literal_eval(node.args[2]) if len(node.args)>2 else 'invalid',
                       'disposition':status,'case_evidence':names})
    assert {r['reason'] for r in result}==set(DISPOSITIONS)
    classified=native.ASSETS+native.LIABILITIES+native.EQUITY+native.INCOME
    assert set(classified)==set(native.ACCOUNTS) and len(classified)==len(native.ACCOUNTS)
    return sorted(result,key=lambda r:r['line'])
