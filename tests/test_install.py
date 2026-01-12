#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))

from main import run_execution_phase, get_manager, MENU_BASE, MENU_EXTRA
from src.utils import Logger, Colors, TUI

def test_install():
    """
    Test script that mimics a user selection and runs the installation.
    Driven by environment variables or defaults.
    """
    logger = Logger(Colors.BLUE)
    logger.info("=== INICIANDO TEST AUTOMATIZADO DE INSTALACION ===")
    
    # 1. Setup Mock State
    # We want to test Base + Extra packages + Zsh + Dotfiles
    # We skip Models to save time/bandwidth in basic tests, unless ENV var set
    
    state = {
        "update_sys": False, # Skip update to save time in repeated tests
        "pkgs_base": [x[0] for x in MENU_BASE],
        "pkgs_extra": [x[0] for x in MENU_EXTRA],
        "models": [],
        "use_gemini": False,
        "dotfiles": True
    }
    
    # Optional: Enable features via ENV
    if os.environ.get("TEST_WITH_GEMINI"):
        state["use_gemini"] = True
        state["gemini_api_key"] = os.environ.get("GEMINI_API_KEY")
        
    # 2. Get Real Components
    try:
        manager = get_manager()
        tui = TUI() # TUI object is needed but won't be used for interaction
    except SystemExit:
        logger.error("Failed to initialize manager. Not a supported OS?")
        sys.exit(1)

    # 3. Run Execution Phase
    try:
        run_execution_phase(state, manager, logger, tui)
    except Exception as e:
        logger.error(f"FATAL: Test execution failed: {e}")
        sys.exit(1)
        
    logger.success("=== TEST COMPLETADO EXITOSAMENTE ===")

if __name__ == "__main__":
    test_install()
