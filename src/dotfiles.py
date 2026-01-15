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

    def __init__(self, repo_path: Path, home_path: Path, logger=None):
        self.repo_path = repo_path
        self.home_path = home_path
        self.logger = logger

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
            if self.logger: self.logger.info(f"Creando directorio: {path}")
            else: print(f"[Info] Creando directorio: {path}")
            
            path.mkdir(parents=True, exist_ok=True)
            # Fix ownership immediately if created as root for a user
            user = self._get_target_user()
            subprocess.run(["chown", "-R", f"{user}:{user}", str(path)], check=False)

        except PermissionError:
            # Silently handle permission escalation
            try:
                # 1. Crear con sudo
                subprocess.run(["sudo", "mkdir", "-p", str(path)], check=True)
                
                # 2. Corregir permisos (chown al usuario actual)
                user = self._get_target_user()
                subprocess.run(["sudo", "chown", "-R", f"{user}:{user}", str(path)], check=True)
                
                if self.logger: self.logger.verbose(f"[Fix] Directorio creado con sudo: {path}")
            except Exception as e:
                msg = f"Fallo fallback de sudo en {path}: {e}"
                if self.logger: self.logger.error(msg)
                else: print(f"[Error] {msg}")
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
            msg = f"Archivo origen no encontrado: {source_file}"
            if self.logger: self.logger.error(msg)
            else: print(f"[Error] {msg}")
            return

        # 2. Asegurar que el directorio destino existe
        self._ensure_dir(dest_file.parent)

        # 3. Verificar estado del destino
        if dest_file.is_symlink():
            # Si ya es un enlace y apunta al lugar correcto, no hacemos nada
            if dest_file.readlink() == source_file:
                if self.logger: self.logger.verbose(f"[Skip] {dest_rel} OK.")
                return
            else:
                # Si apunta a otro lado, lo borramos (es un link roto o viejo)
                if self.logger: self.logger.info(f"Actualizando enlace para {dest_rel}")
                else: print(f"[Update] Actualizando enlace para {dest_rel}")
                dest_file.unlink()

        elif dest_file.exists():
            # Si es un archivo real, hacemos BACKUP
            timestamp = int(time.time())
            backup_name = f"{dest_file}.bak.{timestamp}"
            
            msg = f"Moviendo {dest_rel} a {backup_name}"
            if self.logger: self.logger.warning(msg)
            else: print(f"[Backup] {msg}")
            
            shutil.move(str(dest_file), str(backup_name))

        # 4. Crear el enlace final
        try:
            dest_file.symlink_to(source_file)
            msg = f"Creado: {dest_rel} -> {source_rel}"
            if self.logger: self.logger.success(msg)
            else: print(f"[Link] {msg}")
            
        except PermissionError:
             # Try sudo without warning noise
             try:
                 subprocess.run(["sudo", "ln", "-sf", str(source_file), str(dest_file)], check=True)
                 # Chown del link (usamos -h para no cambiar el target)
                 if pwd:
                     user = self._get_target_user()
                     subprocess.run(["sudo", "chown", "-h", f"{user}:{user}", str(dest_file)], check=True)
                 
                 msg = f"Creado (sudo): {dest_rel} -> {source_rel}"
                 if self.logger: 
                    self.logger.success(msg)
                    self.logger.verbose("Accion realizada con sudo por permisos.")
                 else: print(f"[Link] {msg}")
                 
             except Exception as e:
                 msg = f"Fallo enlace con sudo: {e}"
                 if self.logger: self.logger.error(msg)
                 else: print(f"[Error] {msg}")
                 
        except Exception as e:
            msg = f"Fallo al enlazar {dest_rel}: {e}"
            if self.logger: self.logger.error(msg)
            else: print(f"[Error] {msg}")
