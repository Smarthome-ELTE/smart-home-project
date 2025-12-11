import tkinter as tk
from tkinter import ttk, messagebox
import json
from monitor.monitor_gui import MonitorGUI
from db.database import Database
from Lights.lighting_gui import LightControlPanel

def start_gui(controller=None):
    """Start the enhanced smart home GUI"""
    # Root Window
    root = tk.Tk()
    root.title("Smart Home Lighting System")
    root.geometry("1200x700")
    root.configure(bg="#1e1e2f")

    # Global style (unchanged)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#2b2b3c")
    style.configure("TLabel", background="#2b2b3c", foreground="#ffffff",
                    font=("Segoe UI", 11))
    style.configure("TButton", background="#007acc", foreground="#ffffff",
                    padding=8, font=("Segoe UI", 10, "bold"))
    style.map("TButton", background=[("active", "#008cff")])
    style.configure("TLabelframe", background="#2b2b3c", foreground="#ffffff")
    style.configure("TLabelframe.Label", background="#2b2b3c",
                    foreground="#ffffff", font=("Segoe UI", 11, "bold"))

    # Title
    title = ttk.Label(root, text="🏠 Smart Home Controller", font=("Segoe UI", 18, "bold"))
    title.pack(pady=15)

    # Main container
    main_frame = ttk.Frame(root)
    main_frame.pack(padx=20, pady=10, fill="both", expand=True)

    # Left Panel - Light Controls
    left_panel = ttk.Frame(main_frame, padding=15)
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

    # CRITICAL: Instantiate the LightControlPanel via the import
    light_panel = LightControlPanel(left_panel, controller)
    light_panel.pack(fill="both", expand=True)

    # Right Panel - Monitor
    right_panel = ttk.Frame(main_frame, padding=15)
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

    monitor_gui = MonitorGUI(right_panel)
    monitor_gui.pack(fill="both", expand=True)

    # Auto-refresh every 5 seconds
    def auto_refresh():
        light_panel.load_data()
        monitor_gui.load_events()
        root.after(5000, auto_refresh)  # Refresh every 5 seconds

    root.after(2000, auto_refresh)  # Start after 2 seconds

    # Footer
    ttk.Label(root, text="v0.1 | Made with ❤️ in Python", font=("Segoe UI", 9)).pack(side="bottom", pady=10)

    root.mainloop()


if __name__ == "__main__":
    start_gui()