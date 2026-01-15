import os
import shutil
import time
import subprocess
try:
    import pwd
except ImportError:
    pwd = None
from pathlib import Path

class DotfileManager:
    """
    Administra la creacion de enlaces simbolicos (symlinks)
    entre el repositorio y el directorio Home del usuario.
    """

    def __init__(self, repo_path: Path, home_path: Path):
        self.repo_path = repo_path
        self.home_path = home_path

    def _get_target_user(self):
        """Devuelve el usuario objetivo (SUDO_USER si existe, o actual)"""
        if "SUDO_USER" in os.environ:
            return os.environ["SUDO_USER"]
        return pwd.getpwuid(os.getuid()).pw_name

    def _ensure_dir(self, path: Path):
        """Intenta crear directorio, usando sudo si es necesario."""
        if path.exists():
            return

        try:
            print(f"[Info] Creando directorio: {path}")
            path.mkdir(parents=True, exist_ok=True)
            # Fix ownership immediately if created as root for a user
            user = self._get_target_user()
            subprocess.run(["chown", "-R", f"{user}:{user}", str(path)], check=False)

        except PermissionError:
            print(f"[Warn] Permiso denegado en {path}. Intentando con sudo...")
            try:
                # 1. Crear con sudo
                subprocess.run(["sudo", "mkdir", "-p", str(path)], check=True)
                
                # 2. Corregir permisos (chown al usuario actual)
                user = self._get_target_user()
                subprocess.run(["sudo", "chown", "-R", f"{user}:{user}", str(path)], check=True)
                print(f"[Fix] Directorio creado y permisos corregidos para {user}.")
            except Exception as e:
                print(f"[Error] Fallo fallback de sudo: {e}")
                raise

    def link(self, source_rel: str, dest_rel: str):
        """
        Crea un enlace simbolico.
        source_rel: Ruta relativa dentro del repo (ej: 'config/zshrc')
        dest_rel: Ruta relativa en el home (ej: '.zshrc')
        """
        source_file = self.repo_path / source_rel
        dest_file = self.home_path / dest_rel

        # 1. Verificar que el archivo origen existe en tu carpeta config
        if not source_file.exists():
            print(f"[Error] Archivo origen no encontrado: {source_file}")
            return

        # 2. Asegurar que el directorio destino existe
        self._ensure_dir(dest_file.parent)

        # 3. Verificar estado del destino
        if dest_file.is_symlink():
            # Si ya es un enlace y apunta al lugar correcto, no hacemos nada
            if dest_file.readlink() == source_file:
                print(f"[Skip] {dest_rel} ya esta correctamente enlazado.")
                return
            else:
                # Si apunta a otro lado, lo borramos (es un link roto o viejo)
                print(f"[Update] Actualizando enlace para {dest_rel}")
                dest_file.unlink()

        elif dest_file.exists():
            # Si es un archivo real, hacemos BACKUP
            timestamp = int(time.time())
            backup_name = f"{dest_file}.bak.{timestamp}"
            print(f"[Backup] Moviendo {dest_rel} a {backup_name}")
            shutil.move(str(dest_file), str(backup_name))

        # 4. Crear el enlace final
        try:
            dest_file.symlink_to(source_file)
            print(f"[Link] Creado: {dest_rel} -> {source_rel}")
        except PermissionError:
             print(f"[Warn] Permiso denegado al crear enlace. Intentando sudo...")
             try:
                 subprocess.run(["sudo", "ln", "-sf", str(source_file), str(dest_file)], check=True)
                 # Chown del link (usamos -h para no cambiar el target)
                 if pwd:
                     user = self._get_target_user()
                     subprocess.run(["sudo", "chown", "-h", f"{user}:{user}", str(dest_file)], check=True)
             except Exception as e:
                 print(f"[Error] Fallo enlace con sudo: {e}")
        except Exception as e:
            print(f"[Error] Fallo al enlazar {dest_rel}: {e}")
