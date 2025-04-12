#Code by Turner Miles Peeples

# log.py
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TransactionManager:
    def __init__(self):
        self.transactions = []
        self.categories = ["Invoice", "Deposit", "Expense", "Income"]  # Placeholder categories from PDF
        self.file_path = "transactions.txt"
        logger.debug("TransactionManager initialized")

    def validate_transaction(self, description, amount, category):
        """Validate transaction data before adding or editing."""
        if not description:
            raise ValueError("Description cannot be empty")
        if not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("Amount must be a non-negative number")
        if category not in self.categories:
            raise ValueError(f"Category must be one of {self.categories}")
        logger.debug(f"Validated transaction: description={description}, amount={amount}, category={category}")
        return True

    def add_transaction(self, description, amount, category):
        """Add a new transaction."""
        try:
            self.validate_transaction(description, amount, category)
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            transaction = {
                "Description": description,
                "Amount": float(amount),
                "Category": category,
                "Date": date
            }
            self.transactions.append(transaction)
            self.save_to_file()
            logger.info(f"Added transaction: {transaction}")
            return True
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            raise

    def edit_transaction(self, index, description, amount, category):
        """Edit an existing transaction."""
        try:
            if index < 0 or index >= len(self.transactions):
                raise IndexError("Invalid transaction index")
            self.validate_transaction(description, amount, category)
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.transactions[index] = {
                "Description": description,
                "Amount": float(amount),
                "Category": category,
                "Date": date
            }
            self.save_to_file()
            logger.info(f"Edited transaction at index {index}: {self.transactions[index]}")
            return True
        except Exception as e:
            logger.error(f"Error editing transaction: {e}")
            raise

    def delete_transaction(self, index):
        """Delete a transaction by index."""
        try:
            if index < 0 or index >= len(self.transactions):
                raise IndexError("Invalid transaction index")
            deleted = self.transactions.pop(index)
            self.save_to_file()
            logger.info(f"Deleted transaction: {deleted}")
            return True
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            raise

    def load_from_file(self):
        """Load transactions from file."""
        self.transactions.clear()
        try:
            with open(self.file_path, "r") as file:
                for line in file:
                    try:
                        parts = line.strip().split(", ")
                        if len(parts) != 4:
                            logger.warning(f"Skipping malformed line: {line.strip()}")
                            continue
                        description = parts[0].split(": ")[1]
                        amount = float(parts[1].split(": ")[1])
                        category = parts[2].split(": ")[1]
                        date = parts[3].split(": ")[1]
                        if category not in self.categories:
                            logger.warning(f"Invalid category '{category}' in file, setting to 'Expense'")
                            category = "Expense"
                        self.transactions.append({
                            "Description": description,
                            "Amount": amount,
                            "Category": category,
                            "Date": date
                        })
                    except (IndexError, ValueError) as e:
                        logger.warning(f"Error parsing line '{line.strip()}': {e}")
                        continue
            logger.debug(f"Loaded {len(self.transactions)} transactions from file")
        except FileNotFoundError:
            logger.info("No transaction file found, starting with empty list")
        except PermissionError as e:
            logger.error(f"Permission error accessing file: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading file: {e}")
            raise

    def save_to_file(self):
        """Save transactions to file."""
        try:
            assert self.transactions is not None, "Transaction list is None"
            with open(self.file_path, "w") as file:
                for transaction in self.transactions:
                    file.write(
                        f"Description: {transaction['Description']}, "
                        f"Amount: {transaction['Amount']}, "
                        f"Category: {transaction['Category']}, "
                        f"Date: {transaction['Date']}\n"
                    )
            logger.debug(f"Saved {len(self.transactions)} transactions to file")
        except PermissionError as e:
            logger.error(f"Permission error saving file: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving file: {e}")
            raise

    def get_transactions(self):
        """Return the list of transactions."""
        return self.transactions

    def get_categories(self):
        """Return the list of categories."""
        return self.categories