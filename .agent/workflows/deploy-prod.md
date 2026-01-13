---
description: Migra el código de producción al repositorio BrainBash (Prod) usando MCP.
---

# Workflow deploy-prod

## Este workflow automatiza el despliegue de cambios desde `BrainBashDev` (desarrollo) hacia el repositorio de producción `BrainBash`

### Pasos

1. **Definir Rama de Release**:
    - Genera un nombre de rama único (ej: `deploy-update-[FECHA]`).
    - Usa `mcp_github_create_branch` para crearla en `Ragdoll-Git/BrainBash`.

2. **Leer Archivos Locales (Lista de Producción)**:
    - Lee el contenido de los siguientes archivos locales (Excluyendo tests, logs, docker, .ai, o cualquier archivo de prueba o testeo que exista):
        - `main.py`
        - `install.sh`
        - `src/core.py`, `src/utils.py`, `src/dotfiles.py`, `src/gemini_tool.py`, `src/__init__.py`
        - `src/managers/debian.py`, `src/managers/alpine.py`, `src/managers/fedora.py`, `src/managers/__init__.py`
        - `src/scripts/install_ollama.sh`

3. **Parchear `install.sh`**:
    - **CRÍTICO**: Modifica el contenido leído de `install.sh`.
    - Busca: `https://github.com/Ragdoll-Git/BrainBashDev.git`
    - Reemplaza con: `https://github.com/Ragdoll-Git/BrainBash.git`
    - *Esto asegura que el instalador de producción clone el repo de producción.*

4. **Subir Archivos (Push)**:
    - Usa `mcp_github_push_files` para subir todos los archivos leídos (y el `install.sh` modificado) a la nueva rama en `Ragdoll-Git/BrainBash`.

5. **Crear Pull Request**:
    - Usa `mcp_github_create_pull_request` para abrir un PR desde tu nueva rama hacia `main`.
    - Título sugerido: "Deploy: Actualización de Producción [FECHA]"
    - Si falla por permisos, notifica al usuario con el link directo para crear el PR.
