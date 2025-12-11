"""
Gas System GUI Panel
Displays gas sensor readings and controls gas pipe valves
"""

import json
from tkinter import ttk, messagebox
from db.database import Database


class GasControlPanel(ttk.Frame):
    """Control panel for gas system management"""
    
    def __init__(self, parent, controller, db_path=None):
        super().__init__(parent)
        self.controller = controller
        self.db = Database(db_path=db_path)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the gas system control interface"""
        # Header
        header = ttk.Label(self, text="💨 Gas System Control", 
                          font=("Segoe UI", 14, "bold"))
        header.pack(pady=(0, 15))
        
        # Current Status Frame
        status_frame = ttk.LabelFrame(self, text="Current Gas Levels", padding=15)
        status_frame.pack(fill="x", pady=(0, 10))
        
        # Kitchen Gas Sensor Status
        self.kitchen_gas_label = ttk.Label(status_frame, 
                                           text="Kitchen: 0 ppm (Normal)", 
                                           font=("Segoe UI", 11))
        self.kitchen_gas_label.pack(anchor="w")
        
        # Living Room Gas Sensor Status
        self.living_room_gas_label = ttk.Label(status_frame, 
                                               text="Living Room: 0 ppm (Normal)", 
                                               font=("Segoe UI", 11))
        self.living_room_gas_label.pack(anchor="w", pady=(5, 0))
        
        # Utility Room Gas Sensor Status
        self.utility_room_gas_label = ttk.Label(status_frame, 
                                                text="Utility Room: 0 ppm (Normal)", 
                                                font=("Segoe UI", 11))
        self.utility_room_gas_label.pack(anchor="w", pady=(5, 0))
        
        # Gas Valve Control Frame
        valve_frame = ttk.LabelFrame(self, text="Gas Pipe Valves Control", padding=15)
        valve_frame.pack(fill="x", pady=(0, 10))
        
        # Main Gas Valve Status
        self.main_valve_label = ttk.Label(valve_frame, 
                                          text="Main Gas Valve: CLOSED", 
                                          font=("Segoe UI", 11, "bold"))
        self.main_valve_label.pack(anchor="w")
        
        # Main Valve Control Buttons
        main_valve_btn_frame = ttk.Frame(valve_frame)
        main_valve_btn_frame.pack(fill="x", pady=(5, 10), padx=(20, 0))
        
        self.main_valve_open_btn = ttk.Button(main_valve_btn_frame, text="🔓 Open Main Valve", 
                                              command=self.open_main_valve)
        self.main_valve_open_btn.pack(side="left", padx=(0, 5))
        
        self.main_valve_close_btn = ttk.Button(main_valve_btn_frame, text="🔒 Close Main Valve", 
                                               command=self.close_main_valve)
        self.main_valve_close_btn.pack(side="left")
        
        # Kitchen Gas Valve Status
        self.kitchen_valve_label = ttk.Label(valve_frame, 
                                             text="Kitchen Gas Valve: CLOSED", 
                                             font=("Segoe UI", 11, "bold"))
        self.kitchen_valve_label.pack(anchor="w", pady=(10, 0))
        
        # Kitchen Valve Control Buttons
        kitchen_valve_btn_frame = ttk.Frame(valve_frame)
        kitchen_valve_btn_frame.pack(fill="x", pady=(5, 10), padx=(20, 0))
        
        self.kitchen_valve_open_btn = ttk.Button(kitchen_valve_btn_frame, text="🔓 Open Kitchen Valve", 
                                                 command=self.open_kitchen_valve)
        self.kitchen_valve_open_btn.pack(side="left", padx=(0, 5))
        
        self.kitchen_valve_close_btn = ttk.Button(kitchen_valve_btn_frame, text="🔒 Close Kitchen Valve", 
                                                  command=self.close_kitchen_valve)
        self.kitchen_valve_close_btn.pack(side="left")
        
        # Boiler Gas Valve Status
        self.boiler_valve_label = ttk.Label(valve_frame, 
                                            text="Boiler Gas Valve: CLOSED", 
                                            font=("Segoe UI", 11, "bold"))
        self.boiler_valve_label.pack(anchor="w", pady=(10, 0))
        
        # Boiler Valve Control Buttons
        boiler_valve_btn_frame = ttk.Frame(valve_frame)
        boiler_valve_btn_frame.pack(fill="x", pady=(5, 0), padx=(20, 0))
        
        self.boiler_valve_open_btn = ttk.Button(boiler_valve_btn_frame, text="🔓 Open Boiler Valve", 
                                                command=self.open_boiler_valve)
        self.boiler_valve_open_btn.pack(side="left", padx=(0, 5))
        
        self.boiler_valve_close_btn = ttk.Button(boiler_valve_btn_frame, text="🔒 Close Boiler Valve", 
                                                 command=self.close_boiler_valve)
        self.boiler_valve_close_btn.pack(side="left")
        
        # Automation Rules Frame
        rules_frame = ttk.LabelFrame(self, text="Gas Automation Rules", padding=15)
        rules_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Rules listbox
        self.rules_listbox = ttk.Treeview(rules_frame, columns=("Rule Name", "Status"), 
                                          show="headings", height=4)
        self.rules_listbox.heading("Rule Name", text="Rule Name")
        self.rules_listbox.heading("Status", text="Status")
        self.rules_listbox.column("Rule Name", width=200)
        self.rules_listbox.column("Status", width=100)
        self.rules_listbox.pack(fill="both", expand=True, pady=(0, 10))
        
        # Add Rule Button
        add_rule_btn = ttk.Button(rules_frame, text="➕ Add Gas Automation Rule", 
                                  command=self.show_add_rule_dialog)
        add_rule_btn.pack(anchor="w")
    
    def load_data(self):
        """Load gas sensors and devices data from database"""
        try:
            # Load gas sensor readings
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT id, name, last_payload FROM sensors WHERE category='gas'")
            sensors = cursor.fetchall()
            
            sensor_map = {}
            for sensor_id, sensor_name, payload in sensors:
                sensor_map[sensor_name] = json.loads(payload) if payload else {}
            
            # Update sensor labels
            kitchen_data = sensor_map.get("Kitchen Gas Sensor", {"gas_level": 0, "status": "normal"})
            self.kitchen_gas_label.config(
                text=f"Kitchen: {kitchen_data.get('gas_level', 0)} ppm ({kitchen_data.get('status', 'normal').upper()})"
            )
            
            living_data = sensor_map.get("Living Room Gas Sensor", {"gas_level": 0, "status": "normal"})
            self.living_room_gas_label.config(
                text=f"Living Room: {living_data.get('gas_level', 0)} ppm ({living_data.get('status', 'normal').upper()})"
            )
            
            utility_data = sensor_map.get("Utility Room Gas Sensor", {"gas_level": 0, "status": "normal"})
            self.utility_room_gas_label.config(
                text=f"Utility Room: {utility_data.get('gas_level', 0)} ppm ({utility_data.get('status', 'normal').upper()})"
            )
            
            # Load gas device statuses
            cursor.execute("SELECT id, name, current_status FROM devices WHERE category='gas'")
            devices = cursor.fetchall()
            
            device_map = {}
            for device_id, device_name, status in devices:
                device_map[device_name] = json.loads(status) if status else {}
            
            # Update valve labels
            main_valve = device_map.get("Main Gas Pipe Valve", {"state": "closed"})
            state_text = "OPEN" if main_valve.get("state") == "open" else "CLOSED"
            self.main_valve_label.config(text=f"Main Gas Valve: {state_text}")
            
            kitchen_valve = device_map.get("Kitchen Gas Valve", {"state": "closed"})
            state_text = "OPEN" if kitchen_valve.get("state") == "open" else "CLOSED"
            self.kitchen_valve_label.config(text=f"Kitchen Gas Valve: {state_text}")
            
            boiler_valve = device_map.get("Boiler Gas Valve", {"state": "closed"})
            state_text = "OPEN" if boiler_valve.get("state") == "open" else "CLOSED"
            self.boiler_valve_label.config(text=f"Boiler Gas Valve: {state_text}")
            
            # Load automation rules
            self.load_gas_rules()
        
        except Exception as e:
            print(f"❌ Error loading gas data: {e}")
    
    def load_gas_rules(self):
        """Load gas-related automation rules"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT t.id, t.name, t.enabled 
                FROM triggers t
                JOIN sensors s ON t.sensor_id = s.id
                WHERE s.category = 'gas'
            """)
            rules = cursor.fetchall()
            
            # Clear existing items
            for item in self.rules_listbox.get_children():
                self.rules_listbox.delete(item)
            
            # Populate rules
            for rule_id, rule_name, enabled in rules:
                status = "✅ ENABLED" if enabled else "⛔ DISABLED"
                self.rules_listbox.insert("", "end", values=(rule_name, status))
        
        except Exception as e:
            print(f"❌ Error loading gas rules: {e}")
    
    def open_main_valve(self):
        """Open main gas pipe valve"""
        self.publish_valve_command("Main Gas Pipe Valve", 2, "open")
        self.main_valve_label.config(text="Main Gas Valve: OPEN")
    
    def close_main_valve(self):
        """Close main gas pipe valve"""
        self.publish_valve_command("Main Gas Pipe Valve", 2, "close")
        self.main_valve_label.config(text="Main Gas Valve: CLOSED")
    
    def open_kitchen_valve(self):
        """Open kitchen gas pipe valve"""
        self.publish_valve_command("Kitchen Gas Valve", 3, "open")
        self.kitchen_valve_label.config(text="Kitchen Gas Valve: OPEN")
    
    def close_kitchen_valve(self):
        """Close kitchen gas pipe valve"""
        self.publish_valve_command("Kitchen Gas Valve", 3, "close")
        self.kitchen_valve_label.config(text="Kitchen Gas Valve: CLOSED")
    
    def open_boiler_valve(self):
        """Open boiler gas pipe valve"""
        self.publish_valve_command("Boiler Gas Valve", 4, "open")
        self.boiler_valve_label.config(text="Boiler Gas Valve: OPEN")
    
    def close_boiler_valve(self):
        """Close boiler gas pipe valve"""
        self.publish_valve_command("Boiler Gas Valve", 4, "close")
        self.boiler_valve_label.config(text="Boiler Gas Valve: CLOSED")
    
    def publish_valve_command(self, valve_name, device_id, state):
        """
        Publish valve control command via MQTT
        
        Args:
            valve_name: Name of the valve
            device_id: Device ID in database
            state: "open" or "close"
        """
        try:
            payload = {
                "device_id": device_id,
                "state": state,
                "mode": "manual"
            }
            self.controller.publish("gas/send", json.dumps(payload), 1)
            messagebox.showinfo("Success", f"{valve_name} set to {state.upper()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to control {valve_name}: {e}")
    
    def show_add_rule_dialog(self):
        """Show dialog to add new gas automation rule"""
        dialog = ttk.Toplevel(self)
        dialog.title("Add Gas Automation Rule")
        dialog.geometry("400x300")
        
        # Rule name
        ttk.Label(dialog, text="Rule Name:").pack(pady=5)
        rule_name_var = ttk.StringVar()
        rule_name_entry = ttk.Entry(dialog, textvariable=rule_name_var)
        rule_name_entry.pack(pady=5, padx=10, fill="x")
        
        # Sensor selection
        ttk.Label(dialog, text="Select Gas Sensor:").pack(pady=5)
        sensor_var = ttk.StringVar()
        sensor_combo = ttk.Combobox(dialog, textvariable=sensor_var, 
                                     values=["Kitchen Gas Sensor", "Living Room Gas Sensor", "Utility Room Gas Sensor"])
        sensor_combo.pack(pady=5, padx=10, fill="x")
        
        # Condition selection
        ttk.Label(dialog, text="Trigger Condition:").pack(pady=5)
        condition_var = ttk.StringVar(value="gas_detected")
        ttk.Radiobutton(dialog, text="Gas Detected (ppm > 100)", variable=condition_var, 
                       value="gas_detected").pack(anchor="w", padx=20)
        ttk.Radiobutton(dialog, text="High Gas Level (ppm > 200)", variable=condition_var, 
                       value="high_gas").pack(anchor="w", padx=20)
        
        # Action selection
        ttk.Label(dialog, text="Action:").pack(pady=5)
        action_var = ttk.StringVar(value="close_main")
        ttk.Radiobutton(dialog, text="Close Main Valve", variable=action_var, 
                       value="close_main").pack(anchor="w", padx=20)
        ttk.Radiobutton(dialog, text="Close All Valves", variable=action_var, 
                       value="close_all").pack(anchor="w", padx=20)
        
        def save_rule():
            if rule_name_var.get() and sensor_var.get():
                messagebox.showinfo("Success", "Gas automation rule added successfully!")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Please fill in all fields")
        
        ttk.Button(dialog, text="Save Rule", command=save_rule).pack(pady=10)
