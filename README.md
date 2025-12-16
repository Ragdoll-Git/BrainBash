# 🚀 BrainBash (Multi-Distro Edition)

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Debian%20|%20Alpine%20|%20Fedora-gray?logo=linux)

## 📋 Descripción

**BrainBash** es una aplicación modular escrita en **Python** que detecta automáticamente tu distribución Linux y configura tu entorno en minutos y agrega integracion con IA local y en la nube.

**Soporte actual:**

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

Este proyecto utiliza una *Interfaz de Texto (TUI)* interactiva.

Aparecerá un menú donde podrás seleccionar:

- Actualizar el sistema.
- Instalar paquetes base y extra.
- Instalar entorno de desarrollo personalizado.
- Descargar y configurar modelos de IA local.
- Instalar y despues configurar la integración con Gemini (Google AI).

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

## 🤖 Integración AI

Una vez instalado, tu terminal tendrá acceso a herramientas de IA (requiere Ollama instalado aparte para los modelos locales):

Existen 4 modelos disponibles:

- Qwen3:0.6B : Ligero (523MB-40K tokens)
- Gemma3:1B : Balanceado (815MB-32K tokens)
- Phi4-mini:latest : Pesado (2.5GB-128K tokens)
- Gemini 2.5 Flash (respaldo en la nube): requiere internet y una API Key de Google.
La puede conseguir gratis en <https://aistudio.google.com/>

- `qwen "pregunta"`: Consulta al modelo Qwen 3 0.6B.
- `gemma "pregunta"`: Consulta al modelo Google Gemma 3 1B.
- `phi "pregunta"`: Consulta al modelo Microsoft Phi-4 Mini.
- `gemini "pregunta"`: Consulta a la API de Google Gemini 2.5 Flash (requiere internet y una API Key).

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
