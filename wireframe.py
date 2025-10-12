import tkinter as tk
from tkinter import ttk

# Root Window
root = tk.Tk()
root.title("Smart Home GUI")
root.geometry("600x400")
root.configure(bg="#1e1e2f")  # dark background

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
title = ttk.Label(root, text="🏠 Smart Home Controller", font=("Segoe UI", 16, "bold"))
title.pack(pady=15)

# Frame container
main_frame = ttk.Frame(root)
main_frame.pack(padx=20, pady=10, fill="both", expand=True)

# Controller Frame
controller_frame = ttk.Frame(main_frame, padding=20)
controller_frame.pack(side="left", fill="both", expand=True, padx=10)




controller_label = ttk.Label(controller_frame, text="Controller")
controller_label.pack(pady=10)

controller_button = ttk.Button(controller_frame, text="Run Automation")
controller_button.pack(pady=10)

# Monitor Frame
monitor_frame = ttk.Frame(main_frame, padding=20)
monitor_frame.pack(side="right", fill="both", expand=True, padx=10)

monitor_label = ttk.Label(monitor_frame, text="Monitor")
monitor_label.pack(pady=10)

monitor_button = ttk.Button(monitor_frame, text="View Data")
monitor_button.pack(pady=10)

# Footer
footer = ttk.Label(root, text="v0.1 | Made with ❤️ in Python", font=("Segoe UI", 9))
footer.pack(side="bottom", pady=10)

root.mainloop()
