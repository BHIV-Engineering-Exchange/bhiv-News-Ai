import os
import sys
import subprocess
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(script, *args):
    command = [sys.executable, os.path.join(ROOT, "scripts", script), *args]
    p = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return p.returncode, p.stdout

def main():
    stages = [
        ("run_ingest.py", ()),
        ("format_metadata.py", ()),
    ]
    stages.extend(
        ("generate_audio.py", ("--avatar", avatar, "--voice", "default", "--limit", "10"))
        for avatar in ("asha", "kiran", "dev")
    )
    stages.append(("smart_feed.py", ()))
    output = []
    for script, args in stages:
        rc, stage_output = run(script, *args)
        output.append(stage_output)
        if rc != 0:
            print(json.dumps({
                "status": "error",
                "stage": script,
                "return_code": rc,
                "output": stage_output,
            }))
            return rc

    print(json.dumps({"status": "ok", "output": output}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())