"""
Heating Control Panel GUI Component
Displays heating-specific sensors, devices, and automation rules
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import Database


class HeatingControlPanel(ttk.Frame):
    """Control panel for heating system management"""
    
    def __init__(self, parent, controller=None, db_path=None):
        super().__init__(parent)
        self.controller = controller
        self.db = Database(db_path=db_path)
        self.auto_refresh_job = None
        self.setup_ui()
        self.load_data()
        self.start_auto_refresh()
        
    def setup_ui(self):
        """Setup the heating control interface"""
        # Header
        header = ttk.Label(self, text="🔥 Heating System Control", 
                          font=("Segoe UI", 14, "bold"))
        header.pack(pady=(0, 15))
        
        # Current Status Frame
        status_frame = ttk.LabelFrame(self, text="Current Status", padding=15)
        status_frame.pack(fill="x", pady=(0, 10))
        
        # Status container
        self.status_container = ttk.Frame(status_frame)
        self.status_container.pack(fill="x")
        
        # Temperature Display (Heating Sensors)
        self.temp_labels = {}
        
        # Get heating sensors and create labels
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, name FROM sensors 
            WHERE type = 'DHT22_Heating' 
            ORDER BY id
        """)
        heating_sensors = cursor.fetchall()
        
        if heating_sensors:
            for sensor_id, sensor_name in heating_sensors:
                label = ttk.Label(self.status_container, 
                                text=f"{sensor_name}: --°C", 
                                font=("Segoe UI", 11))
                label.pack(anchor="w", pady=2)
                self.temp_labels[sensor_id] = label
        else:
            # Show message if no sensors
            ttk.Label(self.status_container, 
                     text="No heating sensors found",
                     foreground="gray").pack(anchor="w", pady=2)
        
        # Add separator
        ttk.Separator(self.status_container, orient='horizontal').pack(fill='x', pady=5)
        
        # Heater Status Display (Heating Devices)
        self.heater_labels = {}
        
        cursor.execute("""
            SELECT id, name FROM devices 
            WHERE type = 'SmartHeater_v2' 
            ORDER BY id
        """)
        heating_devices = cursor.fetchall()
        
        if heating_devices:
            for device_id, device_name in heating_devices:
                label = ttk.Label(self.status_container, 
                                text=f"{device_name}: OFF", 
                                font=("Segoe UI", 11),
                                foreground="#666")
                label.pack(anchor="w", pady=2)
                self.heater_labels[device_id] = label
        else:
            # Show message if no devices
            ttk.Label(self.status_container, 
                     text="No heating devices found",
                     foreground="gray").pack(anchor="w", pady=2)
        
        # Automation Rules Frame
        rules_frame = ttk.LabelFrame(self, text="Automation Rules", padding=15)
        rules_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Rules Treeview
        columns = ("Name", "Status")
        self.rules_tree = ttk.Treeview(rules_frame, columns=columns, 
                                       show="headings", height=6)
        
        self.rules_tree.heading("Name", text="Rule Name")
        self.rules_tree.heading("Status", text="Status")
        
        self.rules_tree.column("Name", width=300)
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
        """Load current heating sensor data and automation rules"""
        cursor = self.db.conn.cursor()
        
        # Load heating temperature sensors
        cursor.execute("""
            SELECT id, name, last_payload 
            FROM sensors 
            WHERE type = 'DHT22_Heating'
            ORDER BY id
        """)
        sensors = cursor.fetchall()
        
        for sensor_id, name, payload in sensors:
            if sensor_id in self.temp_labels:
                if payload:
                    try:
                        data = json.loads(payload)
                        temp = data.get('temperature', '--')
                        humidity = data.get('humidity', '--')
                        self.temp_labels[sensor_id].config(
                            text=f"{name}: {temp}°C (Humidity: {humidity}%)",
                            foreground="black"
                        )
                    except Exception as e:
                        self.temp_labels[sensor_id].config(
                            text=f"{name}: Error parsing data",
                            foreground="red"
                        )
                else:
                    self.temp_labels[sensor_id].config(
                        text=f"{name}: No data",
                        foreground="gray"
                    )
        
        # Load heating devices
        cursor.execute("""
            SELECT id, name, current_status 
            FROM devices 
            WHERE type = 'SmartHeater_v2'
            ORDER BY id
        """)
        devices = cursor.fetchall()
        
        for device_id, name, status in devices:
            if device_id in self.heater_labels:
                if status:
                    try:
                        data = json.loads(status)
                        state = data.get('state', 'unknown').upper()
                        target = data.get('target_temp', data.get('temperature', '--'))
                        power = data.get('power', 0)
                        
                        # Format display based on state
                        if state == "ON":
                            status_text = f"{name}: 🔥 ON (Target: {target}°C, Power: {power}W)"
                            color = "#D32F2F"  # Red for ON
                        elif state == "OFF":
                            status_text = f"{name}: ❄️ OFF (Target: {target}°C)"
                            color = "#1976D2"  # Blue for OFF
                        else:
                            status_text = f"{name}: {state}"
                            color = "#666"
                        
                        self.heater_labels[device_id].config(
                            text=status_text,
                            foreground=color
                        )
                    except Exception as e:
                        self.heater_labels[device_id].config(
                            text=f"{name}: Error - {e}",
                            foreground="red"
                        )
                else:
                    self.heater_labels[device_id].config(
                        text=f"{name}: No data",
                        foreground="gray"
                    )
        
        # Load heating automation rules
        self.rules_tree.delete(*self.rules_tree.get_children())
        
        # Broader filter to catch all heating-related rules
        cursor.execute("""
            SELECT id, name, enabled 
            FROM triggers 
            WHERE name LIKE '%Room:%' 
               OR name LIKE '%Heating%'
               OR name LIKE '%Heat%'
               OR name LIKE '%cold%'
               OR name LIKE '%hot%'
            ORDER BY id
        """)
        triggers = cursor.fetchall()
        
        for trigger_id, name, enabled in triggers:
            status = "✓ Enabled" if enabled else "✗ Disabled"
            self.rules_tree.insert("", "end", values=(name, status), 
                                  tags=(trigger_id,))
    
    def start_auto_refresh(self):
        """Start automatic refresh every 2 seconds"""
        self.load_data()
        # Schedule next refresh
        self.auto_refresh_job = self.after(2000, self.start_auto_refresh)
    
    def stop_auto_refresh(self):
        """Stop automatic refresh"""
        if self.auto_refresh_job:
            self.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None
    
    def toggle_rule(self):
        """Toggle selected heating automation rule on/off"""
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
        else:
            messagebox.showerror("Error", "Controller not available")
    
    def show_add_rule_dialog(self):
        """Show dialog to add new heating automation rule"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Heating Automation Rule")
        dialog.geometry("500x450")
        dialog.transient(self)
        dialog.grab_set()
        
        # Rule Name
        ttk.Label(dialog, text="Rule Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(dialog, width=50)
        name_entry.pack(pady=5)
        name_entry.insert(0, "My Custom Heating Rule")
        
        # Sensor Selection
        ttk.Label(dialog, text="Temperature Sensor:").pack(pady=(10, 0))
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, name FROM sensors 
            WHERE type = 'DHT22_Heating'
            ORDER BY id
        """)
        sensors = cursor.fetchall()
        
        sensor_var = tk.StringVar()
        sensor_combo = ttk.Combobox(dialog, textvariable=sensor_var, 
                                   values=[f"{s[0]}: {s[1]}" for s in sensors],
                                   state="readonly", width=47)
        sensor_combo.pack(pady=5)
        if sensors:
            sensor_combo.current(0)
        
        # Condition
        ttk.Label(dialog, text="Condition:").pack(pady=(10, 0))
        
        condition_frame = ttk.Frame(dialog)
        condition_frame.pack(pady=5)
        
        ttk.Label(condition_frame, text="temperature").pack(side="left", padx=5)
        
        operator_var = tk.StringVar(value="<")
        operator_combo = ttk.Combobox(condition_frame, textvariable=operator_var,
                                     values=["<", ">", "<=", ">=", "=="],
                                     state="readonly", width=5)
        operator_combo.pack(side="left", padx=5)
        
        value_entry = ttk.Entry(condition_frame, width=10)
        value_entry.pack(side="left", padx=5)
        value_entry.insert(0, "18")
        
        ttk.Label(condition_frame, text="°C").pack(side="left")
        
        # Device Selection
        ttk.Label(dialog, text="Heater Device:").pack(pady=(10, 0))
        
        cursor.execute("""
            SELECT id, name FROM devices 
            WHERE type = 'SmartHeater_v2'
            ORDER BY id
        """)
        devices = cursor.fetchall()
        
        device_var = tk.StringVar()
        device_combo = ttk.Combobox(dialog, textvariable=device_var,
                                   values=[f"{d[0]}: {d[1]}" for d in devices],
                                   state="readonly", width=47)
        device_combo.pack(pady=5)
        if devices:
            device_combo.current(0)
        
        # Action
        ttk.Label(dialog, text="Action:").pack(pady=(10, 0))
        
        action_frame = ttk.Frame(dialog)
        action_frame.pack(pady=5)
        
        state_var = tk.StringVar(value="on")
        ttk.Radiobutton(action_frame, text="Turn ON", 
                       variable=state_var, value="on").pack(side="left", padx=10)
        ttk.Radiobutton(action_frame, text="Turn OFF", 
                       variable=state_var, value="off").pack(side="left", padx=10)
        
        # Target Temperature
        temp_frame = ttk.Frame(dialog)
        temp_frame.pack(pady=10)
        
        ttk.Label(temp_frame, text="Target Temperature:").pack(side="left", padx=5)
        target_entry = ttk.Entry(temp_frame, width=8)
        target_entry.pack(side="left", padx=5)
        target_entry.insert(0, "22")
        ttk.Label(temp_frame, text="°C").pack(side="left")
        
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
                else:
                    messagebox.showerror("Error", "Controller not available")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add rule: {e}")
        
        ttk.Button(dialog, text="💾 Save Rule", 
                  command=save_rule).pack(pady=20)


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Heating System Test")
    root.geometry("600x700")
    
    # Apply theme
    style = ttk.Style()
    style.theme_use("clam")
    
    panel = HeatingControlPanel(root)
    panel.pack(fill="both", expand=True, padx=20, pady=20)
    
    root.mainloop()