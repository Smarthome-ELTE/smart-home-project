import json
from tkinter import ttk
from db.database import Database


class MonitorGUI(ttk.Frame):
    # Monitor component for displaying smart home events
    
    def __init__(self, parent, db_path=None):
        super().__init__(parent)
        self.db = Database(db_path=db_path)
        self.setup_ui()
        self.load_events()
    
    def setup_ui(self):
        """Setup the monitor interface"""
        # Header
        header = ttk.Label(self, text="📊 Recent Events", font=("Segoe UI", 14, "bold"))
        header.pack(pady=(0, 10))
        
        # Frame for treeview and scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, pady=5)
        
        # Treeview
        columns = ("Type", "Topic", "Payload", "Time")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.tree.heading("Type", text="Type")
        self.tree.heading("Topic", text="Topic")
        self.tree.heading("Payload", text="Payload")
        self.tree.heading("Time", text="Time")
        
        self.tree.column("Type", width=80)
        self.tree.column("Topic", width=200)
        self.tree.column("Payload", width=180)
        self.tree.column("Time", width=140)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Refresh button
        refresh_btn = ttk.Button(self, text="🔄 Refresh", command=self.load_events)
        refresh_btn.pack(pady=5)
    
    def load_events(self):
        """Load recent events from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Fetch events
        events = self.db.get_recent_events(limit=50)
        
        # Populate treeview
        for event in events:
            event_id, source_type, source_id, payload, timestamp = event

            if isinstance(payload, str):
                payload = json.loads(payload)
                if not isinstance(payload, dict):
                    print(f"⚠️ Skipping event {event_id}: payload is not JSON.")
                    continue

            if source_type == 'sensor':
                category = self.db.get_sensor_category(source_id)
            elif source_type == 'device':
                category = self.db.get_device_category(source_id)
            else:
                category = "unknown"

            topic = f"{category}/{payload.get('action', 'none')}"

            # Truncate payload if too long
            payload_short = payload[:40] + "..." if len(payload) > 40 else payload
            # Truncate timestamp to just date and time
            time_short = timestamp.split('.')[0] if timestamp else ""
            
            self.tree.insert("", "end", values=(source_type, topic, payload_short, time_short))