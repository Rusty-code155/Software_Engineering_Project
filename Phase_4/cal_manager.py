# Written by: Turner Miles Peeples

import json
import os
import logging

# Setup logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CalendarManager:
    def __init__(self):
        self.appointments_file = "appointments.json"
        self.appointments = self.load_appointments()

    def load_appointments(self):
        """Load appointments from a JSON file."""
        try:
            if os.path.exists(self.appointments_file):
                with open(self.appointments_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading appointments: {e}")
            return []

    def save_appointments(self):
        """Save appointments to a JSON file."""
        try:
            with open(self.appointments_file, 'w') as f:
                json.dump(self.appointments, f, indent=4)
            logger.debug("Saved appointments")
        except Exception as e:
            logger.error(f"Error saving appointments: {e}")

    def add_appointment(self, title, date, time):
        """Add a new appointment."""
        appointment = {
            "Title": title,
            "Date": date,
            "Time": time
        }
        self.appointments.append(appointment)
        self.save_appointments()
        logger.debug(f"Added appointment: {title} on {date} at {time}")

    def get_appointments(self):
        """Return the list of appointments."""
        return self.appointments