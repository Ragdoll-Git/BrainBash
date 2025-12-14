#!/usr/bin/env python3

# ==========================================
# IMPORTACIONES
# ==========================================

import sys
import os
import subprocess
import time

from pathlib import Path
from src.managers import DebianManager, AlpineManager, FedoraManager
from src.utils import Logger, Colors, TUI
from src.dotfiles import DotfileManager

# ==========================================
# TEXTOS Y TRADUCCIONES DEL MENU (CONFIG)
# ==========================================

# 1. Definimos los textos visuales en variables
TXT_UPDATE  = "Actualizar sistema"
TXT_BASE    = "Archivos Base"
TXT_EXTRA   = "Paquetes Extra"
TXT_DOTS    = "Config personales"
TXT_MODELS  = "IA Local"
TXT_GEMINI  = "IA Nube (respaldo)"
TXT_INSTALL = "INSTALACION"

# 2. Creamos el mapa global usando esas variables
# Esto mapea: Variable (Texto) -> ID Interno
MENU_ACTION_MAP = {
    TXT_UPDATE:  "update",
    TXT_BASE:    "base",
    TXT_EXTRA:   "extra",
    TXT_DOTS:    "dots",
    TXT_MODELS:  "models",
    TXT_GEMINI:  "gemini",
    TXT_INSTALL: "INSTALL"
}

# ==========================================
# DEFINICIONES DE MENU Y DATOS
# ==========================================

# Modelos disponibles
MODELS_MAP = {
    "qwen": "qwen3:0.6b",
    "gemma": "gemma3:1b",
    "phi": "phi4-mini"
}

# Submenu: Paquetes Base
# Formato: (TAG_TECNICO, DESCRIPCION, ESTADO_DEFAULT)
MENU_BASE = [
    ("git", "Git (Control de versiones)", "ON"),
    ("zsh", "Zsh (Shell)", "ON"),
    ("python-dev", "Python Dev + Pip", "ON"),
    ("curl", "Curl", "ON")
]

# Submenu: Paquetes Extra
MENU_EXTRA = [
    ("eza", "Eza (ls moderno)", "ON"),
    ("bat", "Bat (cat moderno)", "ON"),
    ("fzf", "Fzf (Buscador difuso)", "ON"),
    ("tldr", "Tldr (Ayuda simplificada)", "ON"),
    ("zoxide", "Zoxide (Navegacion inteligente)", "ON"),
    ("starship", "Starship (Prompt)", "ON")
]

# Submenu: Modelos Local
MENU_MODELS = [
    ("qwen", "Qwen 3 (0.6B) - Ultraligero", "OFF"),
    ("gemma", "Gemma 3 (1B) - Balanceado ", "OFF"),
    ("phi", "Phi-4 (Mini) - Pesado", "OFF")
]

DOTFILES_MAP = {
    "zshrc": ".zshrc",
    "kitty.conf": ".config/kitty/kitty.conf",
    "starship.toml": ".config/starship.toml"
}

# ==========================================
# FUNCIONES DE INSTALACION
# ==========================================

def get_manager():
    try:
        with open("/etc/os-release") as f: data = f.read().lower()
        if "alpine" in data: return AlpineManager("alpine")
        if "fedora" in data: return FedoraManager("fedora")
        if "debian" in data or "ubuntu" in data: return DebianManager("debian")
    except: pass
    sys.exit(1)

def install_omz(logger):
    if (Path.home() / ".oh-my-zsh").exists():
        logger.info("[Skip] Oh My Zsh ya instalado.")
        return
    logger.info("Descargando Oh My Zsh...")
    subprocess.run('sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended', 
                   shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def setup_ollama(logger, selected_models):
    """Instala Ollama SOLO si hay modelos seleccionados"""
    if not selected_models: return

    # 1. Instalar Motor si falta
    if subprocess.run("command -v ollama", shell=True, stdout=subprocess.DEVNULL).returncode != 0:
        logger.step("Instalando Motor Ollama (Requerido para IA local)")
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)
    
    # 2. Descargar Modelos
    logger.info("Verificando servicio IA...")
    time.sleep(2)
    
    for menu_id in selected_models:
        tag = MODELS_MAP.get(menu_id)
        if tag:
            logger.step(f"IA Local: Descargando {tag}")
            try:
                subprocess.run(f"ollama pull {tag}", shell=True)
            except:
                logger.error(f"Fallo al descargar {tag}")

