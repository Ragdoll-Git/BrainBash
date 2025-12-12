#!/bin/bash

# ==============================================================================
#  SCRIPT DE DESPLIEGUE DE ENTORNO MODERNIZADO (Debian 12/13)
#  Autor: Gemini 3 Pro
#  Prompter: Ragdoll
#  Licencia: MIT
#  Descripción: Configura Zsh, Kitty, Ollama (Local LLMs) y Gemini (Cloud Backup).
# ==============================================================================

# Configuración de seguridad
set -e
set -u

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Variables Globales
USER_HOME=$HOME
ZSH_CUSTOM="$USER_HOME/.oh-my-zsh/custom"

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}    DESPLIEGUE DE ENTORNO DEBIAN + IA (Público & Seguro) ${NC}"
echo -e "${BLUE}=========================================================${NC}"
echo "Este script es idempotente (seguro de correr varias veces)."
echo "Compatibilidad probada: Debian 12 (Bookworm) y Debian 13 (Trixie)."
echo ""

# --- COMPROBACIÓN DE ROOT/SUDO ---
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}[!] Por favor, NO ejecutes este script como root directo.${NC}"
    echo "Ejecútalo como tu usuario normal. El script pedirá sudo cuando sea necesario."
    exit 1
fi

# Verificar sudo
if ! command -v sudo &> /dev/null; then
    echo -e "${RED}[Error] 'sudo' no está instalado. Instálalo como root (apt install sudo) y agrega tu usuario al grupo sudo.${NC}"
    exit 1
fi

# --- MENÚ INTERACTIVO ---
echo -e "${YELLOW}--- SELECCIÓN DE COMPONENTES ---${NC}"
read -p "¿Instalar Paquetes Base (Kitty, Zsh, Eza, Bat, Fzf)? (s/n): " INSTALL_BASE
read -p "¿Configurar Dotfiles (Zshrc, Starship, Temas)? (s/n): " INSTALL_DOTFILES
read -p "¿Instalar Ollama y Modelos Locales? (s/n): " INSTALL_OLLAMA
read -p "¿Configurar Gemini CLI (Requiere API Key de Google)? (s/n): " INSTALL_GEMINI

# ==============================================================================
# 1. PAQUETES BASE (Soporte Debian 12/13)
# ==============================================================================
if [[ "$INSTALL_BASE" =~ ^[sS]$ ]]; then
    echo -e "\n${GREEN}[1/4] Instalando paquetes base...${NC}"
    
    sudo apt update
    sudo apt install -y curl git unzip fontconfig gpg

    # --- Instalación de EZA (Soporte para Debian 12) ---
    if ! command -v eza &> /dev/null; then
        echo "Configurando repositorio para 'eza'..."
        sudo mkdir -p -m 755 /etc/apt/keyrings
        wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg --yes
        echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de/stable/ /" | sudo tee /etc/apt/sources.list.d/gierens.list
        sudo chmod 644 /etc/apt/keyrings/gierens.gpg /etc/apt/sources.list.d/gierens.list
        sudo apt update
        sudo apt install -y eza
    else
        echo "Eza ya instalado."
    fi

    # Instalar resto de herramientas
    sudo apt install -y kitty zsh fzf bat zoxide python3-venv python3-pip \
                        gnome-shell-extension-desktop-icons-ng

    # Fix batcat -> bat
    if [ ! -f ~/.local/bin/bat ]; then
        mkdir -p ~/.local/bin
        ln -s /usr/bin/batcat ~/.local/bin/bat
        echo "Symlink creado para batcat."
    fi
fi

