# Code by Turner Miles Peeples

import json
import os
import logging

logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AccountManager:
    def __init__(self):
        self.account_details = {
            "holder": "John Doe",
            "number": "1234567890"
        }
        self.load_account_details()

    def load_account_details(self):
        try:
            if os.path.exists('account.json'):
                with open('account.json', 'r') as f:
                    content = f.read().strip()
                    if not content:
                        logger.warning("account.json is empty, using default values")
                        self.account_details = {"holder": "John Doe", "number": "1234567890"}
                    else:
                        self.account_details = json.loads(content)
                    logger.debug("Loaded account details")
            else:
                logger.debug("No account file found, using default values")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing account.json: {e}. File content: {content}")
            self.account_details = {"holder": "John Doe", "number": "1234567890"}
        except Exception as e:
            logger.error(f"Error loading account details: {e}")
            self.account_details = {"holder": "John Doe", "number": "1234567890"}

    def get_account_details(self):
        return self.account_details

    def save_account_details(self):
        try:
            with open('account.json', 'w') as f:
                json.dump(self.account_details, f, indent=4)
            logger.debug("Saved account details")
        except Exception as e:
            logger.error(f"Error saving account details: {e}")
            raise