import sys
import builtins
import threading
import subprocess
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from src.post_install_linux.backend.controller import Controller

DARK_BG = "#181818"
DARK_FG = "#f1f1f1"
DARK_ACCENT = "#222222"
DARK_ENTRY = "#232323"
DARK_BTN = "#282828"
DARK_BTN_ACTIVE = "#333333"

class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)
        self.widget.configure(state='disabled')

    def flush(self):
        pass

class InputDialog(simpledialog.Dialog):
    def __init__(self, parent, prompt):
        self.prompt = prompt
        self.input_value = None
        super().__init__(parent, title="Entrada necessária")

    def body(self, master):
        master.configure(bg=DARK_BG)
        label = tk.Label(master, text=self.prompt, bg=DARK_BG, fg=DARK_FG)
        label.pack(padx=10, pady=5)
        self.entry = tk.Entry(master, bg=DARK_ENTRY, fg=DARK_FG, insertbackground=DARK_FG)
        self.entry.pack(padx=10, pady=5)
        return self.entry

    def apply(self):
        self.input_value = self.entry.get()

    def get_input(self):
        return self.input_value

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Post Install Linux")
        self.geometry("800x600")
        self.configure(bg=DARK_BG)

        # Switches (Checkbuttons)
        self.full_install_var = tk.BooleanVar()
        self.install_apps_var = tk.BooleanVar()
        self.apply_theme_var = tk.BooleanVar()
        self.config_terminal_var = tk.BooleanVar()

        options_frame = tk.Frame(self, bg=DARK_BG)
        options_frame.pack(pady=10, padx=10, anchor='w')

        tk.Checkbutton(options_frame, text="Full Install", variable=self.full_install_var,
                       bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor='w')
        tk.Checkbutton(options_frame, text="Install Apps", variable=self.install_apps_var,
                       bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor='w')
        tk.Checkbutton(options_frame, text="Apply Theme", variable=self.apply_theme_var,
                       bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor='w')
        tk.Checkbutton(options_frame, text="Configure Terminal", variable=self.config_terminal_var,
                       bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor='w')

        # Output area
        self.output_view = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=20, state='disabled', font=("Consolas", 10),
                                                     bg=DARK_ACCENT, fg=DARK_FG, insertbackground=DARK_FG)
        self.output_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Execute button
        self.execute_button = tk.Button(self, text="Executar", command=self.on_execute,
                                        bg=DARK_BTN, fg=DARK_FG, activebackground=DARK_BTN_ACTIVE, activeforeground=DARK_FG)
        self.execute_button.pack(pady=10)

        # Instancia controller passando output_view para manipular saída
        self.controller = Controller()

        # Redireciona print() e input()
        sys.stdout = TextRedirector(self.output_view)
        sys.stderr = TextRedirector(self.output_view)
        builtins.input = self.custom_input

        # Armazena a senha sudo só em memória
        self.sudo_password = None

    def custom_input(self, prompt):
        dialog = InputDialog(self, prompt)
        response = dialog.get_input()
        self.output_view.configure(state='normal')
        self.output_view.insert(tk.END, f"{prompt}{response}\n")
        self.output_view.see(tk.END)
        self.output_view.configure(state='disabled')
        return response

    def ask_sudo_password(self):
        if self.sudo_password is None:
            self.sudo_password = simpledialog.askstring("Senha sudo", "Digite sua senha sudo:", show='*', parent=self)
        return self.sudo_password

    def run_sudo_command(self, command):
        password = self.ask_sudo_password()
        if not password:
            print("Operação cancelada pelo usuário.")
            return
        proc = subprocess.Popen(
            f"echo {password} | sudo -S {command}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in proc.stdout:
            print(line, end='')
        proc.wait()

    def on_execute(self):
        self.output_view.configure(state='normal')
        self.output_view.delete(1.0, tk.END)
        self.output_view.configure(state='disabled')
        thread = threading.Thread(target=self.run_tasks)
        thread.start()

    def run_tasks(self):
        # Pede a senha sudo uma vez, se necessário
        if any([self.full_install_var.get(), self.install_apps_var.get(), self.apply_theme_var.get(), self.config_terminal_var.get()]):
            self.ask_sudo_password()

        if self.full_install_var.get():
            print("[+] Executando instalação completa...")
            # Exemplo: self.run_sudo_command("apt update && apt upgrade -y")
            self.controller.install_full()  # Adapte seu controller para receber a senha se necessário

        if self.install_apps_var.get():
            print("[+] Instalando apps...")
            self.controller.install_packages()

        if self.apply_theme_var.get():
            print("[+] Aplicando tema GTK...")
            self.controller.install_gtk_theme()

        if self.config_terminal_var.get():
            print("[+] Configurando terminal...")
            self.controller.install_oh_my_bash()

        print("\n[✓] Concluído.")

        # Limpa a senha da memória ao final
        self.sudo_password = None

def start_gui():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    start_gui()