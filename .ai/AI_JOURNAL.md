# AI Journal & Context

## 1. Necesidades del Usuario y Prioridades (ALTA PRIORIDAD)

*Esta sección es la fuente de verdad sobre lo que el usuario quiere y necesita.*

- **Propósito del Proyecto:** El nombre del proyectro se llama BrainBash. Es un entorno personalizado de desarrollo en la terminal de Linux, con integracion en la terminal de IA local y un respaldo en la nube (Gemini).
- **Necesidades Explícitas/Deducidas:**
  - [x] Contexto Compartido (`context.md`) para IAs (Gemini, Ollama).
  - [x] Modelos Específicos: Qwen 3 (qwen3:0.6b), Gemma 3 (gemma3:1b), Phi 4 Mini (phi4-mini:latest).
  - [x] Robustez en entornos sin SUDO (Docker) y sin TUI gráfica (whiptail).
  - [x] Instalación resiliente (retry/catch en descargas).
  - [x] Configuración interactiva de API Keys.
- **Limitaciones del Agente:**
  - [ ] Los modelos de IA local no deben modificarse, son esos modelos, y la verificacion de que existen se encuentra documentado en la seccion *Documentacion*
  - [ ] Acceso restringido a `.ai/` (requiere bypass via comandos).
- **Objetivos Secundarios:**
  - [x] Mantener limpieza.

## 2. Documentacion general

Link a repositorio de github del proyecto:
<https://github.com/Ragdoll-Git/BrainBash>

Link a modelos de IA:

<https://ollama.com/library/qwen3:0.6b>
<https://ollama.com/library/gemma3:1b>
<https://ollama.com/library/phi4-mini:latest>

## 3. Reglas de Comportamiento del Agente

**INSTRUCCIÓN INVIOLABLE:**
Ante cualquier duda: **PREGUNTAR**.

- **No asumir NADA** ni inventar información que no haya sido dada explícitamente.
- Hacer preguntas de seguimiento después de la respuesta del usuario o en cualquier momento que sea necesario.
- **Principio Rector:** Es mejor mantener informado al usuario de las decisiones que se vayan a tomar antes de actuar, que asumir y equivocarse.

## 3. Registro de Estado del Proyecto

*Log de cambios recientes y estado actual.*

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

- **Fecha: 2025-12-16 (Sesión Actual - Fin)**
  - **Estado**: Funcional y Multi-Distro (Debian, Alpine, Fedora).
  - **Cambios Principales**:
    - **Soporte Alpine**: `sudo` dinámico, paquetes nativos APK para `ollama`, `eza`, `bat` (evitando segfaults de musl).
    - **Soporte Fedora**: Instalación manual (GitHub) para herramientas faltantes en repos (`eza`, `starship`, etc.).
    - **Workflow Desarrollo**: `install.sh` ahora detecta entorno local ("Dev Mode") y evita clonar.
    - **Dependencias**: Agregados `nano`, `whiptail`/`newt` al bootstrap.
    - **Ollama**: Lógica inversa (Manual > Script) y compatibilidad Alpine (`gcompat`).

## 4. Decisiones Técnicas

- **[Decisión]:** Empaquetar `install_ollama.sh` localmente para evitar errores 404/timeout de `ollama.com`.
- **[Decisión]:** Separar secretos en `.brainbash_secrets` (sourced por zshrc) para evitar contaminar el historial de git con API Keys personales.
- **[Decisión]:** **Alpine**: Usar paquetes nativos APK para `ollama` y herramientas modernas siempre que sea posible para evitar problemas de ABI (glibc vs musl). Solo usar manual para lo que no existe (`tldr`).
- **[Decisión]:** **Fedora**: Usar instalación manual (GitHub releases) para herramientas modernas que no están en los repositorios base, evitando fallos de `dnf`.
- **[Decisión]:** **Install Script**: Detectar la presencia de `main.py` para asumir "Modo Desarrollo" y usar los archivos locales en lugar de un `git clone` fresco.

## 5. Próximos Pasos y tareas pendientes

- [x] Refinar detección de SO (DNF, Pacman/Alpine) - Quedó pendiente de validación profunda.
- [ ] Probar instalación en un entorno "limpio" real (no Docker) para validar paths absolutos si los hubiera.
- [x] Invertir el paso de instalacion de Ollama, si no se puede descargar desde GitHub, se debe instalar desde ollama_install.sh
- [x] Agregar paquetes nano, python3 y whiptail a los contenedores docker de debian, alpine y fedora. Para poder usarlos en el script de instalacion.
- [ ] Ajustar temperatura de Gemma (es muy creativa y se desvía del contexto).

## 6. FAQ / Preguntas para el Usuario

*Espacio para que el agente deje preguntas pendientes si la sesión termina y hay dudas no resueltas. Sea especifico y detallado con las preguntas.*

(Sin preguntas pendientes)