def setup_gemini(logger):
    """Configura el entorno para Gemini (Nube)"""
    logger.step("Configurando Gemini (Google AI)")
    
    # Rutas para el entorno virtual
    venv_path = Path.home() / ".gemini-cli" / "venv"
    script_dest = Path.home() / ".gemini-cli" / "gemini_tool.py"
    
    # 1. Crear Venv
    if not venv_path.exists():
        logger.info("Creando entorno virtual Python...")
        try:
            subprocess.run(["python3", "-m", "venv", str(venv_path)], check=True)
        except Exception as e:
            logger.error(f"No se pudo crear venv. Asegurate de instalar python3-venv. Error: {e}")
            return
    
    # 2. Instalar SDK de Google en el venv
    logger.info("Instalando librería google-generativeai...")
    pip_bin = venv_path / "bin" / "pip"
    try:
        subprocess.run([str(pip_bin), "install", "-q", "google-generativeai"], check=True)
    except:
        logger.error("Fallo pip install. Verifica tu internet.")
        return
    
    # 3. Crear script de puente (Wrapper)
    if not script_dest.exists():
        script_dest.parent.mkdir(parents=True, exist_ok=True)
        with open(script_dest, "w") as f:
            f.write("""
import sys
import os
import google.generativeai as genai

# Tu zshrc debe exportar esta variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: Variable GEMINI_API_KEY no configurada.")
    print("Edita tu ~/.zshrc y agrega: export GEMINI_API_KEY='tu_clave'")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

if len(sys.argv) < 2:
    print("Uso: gemini <pregunta>")
    sys.exit(0)

prompt = " ".join(sys.argv[1:])
try:
    response = model.generate_content(prompt)
    print(response.text)
except Exception as e:
    print(f"Error de API: {e}")
""")
    
    logger.success("Gemini configurado en ~/.gemini-cli/")
    logger.info("IMPORTANTE: Obtén tu API Key en aistudio.google.com y agrégala a tu .zshrc")

# ==========================================
# MAIN LOOP
# ==========================================

