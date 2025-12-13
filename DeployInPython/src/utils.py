import subprocess
import shutil
import sys
import time
from typing import List, Tuple

class Colors:
    """
    Codigos ANSI para colorear la salida de texto estandar.
    """
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Paleta
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"

    @staticmethod
    def preview_all():
        """Muestra una vista previa de como se ven los colores en esta terminal"""
        print(f"\n--- VISTA PREVIA DE TEMAS ---")
        print(f"{Colors.RED}➜ Tema ROJO: [ERROR] Fallo crítico{Colors.RESET}")
        print(f"{Colors.GREEN}➜ Tema VERDE: [OK] Todo correcto{Colors.RESET}")
        print(f"{Colors.BLUE}➜ Tema AZUL: [INFO] Instalando paquetes...{Colors.RESET}")
        print(f"{Colors.MAGENTA}➜ Tema MAGENTA: [IA] Ollama está pensando...{Colors.RESET}")
        print(f"{Colors.CYAN}➜ Tema CYAN: [NET] Descargando archivos...{Colors.RESET}")
        print(f"{Colors.YELLOW}➜ Tema AMARILLO: [WARN] Advertencia de disco{Colors.RESET}")
        print("\nPresiona ENTER para elegir tu favorito...")
        input() # Pausa para que el usuario vea los colores

class TUI:
    """
    Maneja la interfaz (whiptail o texto simple).
    """
    def __init__(self):
        self.has_whiptail = shutil.which("whiptail") is not None

    def show_menu(self, title: str, prompt: str, options: List[Tuple[str, str]]) -> str:
        if self.has_whiptail:
            return self._show_whiptail_menu(title, prompt, options)
        else:
            return self._show_simple_menu(title, prompt, options)

    def _show_whiptail_menu(self, title: str, prompt: str, options: List[Tuple[str, str]]) -> str:
        # Altura, Ancho, AlturaLista
        args = ["whiptail", "--title", title, "--menu", prompt, "20", "70", "10"]
        for tag, desc in options:
            args.append(tag)
            args.append(desc)

        try:
            # Whiptail usa stderr para el output de la seleccion
            result = subprocess.run(args, stderr=subprocess.PIPE, check=True)
            return result.stderr.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            sys.exit(0)

    def _show_simple_menu(self, title: str, prompt: str, options: List[Tuple[str, str]]) -> str:
        print(f"\n=== {title} ===")
        print(prompt)
        for idx, (tag, desc) in enumerate(options):
            print(f"{idx + 1}) {desc}")
        
        while True:
            sel = input("Opción (número o nombre): ").strip()
            # Logica simple de seleccion
            if sel.isdigit() and 1 <= int(sel) <= len(options):
                return options[int(sel)-1][0]
            for tag, _ in options:
                if sel == tag: return tag

class Logger:
    """
    Sistema de logs que usa el color elegido por el usuario.
    """
    def __init__(self, theme_color: str = Colors.BLUE):
        self.theme_color = theme_color

    def info(self, message: str):
        print(f"{self.theme_color}[INFO]{Colors.RESET} {message}")

    def success(self, message: str):
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {message}") # Exito siempre verde

    def error(self, message: str):
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {message}") # Error siempre rojo

    def step(self, message: str):
        # El encabezado usa el color del tema + negrita
        print(f"\n{Colors.BOLD}{self.theme_color}=== {message} ==={Colors.RESET}")