# ==============================================================================
# 2. DOTFILES Y ZSH
# ==============================================================================
if [[ "$INSTALL_DOTFILES" =~ ^[sS]$ ]]; then
    echo -e "\n${GREEN}[2/4] Configurando entorno Shell...${NC}"

    # Oh My Zsh (Idempotente)
    if [ ! -d "$HOME/.oh-my-zsh" ]; then
        sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    fi

    # Starship
    if ! command -v starship &> /dev/null; then
        curl -sS https://starship.rs/install.sh | sh -s -- -y
    fi
    mkdir -p ~/.config/starship
    curl -s -o ~/.config/starship/starship.toml https://raw.githubusercontent.com/catppuccin/starship/main/themes/mocha.toml

    # Kitty Theme
    mkdir -p ~/.config/kitty/themes
    curl -s -o ~/.config/kitty/themes/mocha.conf https://raw.githubusercontent.com/catppuccin/kitty/main/themes/mocha.conf
    # Evitar duplicados en kitty.conf
    touch ~/.config/kitty/kitty.conf
    if ! grep -q "include themes/mocha.conf" ~/.config/kitty/kitty.conf; then
        echo "include themes/mocha.conf" >> ~/.config/kitty/kitty.conf
    fi

    # Iconos Escritorio (Solo copia si existe kitty)
    if [ -f /usr/share/applications/kitty.desktop ]; then
        mkdir -p $(xdg-user-dir DESKTOP)
        cp /usr/share/applications/kitty.desktop $(xdg-user-dir DESKTOP)/
        chmod +x $(xdg-user-dir DESKTOP)/kitty.desktop
    fi

    # --- GENERAR .ZSHRC ---
    echo "Generando .zshrc optimizado..."
    cat << 'EOF' > ~/.zshrc
# PATH configuration
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git)
source $ZSH/oh-my-zsh.sh

# --- CONFIGURACIÓN PERSONAL MODERNA ---
alias ls="eza --icons --group-directories-first"
alias ll="eza -al --icons --group-directories-first"
alias cat="batcat"

# Zoxide & Starship
eval "$(zoxide init zsh)"
alias cd="z"
eval "$(starship init zsh)"
export BAT_THEME="Catppuccin Mocha"

# --- FUNCIONES LLM ---

# Qwen (Local)
qwen:() {
    if [ -n "$1" ]; then
        ollama run qwen-local "$*" | sed '/<think>/,/<\/think>/d'
    else
        ollama run qwen-local
    fi
}

# Gemma (Local)
gemma:() {
    if [ -n "$1" ]; then
        ollama run gemma-local "$*" | sed '/^$/d'
    else
        ollama run gemma-local
    fi
}

# Phi (Local)
phi:() {
    if [ -n "$1" ]; then
        ollama run phi-local "$*" | sed '/^$/d'
    else
        ollama run phi-local
    fi
}

# Gemini (Cloud Backup)
gemini:() {
    if [ -f ~/.gemini-cli/gemini_tool.py ]; then
        ~/.gemini-cli/venv/bin/python ~/.gemini-cli/gemini_tool.py "$*"
    else
        echo "Gemini no está configurado. Ejecuta el script de instalación nuevamente."
    fi
}
EOF
    
    # Cambiar shell
    if [ "$SHELL" != "$(which zsh)" ]; then
        echo "Cambiando shell por defecto a Zsh..."
        sudo chsh -s $(which zsh) $USER
    fi
fi

# ==============================================================================
# 3. OLLAMA Y MODELOS
# ==============================================================================
if [[ "$INSTALL_OLLAMA" =~ ^[sS]$ ]]; then
    echo -e "\n${GREEN}[3/4] Configurando IA Local (Ollama)...${NC}"

    # Instalar Ollama si no existe
    if ! command -v ollama &> /dev/null; then
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "Ollama ya está instalado."
    fi

    # Configuración de Keep-Alive (Optimización RAM)
    echo "Configurando liberación de RAM (1 min)..."
    sudo mkdir -p /etc/systemd/system/ollama.service.d
    echo '[Service]
