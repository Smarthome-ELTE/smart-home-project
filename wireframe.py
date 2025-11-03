import tkinter as tk
from tkinter import ttk
from monitor.monitor_gui import MonitorGUI

def start_gui():
    # Root Window
    root = tk.Tk()
    root.title("Smart Home GUI")
    root.geometry("1000x600")
    root.configure(bg="#1e1e2f")

    # Global style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#2b2b3c")
    style.configure("TLabel", background="#2b2b3c", foreground="#ffffff", font=("Segoe UI", 12))
    style.configure("TButton", background="#007acc", foreground="#ffffff", padding=6, font=("Segoe UI", 11, "bold"))
    style.map("TButton", background=[("active", "#008cff")])

    # Title
    title = ttk.Label(root, text="🏠 Smart Home Controller", font=("Segoe UI", 18, "bold"))
    title.pack(pady=15)

    # Frame container
    main_frame = ttk.Frame(root)
    main_frame.pack(padx=20, pady=10, fill="both", expand=True)

    # Controller Frame
    controller_frame = ttk.Frame(main_frame, padding=20)
    controller_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    ttk.Label(controller_frame, text="⚙️ Controller", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

    ttk.Button(controller_frame, text="▶️ Run Automation").pack(pady=5, fill="x")
    ttk.Button(controller_frame, text="⏹️ Stop Automation").pack(pady=5, fill="x")

    ttk.Label(controller_frame, text="").pack(pady=10)

    ttk.Label(controller_frame, text="📋 Automation Rules", font=("Segoe UI", 12)).pack(pady=(10, 5))
    ttk.Button(controller_frame, text="➕ Add Rule").pack(pady=5, fill="x")
    ttk.Button(controller_frame, text="✏️ Edit Rules").pack(pady=5, fill="x")

    # Monitor Frame
    monitor_frame = ttk.Frame(main_frame, padding=20)
    monitor_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

    monitor_gui = MonitorGUI(monitor_frame)
    monitor_gui.pack(fill="both", expand=True)

    # Footer
    ttk.Label(root, text="v0.1 | Made with ❤️ in Python", font=("Segoe UI", 9)).pack(side="bottom", pady=10)

    root.mainloop()
