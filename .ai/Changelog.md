# Changelog

## Log de cambios recientes y estado actual

- **Fecha: 2026-01-12 (Sesión Actual)**
  - **Estado**: Funcional y robusto en Docker. Paquetes migrados a APT y cosmetica (temas) completada.
  - **Cambios Principales**:
    - **Refactorización de Testing**:
      - Se limpió `main.py` eliminando flags de desarrollo (`--auto`) y `argparse`.
      - Se extrajo la lógica de instalación a `run_execution_phase`.
      - Se creó `tests/test_install.py` para pruebas automatizadas (headless) usando la nueva estructura modular.
    - **Validación Multi-Distro**:
      - **Debian**: Validado exitosamente con symlinks (`batcat`, `exa`) y persistencia de shell.
      - **Alpine**: Correcciones críticas: agregado `shadow` (para `chsh`), `py3-pip`, y fallback manual para `thefuck`.
      - **Fedora**: Validado exitosamente ("out-of-the-box").
    - **Hardening**: `main.py` ahora maneja `FileNotFoundError` al intentar cambiar la shell, evitando crashes si `chsh` no existe.
    - **Migración a APT**: Se migraron `eza` (como `exa`), `bat` (como `batcat`), `fzf`, `zoxide` y `tldr` (como `tealdeer`) a los repositorios oficiales de Debian Bookworm.
    - **Symlinks de Compatibilidad**: Se crearon enlaces simbólicos para mantener compatibilidad con configs existentes:
      - `eza` -> `exa`
      - `bat` -> `batcat`
      - `tldr` -> `tealdeer`
    - **Tema Bat**: Se implementó la descarga automática del tema "Catppuccin Mocha" para `bat` en `debian.py`.
    - **Zsh Auto-start**: Se mejoró la lógica de detección de zsh y fallback en `.bashrc`.
    - **TLDR Robustez**: Se agregó auto-update (`tldr --update`) con lógica de reintentos (3 intentos) para mitigar timeouts de red.
    - **Nueva Herramienta**: Se agregó `thefuck` al menú Extra y configuración automática en `zshrc`.
    - **Gemini Fallback**: Implementada estrategia de redundancia en `src/gemini_tool.py` (Prioridad: `3-flash-preview` > `2.5-flash` > `2.5-flash-lite`) para manejar límites de cuota automáticamente.
    - **UX/UI Responsive**: El menú principal ahora se adapta dinámicamente a la resolución de la terminal. El ancho de `whiptail` y la alineación del texto se calculan usando `shutil.get_terminal_size()` para soportar pantallas pequeñas (<80 cols) y grandes.
    - **Organización**: Scripts de depuración movidos a `tests/`.

- **Fecha: 2025-12-17**
  - **Estado**: Funcional con detalles pendientes (Zsh auto-start). Instalador robusto y validado en Docker.
  - **Cambios Principales**:
    - **Docker Optimization**: Agregados `nano`, `whiptail`, `python3` a contenedores Debian/Alpine/Fedora.
    - **Gemma Config**: Ajustada temperatura a 0.4 para reducir alucinaciones.
    - **Fedora Fix**: Solucionado `ollama: command not found` agregando `~/.local/bin` al PATH incondicionalmente.
    - **Gemini Migration**: Migrado de `google.generativeai` a `google.genai` SDK (v2.5).
    - **Ollama Install**: Optimizada prioridad (Curl Oficial > Binarios > Script Local) con validación de "falso positivo" (check post-curl).
    - **Logger Fix**: Agregado método `warning` faltante en `src/utils.py`.
    - **zsh Default**: Implementado `set_default_shell` con `chsh` y fallback `usermod`, aunque requiere revisión en próxima sesión para auto-start.

- **Fecha: 2025-12-16**
  - **Estado**: Funcional y Multi-Distro (Debian, Alpine, Fedora).
  - **Cambios Principales**:
    - Soporte Alpine/Fedora.
    - Lógica inversa Ollama (Manual > Script).
    - Fix sudo y tui.

- **Fecha: 2025-12-16 (Inicial)**
  - Cambios: Creación inicial del archivo AI_JOURNAL.md.

## Log de decisiones

- **[Decision]:** **APT Packages**: Usar paquetes oficiales de Debian (con symlinks) en lugar de GitHub releases para mejorar estabilidad y velocidad en contenedores.
- **[Decision]:** **Dev Environment**: Mantener herramientas de desarrollo (`tests/`, logs) visibles en el repositorio principal, sin ocultarlas excesivamente.
- **[Decision]:** **Gemini SDK**: Migrar a `google.genai` para evitar warnings de deprecación y usar la API v2.5.
- **[Decision]:** **Ollama Install**: Priorizar `curl | sh` oficial por velocidad, pero mantener binarios y script local como fallbacks robustos. Verificar siempre la existencia del binario tras el pipe.
- **[Decision]:** **Zsh Default**: Usar `chsh -s` primariamente, pero incluir fallback a `usermod` (sudo) y verificación contra `/etc/passwd` para robustez.
- **[Decision]:** Empaquetar `install_ollama.sh` localmente para evitar errores 404/timeout de `ollama.com`.
- **[Decision]:** Separar secretos en `.brainbash_secrets` (sourced por zshrc).
- **[Decision]:** **Testing Modular**: No contaminar `main.py` con código de prueba. Usar `tests/test_install.py` que importa la lógica necesaria, manteniendo el entrypoint limpio para producción.
- **[Decision]:** **Alpine Packages**: Instalar `shadow` explícitamente en Alpine para proveer `chsh`/`usermod` y evitar fallos al cambiar de shell.

## Log de tareas pendientes

- [ ] Validar instalación en entorno limpio real ("Clean Real Environment") para confirmar paths absolutos fuera de Docker.
- [/] Refinar detección de SO (DNF, Pacman/Alpine) - Validado en Docker, falta confirmar en "Entorno Real".
- [x] **HECHO**: Limpieza y Refactorización de `main.py` y creación de suite de test (`metrics/test_install.py`).
- [x] **HECHO**: Implementar Fallback de Modelos Gemini (3 Preview -> 2.5 Flash -> 2.5 Lite).
