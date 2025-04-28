# Written by: Turner Miles Peeples

import json
import os
import logging

logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CalendarManager:
    def __init__(self):
        self.appointments = []
        self.load_appointments()

    def load_appointments(self):
        try:
            if os.path.exists('appointments.json'):
                with open('appointments.json', 'r') as f:
                    content = f.read().strip()
                    if not content:
                        logger.warning("appointments.json is empty, using default values")
                        self.appointments = []
                    else:
                        self.appointments = json.loads(content)
                    logger.debug("Loaded appointments")
            else:
                logger.debug("No appointments file found, starting with empty list")
                self.appointments = []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing appointments.json: {e}. File content: {content}")
            self.appointments = []
        except Exception as e:
            logger.error(f"Error loading appointments: {e}")
            self.appointments = []

    def save_appointments(self):
        try:
            with open('appointments.json', 'w') as f:
                json.dump(self.appointments, f, indent=4)
            logger.debug("Saved appointments")
        except Exception as e:
            logger.error(f"Error saving appointments: {e}")
            raise

    def add_appointment(self, title, date, time):
        appointment = {"Title": title, "Date": date, "Time": time}
        self.appointments.append(appointment)
        self.save_appointments()
        logger.debug(f"Added appointment: {appointment}")

    def get_appointments(self):
        return self.appointments