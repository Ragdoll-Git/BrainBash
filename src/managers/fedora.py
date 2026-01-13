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
        subprocess.run(self.sudo_cmd + ["dnf", "makecache"], check=True)

    def install(self, packages: List[str]):
        dnf_packages = []
        manual_packages = []
        
        # Herramientas que no estan en repos base de Fedora (o tienen nombres raros)
        # y preferimos bajar binarios recientes de GitHub
        modern_tools = ["eza", "bat", "fzf", "starship", "zoxide", "tldr"]

        for pkg in packages:
            mapped = self._get_mapped_name(pkg)
            
            if mapped in modern_tools or pkg in modern_tools:
                manual_packages.append(mapped)
            else:
                dnf_packages.append(mapped)
        
        # 1. DNF
        if dnf_packages:
            print(f"[Fedora] Instalando paquetes DNF: {', '.join(dnf_packages)}")
            try:
                # --skip-broken podria ayudar pero mejor ser explicitos
                subprocess.run(
                    self.sudo_cmd + ["dnf", "install", "-y"] + dnf_packages, 
                    check=True
                )
            except subprocess.CalledProcessError:
                print("[Error] Fallo la instalacion con DNF.")
                raise

        # 2. Binarios Manuales
        for tool in manual_packages:
            # Fedora usa glibc, asi que allow_musl=False (default) esta bien
            self._install_binary(tool)
