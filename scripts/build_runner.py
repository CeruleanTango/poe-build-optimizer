### Orchestrator script for FASTBuild ###

import subprocess
import time
import json
import os

from datetime import datetime

SNAPSHOT_BASE = "buildpool/workspace"
LAST_SNAPSHOT = "reports/last_snapshot.txt"

def take_snapshot(tag):
    snap = f"{SNAPSHOT_BASE}@{tag}"
    subprocess.run(["sudo", "zfs", "snapshot", snap], check=True)
    print(f"Snapshot taken: {snap}")
    return snap

def read_last_snapshot():
    if os.path.exists(LAST_SNAPSHOT):
        with open(LAST_SNAPSHOT, "r") as f:
            snap = f.read().strip()
            print(f"Last snapshot found: {snap}")
            return snap
    print("No previous snapshot found -- no changes will be detected")
    return None

def write_last_snapshot(snap):
    with open(LAST_SNAPSHOT, "w") as f:
        f.write(snap)
    print(f"New snapshot written to {LAST_SNAPSHOT}")

def run_build(config_path):
    start = time.time()
    result = subprocess.run(
       ["fbuild", "all", "-config", config_path],
        capture_output=True, text=True
    )
    elapsed = round(time.time()-start, 2)
    print(result.stdout)
    if result.returncode != 0:
        print("Build failed: ", result.stderr)
    return elapsed, result.returncode == 0

def interpret_change(symbol):
    return {
        "M": "modified",
        "+": "added",
        "-": "removed",
        "R": "renamed"
    }.get(symbol, "unknown")

def get_changed_files(snap_before, snap_after):
    result = subprocess.run(
        ["sudo", "zfs", "diff", snap_before, snap_after],
        capture_output=True, text=True
    )
    changed = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            change_type, path = parts
            if not path.endswith("/") and "/" in path:
                filename = path.split("/")[-1]
                changed.append({"file": filename, "change": interpret_change(change_type.strip())})
    return changed

def main():
    build_config = "/home/admin/poe-build-optimizer/build/fbuild.bff"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    pre_snap = read_last_snapshot()

    build_time, success = run_build(build_config)
    post_snap = take_snapshot(f"post-build-{timestamp}")
    write_last_snapshot(post_snap)

    report = {
        "timestamp": timestamp,
        "build_time_seconds": build_time,
        "success":success,
        "post_build_snap": post_snap,
    }

    if None != pre_snap:
        changed_files = get_changed_files(pre_snap, post_snap)

        report.update({
            "pre_build_snap": pre_snap,
            "changed_files": changed_files,
        })

    with open("reports/latest.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nBuild {'succeeded' if success else 'failed'} in {build_time}s")
    print(f"Changed files detected: {len(changed_files)}")
    print("Report written to reports/latest.json")

if __name__ == "__main__":
    main()
