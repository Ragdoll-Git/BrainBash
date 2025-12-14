import subprocess
import os
import shutil
import json
import urllib.request
import platform
from pathlib import Path
from typing import List
from ..core import PackageManager

class DebianManager(PackageManager):
    def update(self):
        print("[Debian] Ejecutando actualización completa del sistema...")
        try:
            # Update (Listas) + Upgrade (Paquetes) + Autoremove (Limpieza)
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "upgrade", "-y"], check=True)
            subprocess.run(["sudo", "apt", "autoremove", "-y"], check=True)
        except subprocess.CalledProcessError:
            print("[Error] Falló la actualización. Continuando bajo su propio riesgo...")

    def install(self, packages: List[str]):
        apt_packages = []
        manual_packages = []
        
        # Mapeo de herramientas modernas a instalación manual
        modern_tools = ["eza", "bat", "htop", "fzf", "starship", "zoxide", "tldr"]

        for pkg in packages:
            # Mapeamos nombre generico a nombre de distro
            mapped = self._get_mapped_name(pkg)
            
            # Clasificamos
            if mapped in modern_tools or pkg in modern_tools:
                manual_packages.append(mapped)
            else:
                apt_packages.append(mapped)

        # 1. APT (Base)
        if apt_packages:
            # Agregamos python3-venv para Gemini
            extras = ["curl", "wget", "tar", "unzip", "python3-venv"] 
            to_install = list(set(apt_packages + extras))
            print(f"[APT] Instalando: {', '.join(to_install)}")
            try:
                subprocess.run(["sudo", "apt", "install", "-y"] + to_install, check=True)
            except subprocess.CalledProcessError:
                print("[Error] Fallo APT.")

        # 2. Binarios GitHub (Extra)
        for tool in manual_packages:
            self._install_binary(tool)
    
    def _get_arch_terms(self):
        arch = platform.machine().lower()
        if arch == "x86_64": return ["x86_64", "amd64"]
        if arch in ["aarch64", "arm64"]: return ["aarch64", "arm64"]
        return [arch]

    def _download_github_asset(self, repo, keyword, output_name, allow_musl=False):
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
                if "musl" in name and not allow_musl: continue
                download_url = asset["browser_download_url"]
                break
            
            if not download_url: return False
            subprocess.run(["curl", "-L", "-o", output_name, download_url], check=True)
            return True
        except: return False

    def _install_binary(self, tool):
        if shutil.which(tool):
            print(f"[Skip] {tool} ya está instalado.")
            return
            
        print(f"[Binario] Instalando {tool}...")
        original_cwd = os.getcwd()
        temp_dir = Path("/tmp/brainbash_bin")
        if temp_dir.exists(): shutil.rmtree(temp_dir)
        temp_dir.mkdir(exist_ok=True)
        
        try:
            os.chdir(temp_dir)
            
            if tool == "eza":
                if self._download_github_asset("eza-community/eza", ".tar.gz", "eza.tar.gz"):
                    subprocess.run("tar -xzf eza.tar.gz", shell=True)
                    subprocess.run("sudo mv ./eza /usr/local/bin/", shell=True)
                    subprocess.run("sudo chmod +x /usr/local/bin/eza", shell=True)
            elif tool == "bat":
                if self._download_github_asset("sharkdp/bat", ".tar.gz", "bat.tar.gz"):
                    subprocess.run("tar -xzf bat.tar.gz", shell=True)
                    subprocess.run("sudo mv bat-*/bat /usr/local/bin/", shell=True)
                    subprocess.run("sudo chmod +x /usr/local/bin/bat", shell=True)
            elif tool == "fzf":
                if self._download_github_asset("junegunn/fzf", ".tar.gz", "fzf.tar.gz"):
                    subprocess.run("tar -xzf fzf.tar.gz", shell=True)
                    subprocess.run("sudo mv fzf /usr/local/bin/", shell=True)
                    subprocess.run("sudo chmod +x /usr/local/bin/fzf", shell=True)
            elif tool == "tldr":
                if self._download_github_asset("dbrgn/tealdeer", "linux", "tldr", allow_musl=True):
                    subprocess.run("chmod +x tldr", shell=True)
                    subprocess.run("sudo mv tldr /usr/local/bin/", shell=True)
            elif tool == "starship":
                subprocess.run("curl -sS https://starship.rs/install.sh | sh -s -- -y", shell=True)
            elif tool == "zoxide":
                subprocess.run("curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh -s -- --bin-dir /usr/local/bin", shell=True)
            
            print(f"{tool} instalado.")
        except Exception as e:
            print(f"Error {tool}: {e}")
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    manager = DebianManager("debian")
    manager.update()