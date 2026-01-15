import sys
import os
import time
from google import genai
from google.genai import types

# Tu zshrc debe exportar esta variable
api_key = os.getenv("GEMINI_API_KEY")

# Fallback: Intentar leer .zshrc si no esta en env (ej: usuario no reinicio shell)
if not api_key:
    try:
        secrets_path = os.path.expanduser("~/.brainbash_secrets")
        if os.path.exists(secrets_path):
            with open(secrets_path, "r") as f:
                for line in f:
                    if "export GEMINI_API_KEY=" in line:
                         parts = line.split("=", 1)
                         if len(parts) > 1:
                             api_key = parts[1].strip().strip("'").strip('"')
                             break
    except:
        pass

if not api_key:
    print("Error: Variable GEMINI_API_KEY no configurada.")
    print("Edita el archivo ~/.brainbash_secrets y agrega: export GEMINI_API_KEY='tu_clave'")
    sys.exit(1)

# Leer contexto compartido si existe
system_instruction = None
context_path = os.path.expanduser("~/.config/brainbash/context.md")
if os.path.exists(context_path):
    try:
        with open(context_path, "r") as f:
            system_instruction = f.read().strip()
    except:
        pass

# Configuracion del Cliente (Nuevo SDK v2.5+)
client = genai.Client(api_key=api_key)

# LISTA DE PRIORIDAD (Fallback Strategy)
# 1. 3 Flash Preview (Mas potente/nuevo)
# 2. 2.5 Flash (Standard)
# 3. 2.5 Flash Lite (Backup economico/rapido)
PRIORITY_MODELS = [
    "gemini-3-flash-preview", 
    "gemini-2.5-flash", 
    "gemini-2.5-flash-lite"
]

def generate_with_fallback(prompt, config=None):
    """
    Intenta generar contenido iterando sobre la lista de modelos.
    Si falla uno, prueba el siguiente.
    """
    last_error = None
    
    for model_id in PRIORITY_MODELS:
        try:
            # print(f"\033[90m(Intento con modelo: {model_id})\033[0m") # Debug visible opcional
            
            response = client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=config
            )
            return response.text
            
        except Exception as e:
            # Capturamos ResourceExhausted, ServiceUnavailable, etc.
            # En python genai sdk suelen ser google.api_core.exceptions, pero aqui capturamos general
            # para simplificar sin importar todo.
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str or "503" in error_str or "not found" in error_str:
                # print(f"\033[33m[Warn] Modelo {model_id} fallo/agotado. Probando siguiente...\033[0m")
                last_error = e
                continue # Probar siguiente
            else:
                # print(f"Error critico no relacionado con cuota: {e}")
                raise e # Lanzar si es otro error (ej: bad request)

    # Si salimos del loop, fallaron todos
    raise Exception(f"Todos los modelos de respaldo fallaron. Ultimo error: {last_error}")

def chat_stream_with_fallback(chat_session, user_input):
    """
    Nota: El objeto 'chat' esta atado a un modelo especifico al crearse.
    Si falla, tendriamos que recrear el chat session con el nuevo modelo 
    y re-enviar el historial.
    
    Para simplicidad en CLI interactivo, si el modelo falla en stream,
    podemos intentar hacer un 'one-shot' con fallback y imprimirlo,
    pero perdemos el estado del objeto 'chat' original si no lo reconstruimos.
    
    Estrategia simple v1: Reintentar la llamada send_message_stream. 
    Si falla por cuota, NO podemos cambiar el modelo de una sesion viva facilmente 
    sin migrar el historial.
    
    Solucion robusta: Mantener el historial (history) nosotros y recrear el cliente.
    """
    try:
        for chunk in chat_session.send_message_stream(user_input):
            yield chunk.text
    except Exception as e:
         # Logica compleja de fallback en chat:
         # 1. Obtener historial actual
         # 2. Crear nueva session con siguiente modelo
         # 3. Re-enviar historial?? (Costoso y lento)
         # Por ahora, notificamos el error y sugerimos esperar.
         yield f"\n[!] Error en chat (Modelo actual saturado o error): {e}\n"

# ==========================================
# EJECUCION
# ==========================================

# MODO 1: Comando directo (gemini: "pregunta")
if len(sys.argv) > 1:
    prompt = " ".join(sys.argv[1:])
    try:
        config = None
        if system_instruction:
            config = types.GenerateContentConfig(system_instruction=system_instruction)

        text = generate_with_fallback(prompt, config)
        print(text)
        
    except Exception as e:
        print(f"Error Fatal de API: {e}")

# MODO 2: Chat Interactivo (gemini:)
else:
    # Por defecto iniciamos con el modelo mas alto.
    # Si falla al inicio, podriamos iterar. Pero hacer fallback DENTRO de una sesion larga es complejo.
    # Vamos a intentar encontrar el "mejor modelo disponible" al arrancar.
    
    active_model = None
    chat = None
    
    # Ping test para elegir modelo inicial
    # print("Conectando con mejor modelo disponible...")
    config = None
    if system_instruction:
        config = types.GenerateContentConfig(system_instruction=system_instruction)

    for model_id in PRIORITY_MODELS:
        try:
            # Dry run creation check? 
            chat = client.chats.create(model=model_id, config=config)
            active_model = model_id
            break
        except:
            continue
            
    if not chat:
        print("Error: No se pudo iniciar ningun modelo (Cuota o Red).")
        sys.exit(1)

    print(f"\033[1;34m--- Chat Gemini (Nube) [{active_model}] ---\033[0m")
    print("Escribe 'exit' o 'salir' para salir.\n")

    while True:
        try:
            user_input = input("\033[1;32mTu > \033[0m")
            if user_input.lower() in ["exit", "salir"]:
                break
            if not user_input.strip():
                continue
            
            # Efecto de streaming
            print("\033[1;34mGemini > \033[0m", end="", flush=True)
            
            # Usamos el generador simple (sin fallback dinamico complejo por ahora)
            full_response = ""
            for text_chunk in chat_stream_with_fallback(chat, user_input):
                if text_chunk:
                    print(text_chunk, end="", flush=True)
                    full_response += text_chunk
            print("\n")
            
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"\nError: {e}")