def main():
    manager = get_manager()
    tui = TUI()
    logger = Logger(Colors.BLUE)

    # ESTADO INICIAL
    state = {
        "update_sys": False, # Por defecto NO actualiza
        "pkgs_base": [x[0] for x in MENU_BASE],  # Por defecto todos ON
        "pkgs_extra": [x[0] for x in MENU_EXTRA], # Por defecto todos ON
        "models": [],       # Por defecto ningun modelo local
        "use_gemini": True, # Gemini SI por defecto
        "dotfiles": True    # Dotfiles SI por defecto
    }

    # Asegurate de que esto este definido arriba en tu archivo (Global o en main)
    # MENU_ACTION_MAP = { TXT_UPDATE: "update", TXT_BASE: "base", ... etc }

    while True:
        # Calcular textos para el menu principal
        c_base = len(state["pkgs_base"])
        c_extra = len(state["pkgs_extra"])
        c_models = len(state["models"])
        s_gemini = "SI" if state["use_gemini"] else "NO"
        s_update = "SI" if state["update_sys"] else "NO"
        s_dots = "SI" if state["dotfiles"] else "NO"

        main_menu_opts = [
            (TXT_UPDATE,  f"sudo apt update & upgrade     [{s_update}]"),
            (TXT_BASE,    f"Git, Python, Zsh, Curl        [{c_base} selecc]"),
            (TXT_EXTRA,   f"Eza, Bat, Fzf, Tldr, Zoxide   [{c_extra} selecc]"),
            (TXT_DOTS,    f"Configuraciones personales    [{s_dots}]"),
            (TXT_MODELS,  f"Qwen, Gemma, Phi4             [{c_models} selecc]"),
            (TXT_GEMINI,  f"Gemini 2.5 flash              [{s_gemini}]"),
            (TXT_INSTALL, f">> INICIAR INSTALACION (ENTER)<<")
        ]

        # 1. Obtenemos el texto visible (Ej: "Actualizar sistema")
        selection_text = tui.show_menu("Menu Principal BrainBash", "Configura tu instalación:", main_menu_opts)
        
        if selection_text is None:
            sys.exit(0)

        # 2. TRADUCCION: Convertimos texto visible a ID interno ("update", "base", etc)
        # Esto es vital para que coincida con tus if de abajo
        selection = MENU_ACTION_MAP.get(selection_text)

        # --- LOGICA DE NAVEGACION ---
        
        if selection == "update":
            state["update_sys"] = not state["update_sys"]

        elif selection == "base":
            current_opts = []
            for tag, desc, default in MENU_BASE:
                # CORRECCION: Usamos la clave correcta del state ("pkgs_base")
                status = "ON" if tag in state["pkgs_base"] else "OFF"
                current_opts.append((tag, desc, status))
            
            # Guardamos en "pkgs_base", no en "Archivos Base"
            state["pkgs_base"] = tui.show_checklist("Paquetes Base", "Selecciona componentes: |Espacio para seleccionar| |Enter para confirmar y volver|", current_opts)

        elif selection == "extra":
            current_opts = []
            for tag, desc, default in MENU_EXTRA:
                # CORRECCION: Usamos "pkgs_extra"
                status = "ON" if tag in state["pkgs_extra"] else "OFF"
                current_opts.append((tag, desc, status))
            state["pkgs_extra"] = tui.show_checklist("Paquetes Extra", "Herramientas modernas: |Espacio para seleccionar| |Enter para confirmar y volver|", current_opts)

        elif selection == "dots":
            state["dotfiles"] = not state["dotfiles"]

        elif selection == "models":
            current_opts = []
            for tag, desc, default in MENU_MODELS:
                status = "ON" if tag in state["models"] else "OFF"
                current_opts.append((tag, desc, status))
            state["models"] = tui.show_checklist("IA Local", "Selecciona modelos: |Espacio para seleccionar| |Enter para confirmar y volver|", current_opts)

        elif selection == "gemini":
            state["use_gemini"] = not state["use_gemini"]

        elif selection == "INSTALL":
            break

    # ==========================================
    # EJECUCION DE TAREAS (ORDEN ESPECIFICO)
    # ==========================================
    
    logger.step("INICIANDO DESPLIEGUE")

    # 1. Update (Opcional)
    if state["update_sys"]:
        manager.update()

    # 2. Paquetes (Base + Extra combinados)
    all_pkgs = state["pkgs_base"] + state["pkgs_extra"]
    if all_pkgs:
        logger.step("Fase 1: Instalando Paquetes")
        manager.install(all_pkgs)

    # 3. Shell (OMZ) - Se instala si seleccionó Zsh
    if "zsh" in state["pkgs_base"]:
        logger.step("Fase 2: Configurando Shell")
        install_omz(logger)

    # 4. Dotfiles
    if state["dotfiles"]:
        logger.step("Fase 3: Aplicando Dotfiles")
        repo_root = Path(__file__).parent.resolve()
        dm = DotfileManager(repo_root, Path.home())
        
        for src, dest in DOTFILES_MAP.items():
            dm.link(f"config/{src}", dest)
        logger.success("Configs aplicadas.")

    # 5. IA Local (Ollama + Modelos) - Solo si seleccionó modelos
    if state["models"]:
        logger.step("Fase 4: IA Local")
        setup_ollama(logger, state["models"])

    # 6. IA Nube (Gemini)
    if state["use_gemini"]:
        setup_gemini(logger)

    logger.step("FINALIZADO")
    logger.info("Reinicia tu terminal para ver los cambios. Puede hacerlo con 'exit' o 'source ~/.zshrc', y despues 'zsh'.")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
