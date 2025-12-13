import subprocess
import os
from pathlib import Path
from typing import List
from ..core import PackageManager

class DebianManager(PackageManager):
    """
    Implementación específica para sistemas basados en Debian (APT).
    """

    def update(self):
        print("[Debian] Actualizando índices de repositorios...")
        # -qq reduce la salida basura, pero mantiene errores
        subprocess.run(["sudo", "apt", "update", "-qq"], check=True)

    def install(self, packages: List[str]):
        # 1. Traducir nombres genéricos a nombres de Debian
        mapped_packages = [self._get_mapped_name(p) for p in packages]
        
        # 2. Filtrar los que ya están instalados para ahorrar tiempo
        #    (Usamos dpkg -s porque es más preciso en Debian que shutil.which para librerías)
        to_install = []
        for pkg in mapped_packages:
            if not self._is_dpkg_installed(pkg):
                to_install.append(pkg)

        if not to_install:
            print("Todos los paquetes ya están instalados.")
            return

        # 3. Instalación
        print(f"[Debian] Instalando: {', '.join(to_install)}")
        try:
            subprocess.run(
                ["sudo", "apt", "install", "-y"] + to_install, 
                check=True
            )
        except subprocess.CalledProcessError:
            print("Error crítico instalando paquetes con APT.")
            raise

        # 4. Fixes Post-Instalación específicos de Debian
        self._fix_batcat()

    def _is_dpkg_installed(self, package_name: str) -> bool:
        """Verifica instalación consultando la base de datos de dpkg"""
        res = subprocess.run(
            ["dpkg", "-s", package_name], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return res.returncode == 0

    def _fix_batcat(self):
        """
        En Debian, el paquete 'bat' instala el binario 'batcat' por conflicto de nombres.
        Creamos un symlink para poder usar 'bat' como en el resto del mundo.
        """
        # Verificamos si existe batcat pero NO bat
        batcat_bin = Path("/usr/bin/batcat")
        local_bin = Path(os.path.expanduser("~/.local/bin"))
        bat_symlink = local_bin / "bat"

        if batcat_bin.exists() and not bat_symlink.exists():
            print("🔧 [Fix] Creando alias 'bat' para 'batcat'...")
            local_bin.mkdir(parents=True, exist_ok=True)
            try:
                bat_symlink.symlink_to(batcat_bin)
                print(f"🔗 Enlace creado: {bat_symlink} -> {batcat_bin}")
            except Exception as e:
                print(f"No se pudo crear el symlink de bat: {e}")