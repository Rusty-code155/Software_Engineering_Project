# Code Written By: Turner Miles Peeples

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
        self.categories = ["Expense", "Invoice", "Deposit", "Transfer"]
        self.payment_methods = ["Credit Card", "Debit Card", "Cash", "Bank Transfer"]
        self.transaction_types = ["All Transactions", "Income", "Expense"]
        logger.debug("TransactionManager initialized")

    def add_transaction(self, description, amount, category, recipient, payment_method, status):
        try:
            transaction = {
                "Description": description,
                "Amount": float(amount),
                "Category": category,
                "Recipient": recipient,
                "PaymentMethod": payment_method,
                "Status": status,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.transactions.append(transaction)
            logger.info(f"Added transaction: {transaction}")
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            raise

    def edit_transaction(self, index, description, amount, category, recipient, payment_method, status):
        try:
            self.transactions[index].update({
                "Description": description,
                "Amount": float(amount),
                "Category": category,
                "Recipient": recipient,
                "PaymentMethod": payment_method,
                "Status": status
            })
            logger.info(f"Edited transaction at index {index}")
        except Exception as e:
            logger.error(f"Error editing transaction: {e}")
            raise

    def delete_transaction(self, index):
        try:
            self.transactions.pop(index)
            logger.info(f"Deleted transaction at index {index}")
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            raise

    def get_transactions(self, category=None, transaction_type=None, start_date=None, end_date=None, recipient=None):
        try:
            filtered = self.transactions
            if category and category != "All":
                filtered = [t for t in filtered if t["Category"] == category]
            if transaction_type and transaction_type != "All Transactions":
                if transaction_type == "Income":
                    filtered = [t for t in filtered if t["Category"] == "Deposit"]
                elif transaction_type == "Expense":
                    filtered = [t for t in filtered if t["Category"] in ["Expense", "Invoice"]]
            if start_date and end_date:
                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    filtered = [
                        t for t in filtered
                        if start <= datetime.strptime(t["Date"], "%Y-%m-%d %H:%M:%S") <= end
                    ]
                except ValueError as e:
                    logger.warning(f"Invalid date format: {e}")
                    raise ValueError("Dates must be in YYYY-MM-DD format")
            if recipient:
                filtered = [t for t in filtered if recipient.lower() in t["Recipient"].lower()]
            logger.debug(f"Retrieved transactions with filters - category: {category}, type: {transaction_type}")
            return filtered
        except Exception as e:
            logger.error(f"Error retrieving transactions: {e}")
            raise

    def get_categories(self):
        return self.categories

    def get_payment_methods(self):
        return self.payment_methods

    def get_transaction_types(self):
        return self.transaction_types

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