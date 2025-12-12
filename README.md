# Despliegue de Entorno Debian + IA (Público & Seguro)

Este repositorio contiene un script de automatización (`deployPublic.sh`) diseñado para configurar rápidamente un entorno de desarrollo moderno y potenciado por Inteligencia Artificial en **Debian 12 (Bookworm)** y **Debian 13 (Trixie)**.

## 🚀 Características

El script es **idempotente** (se puede ejecutar varias veces sin romper nada) y modular. Ofrece un menú interactivo para instalar:

1.  **Paquetes Base Modernos**:
    *   Terminal: `kitty`
    *   Shell: `zsh` + `oh-my-zsh`
    *   Utilidades: `eza` (ls moderno), `bat` (cat con alas), `fzf`, `zoxide`.
2.  **Dotfiles & Estética**:
    *   Tema **Catppuccin Mocha** para Kitty y Starship.
    *   Prompt `starship` configurado.
    *   Configuración automática de `.zshrc`.
3.  **IA Local (Ollama)**:
    *   Instalación automática de Ollama.
    *   Optimización de RAM (liberación tras 1 min de inactividad).
    *   Modelos ligeros pre-configurados con *System Prompts* expertos en Debian:
        *   **Qwen 3 0.6B**: Extremadamente rápido y ligero.
        *   **Gemma 3 1B**: Modelo balanceado de Google.
        *   **Phi-4 Mini**: Modelo inteligente de Microsoft.
4.  **IA en la Nube (Gemini CLI)**:
    *   Herramienta de línea de comandos personalizada en Python.
    *   Requiere Google API Key (Gratuita).
    *   Modo comando (rápido) y modo chat interactivo.

## 📋 Requisitos

*   **Sistema Operativo**: Debian 12 o Debian 13.
*   **Usuario**: Ejecutar como usuario normal con permisos `sudo` (NO como root directo).
*   **Conexión a Internet**.

## 🛠️ Instalación y Uso

### ⚡ Instalación Rápida
```bash
bash <(curl -sL https://raw.githubusercontent.com/Ragdoll-Git/DeployEnvDebian/main/deployPublic.sh)
```

### 📦 Instalación Manual

1.  **Clonar el repositorio** (o descargar el script):
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd DeployEnvDebian
    ```

2.  **Dar permisos de ejecución**:
    ```bash
    chmod +x deployPublic.sh
    ```

3.  **Ejecutar el script**:
    ```bash
    ./deployPublic.sh
    ```

4.  **Seguir las instrucciones en pantalla**:
    *   El script preguntará qué componentes deseas instalar.
    *   Si eliges Gemini, ten a mano tu API Key de Google AI Studio.

## 🤖 Comandos de IA (Post-instalación)

Una vez instalado y recargada la shell (`source ~/.zshrc`), tendrás disponibles los siguientes alias/funciones:

| Comando | Descripción |
| :--- | :--- |
| `qwen: "pregunta"` | Consulta rápida al modelo local Qwen (0.6B). |
| `gemma: "pregunta"` | Consulta al modelo local Gemma (1B). |
| `phi: "pregunta"` | Consulta al modelo local Phi-4. |
| `gemini: "pregunta"` | Consulta a la nube (Gemini 2.5 Flash). |
| `gemini:` | Abre un chat interactivo con Gemini. |

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.