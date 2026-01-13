# 🧠 BrainBash ✨

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Debian%20|%20Alpine%20|%20Fedora-gray?logo=linux)

## 📋 Descripción

**BrainBash** es una aplicación modular escrita en **Python** que detecta automáticamente tu distribución Linux y configura tu entorno en minutos y agrega integracion con IA local (sin internet) y en la nube (con internet).

**Soporte:**

- 🍥 **Debian / Ubuntu / Kali** (apt)
- 🏔️ **Alpine Linux** (apk)
- 🎩 **Fedora / RHEL / CentOS** (dnf)

## 🚀 Instalación Rápida

Podes copiar el siguiente script de instalación en tu terminal:

```bash
bash <(curl -sL https://ragdoll-git.github.io/BrainBash/install.sh)
```

O clonarlo manualmente:

```bash
git clone https://github.com/Ragdoll-Git/BrainBash.git

cd BrainBash

python3 main.py
```

## 🎮 Modo de Uso

Aparecerá un menú donde podrás seleccionar:

- Actualizar el sistema.
- Instalar paquetes base y extra.
- Instalar entorno de desarrollo personalizado.
- Descargar tipos/modelos de IA local.
- Instalar y configurar Gemini 2.5 Flash.

*Después de terminada la instalacion, se puede acceder a cada modelo de IA local con el comando/alias:*

- `qwen: "pregunta"` o `qwen:`
- `gemma: "pregunta"` o `gemma:`
- `phi: "pregunta"` o `phi:`

### Modos de uso en la terminal

#### 1. Pregunta rapida

- `qwen: "pregunta"` - Hacer pregunta y recibir respuesta, ***sin contexto***
- `gemini: "pregunta"` - Hacer pregunta y recibir respuesta, ***sin contexto***


#### 2. Modo interactivo o chat

- `qwen:` - Inicia una sesion/chat con el modelo Qwen 3 0.6B. ***Usa contexto de la sesion.***
- `gemini:` - Inicia una sesion/chat con el modelo Gemini 2.5 Flash. ***Usa contexto de la sesion.***

## 📦 Paquetes Incluidos

El sistema contiene los siguientes paquetes:

| Paquete | Descripción |
| :--- | :--- |
| `zsh` | Shell alternativa mejorada |
| `git` | Control de versiones |
| `fzf` | Búsqueda difusa (Fuzzy Finder) |
| `bat` | Reemplazo de cat con sintaxis ( ejecutandose con cat o con alias batcat) |
| `eza` | Reemplazo moderno de ls |
| `htop` | Monitor de recursos interactivo |
| `tldr` | Páginas de ayuda simplificadas (alternativa a man) |
| `zoxide` | Navegación de directorios inteligente (reemplazo de cd) |
| `curl` | Transferencia de datos |
| `python-dev` | Headers necesarios para compilar herramientas |

## 🤖 Integración IA

Una vez instalado, tu terminal tendrá acceso a herramientas de IA (requiere Ollama instalado para los modelos locales):

Existen 4 tipos de modelos de IA disponibles:

- Qwen3:0.6B : Ligero **(523MB-40K tokens)**
- Gemma3:1B : Balanceado **(815MB-32K tokens)**
- Phi4-mini:latest : Pesado **(2.5GB-128K tokens)**
- Gemini 2.5 Flash (respaldo en la nube): requiere internet y una API Key de Google.
La puede conseguir gratis en <https://aistudio.google.com/>

## 🧪 Testing con Docker

Puedes probar la interfaz en un entorno limpio usando Docker (Modo Interactivo):

```bash
# Prueba en Alpine
docker run -it --rm -v $(pwd):/app -w /app alpine:latest sh -c "apk add python3 sudo && python3 main.py"
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