Environment="OLLAMA_KEEP_ALIVE=1m"' | sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null
    sudo systemctl daemon-reload
    sudo systemctl restart ollama
    
    # Esperar servicio
    echo "Esperando a Ollama..."
    until curl -s http://localhost:11434/api/tags >/dev/null; do sleep 1; done

    # --- SELECCIÓN DE MODELOS ---
    echo -e "${YELLOW}Selecciona qué modelos locales deseas instalar:${NC}"
    echo "1) Qwen 3 0.6B (Muy rápido, ligero)"
    echo "2) Gemma 3 1B (Balanceado de Google)"
    echo "3) Phi-4 Mini (Más inteligente, Microsoft)"
    echo "4) TODOS (Recomendado si tienes +4GB RAM)"
    read -p "Opción (1-4): " MODEL_OPT

    if [[ "$MODEL_OPT" == "1" || "$MODEL_OPT" == "4" ]]; then
        echo "Instalando Qwen..."
        ollama pull qwen3:0.6b
        ollama create qwen-local -f <(echo 'FROM qwen3:0.6b
PARAMETER temperature 0.3
PARAMETER num_ctx 4096
TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
"""
SYSTEM """
Eres un asistente técnico experto en Debian.
1. Respuestas cortas y al grano.
2. Solo entrega el comando si se solicita.
3. No saludes.
"""')
    fi

    if [[ "$MODEL_OPT" == "2" || "$MODEL_OPT" == "4" ]]; then
        echo "Instalando Gemma..."
        ollama pull gemma3:1b
        ollama create gemma-local -f <(echo 'FROM gemma3:1b
PARAMETER temperature 0.2
PARAMETER num_ctx 4096
PARAMETER stop "<end_of_turn>"
PARAMETER stop "<|file_separator|>"
PARAMETER stop "user:"
PARAMETER stop "model:"
SYSTEM """
Eres un asistente técnico experto en Debian.
Instrucciones estrictas:
1. Respuestas cortas y directas.
2. No saludes.
"""')
    fi

    if [[ "$MODEL_OPT" == "3" || "$MODEL_OPT" == "4" ]]; then
        echo "Instalando Phi-4..."
        ollama pull phi4-mini
        ollama create phi-local -f <(echo 'FROM phi4-mini
PARAMETER temperature 0.1
PARAMETER num_ctx 4096
SYSTEM """
Eres un asistente técnico experto en Debian.
Instrucciones estrictas: Respuestas cortas, solo comandos, sin saludos.
"""')
    fi
fi

# ==============================================================================
# 4. GEMINI CLI (BACKUP CLOUD)
# ==============================================================================
if [[ "$INSTALL_GEMINI" =~ ^[sS]$ ]]; then
    echo -e "\n${GREEN}[4/4] Configurando Gemini CLI...${NC}"
    
    # -----------------------------------------------------
    # SEGURIDAD: SOLICITUD DE API KEY
    # -----------------------------------------------------
    echo -e "${RED}IMPORTANTE:${NC} Necesitas una API Key de Google AI Studio."
    echo "Puedes obtenerla gratis en: https://aistudio.google.com/app/apikey"
    echo ""
    while true; do
        read -sp ">> Pega tu Google API Key aquí (el input está oculto): " USER_API_KEY
        echo ""
        if [[ -z "$USER_API_KEY" ]]; then
            echo "La clave no puede estar vacía."
        else
            break
        fi
    done

    # Configuración de entorno
    mkdir -p ~/.gemini-cli
    python3 -m venv ~/.gemini-cli/venv
    ~/.gemini-cli/venv/bin/pip install -q google-generativeai

    echo "Generando script Python con tu clave..."
    
    # Escribimos el script inyectando la variable $USER_API_KEY
    cat << EOF > ~/.gemini-cli/gemini_tool.py
import sys
import google.generativeai as genai

# --- API KEY CONFIGURADA POR EL USUARIO ---
API_KEY = "${USER_API_KEY}"

genai.configure(api_key=API_KEY)

# Configuración
generation_config = {
  "temperature": 0.3,
  "max_output_tokens": 4096,
}

system_instruction = """
Eres un asistente experto en Debian y Linux.
1. Respuestas cortas y directas.
2. Si pido comando, SOLO el comando.
3. Si requieres contexto, usa viñetas.
"""

model = genai.GenerativeModel(
  model_name="gemini-2.5-flash",
  generation_config=generation_config,
  system_instruction=system_instruction
)

# Lógica Principal
user_input = " ".join(sys.argv[1:]).strip()

if user_input:
    # Modo Comando (Rápido)
    try:
        response = model.generate_content(user_input)
        print(response.text.strip())
    except Exception as e:
        print(f"Error de API: {e}")
else:
    # Modo Chat (Interactivo)
    print("\033[1;34m🤖 Gemini Chat (Ctrl+C para salir)\033[0m")
    chat = model.start_chat(history=[])
    while True:
        try:
            q = input("\033[1;32mGemini >>> \033[0m").strip()
            if q.lower() in ['salir', 'exit']: break
            if not q: continue
            response = chat.send_message(q)
            print(f"\n{response.text.strip()}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}\n")
EOF

    echo "Gemini configurado correctamente."
fi

echo -e "\n${BLUE}=========================================================${NC}"
echo -e "${BLUE}    ¡INSTALACIÓN COMPLETADA!                             ${NC}"
echo -e "${BLUE}=========================================================${NC}"
echo "1. Reinicia tu terminal o ejecuta: source ~/.zshrc"
echo "2. Usa 'ollama:', 'gemma:', 'phi:' o 'gemini:' para interactuar."
echo "3. ¡Disfruta!"
