
import sys
import os
sys.path.append('/app')
from src.managers.debian import DebianManager

print("--- DEBUGGING EZA INSTALLATION ---", flush=True)
manager = DebianManager("debian")
# Force reinstall logic
print("Attempting to install 'eza' via manager.install()...", flush=True)
try:
    manager.install(["eza"])
except Exception as e:
    print(f"CRITICAL EXCEPTION: {e}", flush=True)

print("\n--- CHECKING BINARY ---", flush=True)
if os.path.exists("/usr/local/bin/eza"):
    print("SUCCESS: /usr/local/bin/eza exists")
else:
    print("FAILURE: /usr/local/bin/eza NOT found")

print("\n--- CHECKING PATH ---")
print(os.environ["PATH"])
