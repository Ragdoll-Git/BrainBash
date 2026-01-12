
import sys
import shutil
import os
import subprocess
sys.path.append('/app')
from src.managers.debian import DebianManager

print("--- DEBUGGING MIGRATION ---", flush=True)
manager = DebianManager("debian")

# 1. Install new packages
pkgs = ["bat", "fzf", "zoxide", "tldr", "thefuck"]
print(f"Installing: {pkgs}", flush=True)

try:
    manager.install(pkgs)
except Exception as e:
    print(f"CRITICAL EXCEPTION: {e}", flush=True)

# 2. Verify binaries
expected = {
    "bat": ["/usr/bin/batcat", "/usr/local/bin/bat"], # Binary + Symlink
    "fzf": ["/usr/bin/fzf"],
    "zoxide": ["/usr/bin/zoxide"],
    "tldr": ["/usr/bin/tealdeer", "/usr/local/bin/tldr"], # Binary + Symlink
    "thefuck": ["/usr/bin/thefuck"]
}

print("\n--- VERIFICATION BINARIES ---", flush=True)
all_ok = True
for name, paths in expected.items():
    found = False
    for p in paths:
        if os.path.exists(p) or shutil.which(name):
            found = True
            print(f"[OK] {name} found ({p} or PATH)", flush=True)
            break
    if not found:
        print(f"[FAIL] {name} NOT found", flush=True)
        all_ok = False

print("\n--- VERIFICATION THEME ---", flush=True)
try:
    themes = subprocess.check_output(["bat", "--list-themes"], text=True)
    if "Catppuccin Mocha" in themes:
        print("[OK] Theme 'Catppuccin Mocha' found in bat cache.", flush=True)
    else:
        print("[FAIL] Theme 'Catppuccin Mocha' NOT found in bat cache.", flush=True)
        all_ok = False
except Exception as e:
    print(f"[FAIL] Check failed: {e}", flush=True)

print("\n--- VERIFICATION TLDR ---", flush=True)
try:
    # Try to fetch a page. If cache is empty, this fails or asks to update.
    # We use 'tar' as a common command.
    output = subprocess.check_output(["tldr", "tar"], text=True)
    if "Archiving utility" in output or "tar" in output:
         print("[OK] 'tldr tar' returned valid content (Cache works).", flush=True)
    else:
         print("[FAIL] 'tldr tar' output suspicious.", flush=True)
         all_ok = False
except Exception as e:
    print(f"[FAIL] 'tldr tar' failed (Cache likely missing): {e}", flush=True)
    all_ok = False

if all_ok:
    print("\nSUCCESS: All packages migrated, theme installed, and TLDR cached.", flush=True)
else:
    print("\nFAILURE: Missing packages, theme, or TLDR cache.", flush=True)
