import os
import sys
import subprocess
import json

def run(cmd, cwd=None):
    p = subprocess.Popen(cmd, cwd=cwd or os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    out, _ = p.communicate()
    return p.returncode, out.decode('utf-8', errors='ignore')

def main():
    rc, out = run("python scripts/run_ingest.py")
    rc, out = run("python scripts/format_metadata.py")
    for avatar in ["asha", "kiran", "dev"]:
        rc, out = run(f"python scripts/generate_audio.py --avatar {avatar} --voice default --limit 10")
    rc, out = run("python scripts/smart_feed.py")
    print(json.dumps({"status": "ok"}))

if __name__ == "__main__":
    main()