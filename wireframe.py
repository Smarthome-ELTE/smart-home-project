"""
Enhanced Smart Home GUI with Heating System Controls and Gas System Controls
Displays real-time sensor data, device status, and automation rules
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from monitor.monitor_gui import MonitorGUI
from gas.gas_gui import GasControlPanel
from db.database import Database


class HeatingControlPanel(ttk.Frame):
    """Control panel for heating system management"""
    
    def __init__(self, parent, controller, db_path=None):
        super().__init__(parent)
        self.controller = controller
        self.db = Database(db_path=db_path)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup the heating control interface"""
        # Header
        header = ttk.Label(self, text="🔥 Heating System Control", 
                          font=("Segoe UI", 14, "bold"))
        header.pack(pady=(0, 15))
        
        # Current Status Frame
        status_frame = ttk.LabelFrame(self, text="Current Status", padding=15)
        status_frame.pack(fill="x", pady=(0, 10))
        
        # Temperature Display
        self.temp_label = ttk.Label(status_frame, 
                                    text="Living Room: --°C", 
                                    font=("Segoe UI", 12))
        self.temp_label.pack(anchor="w")
        
        self.bedroom_temp_label = ttk.Label(status_frame, 
                                           text="Bedroom: --°C", 
                                           font=("Segoe UI", 12))
        self.bedroom_temp_label.pack(anchor="w", pady=(5, 0))
        
        # Heater Status
        self.heater_label = ttk.Label(status_frame, 
                                     text="Main Heater: OFF", 
                                     font=("Segoe UI", 11))
        self.heater_label.pack(anchor="w", pady=(10, 0))
        
        # Automation Rules Frame
        rules_frame = ttk.LabelFrame(self, text="Automation Rules", padding=15)
        rules_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Rules Treeview
        columns = ("Name", "Status")
        self.rules_tree = ttk.Treeview(rules_frame, columns=columns, 
                                       show="headings", height=6)
        
        self.rules_tree.heading("Name", text="Rule Name")
        self.rules_tree.heading("Status", text="Status")
        
        self.rules_tree.column("Name", width=250)
        self.rules_tree.column("Status", width=100)
        
        # Scrollbar for rules
        scrollbar = ttk.Scrollbar(rules_frame, orient="vertical", 
                                 command=self.rules_tree.yview)
        self.rules_tree.configure(yscroll=scrollbar.set)
        
        self.rules_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons Frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="🔄 Refresh", 
                  command=self.load_data).pack(side="left", padx=(0, 5))
        
        ttk.Button(btn_frame, text="⚙️ Toggle Rule", 
                  command=self.toggle_rule).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="➕ Add Rule", 
                  command=self.show_add_rule_dialog).pack(side="left", padx=5)
        
    def load_data(self):
        """Load current sensor data and automation rules"""
        # Load temperature data
        cursor = self.db.conn.cursor()
        
        # Get latest temperature sensor data
        cursor.execute("""
            SELECT name, last_payload 
            FROM sensors 
            WHERE category = 'temperature'
            ORDER BY id
        """)
        sensors = cursor.fetchall()
        
        for i, (name, payload) in enumerate(sensors):
            if payload:
                try:
                    data = json.loads(payload)
                    temp = data.get('temperature', '--')
                    if i == 0:
                        self.temp_label.config(text=f"{name}: {temp}°C")
                    elif i == 1:
                        self.bedroom_temp_label.config(text=f"{name}: {temp}°C")
                except:
                    pass
        
        # Get heater status
        cursor.execute("""
            SELECT name, current_status 
            FROM devices 
            WHERE category = 'temperature'
            LIMIT 1
        """)
        device = cursor.fetchone()
        
        if device and device[1]:
            try:
                status = json.loads(device[1])
                state = status.get('state', 'unknown').upper()
                target = status.get('target_temp', '--')
                self.heater_label.config(
                    text=f"{device[0]}: {state} (Target: {target}°C)"
                )
            except:
                pass
        
        # Load automation rules
        self.rules_tree.delete(*self.rules_tree.get_children())
        
        triggers = self.db.get_all_triggers()
        for trigger in triggers:
            trigger_id, name, _, _, _, _, enabled, _ = trigger
            status = "✓ Enabled" if enabled else "✗ Disabled"
            self.rules_tree.insert("", "end", values=(name, status), 
                                  tags=(trigger_id,))
    
    def toggle_rule(self):
        """Toggle selected automation rule on/off"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", 
                                 "Please select a rule to toggle.")
            return
        
        item = self.rules_tree.item(selection[0])
        trigger_id = item['tags'][0]
        
        # Toggle in controller
        if self.controller:
            self.controller.switch_trigger(trigger_id)
            self.load_data()
            messagebox.showinfo("Success", "Rule status updated!")
    
    def show_add_rule_dialog(self):
        """Show dialog to add new automation rule"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Automation Rule")
        dialog.geometry("450x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Rule Name
        ttk.Label(dialog, text="Rule Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        name_entry.insert(0, "My Heating Rule")
        
        # Sensor Selection
        ttk.Label(dialog, text="Trigger Sensor:").pack(pady=(10, 0))
        
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id, name FROM sensors WHERE category='temperature'")
        sensors = cursor.fetchall()
        
        sensor_var = tk.StringVar()
        sensor_combo = ttk.Combobox(dialog, textvariable=sensor_var, 
                                   values=[f"{s[0]}: {s[1]}" for s in sensors],
                                   state="readonly", width=37)
        sensor_combo.pack(pady=5)
        if sensors:
            sensor_combo.current(0)
        
        # Condition
        ttk.Label(dialog, text="Condition (e.g., temperature < 18):").pack(pady=(10, 0))
        
        condition_frame = ttk.Frame(dialog)
        condition_frame.pack(pady=5)
        
        ttk.Label(condition_frame, text="temperature").pack(side="left")
        
        operator_var = tk.StringVar(value="<")
        operator_combo = ttk.Combobox(condition_frame, textvariable=operator_var,
                                     values=["<", ">", "<=", ">=", "=="],
                                     state="readonly", width=5)
        operator_combo.pack(side="left", padx=5)
        
        value_entry = ttk.Entry(condition_frame, width=10)
        value_entry.pack(side="left")
        value_entry.insert(0, "18")
        
        # Device Selection
        ttk.Label(dialog, text="Control Device:").pack(pady=(10, 0))
        
        cursor.execute("SELECT id, name FROM devices WHERE category='temperature'")
        devices = cursor.fetchall()
        
        device_var = tk.StringVar()
        device_combo = ttk.Combobox(dialog, textvariable=device_var,
                                   values=[f"{d[0]}: {d[1]}" for d in devices],
                                   state="readonly", width=37)
        device_combo.pack(pady=5)
        if devices:
            device_combo.current(0)
        
        # Action
        ttk.Label(dialog, text="Action:").pack(pady=(10, 0))
        
        action_frame = ttk.Frame(dialog)
        action_frame.pack(pady=5)
        
        state_var = tk.StringVar(value="on")
        ttk.Radiobutton(action_frame, text="Turn ON", 
                       variable=state_var, value="on").pack(side="left", padx=5)
        ttk.Radiobutton(action_frame, text="Turn OFF", 
                       variable=state_var, value="off").pack(side="left", padx=5)
        
        ttk.Label(action_frame, text="Target Temp:").pack(side="left", padx=(10, 0))
        target_entry = ttk.Entry(action_frame, width=8)
        target_entry.pack(side="left", padx=5)
        target_entry.insert(0, "22")
        
        # Save Button
        def save_rule():
            try:
                name = name_entry.get()
                sensor_id = int(sensor_var.get().split(":")[0])
                operator = operator_var.get()
                value = value_entry.get()
                device_id = int(device_var.get().split(":")[0])
                state = state_var.get()
                target_temp = int(target_entry.get())
                
                # Create condition and action
                condition = {"temperature": f"{operator}{value}"}
                action_payload = {"state": state, "temperature": target_temp}
                
                # Add to controller
                if self.controller:
                    self.controller.add_trigger(name, sensor_id, condition, 
                                               device_id, action_payload)
                    self.load_data()
                    dialog.destroy()
                    messagebox.showinfo("Success", "Rule added successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add rule: {e}")
        
        ttk.Button(dialog, text="💾 Save Rule", 
                  command=save_rule).pack(pady=20)


def start_gui(controller=None):
    """Start the enhanced smart home GUI"""
    # Root Window
    root = tk.Tk()
    root.title("Smart Home Heating & Gas System")
    root.geometry("1400x800")
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
    title = ttk.Label(root, text="🏠 Smart Home System - Heating & Gas", 
                     font=("Segoe UI", 20, "bold"))
    title.pack(pady=15)
    
    # Main container with tabs
    notebook = ttk.Notebook(root)
    notebook.pack(padx=20, pady=10, fill="both", expand=True)
    
    # ===== TAB 1: HEATING SYSTEM =====
    heating_frame = ttk.Frame(notebook)
    notebook.add(heating_frame, text="🔥 Heating System")
    
    # Create heating panel in the tab
    heating_main = ttk.Frame(heating_frame)
    heating_main.pack(padx=15, pady=15, fill="both", expand=True)
    
    # Left side - Heating Controls
    left_panel = ttk.Frame(heating_main, padding=15)
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    heating_panel = HeatingControlPanel(left_panel, controller)
    heating_panel.pack(fill="both", expand=True)
    
    # Right side - Monitor
    right_panel = ttk.Frame(heating_main, padding=15)
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    monitor_gui = MonitorGUI(right_panel)
    monitor_gui.pack(fill="both", expand=True)
    
    # ===== TAB 2: GAS SYSTEM =====
    gas_frame = ttk.Frame(notebook)
    notebook.add(gas_frame, text="💨 Gas System")
    
    # Create gas panel in the tab
    gas_main = ttk.Frame(gas_frame)
    gas_main.pack(padx=15, pady=15, fill="both", expand=True)
    
    # Left side - Gas Controls
    gas_left_panel = ttk.Frame(gas_main, padding=15)
    gas_left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    gas_panel = GasControlPanel(gas_left_panel, controller)
    gas_panel.pack(fill="both", expand=True)
    
    # Right side - Monitor (reuse same monitor)
    gas_right_panel = ttk.Frame(gas_main, padding=15)
    gas_right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    gas_monitor = MonitorGUI(gas_right_panel)
    gas_monitor.pack(fill="both", expand=True)
    
    # Auto-refresh panels every 5 seconds
    def auto_refresh():
        try:
            if heating_panel:
                heating_panel.load_data()
            if gas_panel:
                gas_panel.load_data()
            if monitor_gui:
                monitor_gui.load_events()
            if gas_monitor:
                gas_monitor.load_events()
        except:
            pass
        root.after(5000, auto_refresh)  # Refresh every 5 seconds
    
    root.after(2000, auto_refresh)  # Start after 2 seconds
    
    # Footer
    footer = ttk.Label(root, 
                      text="v2.0 | Heating & Gas System Integration | Made with ❤️ in Python", 
                      font=("Segoe UI", 9))
    footer.pack(side="bottom", pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    start_gui()