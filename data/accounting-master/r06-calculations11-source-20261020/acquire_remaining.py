"""One bounded batch: four exact remaining documentary sources, no retries."""
from pathlib import Path
import subprocess
import sys

U=Path(__file__).resolve().parent
failed=[]
for source in ("03-oim","04-xbrlxml","05-schema","06-status"):
    result=subprocess.run([sys.executable,"-B",str(U/"acquire.py"),source,"--trusted"])
    if result.returncode:
        failed.append(source)
print({"batch_complete":True,"failed_sources":failed},flush=True)
raise SystemExit(bool(failed))
