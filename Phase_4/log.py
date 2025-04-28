# Code Written By: Turner Miles Peeples

import json
import os
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('debug.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TransactionManager:
    def __init__(self):
        self.transactions = []
        self.transactions_file = "transactions.json"
        self.load_transactions()
        logger.debug("TransactionManager initialized")

    def load_transactions(self):
        if os.path.exists(self.transactions_file):
            try:
                with open(self.transactions_file, 'r') as f:
                    self.transactions = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.transactions = []
        else:
            self.transactions = []

    def save_transactions(self):
        try:
            with open(self.transactions_file, 'w') as f:
                json.dump(self.transactions, f, indent=4)
        except IOError:
            pass

    def add_transaction(self, description, amount, category, recipient, payment_method, status):
        transaction = {
            "Description": description,
            "Amount": float(amount),
            "Category": category,
            "Recipient": recipient,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "PaymentMethod": payment_method,
            "Status": status
        }
        self.transactions.append(transaction)
        self.save_transactions()
        return transaction

    def get_transactions(self, category=None, transaction_type=None, start_date=None, end_date=None, recipient=None):
        """Return a filtered list of transactions."""
        transactions = self.transactions

        # Filter by category
        if category and category != "All":
            transactions = [t for t in transactions if t["Category"] == category]

        # Filter by transaction type (if needed, assuming type is same as category for now)
        if transaction_type and transaction_type != "All Transactions":
            transactions = [t for t in transactions if t["Category"] == transaction_type]

        # Filter by date range
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                transactions = [t for t in transactions if datetime.strptime(t["Date"], "%Y-%m-%d %H:%M:%S") >= start]
            except ValueError:
                logger.error(f"Invalid start_date format: {start_date}")

        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                transactions = [t for t in transactions if datetime.strptime(t["Date"], "%Y-%m-%d %H:%M:%S") <= end]
            except ValueError:
                logger.error(f"Invalid end_date format: {end_date}")

        # Filter by recipient
        if recipient:
            transactions = [t for t in transactions if t["Recipient"].lower().find(recipient.lower()) != -1]

        return transactions

    def edit_transaction(self, index, description=None, amount=None, category=None, recipient=None, date=None, payment_method=None, status=None):
        if 0 <= index < len(self.transactions):
            updates = {}
            if description is not None:
                updates["Description"] = description
            if amount is not None:
                updates["Amount"] = float(amount)
            if category is not None:
                updates["Category"] = category
            if recipient is not None:
                updates["Recipient"] = recipient
            if date is not None:
                updates["Date"] = date
            if payment_method is not None:
                updates["PaymentMethod"] = payment_method
            if status is not None:
                updates["Status"] = status
            self.transactions[index].update(updates)
            self.save_transactions()
            return self.transactions[index]
        return None

    def delete_transaction(self, index):
        if 0 <= index < len(self.transactions):
            deleted = self.transactions.pop(index)
            self.save_transactions()
            return deleted
        return None

    def get_categories(self):
        return ["Invoice", "Deposit", "Transfer", "Expense"]

    def get_payment_methods(self):
        return ["Credit Card", "Bank Transfer", "Cash"]

    def get_transaction_types(self):
        return ["All Transactions", "Invoice", "Deposit", "Transfer", "Expense", "Payment"]

    def get_summary(self):
        try:
            income = sum(t["Amount"] for t in self.transactions if t["Category"] == "Deposit")
            expenses = sum(t["Amount"] for t in self.transactions if t["Category"] in ["Expense", "Invoice"])
            net = income - expenses
            logger.debug(f"Summary - Income: {income}, Expenses: {expenses}, Net: {net}")
            return {"income": income, "expenses": expenses, "net": net}
        except Exception as e:
            logger.error(f"Error calculating summary: {e}")
            raise