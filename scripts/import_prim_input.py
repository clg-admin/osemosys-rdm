# -*- coding: utf-8 -*-
"""
Import PRIM Input from another model's DVC-tracked platform.

PRIM analyzes a model (e.g. Uganda) whose experiment platform was computed on a
different branch and is NOT regenerated here (EXP runs a different model, e.g.
South Africa). This script materializes that model's platform into PRIM_Input/
from the local DVC cache, using the directory hashes recorded in a given
revision's dvc.lock.

It reconstructs the layout t3f2 expects (see prim_input_root in PRIM_t3f2.yaml):
    PRIM_Input/Executables/...
    PRIM_Input/Experimental_Platform/Futures/...

Usage:
    python scripts/import_prim_input.py                  # rev = origin/final_UGA_model
    python scripts/import_prim_input.py --rev <branch>   # any branch/commit
    python scripts/import_prim_input.py --dry-run        # verify only, copy nothing

Requirements:
    The referenced DVC objects must exist in the local .dvc/cache (there is no
    DVC remote configured). Run this where that model's pipeline was executed,
    or after `dvc pull` if a remote is later configured.

Author: AFR_RDM Team
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

# DVC out basenames we need for PRIM -> destination subdir under PRIM_Input/
WANTED = {
    "Executables": "Executables",
    "Experimental_Platform": "Experimental_Platform",
}


def git_show(rev: str, path: str) -> str:
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], text=True)


def find_dir_hashes(lock_text: str) -> dict:
    """Return {dest_subdir: dir_md5} for the PRIM outs found in a dvc.lock."""
    lock = yaml.safe_load(lock_text)
    found = {}
    for stage in (lock.get("stages") or {}).values():
        for out in stage.get("outs", []) or []:
            name = str(out.get("path", "")).rstrip("/").rsplit("/", 1)[-1]
            if name in WANTED and str(out.get("md5", "")).endswith(".dir"):
                found[WANTED[name]] = out["md5"][:-4]  # strip '.dir'
    return found


def cache_path(root: Path, md5: str) -> Path:
    """Locate a cache object across new (files/md5) and old (flat) layouts."""
    new = root / ".dvc" / "cache" / "files" / "md5" / md5[:2] / md5[2:]
    if new.exists():
        return new
    old = root / ".dvc" / "cache" / md5[:2] / md5[2:]
    if old.exists():
        return old
    return new


def main():
    ap = argparse.ArgumentParser(
        description="Import the PRIM model platform from a revision's DVC cache.")
    ap.add_argument("--rev", default="origin/final_UGA_model",
                    help="Git revision whose dvc.lock points to the PRIM platform "
                         "(default: origin/final_UGA_model).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Verify cache completeness only; do not copy.")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    print("=" * 70)
    print("AFR_RDM - Import PRIM Input")
    print(f"  source revision: {args.rev}")
    print("=" * 70)

    try:
        lock_text = git_show(args.rev, "dvc.lock")
    except subprocess.CalledProcessError:
        print(f"❌ Could not read dvc.lock at '{args.rev}'. Is the revision available?")
        sys.exit(1)

    hashes = find_dir_hashes(lock_text)
    for sub in WANTED.values():
        if sub not in hashes:
            print(f"❌ No '.dir' out for '{sub}' found in {args.rev}:dvc.lock")
            sys.exit(1)

    dst_root = root / "PRIM_Input"
    plan, missing = [], []
    for sub, dir_md5 in hashes.items():
        dir_obj = cache_path(root, dir_md5 + ".dir")
        if not dir_obj.exists():
            print(f"❌ dir object not in cache: {dir_obj}")
            print("   The platform was not computed/cached locally for this revision.")
            sys.exit(1)
        entries = json.loads(dir_obj.read_text(encoding="utf-8"))
        print(f"\n[{sub}]  {len(entries)} files (dir={dir_md5[:12]}...)")
        for e in entries:
            src = cache_path(root, e["md5"])
            dst = dst_root / sub / e["relpath"]
            (plan if src.exists() else missing).append((src, dst))
            if src.exists():
                print(f"   {e['relpath']}")

    if missing:
        print(f"\n❌ {len(missing)} file objects missing from cache; cannot reconstruct.")
        for m in missing[:10]:
            print("   ", m[0])
        sys.exit(1)

    print(f"\n✓ All {len(plan)} objects present in cache.")
    if args.dry_run:
        print("(dry-run) Nothing copied. Re-run without --dry-run to import.")
        return

    for sub in hashes:
        d = dst_root / sub
        if d.exists():
            shutil.rmtree(d)
    for src, dst in plan:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    print(f"\n✅ Imported {len(plan)} files into {dst_root}")
    print("   PRIM reads this via 'prim_input_root' in PRIM_t3f2.yaml.")


if __name__ == "__main__":
    main()
