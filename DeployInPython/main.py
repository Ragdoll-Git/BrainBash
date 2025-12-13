#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Importaciones de nuestros modulos
from src.managers import DebianManager, AlpineManager, FedoraManager
from src.utils import Logger, Colors, TUI
from src.dotfiles import DotfileManager

# ==========================================
# CONFIGURACION
# ==========================================

# Paquetes que queremos en TODAS las maquinas
# Usamos nombres genericos, el Core se encarga de traducir
BASE_PACKAGES = [
    "git",
    "zsh",
    "curl",
    "fzf",
    "bat",   # En Debian instalara batcat automaticamente
    "python-dev"
]

# Archivos de configuracion (Repo -> Home)
# Clave: Ruta relativa en tu carpeta 'config/'
# Valor: Ruta relativa en el home del usuario
DOTFILES_MAP = {
    "zshrc": ".zshrc",
    "kitty.conf": ".config/kitty/kitty.conf",
    "starship.toml": ".config/starship.toml"
}

# ==========================================
# LOGICA PRINCIPAL
# ==========================================

def get_distro_manager():
    """
    Lee /etc/os-release para determinar la distribucion
    y retorna la clase Manager correspondiente.
    """
    try:
        with open("/etc/os-release") as f:
            os_info = f.read().lower()
            
        if "alpine" in os_info:
            return AlpineManager("alpine")
        elif "fedora" in os_info or "rhel" in os_info or "centos" in os_info:
            return FedoraManager("fedora")
        elif "debian" in os_info or "ubuntu" in os_info or "kali" in os_info:
            # Detectamos si es ubuntu o debian especificamente para el mapa
            distro_id = "ubuntu" if "ubuntu" in os_info else "debian"
            return DebianManager(distro_id)
        else:
            print("[Error] Distribucion no soportada automaticamente.")
            print("Soporte actual: Debian/Ubuntu, Alpine, Fedora.")
            sys.exit(1)
            
    except FileNotFoundError:
        print("[Error] No se pudo leer /etc/os-release.")
        sys.exit(1)

def main():
    # 1. Inicializacion y UI
    tui = TUI()
    
    # Vista previa de colores (opcional, como discutimos)
    Colors.preview_all()
    
    # Seleccion de tema usando Whiptail si existe
    theme_options = [
        (Colors.BLUE, "Azul (Estilo Debian)"),
        (Colors.GREEN, "Verde (Hacker)"),
        (Colors.MAGENTA, "Magenta (Cyberpunk)"),
        (Colors.RED, "Rojo (Alerta)")
    ]
    
    selected_color = tui.show_menu(
        "Configuracion Visual",
        "Selecciona el color base para los logs:",
        theme_options
    )
    
    logger = Logger(theme_color=selected_color)
    logger.step("INICIANDO DESPLIEGUE")

    # 2. Deteccion de Distro
    manager = get_distro_manager()
    logger.info(f"Sistema detectado. Usando gestor: {manager.__class__.__name__}")

    # 3. Menu de Acciones
    actions = [
        ("full", "Instalacion Completa (Paquetes + Dotfiles)"),
        ("pkgs", "Solo instalar Paquetes"),
        ("dots", "Solo enlazar Dotfiles (Config)"),
        ("exit", "Salir")
    ]

    action = tui.show_menu(
        "Menu Principal",
        "Que deseas hacer hoy?",
        actions
    )

    if action == "exit":
        sys.exit(0)

    # 4. Ejecucion de Tareas
    
    # --- FASE 1: PAQUETES ---
    if action in ["full", "pkgs"]:
        logger.step("Fase 1: Gestion de Paquetes")
        try:
            manager.update()
            manager.install(BASE_PACKAGES)
            logger.success("Paquetes instalados correctamente.")
        except Exception as e:
            logger.error(f"Fallo en la instalacion de paquetes: {e}")
            sys.exit(1)

    # --- FASE 2: DOTFILES ---
    if action in ["full", "dots"]:
        logger.step("Fase 2: Enlazando Dotfiles")
        
        repo_root = Path(os.getcwd())
        home_root = Path.home()
        
        dot_manager = DotfileManager(repo_root, home_root)
        
        for src, dest in DOTFILES_MAP.items():
            dot_manager.link(f"config/{src}", dest)
            
        logger.success("Enlaces simbolicos creados.")

    logger.step("DESPLIEGUE FINALIZADO")
    logger.info("Reinicia tu terminal o ejecuta 'zsh' para ver los cambios.")

if __name__ == "__main__":
    # Verificacion rapida de root (opcional, apt/apk pediran sudo si falta)
    if os.geteuid() == 0:
        print("[Warn] Estas ejecutando como root. Es recomendable usar usuario normal con sudo.")
        
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrumpido por el usuario.")
        sys.exit(0)