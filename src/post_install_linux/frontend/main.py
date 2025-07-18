import sys
import threading
import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk

# Seu Controller import
from post_install_linux.backend.controller.controller import Controller

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, s):
        # Use after para garantir execução na thread principal do Tkinter
        self.text_widget.after(0, self.text_widget.insert, 'end', s)
        self.text_widget.after(0, self.text_widget.see, 'end')

    def flush(self):
        pass

class PostInstallLinuxApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Post Install Linux")
        self.geometry("600x600")
        self.resizable(False, False)

        self.controller = Controller()
        self.create_widgets()

        # Redireciona stdout e stderr para o terminal embutido
        self.stdout_redirector = TextRedirector(self.text_terminal)
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stdout_redirector

    def create_widgets(self):
        title = ttk.Label(self, text="Installation", font=("Helvetica", 20, "bold"))
        title.pack(pady=15)

        container = ttk.Frame(self)
        container.pack(pady=10)

        self.options = {
            "Full Install": self.controller.install_full,
            "Install Apps": self.controller.install_packages,
            "Apply Theme": self.controller.install_gtk_theme,
            "Configure Terminal": self.controller.setup_aliases_and_tools,
        }

        self.switch_vars = {}
        for option in self.options.keys():
            frame = ttk.Frame(container)
            frame.pack(fill="x", pady=5, padx=15)
            label = ttk.Label(frame, text=option, font=("Helvetica", 14), bootstyle="info")
            label.pack(side="left")
            var = tk.BooleanVar(value=True)
            check = ttk.Checkbutton(frame, variable=var, bootstyle="success-round-toggle")
            check.pack(side="right")
            self.switch_vars[option] = var

        run_btn = ttk.Button(self, text="Run Selected", command=self.run_selected)
        run_btn.pack(pady=10)

        terminal_frame = ttk.Frame(self)
        terminal_frame.pack(padx=15, pady=15, fill="both", expand=True)

        self.text_terminal = tk.Text(
            terminal_frame,
            bg="black",
            fg="white",
            insertbackground="white",
            font=("Courier", 13)
        )
        self.text_terminal.pack(fill="both", expand=True)
        self.text_terminal.insert("end", "meu@linux $ \n")

    def run_selected(self):
        def task():
            for option, method in self.options.items():
                if self.switch_vars[option].get():
                    print(f"Running {option}...")
                    try:
                        method()
                        print(f"{option} completed successfully.")
                    except Exception as e:
                        print(f"Error running {option}: {e}")
            print("All selected tasks finished.")

        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    app = PostInstallLinuxApp()
    app.mainloop()
