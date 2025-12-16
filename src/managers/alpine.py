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
        
        # En Alpine, muchas "modern tools" SI estan en los repos (community/edge).
        # Es preferible usarlas nativas que bajar binarios glibc que segfaultean (como Ollama).
        # Mapeo manual de nombres si difieren
        
        for pkg in packages:
            mapped = self._get_mapped_name(pkg)
            
            # tldr no parece estar en alpine standard ("tealdeer" tampoco en search)
            # asi que lo mandamos a manual. El resto (eza, bat, etc) suele estar.
            if pkg == "tldr" or mapped == "tldr":
                manual_packages.append("tldr")
            else:
                apk_packages.append(mapped)

        # Force install 'ollama' via APK if we are in this manager
        # Esto evita que main.py intente bajar el binario de GitHub que da Segfault
        if "ollama" not in apk_packages:
            apk_packages.append("ollama")

        # Asegurar 'docs' para man pages si se quiere? (opcional)
        # alpine suele separar docs.
        
        # 1. APK
        if apk_packages:
            print(f"[Alpine] Instalando paquetes nativos: {', '.join(apk_packages)}")
            # gcompat puede ser util para tldr manual, pero los nativos no lo necesitan.
            # Agregamos gcompat solo si vamos a instalar manuales binarios glibc
            if manual_packages:
                if "gcompat" not in apk_packages: apk_packages.append("gcompat")
                if "libstdc++" not in apk_packages: apk_packages.append("libstdc++")
                if "curl" not in apk_packages: apk_packages.append("curl")

            cmd = self.sudo_cmd + ["apk", "add", "--no-cache"] + apk_packages
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                print("[Error] Fallo la instalacion con APK.")
                # No hacemos raise inmediato para intentar los manuales? 
                # Mejor fallar si lo basico falla.
                raise

        # 2. Binarios Manuales (Solo tldr)
        for tool in manual_packages:
            # allow_musl=True intentará buscar assets compatibles, o usara gcompat
            self._install_binary(tool, allow_musl=True)