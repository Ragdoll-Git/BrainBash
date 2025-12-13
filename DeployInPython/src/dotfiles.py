import os
import shutil
import time
from pathlib import Path

class DotfileManager:
    """
    Administra la creacion de enlaces simbolicos (symlinks)
    entre el repositorio y el directorio Home del usuario.
    """

    def __init__(self, repo_path: Path, home_path: Path):
        self.repo_path = repo_path
        self.home_path = home_path

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
        if not dest_file.parent.exists():
            print(f"[Info] Creando directorio: {dest_file.parent}")
            dest_file.parent.mkdir(parents=True, exist_ok=True)

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
        except Exception as e:
            print(f"[Error] Fallo al enlazar {dest_rel}: {e}")