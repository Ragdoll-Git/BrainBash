from abc import ABC, abstractmethod
from typing import List
import shutil
import subprocess
import os

# ==========================================
# DICCIONARIO ROSETTA (Mapeo de Paquetes)
# ==========================================
PACKAGE_MAP = {
    "python-dev": {
        "debian": "python3-dev",
        "ubuntu": "python3-dev",
        "alpine": "python3-dev",
        "fedora": "python3-devel"
    },
    "zsh": {"default": "zsh"},
    "curl": {"default": "curl"},
    "kitty": {"default": "kitty"},
    "fzf": {"default": "fzf"},
    
    # === HERRAMIENTAS MODERNAS ===
    "bat": {
        "debian": "bat",  # Debian instala 'batcat', el script debian.py ya hace el symlink
        "default": "bat"
    },
    "eza": {
        "debian": "eza",  # Nota: Requiere repositorios recientes o cargo. Si falla, el script avisa.
        "default": "eza"
    },
    "htop": {"default": "htop"}, # Monitor de recursos
    "tldr": {"default": "tldr"}, # Manuales simplificados
    "zoxide": {"default": "zoxide"}, # "cd" inteligente (requerido por tu zshrc)
    "starship": {"default": "starship"} # Prompt (requerido por tu zshrc)
}

# ==========================================
# CLASE ABSTRACTA
# ==========================================
class PackageManager(ABC):
    def __init__(self, distro_id: str):
        self.distro_id = distro_id
        self._sudo_cmd = [] if os.geteuid() == 0 else ["sudo"]
        
    @property
    def sudo_cmd(self) -> List[str]:
        return self._sudo_cmd

    def _get_mapped_name(self, generic_name: str) -> str:
        mapping = PACKAGE_MAP.get(generic_name, {})
        if self.distro_id in mapping:
            return mapping[self.distro_id]
        if "default" in mapping:
            return mapping["default"]
        return generic_name

    def check_is_installed(self, package: str) -> bool:
        return shutil.which(package) is not None

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def install(self, packages: List[str]):
        pass