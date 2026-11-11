"""Confirm a PyInstaller-built Windows executable starts and stays running.

A quick launch smoke check is not a substitute for a real user acceptance test.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/smoke_frozen.py <exe>", file=sys.stderr)
        return 2
    exe = Path(sys.argv[1]).resolve()
    if not exe.is_file():
        print(f"Missing Windows application: {exe}", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    proc = subprocess.Popen([str(exe)], cwd=str(exe.parent), env=env)
    try:
        time.sleep(12)
        code = proc.poll()
        if code is not None:
            print(f"Application exited during startup (code {code}).", file=sys.stderr)
            return 1
        print(f"Startup smoke check passed: {exe.name}")
        return 0
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=7)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=7)


if __name__ == "__main__":
    raise SystemExit(main())