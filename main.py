#!/usr/bin/env python3

# ==========================================
# IMPORTACIONES
# ==========================================

import sys
import os
import shutil
import subprocess
import time
import textwrap

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
    "phi": "phi4-mini:latest"
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
    ("htop", "Htop (Monitor de recursos)", "ON"),
    ("fzf", "Fzf (Buscador difuso)", "ON"),
    ("tldr", "Tldr (Ayuda simplificada)", "ON"),
    ("zoxide", "Zoxide (Navegacion inteligente)", "ON"),
    ("starship", "Starship (Prompt)", "ON")
]

# Submenu: Modelos Local
MENU_MODELS = [
    ("qwen", "Qwen 3 (0.6B) - Ligero (523MB-40K)", "ON"),
    ("gemma", "Gemma 3 (1B) - Balanceado (815MB-32K)", "OFF"),
    ("phi", "Phi-4 Mini (3.84 B) - Pesado (2.5GB-128K)", "OFF")
]

DOTFILES_MAP = {
    "zshrc": ".zshrc",
    "kitty.conf": ".config/kitty/kitty.conf",
    "starship.toml": ".config/starship.toml",
    "context.md": ".config/brainbash/context.md"
}

# ==========================================
# FUNCIONES DE INSTALACION
# ==========================================

