import threading


try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
except Exception:  
    tk = None
    filedialog = messagebox = scrolledtext = None


from .config import load_config
from .organizer import process_path
from .watcher import start
from .utils import rollback_history


class SmartOrganizerGUI:
   
    BG = "#1e1e2e"
    FG = "#cdd6f4"
    CARD_BG = "#252538"
    INPUT_BG = "#313244"
    INPUT_FG = "#cdd6f4"
    ACCENT_BLUE = "#89b4fa"
    ACCENT_GREEN = "#a6e3a1"
    ACCENT_RED = "#f38ba8"
    ACCENT_YELLOW = "#f9e2af"
    LOG_BG = "#181825"
    LOG_FG = "#a6e3a1"
    BTN_TEXT_DARK = "#11111b"

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Organizer")
        self.root.geometry("850x540")
        self.root.configure(bg=self.BG)

        from pathlib import Path
        self.watch_path_var = tk.StringVar(value=str(Path.cwd()))
        self.dry_run_var = tk.BooleanVar(value=False)
        self._worker_thread: threading.Thread | None = None
        self._watching = False
        self._stop_event: threading.Event | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        # Base container
        frm = tk.Frame(self.root, bg=self.BG, padx=16, pady=16)
        frm.pack(fill="both", expand=True)

        # Header Title
        title_lbl = tk.Label(
            frm,
            text="📂 SMART ORGANIZER",
            font=("Segoe UI", 16, "bold"),
            bg=self.BG,
            fg=self.ACCENT_BLUE,
        )
        title_lbl.pack(anchor="w", pady=(0, 15))

        # Folder to organize row
        target_frm = tk.Frame(frm, bg=self.BG)
        target_frm.pack(fill="x", pady=6)

        tk.Label(
            target_frm,
            text="Folder to Organize:",
            font=("Segoe UI", 10, "bold"),
            bg=self.BG,
            fg=self.FG,
            width=16,
            anchor="w",
        ).pack(side="left")

        self.watch_entry = tk.Entry(
            target_frm,
            textvariable=self.watch_path_var,
            font=("Segoe UI", 10),
            bg=self.INPUT_BG,
            fg=self.INPUT_FG,
            insertbackground=self.FG,
            relief="flat",
            bd=6,
        )
        self.watch_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = tk.Button(
            target_frm,
            text="Browse…",
            font=("Segoe UI", 9, "bold"),
            command=self._pick_watch_path,
            bg=self.INPUT_BG,
            fg=self.FG,
            activebackground=self.ACCENT_BLUE,
            activeforeground=self.BTN_TEXT_DARK,
            relief="flat",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        browse_btn.pack(side="right")

      
        opt = tk.Frame(frm, bg=self.BG)
        opt.pack(fill="x", pady=(10, 15))

        self.dry_run_cb = tk.Checkbutton(
            opt,
            text="Dry-run (simulate only)",
            font=("Segoe UI", 10),
            variable=self.dry_run_var,
            bg=self.BG,
            fg=self.FG,
            activebackground=self.BG,
            activeforeground=self.FG,
            selectcolor=self.BG,
            bd=0,
            padx=0,
            pady=0,
        )
        self.dry_run_cb.pack(side="left")

       
        btns = tk.Frame(frm, bg=self.BG)
        btns.pack(fill="x", pady=(0, 15))

        self.run_btn = tk.Button(
            btns,
            text="Run Once",
            font=("Segoe UI", 10, "bold"),
            command=self._run_once,
            bg=self.ACCENT_BLUE,
            fg=self.BTN_TEXT_DARK,
            activebackground="#74c7ec",
            activeforeground=self.BTN_TEXT_DARK,
            relief="flat",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
        )
        self.run_btn.pack(side="left", padx=(0, 10))

        self.watch_btn = tk.Button(
            btns,
            text="Watch (Real-Time)",
            font=("Segoe UI", 10, "bold"),
            command=self._watch,
            bg=self.ACCENT_GREEN,
            fg=self.BTN_TEXT_DARK,
            activebackground="#94e2d5",
            activeforeground=self.BTN_TEXT_DARK,
            relief="flat",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
        )
        self.watch_btn.pack(side="left", padx=(0, 10))

        self.undo_btn = tk.Button(
            btns,
            text="Undo (Rollback)",
            font=("Segoe UI", 10, "bold"),
            command=self._undo,
            bg=self.ACCENT_YELLOW,
            fg=self.BTN_TEXT_DARK,
            activebackground="#f9e2af",
            activeforeground=self.BTN_TEXT_DARK,
            relief="flat",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
        )
        self.undo_btn.pack(side="left", padx=(0, 10))

        self.exit_btn = tk.Button(
            btns,
            text="Exit",
            font=("Segoe UI", 10, "bold"),
            command=self.root.destroy,
            bg=self.INPUT_BG,
            fg=self.FG,
            activebackground=self.ACCENT_RED,
            activeforeground=self.BTN_TEXT_DARK,
            relief="flat",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
        )
        self.exit_btn.pack(side="right")

        log_frame = tk.LabelFrame(
            frm,
            text=" Execution Logs ",
            font=("Segoe UI", 10, "bold"),
            bg=self.BG,
            fg=self.FG,
            bd=1,
            relief="solid",
            padx=8,
            pady=8,
        )
        log_frame.pack(fill="both", expand=True)

        self.log = scrolledtext.ScrolledText(
            log_frame,
            font=("Courier New", 10),
            bg=self.LOG_BG,
            fg=self.LOG_FG,
            insertbackground=self.FG,
            selectbackground="#45475a",
            selectforeground=self.FG,
            relief="flat",
            bd=0,
            height=16,
            wrap=tk.WORD,
        )
        self.log.pack(fill="both", expand=True)

        self._log("Ready. Select options and run/watch.")

    def _log(self, msg: str) -> None:
        if self.log:
            self.log.insert(tk.END, msg + "\n")
            self.log.see(tk.END)
            self.root.update_idletasks()

    def _pick_watch_path(self) -> None:
        path = filedialog.askdirectory(
            title="Select Folder to Organize",
            initialdir=self.watch_path_var.get(),
        )
        if path:
            self.watch_path_var.set(path)

    def _load_cfg_or_show(self):
        try:
            from .config import resolve_config_path
            cfg_path = resolve_config_path(None)
            cfg = load_config(cfg_path)
            self._log(f"[CFG] Loaded default config: {cfg_path}")
            return cfg
        except Exception as e:
            messagebox.showerror("Error", f"Could not load config file: {e}")
            return None

    def _run_once(self) -> None:
        if self._worker_thread and self._worker_thread.is_alive():
            messagebox.showwarning("Busy", "There is already a task running.")
            return

        cfg = self._load_cfg_or_show()
        if cfg is None:
            return

        watch_path = self.watch_path_var.get().strip()
        if not watch_path:
            messagebox.showerror("Error", "Please select a folder to organize.")
            return

        from pathlib import Path
        cfg.general.watch_paths = [Path(watch_path).expanduser().resolve()]
        dry = bool(self.dry_run_var.get())

        self.run_btn.configure(state="disabled", bg="#45475a")

        def worker():
            self._log(f"[RUN] dry_run={dry} path={watch_path}")
            try:
                process_path(cfg, dry_run=dry)
                self._log("[RUN] Finished organization successfully.")
            except Exception as e:
                self._log(f"[RUN] Error: {e}")
                messagebox.showerror("Error", str(e))
            finally:
                self.root.after(0, lambda: self.run_btn.configure(state="normal", bg=self.ACCENT_BLUE))

        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()

    def _watch(self) -> None:
        if self._watching:
            
            self._log("[WATCH] Requesting watcher to stop...")
            if self._stop_event:
                self._stop_event.set()
            self.watch_btn.configure(text="Stopping...", state="disabled", bg="#45475a")
            return

        cfg = self._load_cfg_or_show()
        if cfg is None:
            return

        watch_path = self.watch_path_var.get().strip()
        if not watch_path:
            messagebox.showerror("Error", "Please select a folder to watch.")
            return

        from pathlib import Path
        cfg.general.watch_paths = [Path(watch_path).expanduser().resolve()]
        dry = bool(self.dry_run_var.get())

        self._watching = True
        self._stop_event = threading.Event()

       
        self.watch_btn.configure(
            text="Stop Watching",
            bg=self.ACCENT_RED,
            activebackground="#efa6b2",
        )

        def worker():
            self._log(f"[WATCH] Started watching dry_run={dry} path={watch_path}")
            try:
                start(cfg, dry_run=dry, stop_event=self._stop_event)
            except Exception as e:
                self._log(f"[WATCH] Error: {e}")
                messagebox.showerror("Error", str(e))
            finally:
                self._watching = False
                self.root.after(0, self._reset_watch_ui)
                self._log("[WATCH] Watcher stopped.")

        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()

    def _reset_watch_ui(self) -> None:
        self.watch_btn.configure(
            text="Watch (Real-Time)",
            state="normal",
            bg=self.ACCENT_GREEN,
            activebackground="#94e2d5",
        )

    def _undo(self) -> None:
        try:
            ok = rollback_history()
            self._log("[UNDO] Rollback executed." if ok else "[UNDO] Nothing to undo.")
        except Exception as e:
            self._log(f"[UNDO] Error: {e}")
            messagebox.showerror("Error", str(e))


def run_gui():
    if tk is None:
        raise ImportError("Tkinter is not available.")
    root = tk.Tk()
    SmartOrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
