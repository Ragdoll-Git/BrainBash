#!/bin/bash

# ==============================================================================
#  Refactorizado con principios SOLID/KISS/DRY
#  SCRIPT DE DESPLIEGUE DE ENTORNO MODERNIZADO (Debian 12/13)
#  Autor: Gemini 3 Pro
#  Prompter: Ragdoll
#  Licencia: MIT
#  Descripción: Entorno de desarrollo de terminal con AI local y en la nube
# ==============================================================================

set -e  # Abortar en error
set -u  # Abortar si falta variable

# --- I. CONFIGURACIÓN GLOBAL (Open/Closed Principle) ---

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Listas de Paquetes
BASE_PACKAGES=("curl" "git" "unzip" "fontconfig" "gpg" "zsh" "fzf" "bat" "zoxide" "python3-venv" "python3-pip")
DESKTOP_PACKAGES=("kitty" "gnome-shell-extension-desktop-icons-ng")

# Rutas
ZSH_CUSTOM="$HOME/.oh-my-zsh/custom"
GEMINI_DIR="$HOME/.gemini-cli"

# --- II. FUNCIONES UTILITARIAS ---

print_step() {
    echo -e "\n${GREEN}=== $1 ===${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

check_root_and_sudo() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}[ERROR] No ejecutes como root. Usa tu usuario normal (el script pedirá sudo).${NC}"
        exit 1
    fi
    if ! command -v sudo &> /dev/null; then
        echo -e "${RED}[ERROR] 'sudo' no encontrado. Instálalo primero.${NC}"
        exit 1
    fi
}

detect_environment() {
    # Retorna 0 (true) si es headless, 1 (false) si tiene escritorio
    if systemctl get-default 2>/dev/null | grep -q "graphical.target"; then
        return 1
    fi
    return 0
}

# --- III. FUNCIONES DEL NÚCLEO (Single Responsibility) ---

install_base_system() {
    print_step "Instalando Sistema Base"
    
    sudo apt update
    local packages=("${BASE_PACKAGES[@]}")

    # Lógica condicional para escritorio
    if ! detect_environment; then
        print_info "Entorno de escritorio detectado. Agregando paquetes GUI."
        packages+=("${DESKTOP_PACKAGES[@]}")
    else
        print_info "Entorno Headless (Servidor) detectado."
    fi

    sudo apt install -y "${packages[@]}"
    
    # Fix Batcat (Debian rename)
    if [ ! -f ~/.local/bin/bat ]; then
        mkdir -p ~/.local/bin
        ln -sf /usr/bin/batcat ~/.local/bin/bat
    fi
}

install_eza_safe() {
    # Instala eza intentando repos oficiales primero, fallback a binario
    if command -v eza &> /dev/null; then
        print_info "Eza ya está instalado."
        return
    fi

    print_info "Instalando Eza..."
    if apt-cache show eza &> /dev/null; then
        sudo apt install -y eza
    else
        print_info "Eza no en repos (Debian 12). Instalando binario..."
        local url="https://github.com/eza-community/eza/releases/latest/download/eza_x86_64-unknown-linux-gnu.tar.gz"
        wget -qO /tmp/eza.tar.gz "$url"
        tar -xzf /tmp/eza.tar.gz -C /tmp
        sudo mv /tmp/eza /usr/local/bin/eza
        sudo chmod +x /usr/local/bin/eza
        rm /tmp/eza.tar.gz
    fi
}

configure_shell_visuals() {
    print_step "Configurando Shell y Visuales"

    # 1. Oh My Zsh
    if [ ! -d "$HOME/.oh-my-zsh" ]; then
        sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    fi

    # 2. Starship
    if ! command -v starship &> /dev/null; then
        curl -sS https://starship.rs/install.sh | sh -s -- -y
    fi
    mkdir -p ~/.config/starship
    curl -s -o ~/.config/starship/starship.toml https://raw.githubusercontent.com/catppuccin/starship/main/themes/mocha.toml

    # 3. Kitty (Solo si no es Headless)
    if ! detect_environment; then
        mkdir -p ~/.config/kitty/themes
        curl -s -o ~/.config/kitty/themes/mocha.conf https://raw.githubusercontent.com/catppuccin/kitty/main/themes/mocha.conf
        touch ~/.config/kitty/kitty.conf
        if ! grep -q "include themes/mocha.conf" ~/.config/kitty/kitty.conf; then
            echo "include themes/mocha.conf" >> ~/.config/kitty/kitty.conf
        fi
        
        # Icono Desktop
        local desktop_dir=$(xdg-user-dir DESKTOP 2>/dev/null || echo ~/Desktop)
        if [ -d "$desktop_dir" ] && [ -f /usr/share/applications/kitty.desktop ]; then
             mkdir -p "$desktop_dir"
             cp /usr/share/applications/kitty.desktop "$desktop_dir/"
             chmod +x "$desktop_dir/kitty.desktop"
        fi
    fi
}

