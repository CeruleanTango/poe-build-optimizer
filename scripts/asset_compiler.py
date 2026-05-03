import os
import time
import json

from datetime import datetime

ASSET_DIR = "/buildpool/workspace/assets"
ASSET_OUTPUT_DIR = "/tmp/asset-out"

COMPILE_TIMES = {
    ".png": 0.4,
    ".glsl": 0.2,
    ".obj": 1.8,
}

def compile_assets(filepath):
    ext = os.path.splitext(filepath)[1]
    delay = COMPILE_TIMES.get(ext, 0.1)
    time.sleep(delay)
    
    filename = os.path.basename(filepath)
    output = os.path.join(ASSET_OUTPUT_DIR, filename + ".compiled")
    os.makedirs(ASSET_OUTPUT_DIR, exist_ok=True)
    with open(output, "w") as f:
        f.write(f"compiled:{filename}:{datetime.now().isoformat()}")
    return filename, delay

def compile_all(changed_files=None):
    """ Only compile changed files if provided, otherwise compile everything """
    results = []
    start = time.time()

    if changed_files is not None:
        targets = [
            f["path"]
            for f in changed_files
            if f["file"].endswith((".png",".glsl",".obj"))
        ]
        print(f"Compiling {len(targets)} changed assets...")
    else:
        targets = []
        for root, _, files in os.walk(ASSET_DIR):
            for f in files:
                targets.append(os.path.join(root, f))
        print(f"Full asset build: compiling {len(targets)} assets...")

    for filepath in targets:
        if os.path.exists(filepath):
            filename, cost = compile_assets(filepath)
            print(f"----Compiled {filename} ({cost}s)")
            results.append({"file":filename, "compile_time": cost})

    total = round(time.time() - start, 2)
    print(f"Asset compilation complete in {total}s")
    return results, total

if __name__ == "__main__":
    results, total = compile_all()
    print(json.dumps({"assets_compiled": results, "total_time": total}))


