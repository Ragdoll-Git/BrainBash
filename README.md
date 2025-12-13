# 🚀 DeployEnvDebian (Multi-Distro Edition)

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Debian%20|%20Alpine%20|%20Fedora-gray?logo=linux)
![CI](https://github.com/Ragdoll-Git/DeployEnvDebian/actions/workflows/test_distros.yml/badge.svg)

Un sistema moderno, agnóstico y robusto para automatizar la configuración de entornos Linux. Diseñado para funcionar tanto de forma interactiva (TUI) como en pipelines de integración continua (CI/CD).

## 📋 Descripción

**DeployEnvDebian** es una aplicación modular escrita en **Python** que detecta automáticamente tu distribución Linux y configura tu entorno de desarrollo en minutos.
**Soporte actual:**
- 🍥 **Debian / Ubuntu / Kali** (apt)
- 🏔️ **Alpine Linux** (apk)
- 🎩 **Fedora / RHEL / CentOS** (dnf)

## 🎯 Características Principales

### 📦 Gestión de Paquetes Inteligente
El sistema traduce automáticamente nombres genéricos a sus equivalentes específicos por distribución:
* *Ejemplo:* `python-dev` se traduce internamente a `python3-dev` (Debian/Alpine) o `python3-devel` (Fedora).

### ⚙️ Dotfiles Seguros
Sistema de enlaces simbólicos (symlinks) con seguridad integrada:
* Crea directorios faltantes automáticamente.
* **Backups automáticos:** Si un archivo de configuración ya existe, lo renombra a `.bak.<timestamp>` antes de enlazar, para que nunca pierdas datos.

### 🤖 Modos Híbridos
* **Modo Interactivo:** Menús visuales (tipo Debian Installer) para uso humano.
* **Modo Desatendido:** Flags de línea de comandos para scripts, Docker y CI/CD.

### 🎨 Personalización Visual
Sistema de logs temáticos. Elige el color de tu terminal:
🔵 Azul (Debian)
🟢 Verde (Hacker)
🟣 Magenta (Cyberpunk)
🔴 Rojo (Alerta)

## 🚀 Instalación Rápida

Como el proyecto ahora reside en la rama principal, la instalación es directa:

```bash
# 1. Clonar el repositorio
git clone [https://github.com/Ragdoll-Git/DeployEnvDebian.git](https://github.com/Ragdoll-Git/DeployEnvDebian.git)
cd DeployEnvDebian

# 2. Ejecutar (Detecta distro automáticamente)
python3 main.py
```
## 🎮 Modos de Uso

1. Modo Interactivo (Recomendado): Simplemente ejecuta el programa sin argumentos. Se abrirá un menú visual:
```bash
python3 main.py
```
## 2. Modo Desatendido (CI/CD & Docker)
Ideal para automatización. No pide confirmación y ejecuta todo de una vez.

```bash
# Instalar todo (Paquetes + Dotfiles) con logs verdes
python3 main.py --all --theme green
```

### Instalar SOLO paquetes
```bash
python3 main.py --packages --theme blue
```

### Instalar SOLO dotfiles
```bash
python3 main.py --dotfiles
```

### Flags Disponibles
| Flag | Descripción |
| :--- | :--- |
| `--all` | Instala paquetes y enlaza dotfiles. |
| `--packages` | Solo instala paquetes base. |
| `--dotfiles` | Solo crea enlaces simbólicos. |
| `--theme` | Color de logs: `blue`, `green`, `red`, `magenta`. |

## 📦 Paquetes Incluidos
El sistema instala automáticamente la base para un entorno moderno:

| Paquete | Descripción |
| :--- | :--- |
| `zsh` | Shell alternativa mejorada |
| `git` | Control de versiones |
| `fzf` | Búsqueda difusa (Fuzzy Finder) |
| `bat` | Reemplazo de cat con sintaxis (fix automático para batcat en Debian) |
| `curl` | Transferencia de datos |
| `python-dev` | Headers necesarios para compilar herramientas |

## 🛠️ Configuración (Dotfiles)
Coloca tus archivos en la carpeta `config/` del repositorio. El script los enlazará automáticamente:

| Fuente en Repo | Destino en Sistema | Propósito |
| :--- | :--- | :--- |
| `config/zshrc` | `~/.zshrc` | Configuración Zsh |
| `config/kitty.conf` | `~/.config/kitty/kitty.conf` | Terminal Kitty |
| `config/starship.toml` | `~/.config/starship.toml` | Prompt Starship |

## 🤖 Integración AI (Zsh)
Una vez instalado, tu terminal tendrá superpoderes (requiere Ollama instalado aparte):
- `qwen "pregunta"`: Respuestas rápidas (Modelo Qwen).
- `gemma "pregunta"`: Respuestas balanceadas (Modelo Google Gemma).
- `phi "pregunta"`: Lógica y matemáticas (Modelo Microsoft Phi).
- `gemini "pregunta"`: Consulta a la API de Google Gemini (requiere API Key).

## 📁 Estructura del Proyecto
```plaintext
DeployEnvDebian/
├── main.py                 # Punto de entrada (CLI + GUI)
├── README.md               # Documentación
├── config/                 # Tus archivos de configuración reales
│   ├── zshrc
│   ├── kitty.conf
│   └── starship.toml
└── src/                    # Código Fuente Modular
    ├── __init__.py
    ├── core.py             # Lógica base abstracta
    ├── dotfiles.py         # Gestor de Symlinks y Backups
    ├── utils.py            # UI, Colores y Logs
    └── managers/           # Implementaciones por Distro
        ├── alpine.py       # Soporte APK
        ├── debian.py       # Soporte APT
        └── fedora.py       # Soporte DNF
```

## 🧪 CI/CD y Testing
El proyecto cuenta con un pipeline de GitHub Actions (`.github/workflows/test_distros.yml`) que prueba automáticamente el script en contenedores limpios de Debian, Alpine y Fedora cada vez que se hace un push.

Para probarlo localmente con Docker:
```bash
# Prueba rápida en Alpine
docker run --rm -v $(pwd):/app -w /app alpine:latest sh -c "apk add python3 sudo && python3 main.py --all --theme green"
```

## ⚙️ Desarrollo: Agregar nuevos paquetes
Para agregar paquetes, edita `main.py` y agrega al diccionario `BASE_PACKAGES`. Si el paquete tiene nombres diferentes en cada distro, edita `src/managers/core.py`:

```python
# src/managers/core.py
PACKAGE_MAP = {
    "tu-paquete": {
        "debian": "nombre-debian",
        "alpine": "nombre-alpine",
        "fedora": "nombre-fedora"
    }
}
```

## 🤝 Contribuir
1. Haz un Fork.
2. Crea tu rama (`git checkout -b feature/nueva-distro`).
3. Haz tus cambios y añade tests.
4. Push a la rama y abre un Pull Request.

## 📄 Licencia
Este proyecto está bajo licencia MIT. Véase el archivo LICENSE para más detalles.

---
Hecho con 🐍 y ❤️ por Ragdoll-Git.