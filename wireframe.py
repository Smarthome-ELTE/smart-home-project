"""
Enhanced Smart Home GUI with Heating System Controls
Displays real-time sensor data, device status, and automation rules
"""

import tkinter as tk
from tkinter import ttk
from monitor.monitor_gui import MonitorGUI
from Heating.heating_gui import HeatingControlPanel


def start_gui(controller=None):
    """Start the enhanced smart home GUI"""
    # Root Window
    root = tk.Tk()
    root.title("Smart Home Heating System")
    root.geometry("1200x700")
    root.configure(bg="#1e1e2f")
    
    # Global style
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
    title = ttk.Label(root, text="🏠 Smart Home Heating System", 
                     font=("Segoe UI", 20, "bold"))
    title.pack(pady=15)
    
    # Main container
    main_frame = ttk.Frame(root)
    main_frame.pack(padx=20, pady=10, fill="both", expand=True)
    
    # Left Panel - Heating Controls (with auto-refresh)
    left_panel = ttk.Frame(main_frame, padding=15)
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    heating_panel = HeatingControlPanel(left_panel, controller=controller)
    heating_panel.pack(fill="both", expand=True)
    
    # Right Panel - Monitor (with auto-refresh)
    right_panel = ttk.Frame(main_frame, padding=15)
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    monitor_gui = MonitorGUI(right_panel)
    monitor_gui.pack(fill="both", expand=True)
    
    # Footer
    footer = ttk.Label(root, 
                      text="v1.0 | Made with ❤️ in Python", 
                      font=("Segoe UI", 9))
    footer.pack(side="bottom", pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    start_gui()