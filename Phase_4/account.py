# Code by Turner Miles Peeples

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('debug.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class AccountManager:
    def __init__(self):
        self.account = {
            "Name": "John Doe",
            "Emails": ["john.doe@example.com"],
            "PhoneNumbers": ["123-456-7890"],
            "SSN": "123-45-6789",
            "ImagePath": ""
        }
        logger.debug("AccountManager initialized")

    def update_account(self, name, emails, phone_numbers, ssn, image_path):
        try:
            self.account.update({
                "Name": name,
                "Emails": emails,
                "PhoneNumbers": phone_numbers,
                "SSN": ssn,
                "ImagePath": image_path
            })
            logger.info("Account updated")
        except Exception as e:
            logger.error(f"Error updating account: {e}")
            raise

    def get_account(self):
        logger.debug("Retrieved account details")
        return self.account