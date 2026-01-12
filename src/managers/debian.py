import subprocess
import os
import shutil
from pathlib import Path
from typing import List
from ..core import PackageManager

class DebianManager(PackageManager):
    def update(self):
        print("[Debian] Ejecutando actualización completa del sistema...")
        try:
            # sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y
            subprocess.run(self.sudo_cmd + ["apt", "update"], check=True)
            subprocess.run(self.sudo_cmd + ["apt", "upgrade", "-y"], check=True)
            subprocess.run(self.sudo_cmd + ["apt", "autoremove", "-y"], check=True)
            # Actualizamos pip aqui para evitar warnings al final
            print("[Debian] Actualizando pip...")
            subprocess.run(self.sudo_cmd + ["python3", "-m", "pip", "install", "--upgrade", "pip", "--break-system-packages"], check=False)
        except subprocess.CalledProcessError:
            print("[Error] Falló la actualización. Continuando bajo su propio riesgo...")

    def install(self, packages: List[str]):
        apt_packages = []
        manual_packages = []
        
        # Mapeo de herramientas modernas a instalación manual
        # SOLO starship queda manual
        modern_tools = ["starship"]

        for pkg in packages:
            # Mapeamos nombre generico a nombre de distro
            mapped = self._get_mapped_name(pkg)
            
            # Caso especial: eza -> exa en Debian Stable
            if pkg == "eza" or mapped == "eza": mapped = "exa"
            # Caso especial: tldr -> tealdeer (Rust version, mas rapida)
            if pkg == "tldr" or mapped == "tldr": mapped = "tealdeer"
            
            # Clasificamos
            if mapped in modern_tools:
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
                subprocess.run(self.sudo_cmd + ["apt", "install", "-y"] + to_install, check=True)
                
                # Post-Install Hacks (Symlinks)
                
                # 1. exa -> eza
                if "exa" in to_install:
                     if shutil.which("exa") and not shutil.which("eza"):
                         print("[Fix] Creando symlink eza -> exa...")
                         subprocess.run(self.sudo_cmd + ["ln", "-s", "/usr/bin/exa", "/usr/local/bin/eza"], check=False)
                
                # 2. bat -> batcat
                if "bat" in to_install:
                     if shutil.which("batcat") and not shutil.which("bat"):
                         print("[Fix] Creando symlink bat -> batcat...")
                         subprocess.run(self.sudo_cmd + ["ln", "-s", "/usr/bin/batcat", "/usr/local/bin/bat"], check=False)
                     
                     # 3. Instalar Tema Catppuccin Mocha
                     print("[Theme] Instalando Catppuccin Mocha para bat...")
                     # Obtener directorio de config (usamos batcat directo por si el symlink fallo o PATH)
                     # Si falla batcat, fallback hardcoded
                     try:
                         config_dir = subprocess.check_output(["batcat", "--config-dir"], text=True).strip()
                     except:
                         config_dir = "/job/.config/bat" if os.environ.get("HOME") == "/job" else f"{os.environ.get('HOME', '/root')}/.config/bat"

                     themes_dir = f"{config_dir}/themes"
                     subprocess.run(self.sudo_cmd + ["mkdir", "-p", themes_dir], check=False)
                     
                     theme_url = "https://raw.githubusercontent.com/catppuccin/bat/main/themes/Catppuccin%20Mocha.tmTheme"
                     subprocess.run(self.sudo_cmd + ["curl", "-L", "-o", f"{themes_dir}/Catppuccin Mocha.tmTheme", theme_url], check=False)
                     
                     print("[Theme] Reconstruyendo cache de bat...")
                     subprocess.run(self.sudo_cmd + ["batcat", "cache", "--build"], check=False)


                # 3. tealdeer -> tldr (A veces tealdeer instala 'tldr', a veces no)
                if "tealdeer" in to_install:
                     # Check if tldr binary exists, if not try to link tealdeer
                     if shutil.which("tealdeer") and not shutil.which("tldr"):
                          print("[Fix] Creando symlink tldr -> tealdeer...")
                          subprocess.run(self.sudo_cmd + ["ln", "-s", "/usr/bin/tealdeer", "/usr/local/bin/tldr"], check=False)
                     
                     # Actualizar cache de tldr
                     print("[TLDR] Actualizando cache (esto puede tardar)...")
                     import time
                     for i in range(3):
                         try:
                             print(f"   > Intento {i+1}/3...")
                             subprocess.run(self.sudo_cmd + ["tldr", "--update"], check=True)
                             print("[TLDR] Cache actualizado.")
                             break
                         except subprocess.CalledProcessError:
                             print(f"   [!] Fallo intento {i+1}. Reintentando en 3s...")
                             time.sleep(3)
                     else:
                         print("[Warning] No se pudo actualizar TLDR. Ejecuta 'tldr --update' manualmente luego.")


            except subprocess.CalledProcessError:
                print("[Error] Fallo APT.")

        # 2. Binarios GitHub (Extra)
        for tool in manual_packages:
            self._install_binary(tool)
    
    def _get_arch_terms(self):
        import platform
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
                if "musl" in name and not allow_musl: continue
                download_url = asset["browser_download_url"]
                break
            
            if not download_url: return False
            subprocess.run(["curl", "-L", "-o", output_name, download_url], check=True)
            return True
        except Exception as e:
            print(f"[DEBUG ERROR] Download failed: {e}")
            return False

    def _install_binary(self, tool):
        if shutil.which(tool):
            print(f"[Skip] {tool} ya está instalado.")
            return
            
        print(f"[Binario] Instalando {tool}...")
        original_cwd = os.getcwd()
        temp_dir = Path("/tmp/brainbash_bin")
        if temp_dir.exists(): shutil.rmtree(temp_dir)
        temp_dir.mkdir(exist_ok=True)
        
        sudo_prefix = " ".join(self.sudo_cmd)
        
        try:
            os.chdir(temp_dir)
            
            # Starship y Zoxide scripting (Zoxide ahora en APT, pero mantenemos script si manager < bookworm? No, asumimos migration total)
            # Aunque Zoxide en APT es version vieja? Debian Bookworm tiene 0.9.0.
            # Starship es el unico que queda aqui por ahora.
            
            if tool == "starship":
                subprocess.run("curl -sS https://starship.rs/install.sh | sh -s -- -y", shell=True)
            
            print(f"{tool} instalado.")
        except Exception as e:
            print(f"Error {tool}: {e}")
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    manager = DebianManager("debian")
    manager.update()