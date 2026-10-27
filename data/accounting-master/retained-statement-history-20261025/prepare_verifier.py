"""Reuse the accepted exact recorder, changing case and module selection."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/retained-source-history-20261025/verify.py').read_text()
text=text.replace('accounting-retained-source-history-20261025.md','accounting-retained-statement-history-20261025.md')
text=text.replace("['test_retained_source_history_v1']","['test_retained_statement_history_v1']")
start=text.index('REGRESSIONS=');end=text.index('def sha(',start)
text=text[:start]+"REGRESSIONS=['test_retained_source_history_v1','test_joint_source_relation_binding_v1','test_typed_history_measurement_attachment_v1','test_retained_temporal_source_binding_v1']\n"+text[end:]
start=text.index('def cases():');end=text.index('def tests():',start)
text=text[:start]+"def cases():\n    sys.path.insert(0,str(HERE))\n    from cases import cases as construct\n    return construct()\n\n"+text[end:]
text=text.replace('adapter.source.source.verify_dependencies()','adapter.balance.verify_dependencies()')
text=text.replace('adapter.source.source.PACKAGE','adapter.balance.PACKAGE')
text=text.replace("HERE/'verify.py',HERE/'examples.py',ROOT/PLAN","HERE/'verify.py',HERE/'examples.py',HERE/'audit.md',HERE/'prepare_verifier.py',ROOT/PLAN")
compile(text,'verify.py','exec');assert not (HERE/'verify.py').exists();(HERE/'verify.py').write_text(text)
print('Prepared statement-history recorder')
