import subprocess
from typing import List
from ..core import PackageManager

class FedoraManager(PackageManager):
    """
    Implementacion especifica para Fedora, RHEL, CentOS y AlmaLinux (DNF).
    """

    def update(self):
        print("[Fedora] Actualizando metadatos de DNF...")
        # makecache solo actualiza la lista de paquetes, similar a apt update
        subprocess.run(["sudo", "dnf", "makecache"], check=True)

    def install(self, packages: List[str]):
        mapped_packages = [self._get_mapped_name(p) for p in packages]
        
        print(f"[Fedora] Instalando: {', '.join(mapped_packages)}")
        
        try:
            subprocess.run(
                ["sudo", "dnf", "install", "-y"] + mapped_packages, 
                check=True
            )
        except subprocess.CalledProcessError:
            print("[Error] Fallo la instalacion con DNF.")
            raise