import os
from monitor.db.database import MonitorDatabase


def test_database():
    """Test MonitorDatabase functionality without affecting real data."""
    test_db_path = os.path.join("monitor", "db", "smart_home_monitor_test.db")
    db = MonitorDatabase(db_path=test_db_path)

    # Clear previous test events
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM events")
    db.conn.commit()

    # Log some test data
    db.log_event("light_sensor", 1, "test/topic", {"sensor": "light", "value": 22.5})
    db.log_event("water_valve", 2, "test/topic", {"sensor": "water", "value": 20})

    # Fetch and print events
    print("Recent test events:")
    for event in db.get_recent_events():
        print(event)


def main():
    print("Main execution started.")
    test_database()


if __name__ == "__main__":
    main()
