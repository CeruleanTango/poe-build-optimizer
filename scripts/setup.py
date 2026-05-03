import subprocess
import os
import shutil
import sys
from pathlib import Path

ZFS_DISK_IMAGE = os.path.expanduser("~/zfs_disk.img")
ZFS_POOL = "buildpool"
ZSF_DATASET = "buildpool/workspace"
ZFS_MNTPOINT = "/buildpool/workspace"
REPO_WKSPC = Path(__file__).parent.parent / "workspace"
FBUILD_OUT = "/tmp/fbuild-out"
ASSET_OUT = "/tmp/asset-out"

def run(cmd, error_msg):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {error_msg)")
        print(result.stderr)
        sys.exit(1)
    return result

def zfs_pool_exists():
    result = subprocess.run(
        ["sudo", "zpool", "list", ZFS_POOL],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def zfs_dataset_exists():
    result = subprocess.run(
        ["sudo", "zfs", "list", ZFS_DATASET],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def create_disk_image():
    if os.path.exists(ZFS_DISK_IMAGE):
        return
    print("Creating ZFS disk image...")
    run(["dd", "if=/dev/zero", f"of={ZFS_DISK_IMAGE}", "bs=1M", "count=512"], "Failed to create disk image")

    print("Disk image created")

def create_zfs_dataset():
    if dataset_exists():
        return
    print("Creating ZFS dataset at {ZFS_DATASET}...")

    run(["sudo", "zfs", "create", ZFS_DATASET], "Failed to create dataset")

    print("ZFS dataset created")

def populate_workspace():
    print(f"Copying workspace files to {ZFS_MNTPOINT}...")

    for src in REPO_WKSPC.rglob("*"):
        if src.is_file():
            relative = src.relative_to(REPO_WKSPC)
            dest = Path(ZFS_MNTPOINT)/relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src,dest)
            print(f"Copied: {relative}")
    print("Workspace populated")

def take_initial
