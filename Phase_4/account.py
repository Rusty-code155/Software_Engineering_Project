# Code by Turner Miles Peeples

import json
import os
import logging

# Setup logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AccountManager:
    def __init__(self):
        self.account_details = {
            "holder": "John Doe",
            "number": "1234567890",
            "email": ""
        }
        self.load_account_details()

    def get_account_details(self):
        return self.account_details

    def save_account_details(self):
        try:
            with open('account.json', 'w') as f:
                json.dump(self.account_details, f, indent=4)
            logger.debug("Saved account details to file")
        except Exception as e:
            logger.error(f"Error saving account details: {e}")
            raise

    def load_account_details(self):
        try:
            if os.path.exists('account.json'):
                with open('account.json', 'r') as f:
                    self.account_details = json.load(f)
                logger.debug("Loaded account details from file")
            else:
                self.save_account_details()
                logger.debug("No account file found, created with default values")
        except Exception as e:
            logger.error(f"Error loading account details: {e}")
            self.account_details = {
                "holder": "John Doe",
                "number": "1234567890",
                "email": ""
            }