# 🚀 DeployEnvDebian (ahora agnóstico)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Debian](https://img.shields.io/badge/Distro-Debian-red)
![Alpine](https://img.shields.io/badge/Distro-Alpine-blue)

Un sistema moderno y multiplataforma para automatizar la configuración de entornos Linux con instalación de paquetes y enlazado de dotfiles.

## 📋 Descripción

**DeployEnvDebian** es una software hecho en Python que despliega y configura tu entorno de desarrollo automáticamente, y detecta tu distribución Linux, realizando: 

- ✅ Instalación automatizada de paquetes base
- ✅ Enlazado de dotfiles personalizados (symlinks)
- ✅ Soporte multi-distribución (Debian, Ubuntu, Alpine, Fedora/RHEL/CentOS)
- ✅ Interfaz interactiva con menús (whiptail o texto simple)
- ✅ Temas de color personalizables
- ✅ Sistema modular y extensible

## 🎯 Características Principales

### 📦 Gestión de Paquetes Multiplataforma

El sistema traduce automáticamente nombres de paquetes genéricos a sus equivalentes específicos de cada distribución:

- **Debian/Ubuntu**: APT (apt)
- **Alpine**: APK (apk)
- **Fedora/RHEL/CentOS**:  DNF (dnf)

**Ejemplo**:  El paquete genérico `python-dev` se traduce automáticamente a: 
- `python3-dev` en Debian/Ubuntu/Alpine
- `python3-devel` en Fedora

### ⚙️ Dotfiles Inteligentes

Sistema de enlaces simbólicos que: 
- Crea automáticamente directorios faltantes
- Hace backup de archivos existentes antes de sobrescribir
- Detecta y actualiza enlaces rotos
- Valida la existencia de archivos origen

### 🎨 Personalización Visual

Elige entre 4 temas de color para los logs:
- 🔵 Azul (Estilo Debian)
- 🟢 Verde (Hacker)
- 🟣 Magenta (Cyberpunk)
- 🔴 Rojo (Alerta)

## 📦 Paquetes Instalados

Los siguientes paquetes se instalan en TODAS las máquinas:

| Paquete | Descripción |
|---------|------------|
| `git` | Control de versiones |
| `zsh` | Shell alternativa mejorada |
| `curl` | Descarga de archivos desde terminal |
| `fzf` | Búsqueda fuzzy interactiva |
| `bat` | Reemplazo moderno de `cat` con sintaxis |
| `python-dev` | Headers de desarrollo de Python |

## 🛠️ Dotfiles Soportados

El sistema enlaza los siguientes archivos de configuración:

| Fuente | Destino | Propósito |
|--------|---------|-----------|
| `config/zshrc` | `~/.zshrc` | Configuración de Zsh |
| `config/kitty. conf` | `~/.config/kitty/kitty.conf` | Emulador Kitty |
| `config/starship.toml` | `~/.config/starship.toml` | Prompt Starship |

## 🚀 Instalación y Uso

### Requisitos Previos

- Python 3.7+
- Acceso a `sudo` (sin necesidad de contraseña para ciertos comandos)
- Conexión a Internet
- Distribución Linux soportada

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/Ragdoll-Git/DeployEnvDebian.git
cd DeployEnvDebian

# 2. Cambiar a la rama de desarrollo Python
git checkout DeployInPython

# 3. Ejecutar el script principal
python3 main.py
```

### Opciones de Instalación

Una vez ejecutado `main.py`, se te presenta un menú con las siguientes opciones:

```
=== Menu Principal ===
Que deseas hacer hoy? 

1) Instalacion Completa (Paquetes + Dotfiles)
2) Solo instalar Paquetes
3) Solo enlazar Dotfiles (Config)
4) Salir
```

**Opción 1 - Instalación Completa**
```bash
# Instala todos los paquetes base + enlaza todos los dotfiles
# Tiempo estimado: 3-5 minutos
```

**Opción 2 - Solo Paquetes**
```bash
# Instala los paquetes base sin tocar los archivos de configuración
# Ideal para máquinas compartidas
```

**Opción 3 - Solo Dotfiles**
```bash
# Enlaza solo los archivos de configuración
# Útil si los paquetes ya están instalados
```

## 📁 Estructura del Proyecto

```
DeployEnvDebian/
├── main.py                 # Punto de entrada principal
├── README.md              # Este archivo
├── config/                # Archivos de configuración (dotfiles)
│   ├── zshrc              # Configuración de Zsh
│   ├── kitty.conf         # Configuración de Kitty Terminal
│   └── starship.toml      # Configuración de Starship Prompt
└── src/                   # Módulos internos
    ├── __init__.py
    ├── managers/          # Gestores de paquetes por distribución
    │   ├── __init__.py
    │   ├── core.py        # Clase base abstracta PackageManager
    │   ├── debian.py      # Implementación para Debian/Ubuntu
    │   ├── alpine.py      # Implementación para Alpine
    │   └── fedora.py      # Implementación para Fedora/RHEL
    ├── utils. py           # Utilidades (Logger, Colors, TUI)
    └── dotfiles.py        # Gestor de enlaces simbólicos
