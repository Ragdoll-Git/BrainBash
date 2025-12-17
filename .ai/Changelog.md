# Changelog

## Log de cambios recientes y estado actual

- **Fecha: 2025-12-17 (Sesión Actual - Fin)**
  - **Estado**: Funcional con detalles pendientes (Zsh auto-start). Instalador robusto y validado en Docker.
  - **Cambios Principales**:
    - **Docker Optimization**: Agregados `nano`, `whiptail`, `python3` a contenedores Debian/Alpine/Fedora.
    - **Gemma Config**: Ajustada temperatura a 0.4 para reducir alucinaciones.
    - **Fedora Fix**: Solucionado `ollama: command not found` agregando `~/.local/bin` al PATH incondicionalmente.
    - **Gemini Migration**: Migrado de `google.generativeai` a `google.genai` SDK (v2.5).
    - **Ollama Install**: Optimizada prioridad (Curl Oficial > Binarios > Script Local) con validación de "falso positivo" (check post-curl).
    - **Logger Fix**: Agregado método `warning` faltante en `src/utils.py`.
    - **zsh Default**: Implementado `set_default_shell` con `chsh` y fallback `usermod`, aunque requiere revisión en próxima sesión para auto-start.

- **Fecha: 2025-12-16 (Sesión Anterior)**
  - **Estado**: Funcional y Multi-Distro (Debian, Alpine, Fedora).
  - **Cambios Principales**:
    - Soporte Alpine/Fedora.
    - Lógica inversa Ollama (Manual > Script).
    - Fix sudo y tui.

- **Fecha: 2025-12-16 (Inicial)**
  - Cambios: Creación inicial del archivo AI_JOURNAL.md.

## Log de decisiones

- **[Decision]:** **Gemini SDK**: Migrar a `google.genai` para evitar warnings de deprecación y usar la API v2.5.
- **[Decision]:** **Ollama Install**: Priorizar `curl | sh` oficial por velocidad, pero mantener binarios y script local como fallbacks robustos. Verificar siempre la existencia del binario tras el pipe.
- **[Decision]:** **Zsh Default**: Usar `chsh -s` primariamente, pero incluir fallback a `usermod` (sudo) y verificación contra `/etc/passwd` para robustez.
- **[Decision]:** Empaquetar `install_ollama.sh` localmente para evitar errores 404/timeout de `ollama.com`.
- **[Decision]:** Separar secretos en `.brainbash_secrets` (sourced por zshrc).

## Log de tareas pendientes

- [ ] **Prioridad**: Lograr que Zsh inicie automáticamente tras la instalación y en reinicios (Reportado como fallando o inconsistente por usuario).
- [ ] Validar instalación en entorno limpio real ("Clean Real Environment") para confirmar paths absolutos fuera de Docker.
- [ ] Refinar detección de SO (DNF, Pacman/Alpine) - Quedó pendiente de validación profunda.
