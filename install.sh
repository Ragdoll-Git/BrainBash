#!/bin/bash

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Iniciando Bootstrap de BrainBash ===${NC}"

# 1. Detectar gestor de paquetes e instalar dependencias mínimas (Git + Python)
echo -e "${GREEN}[+] Verificando dependencias mínimas...${NC}"

if [ -f /etc/debian_version ]; then
    # Debian / Ubuntu
    if ! command -v git &> /dev/null || ! command -v python3 &> /dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq git python3
    fi
elif [ -f /etc/alpine-release ]; then
    # Alpine
    if ! command -v git &> /dev/null || ! command -v python3 &> /dev/null; then
        sudo apk add --no-cache git python3
    fi
elif [ -f /etc/fedora-release ]; then
    # Fedora
    if ! command -v git &> /dev/null || ! command -v python3 &> /dev/null; then
        sudo dnf install -y git python3
    fi
fi

# 2. Preparar directorio temporal
INSTALL_DIR="$HOME/.brainbash-temp"
rm -rf "$INSTALL_DIR"

# 3. Clonar el repositorio
echo -e "${GREEN}[+] Clonando BrainBash...${NC}"
git clone --depth=1 https://github.com/Ragdoll-Git/BrainBash.git "$INSTALL_DIR"

# 4. Ejecutar el script principal (pasando argumentos si los hubo)
echo -e "${GREEN}[+] Ejecutando instalador Python...${NC}"
cd "$INSTALL_DIR"

# Pasamos todos los argumentos ($@) al script de python
python3 main.py "$@"

echo -e "${GREEN}=== BrainBash Finalizado ===${NC}"