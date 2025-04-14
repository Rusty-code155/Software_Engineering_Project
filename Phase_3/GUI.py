#Code by Turner Miles Peeples
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from log import TransactionManager

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=
    [
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TransactionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Transaction Tracker")
        self.root.geometry("800x600")
        self.manager = TransactionManager()
        self.selected_index = None
        self.setup_gui()
        self.load_transactions()
        logger.debug("TransactionGUI initialized")

    def setup_gui(self):
        """Set up the GUI layout based on PDF mockup."""
        # Sidebar
        self.sidebar = tk.Frame(self.root, width=200, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y")
        nav_items = [
            "Dashboard", "Transactions", "Account Information", "Statistics",
            "Calendar", "Settings", "Profile", "Interface", "Wallet",
            "Notifications", "Payment settings"
        ]
        for item in nav_items:
            btn = tk.Button(self.sidebar, text=item, bg="#34495e", fg="white", anchor="w", relief="flat")
            btn.pack(fill="x", pady=2)

        # Header
        self.header = tk.Frame(self.root, height=100, bg="#ecf0f1")
        self.header.pack(side="top", fill="x")
        tk.Label(self.header, text="Current Balance", font=("Arial", 14), bg="#ecf0f1").pack(pady=10)
        self.balance_value = tk.Label(self.header, text="$0.00", font=("Arial", 16, "bold"), bg="#ecf0f1")
        self.balance_value.pack()

        # Main content
        self.main_content = tk.Frame(self.root, bg="#ffffff")
        self.main_content.pack(expand=True, fill="both")

        # Transaction form
        self.form_frame = tk.Frame(self.main_content, bg="#ffffff")
        self.form_frame.pack(pady=10)

        tk.Label(self.form_frame, text="Description:", bg="#ffffff").grid(row=0, column=0, padx=10, pady=5)
        self.entry_description = tk.Entry(self.form_frame, width=30)
        self.entry_description.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.form_frame, text="Amount:", bg="#ffffff").grid(row=1, column=0, padx=10, pady=5)
        self.entry_amount = tk.Entry(self.form_frame, width=30)
        self.entry_amount.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.form_frame, text="Category:", bg="#ffffff").grid(row=2, column=0, padx=10, pady=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            self.form_frame, textvariable=self.category_var, values=self.manager.get_categories(), state="readonly"
        )
        self.category_dropdown.grid(row=2, column=1, padx=10, pady=5)
        self.category_dropdown.set(self.manager.get_categories()[0])

        # Buttons
        self.button_frame = tk.Frame(self.main_content, bg="#ffffff")
        self.button_frame.pack(pady=10)
        tk.Button(self.button_frame, text="Add Transaction", command=self.add_transaction).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="Edit Transaction", command=self.edit_transaction).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="Delete Transaction", command=self.delete_transaction).pack(side="left", padx=5)

        # Transaction table
        self.transaction_display = ttk.Treeview(
            self.main_content, columns=("Description", "Amount", "Category", "Date"), show="headings"
        )
        self.transaction_display.pack(pady=10, fill="both", expand=True)
        self.transaction_display.heading("Description", text="Description")
        self.transaction_display.heading("Amount", text="Amount")
        self.transaction_display.heading("Category", text="Category")
        self.transaction_display.heading("Date", text="Date")
        self.transaction_display.bind("<<TreeviewSelect>>", self.select_transaction)
        logger.debug("GUI setup completed")

    def update_balance(self):
        """Update the displayed balance."""
        try:
            balance = sum(t["Amount"] for t in self.manager.get_transactions())
            self.balance_value.config(text=f"${balance:,.2f}")
            logger.debug(f"Updated balance to ${balance:,.2f}")
        except Exception as e:
            logger.error(f"Error updating balance: {e}")
            self.balance_value.config(text="Error")

    def load_transactions(self):
        """Load and display transactions."""
        try:
            self.manager.load_from_file()
            self.update_transaction_display()
            self.update_balance()
            logger.debug("Transactions loaded and displayed")
        except Exception as e:
            logger.error(f"Error loading transactions: {e}")
            messagebox.showerror("Error", f"Failed to load transactions: {e}")

    def update_transaction_display(self):
        """Update the transaction table."""
        try:
            for row in self.transaction_display.get_children():
                self.transaction_display.delete(row)
            for transaction in self.manager.get_transactions():
                self.transaction_display.insert(
                    "", "end",
                    values=(
                        transaction["Description"],
                        transaction["Amount"],
                        transaction["Category"],
                        transaction["Date"]
                    )
                )
            logger.debug("Transaction display updated")
        except Exception as e:
            logger.error(f"Error updating transaction display: {e}")
            messagebox.showerror("Error", "Failed to update transaction display")

    def add_transaction(self):
        """Add a new transaction from user input."""
        try:
            description = self.entry_description.get().strip()
            amount = self.entry_amount.get().strip()
            category = self.category_var.get()
            if not amount.replace(".", "", 1).isdigit():
                raise ValueError("Amount must be a valid number")
            amount = float(amount)
            self.manager.add_transaction(description, amount, category)
            self.update_transaction_display()
            self.update_balance()
            self.clear_entries()
            messagebox.showinfo("Success", "Transaction added successfully!")
            logger.info("Transaction added via GUI")
        except ValueError as e:
            logger.warning(f"Invalid input for add_transaction: {e}")
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            logger.error(f"Error in add_transaction: {e}")
            messagebox.showerror("Error", f"Failed to add transaction: {e}")

    def edit_transaction(self):
        """Edit the selected transaction."""
        try:
            if self.selected_index is None:
                raise ValueError("No transaction selected")
            description = self.entry_description.get().strip()
            amount = self.entry_amount.get().strip()
            category = self.category_var.get()
            if not amount.replace(".", "", 1).isdigit():
                raise ValueError("Amount must be a valid number")
            amount = float(amount)
            self.manager.edit_transaction(self.selected_index, description, amount, category)
            self.update_transaction_display()
            self.update_balance()
            self.clear_entries()
            self.selected_index = None
            messagebox.showinfo("Success", "Transaction updated successfully!")
            logger.info(f"Transaction edited at index {self.selected_index}")
        except ValueError as e:
            logger.warning(f"Invalid input for edit_transaction: {e}")
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            logger.error(f"Error in edit_transaction: {e}")
            messagebox.showerror("Error", f"Failed to edit transaction: {e}")

    def delete_transaction(self):
        """Delete the selected transaction."""
        try:
            if self.selected_index is None:
                raise ValueError("No transaction selected")
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?"):
                self.manager.delete_transaction(self.selected_index)
                self.update_transaction_display()
                self.update_balance()
                self.clear_entries()
                self.selected_index = None
                messagebox.showinfo("Success", "Transaction deleted successfully!")
                logger.info(f"Transaction deleted at index {self.selected_index}")
        except ValueError as e:
            logger.warning(f"Invalid input for delete_transaction: {e}")
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            logger.error(f"Error in delete_transaction: {e}")
            messagebox.showerror("Error", f"Failed to delete transaction: {e}")

    def select_transaction(self, event):
        """Populate form with selected transaction details."""
        try:
            selected_item = self.transaction_display.selection()
            if not selected_item:
                return
            values = self.transaction_display.item(selected_item, "values")
            for i, t in enumerate(self.manager.get_transactions()):
                if (t["Description"] == values[0] and
                    str(t["Amount"]) == values[1] and
                    t["Category"] == values[2] and
                    t["Date"] == values[3]):
                    self.selected_index = i
                    break
            self.entry_description.delete(0, tk.END)
            self.entry_amount.delete(0, tk.END)
            self.entry_description.insert(0, values[0])
            self.entry_amount.insert(0, values[1])
            self.category_var.set(values[2])
            logger.debug(f"Selected transaction at index {self.selected_index}: {values}")
        except Exception as e:
            logger.error(f"Error selecting transaction: {e}")
            messagebox.showerror("Error", "Failed to select transaction")

    def clear_entries(self):
        """Clear the input fields."""
        self.entry_description.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.category_var.set(self.manager.get_categories()[0])
        logger.debug("Cleared input fields")

if __name__ == "__main__":
    root = tk.Tk()
    app = TransactionGUI(root)
    root.mainloop()