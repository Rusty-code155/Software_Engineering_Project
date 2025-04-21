import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('debug.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class CalendarManager:
    def __init__(self):
        self.planned_payments = []
        self.appointments = []
        logger.debug("CalendarManager initialized")

    def add_planned_payment(self, amount, date, recipient, payment_method):
        try:
            datetime.strptime(date, "%Y-%m-%d")  # Validate date format
            payment = {
                "Amount": float(amount),
                "Date": date,
                "Recipient": recipient,
                "PaymentMethod": payment_method
            }
            self.planned_payments.append(payment)
            logger.info(f"Added planned payment: {payment}")
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            raise ValueError("Date must be in YYYY-MM-DD format")
        except Exception as e:
            logger.error(f"Error adding planned payment: {e}")
            raise

    def add_appointment(self, title, date, time):
        try:
            datetime.strptime(date, "%Y-%m-%d")  # Validate date
            datetime.strptime(time, "%H:%M")  # Validate time
            appointment = {
                "Title": title,
                "Date": date,
                "Time": time
            }
            self.appointments.append(appointment)
            logger.info(f"Added appointment: {appointment}")
        except ValueError as e:
            logger.error(f"Invalid date or time format: {e}")
            raise ValueError("Date must be in YYYY-MM-DD format, Time in HH:MM format")
        except Exception as e:
            logger.error(f"Error adding appointment: {e}")
            raise

    def get_planned_payments(self):
        logger.debug("Retrieved planned payments")
        return self.planned_payments

    def get_appointments(self):
        logger.debug("Retrieved appointments")
        return self.appointments

    def get_upcoming_payments(self):
        try:
            now = datetime.now()
            threshold = now + timedelta(days=7)
            upcoming = [
                p for p in self.planned_payments
                if now <= datetime.strptime(p["Date"], "%Y-%m-%d") <= threshold
            ]
            logger.debug(f"Retrieved upcoming payments: {len(upcoming)}")
            return upcoming
        except Exception as e:
            logger.error(f"Error retrieving upcoming payments: {e}")
            raise

    def get_upcoming_appointments(self):
        try:
            now = datetime.now()
            threshold = now + timedelta(days=7)
            upcoming = [
                a for a in self.appointments
                if now <= datetime.strptime(a["Date"], "%Y-%m-%d") <= threshold
            ]
            logger.debug(f"Retrieved upcoming appointments: {len(upcoming)}")
            return upcoming
        except Exception as e:
            logger.error(f"Error retrieving upcoming appointments: {e}")
            raise