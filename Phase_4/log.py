# Code Written By: Turner Miles Peeples

import json
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TransactionManager:
    def __init__(self):
        self.transactions = []
        self.payment_methods = ["Credit Card", "Debit Card", "Bank Transfer"]
        self.load_data()

    def add_transaction(self, Description, Amount, Category, Recipient, Date, PaymentMethod, Status):
        try:
            parsed_date = datetime.strptime(Date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                parsed_date = datetime.strptime(Date, "%Y-%m-%d")
                Date = parsed_date.strftime("%Y-%m-%d 00:00:00")
            except ValueError:
                logger.warning(f"Invalid date format: {Date}. Using current time instead.")
                Date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        transaction = {
            "Description": Description,
            "Amount": Amount,
            "Category": Category,
            "Recipient": Recipient,
            "Date": Date,
            "PaymentMethod": PaymentMethod,
            "Status": Status
        }
        self.transactions.append(transaction)
        self.save_data()
        logger.debug(f"Added transaction: {transaction}")

    def get_transactions(self):
        return self.transactions

    def add_payment_method(self, method):
        if method and method not in self.payment_methods:
            self.payment_methods.append(method)
            self.save_data()
            logger.debug(f"Added payment method: {method}")
            return True
        logger.warning(f"Failed to add payment method: {method} (already exists or invalid)")
        return False

    def remove_payment_method(self, method):
        if method in self.payment_methods:
            self.payment_methods.remove(method)
            self.save_data()
            logger.debug(f"Removed payment method: {method}")
            return True
        logger.warning(f"Failed to remove payment method: {method} (not found)")
        return False

    def reassign_payment_method(self, old_method, new_method):
        if old_method not in self.payment_methods or new_method not in self.payment_methods:
            logger.warning(f"Cannot reassign payment method: {old_method} or {new_method} not found")
            return False

        if old_method == new_method:
            logger.warning("Old and new payment methods are the same; no reassignment needed")
            return True

        updated = False
        for t in self.transactions:
            if t["PaymentMethod"] == old_method:
                t["PaymentMethod"] = new_method
                updated = True
        if updated:
            self.save_data()
            logger.debug(f"Reassigned transactions from {old_method} to {new_method}")
        return True

    def get_payment_methods(self):
        return self.payment_methods

    def save_data(self):
        try:
            data = {
                "transactions": self.transactions,
                "payment_methods": self.payment_methods
            }
            with open('transactions.json', 'w') as f:
                json.dump(data, f, indent=4)
            logger.debug("Saved data to file")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise

    def load_data(self):
        try:
            if os.path.exists('transactions.json'):
                with open('transactions.json', 'r') as f:
                    content = f.read().strip()
                    if not content:
                        logger.warning("transactions.json is empty, using default values")
                        self.transactions = []
                        self.payment_methods = ["Credit Card", "Debit Card", "Bank Transfer"]
                    else:
                        data = json.loads(content)
                        self.transactions = data.get("transactions", [])
                        self.payment_methods = data.get("payment_methods", ["Credit Card", "Debit Card", "Bank Transfer"])
                    logger.debug("Loaded data from file")
            else:
                self.transactions = []
                self.payment_methods = ["Credit Card", "Debit Card", "Bank Transfer"]
                logger.debug("No data file found, starting with default values")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing transactions.json: {e}. File content: {content}")
            self.transactions = []
            self.payment_methods = ["Credit Card", "Debit Card", "Bank Transfer"]
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.transactions = []
            self.payment_methods = ["Credit Card", "Debit Card", "Bank Transfer"]