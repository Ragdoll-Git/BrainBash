# Necesidades del usuario

## Necesidades base *(NO MODIFICAR)*

*El agente NO PUEDE agregar o modificar las necesidades base*

- Desplegar paquetes base, extra, e IAs en cualquier distribucion de forma eficiente, segura y con el menor contacto del usuario posible. Lo unico que debe hacer el usuario es ejecutar el script de instalacion, seleccionar los paquetes que desea instalar, seleccionar el modelo de IA que desea usar, y copiar la API. El programa se debe encargar de todo el resto.

- El programa debe ser capaz de detectar la distribucion en el que se esta ejecutando y actuar de manera apropiada.

- El programa debe ser capaz de autorrepararse si algo falla (Instalación resiliente). Tener fallbacks en cada paso. Por ejemplo, si no se puede instalar un paquete, el programa debe intentar instalarlo de otra manera, o saltar el paso si no es esencial. Tener retry/catch en descargas, o busqueda de paquetes/modelos en otros mirrors oficiales. Ej: Binarios de Github, forks, etc.

- Las IAs deben compartir un contexto (`context.md`) tanto local como en la nube (Gemini).

- NO cambiar los modelos específicos: Qwen 3 (qwen3:0.6b), Gemma 3 (gemma3:1b), Phi 4 Mini (phi4-mini:latest).

- Robustez en entornos sin SUDO (Docker) y/o sin TUI gráfica (whiptail). Pero en entorno de produccion debe existir SUDO.

- Configuración interactiva de API Keys.

- Auto-arranque de terminal zsh cuando termina la instalacion. Y auto-arranque cada vez que se inicia el sistema.

## Necesidades nuevas/deducidas *(EL AGENTE PUEDE MODIFICAR)*

*El agente PUEDE agregar o modificar las necesidades nuevas/deducidas*

- **Prioridad de Instalación**: Preferir paquetes oficiales (APT) sobre descargas manuales de GitHub para mejorar estabilidad, velocidad y facilidad de actualización, usando symlinks si es necesario, pero si no es posible, usar descargas manuales de GitHub.
- **Robustez**: Evitar falsos positivos en pipes de shell (`curl | sh`).
- **Persistencia**: El usuario requiere que la shell por defecto cambie *realmente* y persista tras reinicios.
- **Persistencia**: El usuario requiere que la shell por defecto cambie *realmente* y persista tras reinicios, lo cual ha mostrado dificultades en entornos Docker/Sudo.