# --- IV. GESTIÓN DE MODELOS (DRY) ---

setup_ollama_service() {
    print_step "Configurando Ollama (Motor IA)"
    
    if ! command -v ollama &> /dev/null; then
        curl -fsSL https://ollama.com/install.sh | sh
    else
        print_info "Ollama ya instalado."
    fi

    # Configuración Systemd (Keep Alive)
    sudo mkdir -p /etc/systemd/system/ollama.service.d
    echo '[Service]
Environment="OLLAMA_KEEP_ALIVE=1m"' | sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null
    
    sudo systemctl daemon-reload
    sudo systemctl restart ollama
    
    print_info "Esperando arranque de API Ollama..."
    until curl -s http://localhost:11434/api/tags >/dev/null; do sleep 1; done
}

create_local_model() {
    local name="$1"
    local base_model="$2"
    local temp="$3"
    local stop_params="$4" # Opcional

    print_info "Creando modelo optimizado: $name (Base: $base_model)..."
    ollama pull "$base_model"
    
    # Construcción dinámica del Modelfile
    local modelfile="FROM $base_model
PARAMETER temperature $temp
PARAMETER num_ctx 4096
SYSTEM \"\"\"
Eres un asistente experto en Debian y Linux.
1. Respuestas cortas y directas.
2. Si pido comando, SOLO el comando.
3. Si requieres contexto, usa viñetas.
\"\"\""

    if [ -n "$stop_params" ]; then
        modelfile="$modelfile
$stop_params"
    fi

    # Hack para pasar el string multilinea a create
    echo "$modelfile" | ollama create "$name" -f -
}

select_and_install_models() {
    echo -e "${YELLOW}Selecciona modelos a instalar:${NC}"
    echo "1) Qwen (Rápido)"
    echo "2) Gemma (Balanceado)"
    echo "3) Phi-4 (Inteligente/Pesado)"
    echo "4) TODOS"
    read -p "Opción: " opt

    case $opt in
        1|4) 
            # Qwen necesita template especial, se lo agregamos hardcoded aqui por simplicidad o extendemos la funcion
            # Para mantener KISS, usaremos la funcion base, Qwen suele inferir bien, pero si falla el template, se añade.
            create_local_model "qwen-local" "qwen3:0.6b" "0.3" "" 
            ;;
    esac
    case $opt in
        2|4)
            local stops='PARAMETER stop "<end_of_turn>"
PARAMETER stop "user:"
PARAMETER stop "model:"'
            create_local_model "gemma-local" "gemma3:1b" "0.2" "$stops"
            ;;
    esac
    case $opt in
        3|4)
            create_local_model "phi-local" "phi4-mini" "0.1" ""
            ;;
    esac
}

# --- V. INTEGRACIÓN GEMINI (Seguridad mejorada) ---

