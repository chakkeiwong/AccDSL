from pathlib import Path
import json
import common_text as t
from source_export import from_program
HERE=Path(__file__).resolve().parent
for owner in ['alpha','beta']:
 body=json.loads((HERE.parent/'authored-event-contract-20261026/examples'/f'{owner}.program.json').read_text())
 source,resources=from_program(body)
 compiled=t.compile_text(source,resources)
 assert compiled['program']==body
 out=HERE/'examples';out.mkdir(exist_ok=True)
 (out/f'{owner}.acc').write_bytes(source.encode())
 (out/f'{owner}.resources.json').write_text(json.dumps(resources,indent=2)+chr(10))
 print(json.dumps({'company':owner,'compiled_exact':True,'source_bytes':len(source.encode()),'resources':len(resources),'commands':len(body['commands'])}))
