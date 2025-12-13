from abc import ABC, abstractmethod
from typing import List
import shutil
import subprocess

# ==========================================
# DICCIONARIO ROSETTA (Mapeo de Paquetes)
# ==========================================
# Estructura: "nombre_generico": {"distro": "nombre_real"}
PACKAGE_MAP = {
    "python-dev": {
        "debian": "python3-dev",
        "ubuntu": "python3-dev",
        "alpine": "python3-dev",
        "fedora": "python3-devel"
    },
    "docker": {
        "debian": "docker.io",
        "ubuntu": "docker.io",
        "alpine": "docker",
        "fedora": "moby-engine"
    },
    "zsh": {
        "default": "zsh"
    },
    "git": {
        "default": "git"
    },
    "curl": {
        "default": "curl"
    },
    "kitty": {
        "default": "kitty"
    },
    "fzf": {
        "default": "fzf"
    },
    "bat": {
        "debian": "bat",  # Ojo: en Debian a veces es 'bat', el fix de 'batcat' lo haremos en código
        "default": "bat"
    }
}

# ==========================================
# CLASE ABSTRACTA (El Contrato)
# ==========================================
class PackageManager(ABC):
    """
    Clase base que obliga a todos los gestores (Debian, Alpine, etc.)
    a implementar los métodos update e install.
    """

    def __init__(self, distro_id: str):
        self.distro_id = distro_id

    def _get_mapped_name(self, generic_name: str) -> str:
        """Traduce el nombre genérico al específico de la distro"""
        mapping = PACKAGE_MAP.get(generic_name, {})
        
        # 1. Busca coincidencia exacta con la distro (ej: "debian")
        if self.distro_id in mapping:
            return mapping[self.distro_id]
        
        # 2. Si no, busca "default"
        if "default" in mapping:
            return mapping["default"]
        
        # 3. Si no hay mapa, asume que el nombre es igual al genérico
        return generic_name

    def check_is_installed(self, package: str) -> bool:
        """Verifica si un comando existe en el PATH (método agnóstico universal)"""
        return shutil.which(package) is not None

    @abstractmethod
    def update(self):
        """Debe actualizar los repositorios"""
        pass

    @abstractmethod
    def install(self, packages: List[str]):
        """Debe instalar una lista de paquetes"""
        pass