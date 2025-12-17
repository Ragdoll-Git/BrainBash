# Changelog

## Log de cambios recientes y estado actual

- **Fecha: 2025-12-16 (Sesión Actual - Fin)**
  - **Estado**: Funcional y Multi-Distro (Debian, Alpine, Fedora).
  - **Cambios Principales**:
    - **Soporte Alpine**: `sudo` dinámico, paquetes nativos APK para `ollama`, `eza`, `bat` (evitando segfaults de musl).
    - **Soporte Fedora**: Instalación manual (GitHub) para herramientas faltantes en repos (`eza`, `starship`, etc.).
    - **Workflow Desarrollo**: `install.sh` ahora detecta entorno local ("Dev Mode") y evita clonar.
    - **Dependencias**: Agregados `nano`, `whiptail`/`newt` al bootstrap.
    - **Ollama**: Lógica inversa (Manual > Script) y compatibilidad Alpine (`gcompat`).

- **Fecha: 2025-12-16 (Sesión Anterior)**
  - **Cambios:**
    - Implementación de `config/context.md` y sistema de plantillas `Modelfile`.
    - Fix crítico para uso de `sudo` en Docker (detección dinámica de root).
    - Implementación de `_simple_checklist` para TUI fallback (sin whiptail).
    - Corrección de tags de modelos Ollama a versiones válidas (`qwen3`, `gemma3`, `phi4-mini`).
    - Agregado `htop` a paquetes extra (instalación vía apt).
    - Prompt interactivo para Gemini API Key y corrección de alias zsh.
    - Auto-arranque de servidor `ollama serve` si está detenido.
  - **Estado funcional:** Estable. Instalador probado en Docker y validado por usuario.

- **Fecha: 2025-12-16 (Inicial)**
  - Cambios: Creación inicial del archivo AI_JOURNAL.md.
  - Estado funcional: Inicialización.

## Log de decisiones

- **[Decision]:** Empaquetar `install_ollama.sh` localmente para evitar errores 404/timeout de `ollama.com`.
- **[Decision]:** Separar secretos en `.brainbash_secrets` (sourced por zshrc) para evitar contaminar el historial de git con API Keys personales.
- **[Decision]:** **Alpine**: Usar paquetes nativos APK para `ollama` y herramientas modernas siempre que sea posible para evitar problemas de ABI (glibc vs musl). Solo usar manual para lo que no existe (`tldr`).
- **[Decision]:** **Fedora**: Usar instalación manual (GitHub releases) para herramientas modernas que no están en los repositorios base, evitando fallos de `dnf`.
- **[Decision]:** **Install Script**: Detectar la presencia de `main.py` para asumir "Modo Desarrollo" y usar los archivos locales en lugar de un `git clone` fresco.

## Log de tareas pendientes

- [x] Refinar detección de SO (DNF, Pacman/Alpine) - Quedó pendiente de validación profunda.
- [ ] Probar instalación en un entorno "limpio" real (no Docker) para validar paths absolutos si los hubiera.
- [x] Invertir el paso de instalacion de Ollama, si no se puede descargar desde GitHub, se debe instalar desde ollama_install.sh
- [ ] Agregar e instalar paquetes nano, python3, whiptail a los contenedores docker de debian, alpine y fedora. Para poder usarlos en el script de instalacion y no tener que estar instalandolos cada vez que se quiera reconstruir un contenedor.
- [ ] Ajustar temperatura de Gemma (es muy creativa y se desvía del contexto).
- [ ] Se debe agregar un archivo de configuracion para que el usuario pueda modificar las variables de entorno, como la API Key de Gemini, la direccion del servidor de Ollama, etc.
