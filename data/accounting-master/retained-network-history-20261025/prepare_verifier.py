"""Prepare the exact recorder for the complete-network composition."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/retained-statement-history-20261025/verify.py').read_text()
text=text.replace('accounting-retained-statement-history-20261025.md','accounting-retained-network-history-20261025.md')
text=text.replace("['test_retained_statement_history_v1']","['test_retained_network_history_v1']")
start=text.index('REGRESSIONS=');end=text.index('def sha(',start)
text=text[:start]+"REGRESSIONS=['test_retained_statement_network_v1','test_retained_statement_history_v1','test_typed_history_measurement_attachment_v1']\n"+text[end:]
text=text.replace('adapter.balance.verify_dependencies()','adapter.network.source.verify_dependencies()')
text=text.replace('adapter.balance.PACKAGE','adapter.network.source.PACKAGE')
text=text.replace("HERE/'prepare_verifier.py',ROOT/PLAN","HERE/'prepare_verifier.py',ROOT/PLAN")
compile(text,'verify.py','exec');assert not (HERE/'verify.py').exists();(HERE/'verify.py').write_text(text)
print('Prepared network-history recorder')
