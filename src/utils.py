import subprocess
import shutil
import sys
from typing import List, Tuple

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    
    @staticmethod
    def preview_all():
        print(f"\n--- VISTA PREVIA DE TEMAS ---")
        print(f"{Colors.BLUE}➜ AZUL (Debian){Colors.RESET} | {Colors.GREEN}➜ VERDE (Hacker){Colors.RESET}")
        print(f"{Colors.MAGENTA}➜ MAGENTA (Cyberpunk){Colors.RESET} | {Colors.RED}➜ ROJO (Admin){Colors.RESET}")
        print("\n")

class TUI:
    def __init__(self):
        self.has_whiptail = shutil.which("whiptail") is not None

    def show_menu(self, title: str, prompt: str, options: List[Tuple[str, str]]) -> str:
        """Menu de seleccion unica"""
        if self.has_whiptail:
            return self._whiptail_menu(title, prompt, options)
        return self._simple_menu(title, prompt, options)

    def show_checklist(self, title: str, prompt: str, options: List[Tuple[str, str, str]]) -> List[str]:
        """
        Menu de seleccion multiple.
        Options format: (TAG, DESCRIPCION, ESTADO ["ON"/"OFF"])
        """
        if self.has_whiptail:
            return self._whiptail_checklist(title, prompt, options)
        else:
            return self._simple_checklist(title, prompt, options)

    def _whiptail_menu(self, title: str, prompt: str, options: List[Tuple[str, str]]) -> str:
        # Detectar tamaño de terminal
        cols, lines = shutil.get_terminal_size(fallback=(80, 24))
        
        # Ajustar ancho (max 100, margen 4)
        width = min(100, cols - 4)
        if width < 40: width = 40 # Minimo razonable
        
        # Ajustar alto (max 22, margen 4)
        height = min(24, lines - 4)
        list_height = height - 8 # Espacio para bordes y titulo
        if list_height < 2: list_height = 2

        args = ["whiptail", "--title", title, "--menu", prompt, str(height), str(width), str(list_height)]
        for tag, desc in options:
            args.extend([tag, desc])
        try:
            res = subprocess.run(args, stderr=subprocess.PIPE, check=True)
            return res.stderr.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            sys.exit(0)

    def _whiptail_checklist(self, title: str, prompt: str, options: List[Tuple[str, str, str]]) -> List[str]:
        # Detectar tamaño de terminal
        cols, lines = shutil.get_terminal_size(fallback=(80, 24))
        
        # Ajustar ancho (max 100, margen 4)
        width = min(100, cols - 4)
        if width < 40: width = 40
        
        # Ajustar alto
        height = min(26, lines - 4)
        list_height = height - 8
        if list_height < 2: list_height = 2
        
        # whiptail --checklist text height width list-height [tag item status]...
        args = ["whiptail", "--title", title, "--checklist", prompt, str(height), str(width), str(list_height)]
        for tag, desc, status in options:
            args.extend([tag, desc, status])
        
        try:
            # Whiptail devuelve "opt1" "opt2" "opt3"
            res = subprocess.run(args, stderr=subprocess.PIPE, check=True)
            output = res.stderr.decode('utf-8').strip()
            # Limpiamos las comillas que devuelve whiptail
            return [x.strip('"') for x in output.split(" ")] if output else []
        except subprocess.CalledProcessError:
            sys.exit(0)

    def _simple_menu(self, title: str, prompt: str, options: List[Tuple[str, str]]) -> str:
        print(f"\n=== {title} ===")
        for idx, (tag, desc) in enumerate(options):
            print(f"{idx + 1}) {desc}")
        sel = input("Opcion: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(options):
            return options[int(sel)-1][0]
        return options[0][0]

    def _simple_checklist(self, title: str, prompt: str, options: List[Tuple[str, str, str]]) -> List[str]:
        # Convertimos las opciones a un diccionario mutable para el loop
        # Format: (tag, desc, status)
        selection_state = {tag: (status == "ON") for tag, _, status in options}
        
        while True:
            print(f"\n=== {title} ===")
            print(prompt)
            print("-" * 40)
            
            # Mostrar opciones
            opts_list = [] # Para poder acceder por indice
            for i, (tag, desc, _) in enumerate(options):
                is_selected = selection_state[tag]
                mark = "[x]" if is_selected else "[ ]"
                print(f"{i+1}) {mark} {desc}")
                opts_list.append(tag)
            
            print("-" * 40)
            print("Escribe el numero para alternar selección.")
            print("C o Enter para confirmar y continuar.")
            
            inp = input("Opcion: ").strip().lower()
            
            if inp == "" or inp == "c":
                break
            
            if inp.isdigit():
                idx = int(inp) - 1
                if 0 <= idx < len(opts_list):
                    tag_toggled = opts_list[idx]
                    selection_state[tag_toggled] = not selection_state[tag_toggled]
        
        # Retornamos solo los que quedaron en True
        return [tag for tag, is_on in selection_state.items() if is_on]

class Logger:
    def __init__(self, theme_color: str = Colors.BLUE, log_file: str = None):
        self.theme_color = theme_color
        self.log_file = log_file
        
        # Initialize log file (overwrite)
        if self.log_file:
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write("=== BrainBash Installer Log ===\n")
            except Exception as e:
                print(f"[Error] No se pudo crear log file: {e}")
                self.log_file = None

    def _log(self, prefix, msg, color=None, to_stdout=True):
        # 1. Stdout
        if to_stdout:
            if color:
                print(f"{color}{prefix}{Colors.RESET} {msg}")
            else:
                print(f"{prefix} {msg}")
        
        # 2. File
        if self.log_file:
            try:
                # Remove ANSI colors for file
                clean_msg = f"{prefix} {msg}\n"
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(clean_msg)
            except: pass

    def info(self, msg): self._log("[INFO]", msg, self.theme_color)
    def success(self, msg): self._log("[OK]", msg, Colors.GREEN)
    def warning(self, msg): self._log("[AVISO]", msg, Colors.YELLOW)
    def error(self, msg): self._log("[ERROR]", msg, Colors.RED)
    
    def step(self, msg): 
        self._log(f"\n=== {msg} ===", "", self.theme_color + Colors.BOLD)

    def verbose(self, msg):
        """Log only to file, not stdout (for streamlined operations)"""
        self._log("[VERBOSE]", msg, to_stdout=False)

if __name__ == "__main__":
    tui = TUI()