```

## ⚙️ Configuración Avanzada

### Agregar Nuevos Paquetes

Edita `main.py` y agrega al diccionario `BASE_PACKAGES`:

```python
BASE_PACKAGES = [
    "git",
    "zsh",
    "curl",
    "fzf",
    "bat",
    "python-dev",
    "tu-nuevo-paquete"  # ← Agregar aquí
]
```

Luego, mapea el nombre en `src/managers/core.py`:

```python
PACKAGE_MAP = {
    "tu-nuevo-paquete": {
        "debian": "nombre-en-debian",
        "ubuntu": "nombre-en-ubuntu",
        "alpine": "nombre-en-alpine",
        "fedora": "nombre-en-fedora"
    }
}
```

### Agregar Nuevos Dotfiles

Edita el diccionario `DOTFILES_MAP` en `main.py`:

```python
DOTFILES_MAP = {
    "zshrc": ". zshrc",
    "kitty.conf": ".config/kitty/kitty.conf",
    "starship.toml":  ".config/starship.toml",
    "nuevo-config":  ". config/nuevo-config/config"  # ← Agregar aquí
}
```

Coloca el archivo en la carpeta `config/` del repositorio.

### Agregar Soporte para Nueva Distribución

1. Crea un nuevo archivo en `src/managers/` (ej: `arch.py`):

```python
import subprocess
from typing import List
from .. core import PackageManager

class ArchManager(PackageManager):
    """Implementación para Arch Linux (Pacman)"""
    
    def update(self):
        subprocess.run(["sudo", "pacman", "-Sy"], check=True)
    
    def install(self, packages: List[str]):
        mapped_packages = [self._get_mapped_name(p) for p in packages]
        subprocess.run(["sudo", "pacman", "-S", "--noconfirm"] + mapped_packages, check=True)
```

2. Importa la clase en `src/managers/__init__.py`:

```python
from .arch import ArchManager
__all__ = ["DebianManager", "AlpineManager", "FedoraManager", "ArchManager"]
```

3. Agrega la detección en `main.py`:

```python
if "arch" in os_info: 
    return ArchManager("arch")
```

4. Mapea los paquetes en `core.py`:

```python
"python-dev": {
    "debian": "python3-dev",
    "arch": "python",  # ← Agregar aquí
    ... 
}
```

## 🤖 Integración AI (Zshrc)

La configuración de Zsh incluye funciones para trabajar con modelos locales y en nube:

### Modelos Locales (Ollama)

**QWEN** - Rápido y ligero
```bash
qwen "¿Cuál es la capital de Francia?"
```

**GEMMA** - Balanceado
```bash
gemma "Explica recursión en Python"
```

**PHI** - Optimizado para lógica
```bash
phi "Resuelve este problema de algoritmia..."
```

### Modelo en Nube (Gemini)

```bash
gemini "Tu pregunta aquí"
```

*Requiere configuración previa de la API Key en las variables de entorno*

## 🔧 Solución de Problemas

### "Distribución no soportada"

**Problema**:  El script no reconoce tu distribución. 

**Solución**:  
```bash
cat /etc/os-release
# Verifica el contenido y abre un issue en GitHub
```

### "No se pudo leer /etc/os-release"

**Problema**:  El archivo de identificación del sistema no existe.

**Solución**:  Esto es muy raro. Verifica que estés en un sistema Linux real: 
```bash
uname -a
```

### "Fallo al instalar paquete X"

**Problema**: Un paquete no se instala correctamente.

**Solución**:
```bash
# Intenta instalarlo manualmente
sudo apt install nombre-paquete  # o apk, dnf, etc. 

# Verifica que el nombre sea correcto en PACKAGE_MAP
# Abre un issue con el error exacto
```

### "Enlace simbólico ya existe"

**Problema**: El script dice que el enlace ya está creado pero no funciona.

**Solución**:  El script automaticamente hace backup con timestamp: 
```bash
# Los backups están en tu home con extensión .bak. TIMESTAMP
ls ~/*.bak.*
```

### "Error de permisos (Permission Denied)"

**Problema**: El script no tiene permisos para crear directorios.

**Solución**:
```bash
# Verifica que tengas permisos en tu home
ls -la ~/ | head
# Si todo es del root, necesitas cambiar la propiedad
sudo chown -R $USER:$USER ~
```

## 📝 Notas Técnicas

### Detección Automática de Distribución

El script lee `/etc/os-release` para determinar qué gestor de paquetes usar: 

```python
# Alpine → AlpineManager (apk)
# Fedora/RHEL/CentOS → FedoraManager (dnf)
# Debian/Ubuntu/Kali → DebianManager (apt)
```

### Fixes Post-Instalación

**Debian Batcat Fix**:  En Debian, el paquete `bat` se instala como `batcat` para evitar conflictos.  El script crea automáticamente un symlink `~/.local/bin/bat` → `/usr/bin/batcat`.

### Sistema de Logs Modular

La clase `Logger` permite cambiar el tema de color sin tocar el código:

```python
logger = Logger(theme_color=Colors.BLUE)
logger.info("Mensaje informativo")     # En azul
logger.success("¡Éxito!")              # Siempre verde
logger.error("Error crítico")          # Siempre rojo
logger.step("SECCIÓN IMPORTANTE")      # Título en azul negrita
```

### Interfaz Agnóstica

Si `whiptail` no está disponible, el script automáticamente cae a menús de texto simple. 

## 🤝 Contribución

¿Quieres mejorar DeployEnvDebian? 

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/mi-feature`)
3. Commit tus cambios (`git commit -m "Agrego soporte para X"`)
4. Push a la rama (`git push origin feature/mi-feature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT.  Véase el archivo `LICENSE` para más detalles.

## 👤 Autor

**Ragdoll-Git** - [Perfil de GitHub](https://github.com/Ragdoll-Git)

## 📞 Soporte

¿Encontraste un bug?  ¿Tienes una sugerencia? 

- 🐛 [Abre un Issue](https://github.com/Ragdoll-Git/DeployEnvDebian/issues)
- 💬 [Discusiones](https://github.com/Ragdoll-Git/DeployEnvDebian/discussions)

---

**¡Espero que disfrutes configurando tus máquinas Linux con DeployEnvDebian!** 🎉
