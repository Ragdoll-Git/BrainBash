from abc import ABC, abstractmethod
from typing import List
import shutil
import subprocess
import os
import platform
from pathlib import Path

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
        self.logger = None

    def set_logger(self, logger):
        self.logger = logger

    def _log_info(self, msg):
        if self.logger: self.logger.info(msg)
        else: print(f"[INFO] {msg}")

    def _log_warn(self, msg):
        if self.logger: self.logger.warning(msg)
        else: print(f"[WARN] {msg}")

    def _log_error(self, msg):
        if self.logger: self.logger.error(msg)
        else: print(f"[ERROR] {msg}")
        
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

    @abstractmethod
    def install_fontconfig(self):
        """Instala fontconfig para poder usar fc-cache"""
        pass

    def _install_nerd_fonts(self):
        """Instala MesloLGS NF para Starship"""
        self._log_info("Instalando Nerd Fonts (MesloLGS NF)...")
        
        # 1. Directorio de fuentes local
        home = Path.home()
        fonts_dir = home / ".local" / "share" / "fonts"
        fonts_dir.mkdir(parents=True, exist_ok=True)
        
        # URLs de MesloLGS NF
        base_url = "https://github.com/romkatv/powerlevel10k-media/raw/master"
        fonts = [
            "MesloLGS NF Regular.ttf",
            "MesloLGS NF Bold.ttf",
            "MesloLGS NF Italic.ttf",
            "MesloLGS NF Bold Italic.ttf"
        ]
        
        try:
            for font in fonts:
                target = fonts_dir / font
                if not target.exists():
                    self._log_info(f"   > Descargando {font}...")
                    subprocess.run(["curl", "-fLo", str(target), f"{base_url}/{font}"], check=True)
            
            # Refrescar cache
            self._log_info("   > Actualizando cache de fuentes...")
            
            # Verificar si existe fc-cache, si no, instalar fontconfig via manager especifico
            if not shutil.which("fc-cache"):
                self.install_fontconfig()

            if shutil.which("fc-cache"):
                subprocess.run(["fc-cache", "-fv"], check=False, stdout=subprocess.DEVNULL)
                self._log_info("Instalacion de fuentes completada.")
            else:
                self._log_warn("'fc-cache' no encontrado incluso tras intentar instalar fontconfig.")
                
        except Exception as e:
            self._log_error(f"Fallo instalando fuentes: {e}")

    # ==========================================
    # METODOS DE AYUDA (Instalación manual)
    # ==========================================

    def _get_arch_terms(self):
        arch = platform.machine().lower()
        if arch == "x86_64": return ["x86_64", "amd64"]
        if arch in ["aarch64", "arm64"]: return ["aarch64", "arm64"]
        return [arch]

    def _download_github_asset(self, repo, keyword, output_name, allow_musl=False):
        import urllib.request
        import json
        
        print(f"⬇️  [GitHub] Buscando {output_name} en {repo}...")
        try:
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'python'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
            
            arch_terms = self._get_arch_terms()
            download_url = None
            
            for asset in data["assets"]:
                name = asset["name"].lower()
                if "linux" not in name and "unknown-linux" not in name: continue
                if not any(term in name for term in arch_terms): continue
                if keyword and keyword not in name: continue
                # Si allow_musl es False, evitamos musl (para glibc distros)
                # Si es True, PREFERIMOS musl si estamos en Alpine?
                # Simplificacion: Si allow_musl es False, saltamos 'musl'.
                if "musl" in name and not allow_musl: continue
                
                download_url = asset["browser_download_url"]
                # Si encontramos uno bueno, paramos (o podriamos priorizar musl para alpine)
                break
            
            if not download_url: return False
            subprocess.run(["curl", "-L", "-o", output_name, download_url], check=True)
            return True
        except Exception as e:
            print(f"Error descargando asset: {e}")
            return False

    def _install_binary(self, tool, allow_musl=False):
        if shutil.which(tool):
            self._log_info(f"{tool} ya está instalado.")
            return
            
        self._log_info(f"Instalando {tool}...")
        original_cwd = os.getcwd()
        temp_dir = Path("/tmp/brainbash_bin")
        if temp_dir.exists(): shutil.rmtree(temp_dir)
        temp_dir.mkdir(exist_ok=True)
        
        sudo_prefix = " ".join(self.sudo_cmd)
        
        try:
            os.chdir(temp_dir)
            
            if tool == "eza":
                if self._download_github_asset("eza-community/eza", ".tar.gz", "eza.tar.gz", allow_musl):
                    subprocess.run("tar -xzf eza.tar.gz", shell=True)
                    # A veces descomprime en ./eza o ./bin/eza, asumimos ./eza o buscamos
                    if os.path.exists("eza"):
                        subprocess.run(f"{sudo_prefix} mv ./eza /usr/local/bin/", shell=True)
                    elif os.path.exists("./bin/eza"):
                        subprocess.run(f"{sudo_prefix} mv ./bin/eza /usr/local/bin/", shell=True)
                    else:
                        # Fallback generico: buscar archivo ejecutable
                        pass
                    subprocess.run(f"{sudo_prefix} chmod +x /usr/local/bin/eza", shell=True)
            elif tool == "bat":
                if self._download_github_asset("sharkdp/bat", ".tar.gz", "bat.tar.gz", allow_musl):
                    subprocess.run("tar -xzf bat.tar.gz", shell=True)
                    subprocess.run(f"{sudo_prefix} mv bat-*/bat /usr/local/bin/", shell=True)
                    subprocess.run(f"{sudo_prefix} chmod +x /usr/local/bin/bat", shell=True)
            elif tool == "fzf":
                if self._download_github_asset("junegunn/fzf", ".tar.gz", "fzf.tar.gz", allow_musl):
                    subprocess.run("tar -xzf fzf.tar.gz", shell=True)
                    subprocess.run(f"{sudo_prefix} mv fzf /usr/local/bin/", shell=True)
                    subprocess.run(f"{sudo_prefix} chmod +x /usr/local/bin/fzf", shell=True)
            elif tool == "tldr":
                # Tealdeer
                if self._download_github_asset("dbrgn/tealdeer", "linux", "tldr", allow_musl):
                    subprocess.run("chmod +x tldr", shell=True)
                    subprocess.run(f"{sudo_prefix} mv tldr /usr/local/bin/", shell=True)
            elif tool == "starship":
                subprocess.run("curl -sS https://starship.rs/install.sh | sh -s -- -y", shell=True)
                self._install_nerd_fonts()
            elif tool == "zoxide":
                 # Zoxide script installs to ~/.local/bin by default usually, but we forced /usr/local/bin before
                 # The script param --bin-dir requires write access.
                 # Using sudo if needed.
                 # Updated URL to use verified one if needed
                 cmd = f"curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | {sudo_prefix} sh -s -- --bin-dir /usr/local/bin"
                 subprocess.run(cmd, shell=True)
            
            self._log_info(f"{tool} instalado.")
        except Exception as e:
            self._log_error(f"Error {tool}: {e}")
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir, ignore_errors=True)
