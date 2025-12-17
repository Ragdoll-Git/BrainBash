import sys
import os
from google import genai

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

# Configuracion del Cliente (Nuevo SDK)
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.5-flash"

# MODO 1: Comando directo (gemini: "pregunta")
if len(sys.argv) > 1:
    prompt = " ".join(sys.argv[1:])
    try:
        # Generate content (configuramos system_instruction aqui si es necesario, 
        # en el nuevo SDK suele ir en el config o en la llamada)
        config = None
        if system_instruction:
            from google.genai import types
            config = types.GenerateContentConfig(system_instruction=system_instruction)

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=config
        )
        print(response.text)
    except Exception as e:
        print(f"Error de API: {e}")

# MODO 2: Chat Interactivo (gemini:)
else:
    # Configurar chat config
    chat_config = None
    if system_instruction:
        from google.genai import types
        chat_config = types.GenerateContentConfig(system_instruction=system_instruction)

    chat = client.chats.create(model=MODEL_ID, config=chat_config)
    
    print("\033[1;34m--- Chat Gemini (Nube) ---\033[0m")
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
            
            for chunk in chat.send_message_stream(user_input):
                 if chunk.text:
                    print(chunk.text, end="", flush=True)
            print("\n")
            
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"\nError: {e}")