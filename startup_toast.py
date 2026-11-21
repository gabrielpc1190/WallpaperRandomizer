"""Small transient splash shown at program startup.

Displays a borderless topmost toast in the bottom-right corner that auto-
closes after a configurable delay. Runs in its own daemon thread so it does
not block the tray icon or the background download/rotation loops.
"""

import threading
import tkinter as tk


def _run_toast(message: str, duration_ms: int) -> None:
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    try:
        # Slight transparency looks closer to a native Win11 notification.
        root.attributes('-alpha', 0.93)
    except tk.TclError:
        pass

    bg = '#202020'
    accent = '#4c9aff'
    root.configure(bg=bg)

    frame = tk.Frame(root, bg=bg, highlightthickness=1, highlightbackground=accent)
    frame.pack(fill='both', expand=True)

    tk.Label(
        frame,
        text="Wallpaper Randomizer",
        fg=accent,
        bg=bg,
        font=('Segoe UI Semibold', 10),
        anchor='w',
    ).pack(fill='x', padx=16, pady=(10, 0))

    tk.Label(
        frame,
        text=message,
        fg='white',
        bg=bg,
        font=('Segoe UI', 9),
        anchor='w',
    ).pack(fill='x', padx=16, pady=(2, 10))

    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    # Bottom-right, leaving room for the taskbar.
    x = sw - w - 20
    y = sh - h - 60
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.after(duration_ms, root.destroy)
    try:
        root.mainloop()
    except Exception:
        # Any Tk error here must not crash the startup thread.
        pass


def show(message: str = "Se inició correctamente.", duration_ms: int = 2000) -> None:
    """Fire the toast in a daemon thread so callers aren't blocked."""
    threading.Thread(
        target=_run_toast,
        args=(message, duration_ms),
        daemon=True,
    ).start()
