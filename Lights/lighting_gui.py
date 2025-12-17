import tkinter as tk
from tkinter import ttk, messagebox
import json
# Assuming MonitorGUI is in monitor_gui.py and Database is in db/database.py
from monitor.monitor_gui import MonitorGUI
from db.database import Database
import datetime


# --- 1. LIGHT CONTROL PANEL CLASS ---

class LightControlPanel(ttk.Frame):
    """Control panel for lighting system management"""

    def __init__(self, parent, controller, db_path=None):
        super().__init__(parent)
        self.controller = controller
        self.db = Database(db_path=db_path)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup the lighting control interface (WITHOUT Status Frame)"""
        # Header
        header = ttk.Label(self, text="💡 Lighting System Control",
                           font=("Segoe UI", 14, "bold"))
        header.pack(pady=(0, 15))

        # --- REMOVED: Current Status Frame and Labels (self.ambient_label, self.bulb_label) ---

        # Automation Rules Frame (Now placed higher up)
        rules_frame = ttk.LabelFrame(self, text="Automation Rules", padding=15)
        rules_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Rules Treeview (Identical structure to Heating GUI)
        columns = ("Name", "Status")
        self.rules_tree = ttk.Treeview(rules_frame, columns=columns,
                                       show="headings", height=6)

        self.rules_tree.heading("Name", text="Rule Name")
        self.rules_tree.heading("Status", text="Status")

        self.rules_tree.column("Name", width=250)
        self.rules_tree.column("Status", width=100)

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
        """Load current sensor data and automation rules (Status update logic removed)"""
        cursor = self.db.conn.cursor()

        # --- START: REMOVED STATUS UPDATE LOGIC ---

        # REMOVED: Get latest light sensor data query and update of self.ambient_label
        cursor.execute("""
            SELECT name, last_payload 
            FROM sensors 
            WHERE category = 'light'
            LIMIT 1
        """)
        # The fetched sensor data is now unused, but the query remains harmless.
        sensor = cursor.fetchone()
        # The original code here used self.ambient_label.config(...) which is now removed.

        # REMOVED: Get light device status query and update of self.bulb_label
        cursor.execute("""
            SELECT name, current_status 
            FROM devices 
            WHERE category = 'light'
            LIMIT 1
        """)
        # The fetched device data is now unused, but the query remains harmless.
        device = cursor.fetchone()
        # The original code here used self.bulb_label.config(...) which is now removed.

        # --- END: REMOVED STATUS UPDATE LOGIC ---

        # Load automation rules (This remains, as it's the main function)
        self.rules_tree.delete(*self.rules_tree.get_children())

        triggers = self.db.get_all_triggers()
        for trigger in triggers:
            trigger_id, name, _, _, _, _, enabled, _ = trigger
            status = "✓ Enabled" if enabled else "✗ Disabled"
            self.rules_tree.insert("", "end", values=(name, status),
                                   tags=(trigger_id,))

    # ... (toggle_rule and show_add_rule_dialog remain unchanged, but now call the simplified load_data) ...

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
            # NOTE: switch_trigger needs to know the current state to flip it
            # The Controller's switch_trigger method is expected to handle the state flip
            self.controller.switch_trigger(trigger_id)
            self.load_data()
            messagebox.showinfo("Success", "Rule status updated!")

    def show_add_rule_dialog(self):
        """Show dialog to add new automation rule (Light specific)"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Light Automation Rule")
        dialog.geometry("500x550")
        dialog.transient(self)
        dialog.grab_set()

        # Rule Name
        ttk.Label(dialog, text="Rule Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        name_entry.insert(0, "My Light Rule (Brightness)")

        # Sensor Selection (Light)
        ttk.Label(dialog, text="Trigger Sensor:").pack(pady=(10, 0))
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id, name FROM sensors WHERE category='light'")
        sensors = cursor.fetchall()

        sensor_var = tk.StringVar()
        sensor_combo = ttk.Combobox(dialog, textvariable=sensor_var,
                                   values=[f"{s[0]}: {s[1]}" for s in sensors],
                                   state="readonly", width=37)
        sensor_combo.pack(pady=5)
        if sensors:
            sensor_combo.current(0)

        # Condition (Brightness specific)
        ttk.Label(dialog, text="Condition (e.g., brightness < 50):").pack(pady=(10, 0))

        ttk.Label(dialog, text="brightness").pack()

        condition_frame = ttk.Frame(dialog)
        condition_frame.pack(pady=5)

        operator_var = tk.StringVar(value="<")
        operator_combo = ttk.Combobox(condition_frame, textvariable=operator_var,
                                     values=["<", ">", "<=", ">=", "=="],
                                     state="readonly", width=5)
        operator_combo.pack(side="left", padx=5)

        value_entry = ttk.Entry(condition_frame, width=10)
        value_entry.pack(side="left")
        value_entry.insert(0, "50")

        ttk.Label(dialog, text="For Range (e.g., & <=80):").pack()
        range_entry = ttk.Entry(dialog, width=20)
        range_entry.pack(pady=5)

        # Device Selection (Light)
        ttk.Label(dialog, text="Control Device:").pack(pady=(10, 0))
        cursor.execute("SELECT id, name FROM devices WHERE category='light'")
        devices = cursor.fetchall()

        device_var = tk.StringVar()
        device_combo = ttk.Combobox(dialog, textvariable=device_var,
                                   values=[f"{d[0]}: {d[1]}" for d in devices],
                                   state="readonly", width=37)
        device_combo.pack(pady=5)
        if devices:
            device_combo.current(0)

        # Action (Light specific)
        ttk.Label(dialog, text="Action Payload:").pack(pady=(10, 0))

        action_frame = ttk.Frame(dialog)
        action_frame.pack(pady=5)

        ttk.Label(action_frame, text="State:").pack(side="left")
        state_var = tk.StringVar(value="on")
        ttk.Radiobutton(action_frame, text="ON",
                       variable=state_var, value="on").pack(side="left", padx=5)
        ttk.Radiobutton(action_frame, text="OFF",
                       variable=state_var, value="off").pack(side="left", padx=5)

        ttk.Label(action_frame, text="B:").pack(side="left", padx=(10, 0))
        brightness_entry = ttk.Entry(action_frame, width=5)
        brightness_entry.pack(side="left", padx=5)
        brightness_entry.insert(0, "100")

        ttk.Label(action_frame, text="H:").pack(side="left", padx=(10, 0))
        hue_entry = ttk.Entry(action_frame, width=5)
        hue_entry.pack(side="left", padx=5)
        hue_entry.insert(0, "0")

        ttk.Label(action_frame, text="S:").pack(side="left", padx=(10, 0))
        sat_entry = ttk.Entry(action_frame, width=5)
        sat_entry.pack(side="left", padx=5)
        sat_entry.insert(0, "0")

        # Save Button
        def save_rule():
            try:
                name = name_entry.get()
                sensor_id = int(sensor_var.get().split(":")[0])

                # Construct the condition string (handling the new range format)
                operator = operator_var.get()
                value = value_entry.get()
                range_str = range_entry.get().strip()

                condition_str = f"{operator}{value}"
                if range_str:
                    condition_str += f" & {range_str}"

                condition = {"brightness": condition_str}

                device_id = int(device_combo.get().split(":")[0])
                state = state_var.get()
                brightness = int(brightness_entry.get())
                hue = int(hue_entry.get())
                saturation = int(sat_entry.get())

                # Construct the action payload
                action_payload = {
                    "state": state,
                    "brightness": brightness,
                    "hue": hue,
                    "saturation": saturation
                }

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