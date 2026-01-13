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
            # asi que lo mandamos a manual.
            if pkg == "tldr" or mapped == "tldr":
                manual_packages.append("tldr")
            elif pkg == "thefuck" or mapped == "thefuck":
                manual_packages.append("thefuck")
            else:
                apk_packages.append(mapped)

        # Force install 'ollama' via APK if we are in this manager
        if "ollama" not in apk_packages:
            apk_packages.append("ollama")

        # Asegurar pip si vamos a usar pip (para thefuck)
        if "thefuck" in manual_packages or "python3-dev" in apk_packages:
             if "py3-pip" not in apk_packages: apk_packages.append("py3-pip")

        # 1. APK
        if apk_packages:
            print(f"[Alpine] Instalando paquetes nativos: {', '.join(apk_packages)}")
            # gcompat puede ser util para tldr manual, pero los nativos no lo necesitan.
            if manual_packages:
                if "gcompat" not in apk_packages: apk_packages.append("gcompat")
                if "libstdc++" not in apk_packages: apk_packages.append("libstdc++")
                if "curl" not in apk_packages: apk_packages.append("curl")
            
            # Ensure 'shadow' is installed for chsh/usermod
            if "shadow" not in apk_packages: apk_packages.append("shadow")

            cmd = self.sudo_cmd + ["apk", "add", "--no-cache"] + apk_packages
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                print("[Error] Fallo la instalacion con APK.")
                raise

        # 2. Binarios Manuales (Solo tldr, thefuck)
        for tool in manual_packages:
            self._install_binary(tool, allow_musl=True)

    def _install_binary(self, tool, allow_musl=False):
        if tool == "thefuck":
            print("[Alpine] Instalando 'thefuck' via Pip...")
            try:
                # Alpine 3.19+ requiere --break-system-packages o venv
                subprocess.run(self.sudo_cmd + ["pip", "install", "thefuck", "--break-system-packages"], check=True)
                return
            except Exception as e:
                print(f"[Error] Fallo instalando thefuck: {e}")
                return

        # Delegar al padre para el resto de binarios (tldr, eza, bat, etc si fueran manuales)
        # Pero alpine.py original usaba _install_binary genericamente que no sabe volver al padre
        # si sobreescribe el metodo sin llamar super.
        # El metodo original en core.py es: _install_binary(self, tool, allow_musl=False)
        # AQUI NO ESTAMOS HEREDANDO, estamos definiendo si sobreescribimos.
        # Re-usamos la logica de core llamando a super (si fuera posible, pero aqui es override?)
        # Base class tiene _install_binary.
        
        super()._install_binary(tool, allow_musl)
