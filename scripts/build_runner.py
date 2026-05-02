### Orchestrator script for FASTBuild ###

import subprocess
import time
import json

from datetime import datetime

SNAPSHOT_BASE = "buildpool/workspace"

def take_snapshot(tag):
    snap = f"{SNAPSHOT_BASE}@{tag}"
    subprocess.run(["sudo", "zfs", "snapshot", snap], check=True)
    print(f"Snapshot taken: {snap}")
    return snap

def run_build():
    start = time.time()
    result = subprocess.run(
       ["fbuild", "all", "-config", "/home/admin/poe-build-optimizer/build/fbuild.bff"],
        capture_output=True, text=True
    )
    elapsed = round(time.time()-start, 2)
    print(result.stdout)
    if result.returncode != 0:
        print("Build failed: ", result.stderr)
    return elapsed, result.returncode == 0

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    take_snapshot(f"pre-build-{timestamp}")
    build_time, success = run_build()
    take_snapshot(f"post-build-{timestamp}")

    report = {
        "timestamp": timestamp,
        "build_time_seconds": build_time,
        "success": success,
    }

    with open("reports/latest.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nBuild {'succeeded' if success else 'failed'} in {build_time}s")
    print("Report written to reports/latest.json")

if __name__ == "__main__":
    main()
