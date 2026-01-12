# AI Journal & Context

## 1. Necesidades del Usuario y Prioridades (ALTA PRIORIDAD)

*Esta sección es la fuente de verdad sobre lo que el usuario quiere y necesita.*

- **Propósito del Proyecto:** El nombre del proyecto se llama BrainBash. Es un entorno personalizado para la terminal de Linux, usando zsh, y paquetes extra como eza, bat, starship, con integracion de IA local en la terminal, y respaldo en la nube (Gemini).

- **Necesidades Explícitas:**
  - Detectar las necesidades nuevas en el archivo project_objetives.md, que el usuario ha mencionado o se han detectado/deducido en cada sesion. Esas necesidades deben ser las prioridades mas altas para respetar en el proyecto.

  - El codigo existe en un entorno de desarrollo en Windows, por lo que hay que tener en cuenta que el agente debe sugerir herramientas, configuraciones o comandos que sean compatibles con la terminal de Windows (CMD, PowerShell, Git Bash).
  
  - El codigo debe ser ready to go (listo para ser desplegado en produccion), por lo que se debe evitar el codigo que no sea necesario para el entorno de produccion. Como variables de entorno hardcodeadas, uso de root, direcciones hardcodeadas, API keys, logs, etc. Todo lo que no represente un entorno de usuario real.

  - Se esta usando contenedor en docker para validar el proyecto en diferentes entornos. Como Alpine, Debian, Fedora. El agente tiene la libertad de sugerir, agregar o implementar herramientas, configuraciones o comandos de pruebas para validar localmente el proyecto de la manera mas rapida y eficiente.

  - Si existen contenedores docker en el proyecto, o alguna configuracion docker, pregunta si debes reiniciar los contenedores y/o hacer un rebuild.

- **Limitaciones del Agente:**
  - Los modelos de IA local no deben modificarse, son esos modelos, y la verificacion de que existen se encuentra documentado en la seccion *Documentacion*

- **Objetivos Secundarios:**
  - Hacer el codigo modular, robusto y lo mas simple posible, siguiendo buenas practicas de programacion,
    - S.O.L.I.D (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion),
    - K.I.S.S (Keep It Simple, Stupid),
    - D.R.Y (Don't Repeat Yourself)

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

- **No asumir NADA**, no inventar información que no haya sido dada explícitamente.
- Hacer preguntas de seguimiento después de la respuesta del usuario o en cualquier momento que sea necesario.
- **Principio Rector:** Es mejor mantener informado al usuario de las decisiones que se vayan a tomar antes de actuar, que asumir y equivocarse.

## 3. Registro de Estado del Proyecto

- Realice un registro de los cambios que se vayan haciendo en el proyecto detalladamente y en orden cronologico (fecha y hora), y lo mas reciente al principio.
- El registro se debe hacer en el archivo changelog.md
- Explique en el registro que cambios se hicieron, por que se hicieron y como se hicieron. Todo de la forma mas detallada y posible, no importa la cantidad de letras o espacio que ocupe.

## 4. Decisiones Técnicas

- Explique en el registro que decisiones se tomaron, por que se tomaron y como se tomaron. Todo de la forma mas detallada y posible, no importa la cantidad de letras o espacio que ocupe.
- Las decisiones tomadas en el proyecto debe decirse quien la ha tomado, por el usuario o por el agente, y deben registrarse en el archivo changelog.md. Por Ej: [Decision]: Hecha por el usuario, o [Decision]: Hecha por el agente.
- Cada decision debe estar en orden cronologico (fecha y hora), y lo mas reciente al principio.

## 5. Próximos Pasos y tareas pendientes

- Todas las tareas hechas o pendientes se deben registrar en el archivo changelog.md. Cada tarea debe estar en orden cronologico (fecha y hora), y lo mas reciente al principio.
- Las tareas completadas pueden marcarse con [x] y las pendientes con [ ]
- Las tareas realizadas deben estar vinculadas con las decisiones y los cambios que se hicieron en el proyecto.
  - Por ej: [x] Invertir el paso de instalacion de Ollama, si no se puede descargar desde GitHub, se debe instalar desde ollama_install.sh,
    - **Decision:** Hecha por el usuario, o **Decision:** Hecha por el agente
    - Se realizo el cambio, cambiando el orden de la instalacion de Ollama, ejecutando la url <https://github.com/ollama/ollama/releases/latest/download/ollama-linux-{arch}.tgz> antes de ollama_install.sh. Se cambio el codigo desde la linea 204 a 250 en el archivo main.py, y archivo2.py, etc.

## 6. FAQ / Preguntas para el Usuario

- En el archivo questions.md el agente debe dejar preguntas pendientes si la sesión termina y hay dudas/sugerencias no respondidas o resueltas. Sea especifico y detallado con las preguntas.
