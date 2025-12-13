# Este archivo expone las clases principales del paquete src
# para facilitar su importacion desde el main.py

from .core import PackageManager
from .utils import Colors, Logger, TUI

# Definimos que es lo que se exporta cuando alguien hace "from src import *"
__all__ = ["PackageManager", "Colors", "Logger", "TUI"]