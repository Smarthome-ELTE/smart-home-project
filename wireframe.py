import tkinter as tk
from tkinter import ttk
from monitor.monitor_gui import MonitorGUI

# Root Window
root = tk.Tk()
root.title("Smart Home GUI")
root.geometry("1000x600")
root.configure(bg="#1e1e2f")

# Global style
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TFrame",
    background="#2b2b3c",
)
style.configure(
    "TLabel",
    background="#2b2b3c",
    foreground="#ffffff",
    font=("Segoe UI", 12)
)
style.configure(
    "TButton",
    background="#007acc",
    foreground="#ffffff",
    padding=6,
    font=("Segoe UI", 11, "bold")
)
style.map("TButton", background=[("active", "#008cff")])

# Title
title = ttk.Label(root, text="🏠 Smart Home Controller", font=("Segoe UI", 18, "bold"))
title.pack(pady=15)

# Frame container
main_frame = ttk.Frame(root)
main_frame.pack(padx=20, pady=10, fill="both", expand=True)

# Controller Frame (Left side)
controller_frame = ttk.Frame(main_frame, padding=20)
controller_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

controller_label = ttk.Label(controller_frame, text="⚙️ Controller", font=("Segoe UI", 14, "bold"))
controller_label.pack(pady=(0, 20))

# Controller buttons
controller_button = ttk.Button(controller_frame, text="▶️ Run Automation")
controller_button.pack(pady=5, fill="x")

stop_button = ttk.Button(controller_frame, text="⏹️ Stop Automation")
stop_button.pack(pady=5, fill="x")

# Spacer
ttk.Label(controller_frame, text="").pack(pady=10)

# Rules section
rules_label = ttk.Label(controller_frame, text="📋 Automation Rules", font=("Segoe UI", 12))
rules_label.pack(pady=(10, 5))

add_rule_btn = ttk.Button(controller_frame, text="➕ Add Rule")
add_rule_btn.pack(pady=5, fill="x")

edit_rule_btn = ttk.Button(controller_frame, text="✏️ Edit Rules")
edit_rule_btn.pack(pady=5, fill="x")

# Monitor Frame (Right side) - Embed the MonitorGUI component
monitor_frame = ttk.Frame(main_frame, padding=20)
monitor_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

# Create and pack the monitor GUI
monitor_gui = MonitorGUI(monitor_frame)
monitor_gui.pack(fill="both", expand=True)

# Footer
footer = ttk.Label(root, text="v0.1 | Made with ❤️ in Python", font=("Segoe UI", 9))
footer.pack(side="bottom", pady=10)

root.mainloop()