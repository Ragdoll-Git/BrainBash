import subprocess
from typing import List
from ..core import PackageManager

class AlpineManager(PackageManager):
    """
    Implementacion especifica para Alpine Linux (APK).
    Ideal para entornos ligeros y contenedores.
    """

    def update(self):
        print("[Alpine] Actualizando indices de repositorios...")
        # Usamos self.sudo_cmd que detecta si somos root o no
        subprocess.run(self.sudo_cmd + ["apk", "update"], check=True)

    def install(self, packages: List[str]):
        apk_packages = []
        manual_packages = []
        
        # Lista de herramientas que preferimos instalar manualmente (o no estan en repos base)
        # Nota: Alpine v3.23 (latest) tiene muchos, pero mejor asegurar versiones recientes
        # y evitar problemas de nombres (tealdeer vs tldr).
        modern_tools = ["eza", "bat", "fzf", "starship", "zoxide", "tldr"]

        for pkg in packages:
            mapped = self._get_mapped_name(pkg)
            
            if mapped in modern_tools or pkg in modern_tools:
                manual_packages.append(mapped)
            else:
                apk_packages.append(mapped)
        
        # 1. APK
        if apk_packages:
            print(f"[Alpine] Instalando paquetes base: {', '.join(apk_packages)}")
            cmd = self.sudo_cmd + ["apk", "add", "--no-cache"] + apk_packages
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                print("[Error] Fallo la instalacion con APK.")
                raise

        # 2. Binarios Manuales
        # Para Alpine es CRITICO usar allow_musl=True porque usa musl libc
        for tool in manual_packages:
            self._install_binary(tool, allow_musl=True)