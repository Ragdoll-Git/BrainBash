import sys
import os

# Agregamos el directorio raiz al path para poder importar src
sys.path.append(os.getcwd())

from src.managers import DebianManager, AlpineManager, FedoraManager
from main import get_manager

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify_os.py <ExpectedManagerClass>")
        sys.exit(1)

    expected_class_name = sys.argv[1]
    
    print(f"--- Verifying OS Detection (Expected: {expected_class_name}) ---")
    
    # 1. Ejecutar deteccion
    try:
        manager = get_manager()
    except SystemExit:
        print("FAIL: get_manager() called sys.exit() (OS not detected)")
        sys.exit(1)
        
    actual_class_name = type(manager).__name__
    print(f"Detected Manager: {actual_class_name}")

    # 2. Verificar
    if expected_class_name in actual_class_name:
        print("SUCCESS: Detection correct.")
        sys.exit(0)
    else:
        print(f"FAIL: Expected {expected_class_name}, but got {actual_class_name}")
        sys.exit(1)
