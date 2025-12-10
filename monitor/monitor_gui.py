"""
Monitor GUI Component - Displays recent MQTT events
Shows sensor readings and device status updates
"""

import json
from tkinter import ttk
from db.database import Database


class MonitorGUI(ttk.Frame):
    """Monitor component for displaying smart home events"""
    
    def __init__(self, parent, db_path=None):
        super().__init__(parent)
        self.db = Database(db_path=db_path)
        self.auto_refresh_job = None
        self.setup_ui()
        self.load_events()
        self.start_auto_refresh()
    
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
            event_id, source_type, source_id, payload_str, timestamp = event

            try:
                # Parse payload
                if isinstance(payload_str, str):
                    payload = json.loads(payload_str)
                else:
                    payload = payload_str
                    
                if not isinstance(payload, dict):
                    print(f"⚠️ Skipping event {event_id}: payload is not a dict.")
                    continue
                
                # Determine topic based on source type and category
                if source_type == 'sensor':
                    category = self.db.get_sensor_category(source_id)
                    # Sensors publish to /get
                    topic = f"{category}/get"
                elif source_type == 'device':
                    category = self.db.get_device_category(source_id)
                    # Devices receive on /send and respond with /status
                    action = payload.get('action', 'status')
                    topic = f"{category}/{action}"
                else:
                    # Unknown source
                    topic = "unknown/unknown"
                
                # Format payload for display
                payload_display = str(payload)
                if len(payload_display) > 60:
                    payload_display = payload_display[:60] + "..."
                
                # Format timestamp
                time_short = timestamp.split('.')[0] if timestamp else ""
                
                # Insert into tree
                self.tree.insert("", "end", values=(
                    source_type, 
                    topic, 
                    payload_display, 
                    time_short
                ))
                
            except json.JSONDecodeError:
                print(f"⚠️ Event {event_id}: Invalid JSON payload")
                continue
            except Exception as e:
                print(f"⚠️ Event {event_id}: Error processing - {e}")
                continue
    
    def start_auto_refresh(self):
        """Start automatic refresh every 2 seconds"""
        self.load_events()
        # Schedule next refresh
        self.auto_refresh_job = self.after(2000, self.start_auto_refresh)
    
    def stop_auto_refresh(self):
        """Stop automatic refresh"""
        if self.auto_refresh_job:
            self.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None