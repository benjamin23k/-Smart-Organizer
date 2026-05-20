import threading

# Tkinter es dependiente de librerías del sistema (tk). Si no están instaladas,
# el módulo debe seguir importándose para que el CLI funcione.
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
except Exception:  # pragma: no cover
    tk = None
    filedialog = messagebox = scrolledtext = None


from .config import load_config
from .organizer import process_path
from .watcher import start
from .utils import rollback_history


class SmartOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Organizer")
        self.root.geometry("820x520")

   
        self.config_path_var = tk.StringVar(value="tests/config.example.toml")

        self.dry_run_var = tk.BooleanVar(value=False)
        self._worker_thread: threading.Thread | None = None
        self._watching = False

        self._build_ui()

    def _build_ui(self) -> None:
        frm = tk.Frame(self.root, padx=12, pady=12)
        frm.pack(fill="both", expand=True)

      
        top = tk.Frame(frm)
        top.pack(fill="x")

        tk.Label(top, text="Config TOML:").pack(side="left")
        tk.Entry(top, textvariable=self.config_path_var, width=55).pack(side="left", padx=8)
        tk.Button(top, text="Search…", command=self._pick_config).pack(side="left")


        opt = tk.Frame(frm)
        opt.pack(fill="x", pady=(10, 10))

        tk.Checkbutton(opt, text="Dry-run (no mover)", variable=self.dry_run_var).pack(
            side="left"
        )

        btns = tk.Frame(frm)
        btns.pack(fill="x", pady=(0, 10))

        tk.Button(btns, text="Run (1 vez)", width=18, command=self._run_once).pack(
            side="left", padx=(0, 10)
        )
        tk.Button(btns, text="Watch (real time)", width=22, command=self._watch).pack(

            side="left", padx=(0, 10)
        )
        tk.Button(btns, text="Undo (rollback)", width=18, command=self._undo).pack(
            side="left", padx=(0, 10)
        )
        tk.Button(btns, text="Exit", width=10, command=self.root.destroy).pack(

            side="right"
        )

        # Log
        log_frame = tk.LabelFrame(frm, text="Log")
        log_frame.pack(fill="both", expand=True)

        self.log = scrolledtext.ScrolledText(log_frame, height=16, wrap=tk.WORD)
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

        self._log("Ready. Use Run or Watch.")


    def _log(self, msg: str) -> None:
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update_idletasks()

    def _pick_config(self) -> None:
        path = filedialog.askopenfilename(
            title="Select config.toml",
            filetypes=[("TOML", "*.toml"), ("All files", "*.*")],

        )
        if path:
            self.config_path_var.set(path)

    def _load_cfg_or_show(self):
        try:
            cfg_path = self.config_path_var.get().strip()
            if not cfg_path:
                raise ValueError("Empty path")

            from pathlib import Path
            cfg = load_config(Path(cfg_path))
            self._log(f"[CFG] loaded: {cfg_path}")

            return cfg
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar config: {e}")
            return None

    def _run_once(self) -> None:
        if self._worker_thread and self._worker_thread.is_alive():
            messagebox.showwarning("Busy", "There is already a task running.")

            return

        cfg = self._load_cfg_or_show()
        if cfg is None:
            return

        dry = bool(self.dry_run_var.get())

        def worker():
            self._log(f"[RUN] dry_run={dry} cfg={self.config_path_var.get()}")
            try:
                process_path(cfg, dry_run=dry)
                self._log("[RUN] Finished.")

            except Exception as e:
                self._log(f"[RUN] Error: {e}")
                messagebox.showerror("Error", str(e))

        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()

    def _watch(self) -> None:
        cfg = self._load_cfg_or_show()
        if cfg is None:
            return

        if self._watching:
            messagebox.showinfo("Info", "You are already in Watch mode (single instance).")

            return

        dry = bool(self.dry_run_var.get())
        self._watching = True

        def worker():
            self._log(f"[WATCH] dry_run={dry} cfg={self.config_path_var.get()}")
            try:
                start(cfg, dry_run=dry)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                self._log(f"[WATCH] Error: {e}")
                messagebox.showerror("Error", str(e))
            finally:
                self._watching = False
                self._log("[WATCH] Finished.")


        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()

    def _undo(self) -> None:
        try:
            ok = rollback_history()
            self._log("[UNDO] OK" if ok else "[UNDO] Nothing to undo")

        except Exception as e:
            messagebox.showerror("Error", str(e))


def run_gui():
    root = tk.Tk()
    SmartOrganizerGUI(root)
    root.mainloop()

