# poe-build-optimizer

This is a build pipeline demo using ZFS snapshot, FASTBuild, and Python to
manage and track C++ compilation. Built as a demonstration of build engineering
concepts relevant to the GGG pipeline stack.

## Tools used

- **ZFS** - build state versioning and change tracking, for optimizing build times
by avoiding re-compiling code or assets that were unchanged
- **FASTBuildv1.15** - C++ compilation
- **Python3.12** - Scripted layer that ties snapshots and builds together

## How it works

- Python script takes a ZFS snapshot before the build.
- FASTBuild compiles the c++ source files from the ZFS workspace.
- Python script takes a second ZFS snapshot after the build has succeeded.
- Create a JSON report with build time and success status.
-- "zfs diff" command can be used between any two snapshots to see what file have been modified

## OS Used
- Ubuntu 24.04 LTS

