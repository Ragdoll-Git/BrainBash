from .debian import DebianManager
from .alpine import AlpineManager
from .fedora import FedoraManager

# Esto permite importar las clases directamente desde el paquete managers
# Ejemplo: from src.managers import DebianManager
__all__ = ["DebianManager", "AlpineManager", "FedoraManager"]