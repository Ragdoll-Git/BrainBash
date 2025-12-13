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
        subprocess.run(["sudo", "apk", "update"], check=True)

    def install(self, packages: List[str]):
        # Traducir nombres usando el diccionario Rosetta del core
        mapped_packages = [self._get_mapped_name(p) for p in packages]
        
        print(f"[Alpine] Instalando paquetes: {', '.join(mapped_packages)}")
        
        # En Alpine usamos --no-cache para no guardar los indices en disco
        # y mantener el sistema lo mas ligero posible.
        cmd = ["sudo", "apk", "add", "--no-cache"] + mapped_packages
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print("[Error] Fallo la instalacion con APK.")
            raise