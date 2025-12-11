"""
Heating Control Panel GUI Component - FIXED VERSION
Shows ALL heating rules, not just ones with "Bedroom" in the name
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import sys
import os

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
              AND name LIKE '%Bedroom%'
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
              AND name LIKE '%Bedroom%'
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
        
        ttk.Button(btn_frame, text="🗑️ Delete Rule", 
                  command=self.delete_rule).pack(side="left", padx=5)
        
    def load_data(self):
        """Load current heating sensor data and automation rules"""
        cursor = self.db.conn.cursor()
        
        # Load heating temperature sensors
        cursor.execute("""
            SELECT id, name, last_payload 
            FROM sensors 
            WHERE type = 'DHT22_Heating'
              AND name LIKE '%Bedroom%'
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
                            foreground="#00D9FF"  # Bright cyan
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
              AND name LIKE '%Bedroom%'
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
                            color = "#FF5252"  # Bright red
                        elif state == "OFF":
                            status_text = f"{name}: ❄️ OFF (Target: {target}°C)"
                            color = "#64B5F6"  # Light blue
                        else:
                            status_text = f"{name}: {state}"
                            color = "#FFD740"  # Yellow
                        
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
        
        # Load heating automation rules - SHOW ALL RULES!
        self.rules_tree.delete(*self.rules_tree.get_children())
        
        # FIXED: Show ALL rules with DHT22_Heating sensors (no name filter!)
        cursor.execute("""
            SELECT t.id, t.name, t.enabled 
            FROM triggers t
            INNER JOIN sensors s ON t.sensor_id = s.id
            WHERE s.type = 'DHT22_Heating'
            ORDER BY t.id
        """)
        triggers = cursor.fetchall()
        
        # Only print on first load or when count changes
        if not hasattr(self, '_last_rule_count') or self._last_rule_count != len(triggers):
            print(f"📋 GUI: Loaded {len(triggers)} heating rules")
            self._last_rule_count = len(triggers)
        
        for trigger_id, name, enabled in triggers:
            status = "✓ Enabled" if enabled else "✗ Disabled"
            self.rules_tree.insert("", "end", values=(name, status), 
                                  tags=(trigger_id,))
    
    def start_auto_refresh(self):
        """Start automatic refresh every 5 seconds"""
        self.load_data()
        self.auto_refresh_job = self.after(5000, self.start_auto_refresh)  # Changed from 2000 to 5000
    
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
        
        if self.controller:
            self.controller.switch_trigger(trigger_id)
            self.load_data()
            messagebox.showinfo("Success", "Rule status updated!")
        else:
            messagebox.showerror("Error", "Controller not available")
    
    def delete_rule(self):
        """Delete selected automation rule with confirmation"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", 
                                 "Please select a rule to delete.")
            return
        
        item = self.rules_tree.item(selection[0])
        trigger_id = item['tags'][0]
        rule_name = item['values'][0]
        
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this rule?\n\n'{rule_name}'\n\nThis action cannot be undone."
        )
        
        if not confirm:
            return
        
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM triggers WHERE id = ?", (trigger_id,))
            self.db.conn.commit()
            
            self.load_data()
            messagebox.showinfo("Success", f"Rule '{rule_name}' deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete rule: {e}")
    
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
        name_entry.insert(0, "New Heating Rule")
        name_entry.select_range(0, tk.END)  # Select all text for easy editing
        
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
                # Validate inputs
                name = name_entry.get().strip()
                if not name:
                    messagebox.showerror("Invalid Input", "Please enter a rule name!")
                    return
                
                if not sensor_var.get():
                    messagebox.showerror("Invalid Input", "Please select a sensor!")
                    return
                
                if not device_var.get():
                    messagebox.showerror("Invalid Input", "Please select a device!")
                    return
                
                sensor_id = int(sensor_var.get().split(":")[0])
                operator = operator_var.get()
                value = value_entry.get().strip()
                device_id = int(device_var.get().split(":")[0])
                state = state_var.get()
                target_temp = target_entry.get().strip()
                
                if not value:
                    messagebox.showerror("Invalid Input", "Please enter a temperature value!")
                    return
                
                if not target_temp:
                    messagebox.showerror("Invalid Input", "Please enter a target temperature!")
                    return
                
                # Create condition and action
                condition = {"temperature": f"{operator}{value}"}
                action_payload = {"state": state, "temperature": int(target_temp)}
                
                print(f"🆕 Adding rule: {name}")
                print(f"   Condition: {condition}")
                print(f"   Action: {action_payload}")
                
                # Add to controller
                if self.controller:
                    self.controller.add_trigger(name, sensor_id, condition, 
                                               device_id, action_payload)
                    dialog.destroy()  # Close dialog FIRST
                    self.load_data()  # Then reload data
                    messagebox.showinfo("Success", f"Rule '{name}' added successfully!")
                else:
                    messagebox.showerror("Error", "Controller not available")
                
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Please enter valid numbers: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add rule: {e}")
        
        ttk.Button(dialog, text="💾 Save Rule", 
                  command=save_rule).pack(pady=20)


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Heating System Test")
    root.geometry("600x700")
    
    style = ttk.Style()
    style.theme_use("clam")
    
    panel = HeatingControlPanel(root)
    panel.pack(fill="both", expand=True, padx=20, pady=20)
    
    root.mainloop()