def get_manager():
    """
    Detecta el gestor de paquetes basado en /etc/os-release (ID y ID_LIKE).
    Retorna la instancia del Manager correspondiente o sale con error.
    """
    try:
        os_info = {}
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        # Eliminar comillas si existen
                        os_info[k] = v.strip('"').strip("'")
        
        distro_id = os_info.get("ID", "").lower()
        distro_like = os_info.get("ID_LIKE", "").lower()
        
        # 1. Alpine
        if distro_id == "alpine":
            return AlpineManager("alpine")
            
        # 2. Fedora / RedHat family
        if distro_id in ["fedora", "rhel", "centos", "almalinux", "rocky"] or "fedora" in distro_like:
            return FedoraManager("fedora")
            
        # 3. Debian / Ubuntu family
        if distro_id in ["debian", "ubuntu", "linuxmint", "pop", "kali"] or "debian" in distro_like or "ubuntu" in distro_like:
            return DebianManager("debian")
            
    except Exception as e:
        print(f"[Error] Fallo la deteccion de OS: {e}")

    # Fallback o error total
    print("[Error] Sistema operativo no soportado o no detectado.")
    print("Sistemas soportados: Debian/Ubuntu, Fedora/RHEL, Alpine.")
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

    def ensure_ollama_running():
        # Check simple
        if subprocess.run("ollama list", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return True
        
        logger.info("Iniciando servidor Ollama...")
        # Start in background
        try:
            # Asegurar que ~/.local/bin este en el PATH para el subprocess
            env = os.environ.copy()
            user_bin = Path.home() / ".local" / "bin"
            if str(user_bin) not in env["PATH"]:
                env["PATH"] = f"{user_bin}:{env['PATH']}"

            # Usamos Popen para no bloquear, redirigiendo salida a archivo para debug
            log_path = Path("ollama.log")
            with open(log_path, "w") as log_file:
                 subprocess.Popen(["ollama", "serve"], stdout=log_file, stderr=subprocess.STDOUT, env=env)
        except Exception as e:
            logger.error(f"No se pudo iniciar Ollama: {e}")
            return False

        # Wait loop (max 10s)
        logger.info("Esperando servicio...")
        for _ in range(20):
            time.sleep(0.5)
            # Check with env
            if subprocess.run("ollama list", shell=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                logger.success("Servidor Ollama iniciado.")
                return True
        
        # Si falló, mostramos las ultimas lineas del log
        if log_path.exists():
            try:
                with open(log_path, "r") as f:
                    logger.error(f"Log de Ollama (Ultimas lineas):\n{f.read()[-500:]}")
            except: pass
            
        return False

    # 1. Instalar Motor si falta
    # Verificamos PATH manual
    user_bin = Path.home() / ".local" / "bin"
    ollama_bin = user_bin / "ollama"
    
    is_installed = False
    if ollama_bin.exists():
        is_installed = True
    elif subprocess.run("command -v ollama", shell=True, stdout=subprocess.DEVNULL).returncode == 0:
         is_installed = True

    if not is_installed:
        logger.step("Instalando Motor Ollama (Requerido para IA local)")
        # 1. Intento descarga manual directa (GitHub)
        installed_manual = False
        try:
            logger.info("Intentando descarga directa desde GitHub...")
            arch = os.uname().machine
            if arch == "x86_64": arch = "amd64"
            elif arch in ["aarch64", "arm64"]: arch = "arm64"
            
            url = f"https://github.com/ollama/ollama/releases/latest/download/ollama-linux-{arch}.tgz"
            
            # Dir temporal
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdirname:
                tmp_tar = Path(tmpdirname) / "ollama.tgz"
                subprocess.run(["curl", "-L", "-o", str(tmp_tar), url], check=True)
                subprocess.run(["tar", "-xzf", str(tmp_tar), "-C", tmpdirname], check=True)
                
                # Mover binario
                binary_src = Path(tmpdirname) / "bin" / "ollama" 
                # A veces el tar tiene ./bin/ollama o solo ./ollama?
                # Revisar estructura: ollama-linux-amd64.tgz -> ./bin/ollama
                
                if not binary_src.exists():
                     # Intento raiz
                     binary_src = Path(tmpdirname) / "ollama"
                
                if binary_src.exists():
                    user_bin.mkdir(parents=True, exist_ok=True)
                    target = user_bin / "ollama"
                    shutil.copy2(binary_src, target)
                    target.chmod(0o755)
                    logger.success(f"Ollama instalado en {target}")
                    installed_manual = True
                else:
                    logger.warning("No se encontro binario en el tgz.")

        except Exception as e:
            logger.error(f"Fallo descarga manual: {e}")
        
        # 2. Fallback a Script
        if not installed_manual:
             logger.info("Usando script de instalacion (Fallback)...")
             try:
                local_script = Path(__file__).parent / "src" / "scripts" / "install_ollama.sh"
                if local_script.exists():
                    subprocess.run(f"sh {local_script}", shell=True, check=True)
                else:
                    subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
             except subprocess.CalledProcessError:
                logger.error("Fallo la instalacion de Ollama.")
                return

    if not ensure_ollama_running():
         logger.error("No se pudo conectar a Ollama. Ejecuta 'ollama serve' manualmente.")
         return

    # 2. Leer contexto compartido
    context_path = Path.home() / ".config" / "brainbash" / "context.md"
    system_prompt = ""
    if context_path.exists():
        try:
            with open(context_path, "r") as f:
                # Escapamos comillas triples para no romper el Modelfile
                system_prompt = f.read().strip().replace('"""', '\\"\\"\\"')
                logger.info("Contexto compartido cargado.")
        except Exception as e:
            logger.error(f"Error leyendo contexto: {e}")

    # 3. Descargar Modelos y crear alias
    logger.info("Verificando servicio IA...")
    time.sleep(2)
    
    for menu_id in selected_models:
        tag_original = MODELS_MAP.get(menu_id) # qwen3:0.6b
        
        # Definimos el nombre que espera el zshrc
        tag_alias = f"{menu_id}-local"         # Ej: qwen-local
        
        if tag_original:
            logger.step(f"IA Local: Configurando {tag_alias}")
            try:
                # 1. Pull del original
                logger.info(f"Descargando base: {tag_original}...")
                subprocess.run(f"ollama pull {tag_original}", shell=True, check=True)
                
                # 2. Crear Modelfile usando la plantilla
                if system_prompt:
                    logger.info(f"Creando {tag_alias} con contexto...")
                    
                    template_path = Path(__file__).parent / "config" / "Modelfile"
                    if not template_path.exists():
                         logger.error("No se encontro config/Modelfile")
                         continue

                    with open(template_path, "r") as f:
                        template_content = f.read()
                    
                    # Reemplazamos las variables
                    final_modelfile = template_content.replace("${BASE_MODEL}", tag_original)
                    final_modelfile = final_modelfile.replace("${SYSTEM_PROMPT}", system_prompt)

                    # Escribimos el archivo final temporalmente
                    modelfile_path = "Modelfile.gen"
                    try:
                        with open(modelfile_path, "w", encoding="utf-8") as f:
                            f.write(final_modelfile)
                        
                        subprocess.run(
                            ["ollama", "create", tag_alias, "-f", modelfile_path],
                            check=True
                        )
                    finally:
                         if os.path.exists(modelfile_path):
                            os.remove(modelfile_path)
                else:
                    # Fallback al viejo "cp" si no hay contexto
                    logger.info(f"Creando alias (sin contexto): {tag_alias}...")
                    subprocess.run(f"ollama cp {tag_original} {tag_alias}", shell=True, check=True)
                
                # 3. Crear wrapper (script ejecutable)
                bin_dir = Path.home() / ".local" / "bin"
                bin_dir.mkdir(parents=True, exist_ok=True)
                
                wrapper_path = bin_dir / menu_id
                logger.info(f"Creando comando: {menu_id}...")
                
                with open(wrapper_path, "w") as f:
                    # $@ pasa todos los argumentos al comando ollama
                    f.write(f'#!/bin/sh\nexec ollama run {tag_alias} "$@"\n')
                
                # Hacer ejecutable (+x)
                wrapper_path.chmod(0o755)

            except subprocess.CalledProcessError as e:
                logger.error(f"Fallo al configurar {tag_alias}: {e}")

def setup_gemini(logger, tui):
    """Configura Gemini usando el script src/gemini_tool.py"""
    logger.step("Configurando Gemini (Google AI)")
    
    # 0. Preguntar por API Key
    print("\n--- Configuracion de API Key ---")
    print("Si tienes una API Key de Google Gemini, ingrésala ahora.")
    print("Si no, presiona Enter para configurar después.")
    api_key = input("API Key > ").strip()
    
    if api_key:
        secrets_path = Path.home() / ".brainbash_secrets"
        try:
            # Escribir en archivo de secretos (siempre override o append, aqui simplificamos create)
            with open(secrets_path, "w") as f:
                f.write(f"export GEMINI_API_KEY='{api_key}'\n")
            logger.success("API Key guardada en ~/.brainbash_secrets")
        except Exception as e:
            print(f"[Error] No se pudo guardar la Key: {e}")
    else:
        print("[INFO] Saltando configuración de Key. Recuerda agregarla manualmente luego en ~/.brainbash_secrets")
    
    # 1. Definir rutas
    # Ubicacion del codigo fuente en tu proyecto
    source_script = Path(__file__).parent / "src" / "gemini_tool.py"
    
    # Destinos
    venv_path = Path.home() / ".gemini-cli" / "venv" 
    bin_dir = Path.home() / ".local" / "bin"
    dest_script = bin_dir / "gemini" 
    
    # Asegurar directorios
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    if not source_script.exists():
        logger.error(f"No se encontro el archivo fuente: {source_script}")
        return

    # 2. Crear Venv (si falta)
    if not venv_path.exists():
        logger.info("Creando entorno virtual...")
        try:
            subprocess.run(["python3", "-m", "venv", str(venv_path)], check=True)
        except Exception as e:
            logger.error(f"Error creando venv: {e}")
            return
    
    # 3. Instalar librerias
    logger.info("Instalando dependencias...")
    pip_bin = venv_path / "bin" / "pip"
    python_bin = venv_path / "bin" / "python3"
    
    try:
        # Actualizar pip primero para evitar warnings
        subprocess.run([str(pip_bin), "install", "-q", "--upgrade", "pip"], check=True)
        subprocess.run([str(pip_bin), "install", "-q", "google-generativeai"], check=True)
    except:
        logger.error("Fallo pip install.")
        return
    
    # 4. Instalar el script con el Shebang Magico
    logger.info("Instalando script ejecutable...")
    try:
        # Leemos tu codigo original
        with open(source_script, "r") as f:
            original_code = f.read()
            
        # Le agregamos la linea que le dice "Usa el Python del venv"
        shebang = f"#!{python_bin}\n"
        final_content = shebang + original_code
        
        # Escribimos en ~/.local/bin/gemini
        with open(dest_script, "w") as f:
            f.write(final_content)
            
        # Hacemos ejecutable
        dest_script.chmod(0o755)
        logger.success("Gemini instalado correctamente.")
        
    except Exception as e:
        logger.error(f"Error al instalar script: {e}")

# ==========================================
# MAIN LOOP
# ==========================================

def main():
    manager = get_manager()
    tui = TUI()
    logger = Logger(Colors.GREEN)

    # ESTADO INICIAL
    state = {
        "update_sys": False, # Por defecto NO actualiza
        "pkgs_base": [x[0] for x in MENU_BASE],  # Por defecto todos ON
        "pkgs_extra": [x[0] for x in MENU_EXTRA], # Por defecto todos ON
        "models": [],       # Por defecto ningun modelo local
        "use_gemini": True, # Gemini SI por defecto
        "dotfiles": True    # Dotfiles SI por defecto
    }

    while True:
        # Calcular textos para el menu principal
        c_base = len(state["pkgs_base"])
        c_extra = len(state["pkgs_extra"])
        c_models = len(state["models"])
        s_gemini = "SI" if state["use_gemini"] else "NO"
        s_update = "SI" if state["update_sys"] else "NO"
        s_dots = "SI" if state["dotfiles"] else "NO"

        prefix = "sudo " if os.geteuid() != 0 else ""
        main_menu_opts = [
            (TXT_UPDATE,  f"{prefix} update & upgrade           [{s_update}]"),
            (TXT_BASE,    f"Git, Python, Zsh, Curl              [{c_base} selecc]"),
            (TXT_EXTRA,   f"Eza, Bat, Fzf, Tldr, Zoxide, Htop   [{c_extra} selecc]"),
            (TXT_DOTS,    f"Configuraciones personales          [{s_dots}]"),
            (TXT_MODELS,  f"Qwen, Gemma, Phi4                   [{c_models} selecc]"),
            (TXT_GEMINI,  f"Gemini 2.5 flash                    [{s_gemini}]"),
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
        logger.step("Instalando Paquetes")
        manager.install(all_pkgs)

    # 3. Shell (OMZ) - Se instala si seleccionó Zsh
    if "zsh" in state["pkgs_base"]:
        logger.step("Configurando Shell")
        install_omz(logger)

    # 4. Dotfiles
    if state["dotfiles"]:
        logger.step("Aplicando Config. Personales")
        repo_root = Path(__file__).parent.resolve()
        dm = DotfileManager(repo_root, Path.home())
        
        for src, dest in DOTFILES_MAP.items():
            dm.link(f"config/{src}", dest)
        logger.success("Configs aplicadas.")

    # 5. IA Local (Ollama + Modelos)
    if state["models"]:
        logger.step("Configurando IA Local")
        setup_ollama(logger, state["models"])

    # 6. IA Nube (Gemini)
    if state["use_gemini"]:
        setup_gemini(logger, tui)

    logger.step("FINALIZADO")
    logger.info("Reinicia tu terminal para ver los cambios. O usa 'zsh' para iniciar.")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)