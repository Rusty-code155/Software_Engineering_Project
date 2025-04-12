#Code by Turner Miles Peeples
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import tkinter.ttk as ttk

transactions = []

def load_from_file():
    try:
        with open("transactions.txt", "r") as file:
            for line in file:
                parts = line.strip().split(", ")
                description = parts[0].split(": ")[1]
                amount = float(parts[1].split(": ")[1])
                date = parts[2].split(": ")[1]
                transaction = {"Description": description, "Amount": amount, "Date": date}
                transactions.append(transaction)
    except FileNotFoundError:
        # If the file doesn't exist, just pass
        pass

def save_to_file():
    with open("transactions.txt", "a") as file:
        for transaction in transactions:
            file.write(f"Description: {transaction['Description']}, Amount: {transaction['Amount']}, Date: {transaction['Date']}\n")

def add_transaction():
    try:
        description = entry_description.get()
        amount = entry_amount.get()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not amount.replace(".", "", 1).isdigit():
            raise ValueError("Amount must be a valid number.")
        amount = float(amount)
        transaction = {"Description": description, "Amount": amount, "Date": date}
        transactions.append(transaction)
        update_transaction_display()
        save_to_file()
        entry_description.delete(0, tk.END)
        entry_amount.delete(0, tk.END)
        messagebox.showinfo("Success", "Transaction added successfully!")
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid input: {e}")
        
def update_transaction_display():
    for row in transaction_display.get_children():
        transaction_display.delete(row)
    for transaction in transactions:
        transaction_display.insert("", "end", values=(transaction["Description"], transaction["Amount"], transaction["Date"]))

root = tk.Tk()
root.title("Transaction Tracker")
label_description = tk.Label(root, text="Description:")
label_description.grid(row=0, column=0, padx=10, pady=5)
entry_description = tk.Entry(root, width=30)
entry_description.grid(row=0, column=1, padx=10, pady=5)
label_amount = tk.Label(root, text="Amount:")
label_amount.grid(row=1, column=0, padx=10, pady=5)
entry_amount = tk.Entry(root, width=30)
entry_amount.grid(row=1, column=1, padx=10, pady=5)
button_add = tk.Button(root, text="Add Transaction", command=add_transaction)
button_add.grid(row=2, columnspan=2, pady=10)
transaction_display = ttk.Treeview(root, columns=("Description", "Amount", "Date"), show="headings")
transaction_display.grid(row=3, columnspan=2, padx=10, pady=10)
transaction_display.heading("Description", text="Description")
transaction_display.heading("Amount", text="Amount")
transaction_display.heading("Date", text="Date")
load_from_file()
update_transaction_display()
root.mainloop()
# Code by Turner Miles Peeples