setup_gemini_client() {
    print_step "Configurando Cliente Gemini"

    echo -e "${YELLOW}Ingresa tu Google API Key (No se mostrará):${NC}"
    read -sp "API Key: " api_key
    echo ""
    
    if [ -z "$api_key" ]; then
        echo "Clave vacía. Saltando configuración."
        return
    fi

    # 1. Crear entorno Python
    mkdir -p "$GEMINI_DIR"
    python3 -m venv "$GEMINI_DIR/venv"
    "$GEMINI_DIR/venv/bin/pip" install -q google-generativeai

    # 2. Crear script (SIN LA CLAVE HARDCODEADA)
    cat << 'EOF' > "$GEMINI_DIR/gemini_tool.py"
import sys
import os
import google.generativeai as genai

# SEGURIDAD: Leer variable de entorno
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: Variable GEMINI_API_KEY no encontrada.")
    sys.exit(1)

genai.configure(api_key=API_KEY)

config = {"temperature": 0.3, "max_output_tokens": 4096}
sys_instruct = "Eres un experto en Debian. Respuestas cortas y solo comandos si se pide."

model = genai.GenerativeModel("gemini-2.5-flash", generation_config=config, system_instruction=sys_instruct)

user_input = " ".join(sys.argv[1:]).strip()

try:
    if user_input:
        print(model.generate_content(user_input).text.strip())
    else:
        print("Gemini Chat (Ctrl+C salir)")
        chat = model.start_chat(history=[])
        while True:
            q = input("Gemini >>> ").strip()
            if q.lower() in ['exit','quit']: break
            if q: print(f"\n{chat.send_message(q).text.strip()}\n")
except Exception as e:
    print(f"Error: {e}")
EOF

    # 3. Guardar la clave en una variable exportada en .zshrc temporalmente para esta sesión y futura
    # Nota: Lo ideal es .zshenv o un gestor de secretos, pero para este scope .zshrc funciona.
    export GEMINI_API_KEY="$api_key" 
    
    # Añadir al .zshrc si no existe
    if ! grep -q "export GEMINI_API_KEY" ~/.zshrc; then
        echo "" >> ~/.zshrc
        echo "# Google Gemini Key" >> ~/.zshrc
        echo "export GEMINI_API_KEY=\"$api_key\"" >> ~/.zshrc
    fi
}

# --- VI. GENERACIÓN DE ARCHIVOS DE CONFIGURACIÓN ---

generate_zshrc() {
    print_step "Generando .zshrc final"
    
    # Hacemos backup si existe
    [ -f ~/.zshrc ] && cp ~/.zshrc ~/.zshrc.bak

    cat << 'EOF' > ~/.zshrc
# --- PATH & ZSH ---
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git)
source $ZSH/oh-my-zsh.sh

# --- ALIAS MODERNOS ---
alias ls="eza --icons --group-directories-first"
alias ll="eza -al --icons --group-directories-first"
alias cat="batcat"
alias cd="z"

# --- INIT ---
eval "$(zoxide init zsh)"
eval "$(starship init zsh)"
export BAT_THEME="Catppuccin Mocha"

# --- FUNCIONES IA (Helpers) ---
clean_think() { sed '/<think>/,/<\/think>/d'; }
clean_empty() { sed '/^$/d'; }

qwen() {
    [ -n "$1" ] && ollama run qwen-local "$*" | clean_think || ollama run qwen-local
}

gemma() {
    [ -n "$1" ] && ollama run gemma-local "$*" | clean_empty || ollama run gemma-local
}

phi() {
    [ -n "$1" ] && ollama run phi-local "$*" | clean_empty || ollama run phi-local
}

gemini() {
    if [ -f ~/.gemini-cli/gemini_tool.py ]; then
        ~/.gemini-cli/venv/bin/python ~/.gemini-cli/gemini_tool.py "$*"
    else
        echo "Gemini no configurado."
    fi
}

# --- SECRETOS ---
# (Se añadirán abajo automáticamente si se configuraron)
EOF

    # Si ya configuramos gemini en este run, asegurarnos que la key persista
    if [ -n "${GEMINI_API_KEY:-}" ]; then
        echo "export GEMINI_API_KEY=\"$GEMINI_API_KEY\"" >> ~/.zshrc
    fi
}

# --- VII. FUNCIÓN PRINCIPAL (ORQUESTADOR) ---

main() {
    check_root_and_sudo
    
    print_step "MENÚ DE INSTALACIÓN"
    read -p "¿Instalar Base y Dotfiles? (s/n): " do_base
    read -p "¿Configurar Ollama (Local AI)? (s/n): " do_ollama
    read -p "¿Configurar Gemini (Cloud AI)? (s/n): " do_gemini

    if [[ "$do_base" =~ ^[sS]$ ]]; then
        install_base_system
        install_eza_safe
        configure_shell_visuals
        generate_zshrc
        
        # Cambiar shell si es necesario
        if [ "$SHELL" != "$(which zsh)" ]; then
            print_info "Cambiando shell a Zsh..."
            sudo chsh -s $(which zsh) $USER
        fi
    fi

    if [[ "$do_ollama" =~ ^[sS]$ ]]; then
        setup_ollama_service
        select_and_install_models
    fi

    if [[ "$do_gemini" =~ ^[sS]$ ]]; then
        setup_gemini_client
    fi

    print_step "INSTALACIÓN COMPLETADA"
    echo "Reinicia tu terminal o ejecuta 'source ~/.zshrc' para empezar."
}

# Entry Point
main "$@"