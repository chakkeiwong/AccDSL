"""Run only the two documentary profile checks and preserve their evidence."""
import datetime
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]

def main():
    attempts = ROOT / "validation-attempts"
    attempts.mkdir(exist_ok=True)
    attempt = attempts / f"{len(list(attempts.iterdir())) + 1:03d}"
    attempt.mkdir(exist_ok=False)
    evidence = {
        "purpose": "Deterministic documentary validation, not product execution",
        "git_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
        "cpu_gpu": "CPU-only documentary JSON/rational checks; no GPU framework imported",
        "random_seeds": "N/A: deterministic",
        "plan": str(ROOT.parent / "customer-successor-plan.md"),
        "runs": [],
    }
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for name in ["build_exchanges.py", "verify_exchanges.py"]:
        command = [sys.executable, str(ROOT / name)]
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        tick = time.monotonic()
        result = subprocess.run(command, cwd=REPO, env=env, text=True, capture_output=True)
        log = attempt / (name.removesuffix(".py") + ".log")
        log.write_text(result.stdout + result.stderr)
        entry = {"command": command, "cwd": str(REPO), "started_utc": started,
                 "wall_seconds": time.monotonic() - tick,
                 "exit_code": result.returncode, "log": str(log)}
        evidence["runs"].append(entry)
        (ROOT / "validation-run.json").write_text(json.dumps(evidence, indent=2) + "\n")
        (attempt / "validation-run.json").write_text(json.dumps(evidence, indent=2) + "\n")
        if name == "verify_exchanges.py":
            for output in ["checks.json", "independent-finances.json"]:
                (attempt / output).write_bytes((ROOT / output).read_bytes())
        print(json.dumps(entry), flush=True)
        print((result.stdout + result.stderr)[-3500:], flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)

if __name__ == "__main__":
    main()
