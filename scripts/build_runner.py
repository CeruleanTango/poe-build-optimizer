### Orchestrator script for FASTBuild ###

import subprocess
import time
import json
import os

from datetime import datetime

import asset_compiler

SNAPSHOT_BASE = "buildpool/workspace"
LAST_SNAPSHOT = "reports/last_snapshot.txt"
LAST_ASSET_SNAPSHOT = "reports/last_asset_snapshot.txt"

def take_snapshot(tag):
    snap = f"{SNAPSHOT_BASE}@{tag}"
    subprocess.run(["sudo", "zfs", "snapshot", snap], check=True)
    print(f"Snapshot taken: {snap}")
    return snap

def read_last_snapshot(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            snap = f.read().strip()
            print(f"Last snapshot found: {snap}")
            return snap
    print("No previous snapshot found -- no changes will be detected")
    return None

def write_last_snapshot(path, snap):
    with open(path, "w") as f:
        f.write(snap)
    print(f"New snapshot written to {path}")

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

def get_changed_files(snap_before, snap_after, filter_path=None):
    if None == snap_before:
        return []

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
                if filter_path and filter_path not in path:
                    # Only include files in filter_path
                    continue
                filename = path.split("/")[-1]
                changed.append({"file": filename, "change": interpret_change(change_type.strip())})
    return changed

def run_asset_compile(post_snap):
    pre_asset_snap = read_last_snapshot(LAST_ASSET_SNAPSHOT)

    if None == pre_asset_snap:
        print("First asset build - compiling all assets...")
        results, total = asset_compiler.compile_all()
        write_last_snapshot(LAST_ASSET_SNAPSHOT, post_snap)
        return {
            "skipped": False,
            "reason": "first run",
            "assets_compiled": results,
            "asset_build_time": total
        }

    changed_assets = get_changed_files(pre_asset_snap, post_snap, filter_path="/assets/")

    if not changed_assets:
        print("No asset changes detected - skipping asset compilation.")
        return {
            "skipped": True,
            "reason": "no changes detected",
            "assets_compiled": [],
            "asset_build_time": 0,
        }

    print(f"{len(changed_assets)} assets changed - compiling...")
    results, total = asset_compiler.compile_all(changed_files=changed_assets)
    write_last_snapshot(LAST_ASSET_SNAPSHOT, post_snap)
    return {
        "skipped": False,
        "reason": "asset changes detected",
        "assets_compiled": results,
        "asset_build_time": total,
    }

def main():
    build_config = "/home/admin/poe-build-optimizer/build/fbuild.bff"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    pre_snap = read_last_snapshot(LAST_SNAPSHOT)

    build_time, success = run_build(build_config)
    post_snap = take_snapshot(f"post-build-{timestamp}")
    write_last_snapshot(LAST_SNAPSHOT, post_snap)

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

    print("\n---Asset Pipeline---")
    asset_result = run_asset_compile(post_snap)

    report.update({
        "asset_pipeline":asset_result
    })

    total_build_time = build_time + asset_result["asset_build_time"]
    total_changes = len(changed_files) + len(asset_result["assets_compiled"])

    with open("reports/latest.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nBuild {'succeeded' if success else 'failed'} in {total_build_time}s")
    print(f"Changed files detected: {total_changes}")
    print("Report written to reports/latest.json")

if __name__ == "__main__":
    main()
