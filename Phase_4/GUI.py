# Written by: Turner Miles Peeples

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from log import TransactionManager
from stats import StatsManager
from account import AccountManager
from cal_manager import CalendarManager
from wallet import WalletManager

logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TransactionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Transaction Manager")
        self.root.geometry("800x600")

        self.transaction_manager = TransactionManager()
        self.account_manager = AccountManager()
        self.stats_manager = StatsManager(self.transaction_manager)
        self.calendar_manager = CalendarManager()
        self.wallet_manager = WalletManager()

        self.themes = {
            "Light": {"bg": "#f0f0f0", "fg": "#000000", "content_bg": "#ffffff", "button_bg": "#4CAF50", "button_fg": "#ffffff"},
            "Dark": {"bg": "#333333", "fg": "#ffffff", "content_bg": "#444444", "button_bg": "#2196F3", "button_fg": "#ffffff"}
        }
        self.current_theme = "Light"

        self.tab_frames = {}
        self.sidebar_buttons = {}
        self.setup_gui()

    def setup_gui(self):
        self.root.configure(bg=self.themes[self.current_theme]["bg"])

        if not hasattr(self, 'sidebar'):
            self.sidebar = tk.Frame(self.root, bg=self.themes[self.current_theme]["bg"], width=150)
            self.sidebar.pack(side="left", fill="y")
        else:
            self.sidebar.configure(bg=self.themes[self.current_theme]["bg"])

        self.tabs = ["Dashboard", "Transactions", "Account", "Statistics", "Calendar", "Notifications", "Wallet", "Settings", "Payment"]
        for tab in self.tabs:
            if tab not in self.sidebar_buttons:
                btn = tk.Button(self.sidebar, text=tab, command=lambda t=tab: self.switch_tab(t),
                                font=("Arial", 12), relief="flat", pady=10)
                btn.pack(fill="x", pady=2)
                self.sidebar_buttons[tab] = btn

        for btn in self.sidebar_buttons.values():
            btn.configure(bg=self.themes[self.current_theme]["button_bg"],
                         fg=self.themes[self.current_theme]["button_fg"])

        if not hasattr(self, 'content'):
            self.content = tk.Frame(self.root, bg=self.themes[self.current_theme]["content_bg"])
            self.content.pack(side="right", expand=True, fill="both")
        else:
            self.content.configure(bg=self.themes[self.current_theme]["content_bg"])

        for tab in self.tabs:
            if tab not in self.tab_frames:
                self.tab_frames[tab] = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        
        self.switch_tab("Dashboard")

    def update_theme(self):
        self.root.configure(bg=self.themes[self.current_theme]["bg"])
        self.sidebar.configure(bg=self.themes[self.current_theme]["bg"])
        self.content.configure(bg=self.themes[self.current_theme]["content_bg"])

        for btn in self.sidebar_buttons.values():
            btn.configure(bg=self.themes[self.current_theme]["button_bg"],
                         fg=self.themes[self.current_theme]["button_fg"])

        for tab, frame in self.tab_frames.items():
            frame.configure(bg=self.themes[self.current_theme]["content_bg"])
            for widget in frame.winfo_children():
                self._update_widget_theme(widget)

        logger.debug(f"Theme updated to {self.current_theme}")

    def _update_widget_theme(self, widget, depth=0, max_depth=10):
        if depth > max_depth:
            logger.warning(f"Maximum recursion depth ({max_depth}) reached in _update_widget_theme")
            return

        try:
            if isinstance(widget, (tk.Label, tk.Text)):
                widget.configure(bg=self.themes[self.current_theme]["content_bg"],
                               fg=self.themes[self.current_theme]["fg"])
            elif isinstance(widget, (tk.Button, ttk.Button)):
                widget.configure(bg=self.themes[self.current_theme]["button_bg"],
                               fg=self.themes[self.current_theme]["button_fg"])
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=self.themes[self.current_theme]["content_bg"])
            elif isinstance(widget, (tk.Entry, ttk.Combobox)):
                widget.configure(bg=self.themes[self.current_theme]["content_bg"],
                               fg=self.themes[self.current_theme]["fg"])
        except tk.TclError:
            pass

        for child in widget.winfo_children():
            self._update_widget_theme(child, depth + 1, max_depth)

    def switch_tab(self, tab_name):
        for tab in self.tab_frames.values():
            tab.pack_forget()
        
        self.current_tab = tab_name
        self.tab_frames[tab_name].pack(expand=True, fill="both")
        
        setup_method = getattr(self, f"setup_{tab_name.lower()}", None)
        if setup_method:
            setup_method()

    def setup_dashboard(self):
        frame = self.tab_frames["Dashboard"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Current Balance", font=("Arial", 16, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=(10, 0), padx=20)

        self.balance_value = tk.Label(frame, text="$0.00", font=("Arial", 30),
                                     bg=self.themes[self.current_theme]["content_bg"],
                                     fg=self.themes[self.current_theme]["fg"])
        self.balance_value.pack(anchor="w", padx=20)

        self.summary_label = tk.Label(frame, text="Income: $0.00 | Expenses: $0.00 | Net: $0.00", font=("Arial", 12),
                                     bg=self.themes[self.current_theme]["content_bg"],
                                     fg=self.themes[self.current_theme]["fg"])
        self.summary_label.pack(anchor="w", padx=20, pady=5)

        tk.Label(frame, text="Recent Payments", font=("Arial", 14, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", padx=20, pady=10)
        self.recent_payments = ttk.Treeview(frame, columns=("Amount", "Recipient", "Date"), show="headings", height=3)
        self.recent_payments.heading("Amount", text="Amount")
        self.recent_payments.heading("Recipient", text="Recipient")
        self.recent_payments.heading("Date", text="Date")
        self.recent_payments.pack(fill="x", padx=20)

        tk.Label(frame, text="Wallet Preview", font=("Arial", 14, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", padx=20, pady=10)
        self.wallet_preview = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        self.wallet_preview.pack(fill="x", padx=20)

        self.update_dashboard()

    def update_dashboard(self):
        try:
            transactions = self.transaction_manager.get_transactions()
            income = sum(t["Amount"] for t in transactions if t["Category"] == "Deposit")
            expenses = sum(t["Amount"] for t in transactions if t["Category"] in ["Expense", "Invoice"])
            net = income - expenses

            self.balance_value.config(text=f"${net:.2f}")
            self.summary_label.config(text=f"Income: ${income:.2f} | Expenses: ${expenses:.2f} | Net: ${net:.2f}")

            for row in self.recent_payments.get_children():
                self.recent_payments.delete(row)
            for t in transactions[-3:]:
                self.recent_payments.insert("", "end", values=(f"${t['Amount']:.2f}", t["Recipient"], t["Date"]))

            for widget in self.wallet_preview.winfo_children():
                widget.destroy()
            cards = self.wallet_manager.get_cards()
            for card in cards[:2]:
                tk.Label(self.wallet_preview, text=f"{card['Type']}: {card['Number'][-4:]}", font=("Arial", 12),
                         bg=self.themes[self.current_theme]["content_bg"],
                         fg=self.themes[self.current_theme]["fg"]).pack(anchor="w")

            logger.debug("Updated dashboard")
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            messagebox.showerror("Error", f"Failed to update dashboard: {e}")

    def setup_transactions(self):
        frame = self.tab_frames["Transactions"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Transactions", font=("Arial", 16, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=20)

        columns = ("Amount", "Category", "Recipient", "Date")
        self.transaction_list = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.transaction_list.heading(col, text=col, command=lambda c=col: self.sort_transactions(c))
        self.transaction_list.pack(expand=True, fill="both", padx=20, pady=5)

        form = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        form.pack(fill="x", padx=20, pady=5)

        tk.Label(form, text="Amount:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=0, padx=5, pady=5)
        self.entry_amount = tk.Entry(form)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Category:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(form, textvariable=self.category_var, values=["Expense", "Deposit", "Invoice"], state="readonly")
        self.category_dropdown.grid(row=0, column=3, padx=5, pady=5)
        self.category_dropdown.set("Expense")

        tk.Label(form, text="Recipient:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=1, column=0, padx=5, pady=5)
        self.entry_recipient = tk.Entry(form)
        self.entry_recipient.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Payment Method:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=1, column=2, padx=5, pady=5)
        self.payment_var = tk.StringVar()
        self.payment_dropdown = ttk.Combobox(form, textvariable=self.payment_var, values=self.transaction_manager.get_payment_methods(), state="readonly")
        self.payment_dropdown.grid(row=1, column=3, padx=5, pady=5)
        self.payment_dropdown.set(self.transaction_manager.get_payment_methods()[0] if self.transaction_manager.get_payment_methods() else "")

        tk.Button(form, text="Add Transaction", command=self.add_transaction,
                  bg=self.themes[self.current_theme]["button_bg"],
                  fg=self.themes[self.current_theme]["button_fg"]).grid(row=2, column=0, columnspan=2, pady=5)

        tk.Button(form, text="Edit Selected Transaction", command=self.edit_transaction,
                  bg=self.themes[self.current_theme]["button_bg"],
                  fg=self.themes[self.current_theme]["button_fg"]).grid(row=2, column=2, columnspan=2, pady=5)

        self.update_transaction_list()

    def sort_transactions(self, column):
        transactions = self.transaction_manager.get_transactions()
        reverse = getattr(self, f"sort_reverse_{column}", False)
        if column == "Amount":
            transactions.sort(key=lambda t: t[column], reverse=reverse)
        elif column == "Date":
            transactions.sort(key=lambda t: datetime.strptime(t[column], "%Y-%m-%d %H:%M:%S"), reverse=reverse)
        else:
            transactions.sort(key=lambda t: t[column], reverse=reverse)

        setattr(self, f"sort_reverse_{column}", not reverse)
        self.transaction_manager.transactions = transactions
        self.update_transaction_list()

    def add_transaction(self):
        try:
            amount = float(self.entry_amount.get())
            category = self.category_var.get()
            recipient = self.entry_recipient.get()
            payment_method = self.payment_var.get()

            if not payment_method:
                messagebox.showerror("Error", "Please select a payment method")
                return

            transaction = {
                "Description": f"{category} to {recipient}",
                "Amount": amount,
                "Category": category,
                "Recipient": recipient,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "PaymentMethod": payment_method,
                "Status": "Completed"
            }
            self.transaction_manager.add_transaction(**transaction)
            self.update_transaction_list()
            self.update_dashboard()
            messagebox.showinfo("Success", "Transaction added successfully")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            messagebox.showerror("Error", f"Failed to add transaction: {e}")

    def edit_transaction(self):
        selected = self.transaction_list.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a transaction to edit")
            return

        item = self.transaction_list.item(selected[0])
        values = item['values']
        amount, category, recipient, date = values

        transactions = self.transaction_manager.get_transactions()
        transaction = None
        for t in transactions:
            if (f"${t['Amount']:.2f}" == amount and t['Category'] == category and
                t['Recipient'] == recipient and t['Date'] == date):
                transaction = t
                break

        if not transaction:
            messagebox.showerror("Error", "Transaction not found")
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Transaction")
        edit_window.geometry("400x300")

        tk.Label(edit_window, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        entry_amount = tk.Entry(edit_window)
        entry_amount.grid(row=0, column=1, padx=5, pady=5)
        entry_amount.insert(0, transaction["Amount"])

        tk.Label(edit_window, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        category_var = tk.StringVar(value=transaction["Category"])
        category_dropdown = ttk.Combobox(edit_window, textvariable=category_var, values=["Expense", "Deposit", "Invoice"], state="readonly")
        category_dropdown.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(edit_window, text="Recipient:").grid(row=2, column=0, padx=5, pady=5)
        entry_recipient = tk.Entry(edit_window)
        entry_recipient.grid(row=2, column=1, padx=5, pady=5)
        entry_recipient.insert(0, transaction["Recipient"])

        tk.Label(edit_window, text="Payment Method:").grid(row=3, column=0, padx=5, pady=5)
        payment_var = tk.StringVar(value=transaction["PaymentMethod"])
        payment_dropdown = ttk.Combobox(edit_window, textvariable=payment_var, values=self.transaction_manager.get_payment_methods(), state="readonly")
        payment_dropdown.grid(row=3, column=1, padx=5, pady=5)

        def save_changes():
            try:
                new_amount = float(entry_amount.get())
                new_category = category_var.get()
                new_recipient = entry_recipient.get()
                new_payment_method = payment_var.get()

                transaction["Amount"] = new_amount
                transaction["Category"] = new_category
                transaction["Recipient"] = new_recipient
                transaction["PaymentMethod"] = new_payment_method
                transaction["Description"] = f"{new_category} to {new_recipient}"

                self.transaction_manager.save_data()
                self.update_transaction_list()
                self.update_dashboard()
                edit_window.destroy()
                messagebox.showinfo("Success", "Transaction updated successfully")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
            except Exception as e:
                logger.error(f"Error updating transaction: {e}")
                messagebox.showerror("Error", f"Failed to update transaction: {e}")

        tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=4, column=0, columnspan=2, pady=10)

    def update_transaction_list(self):
        try:
            for row in self.transaction_list.get_children():
                self.transaction_list.delete(row)
            transactions = self.transaction_manager.get_transactions()
            for t in transactions:
                self.transaction_list.insert("", "end", values=(f"${t['Amount']:.2f}", t["Category"], t["Recipient"], t["Date"]))
            logger.debug("Updated transaction list")
        except Exception as e:
            logger.error(f"Error updating transaction list: {e}")
            messagebox.showerror("Error", f"Failed to update transaction list: {e}")

    def setup_account(self):
        frame = self.tab_frames["Account"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Account Information", font=("Arial", 16, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=20)

        details = self.account_manager.get_account_details()
        self.account_holder_label = tk.Label(frame, text=f"Account Holder: {details['holder']}", font=("Arial", 12),
                                            bg=self.themes[self.current_theme]["content_bg"],
                                            fg=self.themes[self.current_theme]["fg"])
        self.account_holder_label.pack(anchor="w", padx=20)
        self.account_number_label = tk.Label(frame, text=f"Account Number: {details['number']}", font=("Arial", 12),
                                            bg=self.themes[self.current_theme]["content_bg"],
                                            fg=self.themes[self.current_theme]["fg"])
        self.account_number_label.pack(anchor="w", padx=20)
        self.account_email_label = tk.Label(frame, text=f"Email: {details.get('email', 'Not set')}", font=("Arial", 12),
                                            bg=self.themes[self.current_theme]["content_bg"],
                                            fg=self.themes[self.current_theme]["fg"])
        self.account_email_label.pack(anchor="w", padx=20)

        tk.Label(frame, text="Edit Account Details", font=("Arial", 14, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", padx=20, pady=10)
        edit_form = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        edit_form.pack(fill="x", padx=20)

        tk.Label(edit_form, text="Account Holder:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=0, padx=5, pady=5)
        self.entry_account_holder = tk.Entry(edit_form)
        self.entry_account_holder.grid(row=0, column=1, padx=5, pady=5)
        self.entry_account_holder.insert(0, details["holder"])

        tk.Label(edit_form, text="Account Number:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=1, column=0, padx=5, pady=5)
        self.entry_account_number = tk.Entry(edit_form)
        self.entry_account_number.grid(row=1, column=1, padx=5, pady=5)
        self.entry_account_number.insert(0, details["number"])

        tk.Label(edit_form, text="Email:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=2, column=0, padx=5, pady=5)
        self.entry_account_email = tk.Entry(edit_form)
        self.entry_account_email.grid(row=2, column=1, padx=5, pady=5)
        self.entry_account_email.insert(0, details.get("email", ""))

        tk.Button(edit_form, text="Save Changes", command=self.save_account_details,
                  bg=self.themes[self.current_theme]["button_bg"],
                  fg=self.themes[self.current_theme]["button_fg"]).grid(row=3, column=0, columnspan=2, pady=5)

    def save_account_details(self):
        try:
            new_holder = self.entry_account_holder.get()
            new_number = self.entry_account_number.get()
            new_email = self.entry_account_email.get()
            self.account_manager.account_details["holder"] = new_holder
            self.account_manager.account_details["number"] = new_number
            self.account_manager.account_details["email"] = new_email
            self.account_holder_label.config(text=f"Account Holder: {new_holder}")
            self.account_number_label.config(text=f"Account Number: {new_number}")
            self.account_email_label.config(text=f"Email: {new_email if new_email else 'Not set'}")
            self.account_manager.save_account_details()
            messagebox.showinfo("Success", "Account details updated successfully")
        except Exception as e:
            logger.error(f"Error updating account details: {e}")
            messagebox.showerror("Error", f"Failed to update account details: {e}")

    def setup_statistics(self):
        frame = self.tab_frames["Statistics"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Statistics", font=("Arial", 16, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=20)

        self.stats_notebook = ttk.Notebook(frame)
        self.stats_notebook.pack(expand=True, fill="both", padx=20, pady=5)

        pie_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(pie_frame, text="Pie Chart")
        pie_label = tk.Label(pie_frame, text="", font=("Arial", 12))
        pie_label.pack(expand=True, fill="both")
        try:
            pie_result = self.stats_manager.get_pie_chart(pie_frame)
            if pie_result:
                pie_canvas, pie_fig = pie_result
                pie_canvas.get_tk_widget().pack(expand=True, fill="both")
            else:
                pie_label.configure(text="No transaction data available")
        except Exception as e:
            logger.error(f"Failed to generate pie chart: {e}")
            pie_label.configure(text="Error generating pie chart")

        bar_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(bar_frame, text="Bar Chart")
        bar_label = tk.Label(bar_frame, text="", font=("Arial", 12))
        bar_label.pack(expand=True, fill="both")
        try:
            bar_result = self.stats_manager.get_bar_chart(bar_frame)
            if bar_result:
                bar_canvas, bar_fig = bar_result
                bar_canvas.get_tk_widget().pack(expand=True, fill="both")
            else:
                bar_label.configure(text="No spending data available")
        except Exception as e:
            logger.error(f"Failed to generate bar chart: {e}")
            bar_label.configure(text="Error generating bar chart")

        scatter_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(scatter_frame, text="Scatter Plot")
        scatter_label = tk.Label(scatter_frame, text="", font=("Arial", 12))
        scatter_label.pack(expand=True, fill="both")
        try:
            scatter_result = self.stats_manager.get_scatter_plot(scatter_frame)
            if scatter_result:
                scatter_canvas, scatter_fig = scatter_result
                scatter_canvas.get_tk_widget().pack(expand=True, fill="both")
            else:
                scatter_label.configure(text="No spending data available")
        except Exception as e:
            logger.error(f"Failed to generate scatter plot: {e}")
            scatter_label.configure(text="Error generating scatter plot")

        line_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(line_frame, text="Line Graph")
        line_label = tk.Label(line_frame, text="", font=("Arial", 12))
        line_label.pack(expand=True, fill="both")
        try:
            line_result = self.stats_manager.get_line_graph(line_frame)
            if line_result:
                line_canvas, line_fig = line_result
                line_canvas.get_tk_widget().pack(expand=True, fill="both")
            else:
                line_label.configure(text="No spending data available")
        except Exception as e:
            logger.error(f"Failed to generate line graph: {e}")
            line_label.configure(text="Error generating line graph")

        self.update_stats()

    def update_stats(self):
        try:
            transactions = self.transaction_manager.get_transactions()
            total_income = sum(t["Amount"] for t in transactions if t["Category"] == "Deposit")
            total_expenses = sum(t["Amount"] for t in transactions if t["Category"] in ["Expense", "Invoice"])
            logger.debug("Updated stats")
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            messagebox.showerror("Error", f"Failed to update stats: {e}")

    def setup_calendar(self):
        frame = self.tab_frames["Calendar"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Payment Information", font=("Arial", 16, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=20)

        self.cal_notebook = ttk.Notebook(frame)
        self.cal_notebook.pack(expand=True, fill="both", padx=20)

        self.payments_frame = ttk.Frame(self.cal_notebook)
        self.planned_frame = ttk.Frame(self.cal_notebook)
        self.appointments_frame = ttk.Frame(self.cal_notebook)

        self.cal_notebook.add(self.payments_frame, text="Payments")
        self.cal_notebook.add(self.planned_frame, text="Planned Payments")
        self.cal_notebook.add(self.appointments_frame, text="Appointments")

        tk.Label(self.payments_frame, text="Calendar Overview", font=("Arial", 14, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=10)
        self.calendar = tk.Text(self.payments_frame, height=10, wrap=tk.WORD,
                               bg=self.themes[self.current_theme]["content_bg"],
                               fg=self.themes[self.current_theme]["fg"])
        self.calendar.pack(expand=True, fill="both", padx=10, pady=5)

        tk.Label(self.planned_frame, text="Add Planned Payment", font=("Arial", 14, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=10)
        self.planned_form = tk.Frame(self.planned_frame, bg=self.themes[self.current_theme]["content_bg"])
        self.planned_form.pack(fill="x", padx=10)

        tk.Label(self.planned_form, text="Amount:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=0, padx=5, pady=5)
        self.entry_plan_amount = tk.Entry(self.planned_form)
        self.entry_plan_amount.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.planned_form, text="Date (YYYY-MM-DD):", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=1, column=0, padx=5, pady=5)
        self.entry_plan_date = tk.Entry(self.planned_form)
        self.entry_plan_date.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.planned_form, text="Recipient:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=2, column=0, padx=5, pady=5)
        self.entry_plan_recipient = tk.Entry(self.planned_form)
        self.entry_plan_recipient.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.planned_form, text="Payment Method:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=3, column=0, padx=5, pady=5)
        self.plan_payment_var = tk.StringVar()
        self.plan_payment_dropdown = ttk.Combobox(
            self.planned_form, textvariable=self.plan_payment_var,
            values=self.transaction_manager.get_payment_methods(), state="readonly"
        )
        self.plan_payment_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.plan_payment_dropdown.set(self.transaction_manager.get_payment_methods()[0] if self.transaction_manager.get_payment_methods() else "")

        tk.Button(self.planned_form, text="Add Planned Payment", command=self.add_planned_payment,
                  bg=self.themes[self.current_theme]["button_bg"],
                  fg=self.themes[self.current_theme]["button_fg"]).grid(row=4, column=0, columnspan=2, pady=5)

        tk.Label(self.appointments_frame, text="Add Appointment", font=("Arial", 14, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=10)
        self.appointment_form = tk.Frame(self.appointments_frame, bg=self.themes[self.current_theme]["content_bg"])
        self.appointment_form.pack(fill="x", padx=10)

        tk.Label(self.appointment_form, text="Title:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=0, padx=5, pady=5)
        self.entry_appointment_title = tk.Entry(self.appointment_form)
        self.entry_appointment_title.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.appointment_form, text="Date (YYYY-MM-DD):", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=1, column=0, padx=5, pady=5)
        self.entry_appointment_date = tk.Entry(self.appointment_form)
        self.entry_appointment_date.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.appointment_form, text="Time (HH:MM):", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=2, column=0, padx=5, pady=5)
        self.entry_appointment_time = tk.Entry(self.appointment_form)
        self.entry_appointment_time.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(self.appointment_form, text="Add Appointment", command=self.add_appointment,
                  bg=self.themes[self.current_theme]["button_bg"],
                  fg=self.themes[self.current_theme]["button_fg"]).grid(row=3, column=0, columnspan=2, pady=5)

        self.update_calendar()

    def add_planned_payment(self):
        try:
            amount = float(self.entry_plan_amount.get())
            transaction_date = self.entry_plan_date.get()
            recipient = self.entry_plan_recipient.get()
            payment_method = self.plan_payment_var.get()

            if not payment_method:
                messagebox.showerror("Error", "Please select a payment method")
                return

            transaction = {
                "Description": f"Planned payment to {recipient}",
                "Amount": amount,
                "Category": "Expense",
                "Recipient": recipient,
                "Date": transaction_date,
                "PaymentMethod": payment_method,
                "Status": "Planned"
            }
            self.transaction_manager.add_transaction(**transaction)
            self.update_calendar()
            messagebox.showinfo("Success", "Planned payment added successfully")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount or date format")
        except Exception as e:
            logger.error(f"Error adding planned payment: {e}")
            messagebox.showerror("Error", f"Failed to change plan: {e}")

    def add_appointment(self):
        try:
            title = self.entry_appointment_title.get()
            date = self.entry_appointment_date.get()
            time = self.entry_appointment_time.get()
            self.calendar_manager.add_appointment(title, date, time)
            self.update_calendar()
            messagebox.showinfo("Success", "Appointment added successfully")
        except Exception as e:
            logger.error(f"Error adding appointment: {e}")
            messagebox.showerror("Error", f"Failed to add appointment: {e}")

    def update_calendar(self):
        try:
            self.calendar.delete(1.0, tk.END)
            transactions = self.transaction_manager.get_transactions()
            appointments = self.calendar_manager.get_appointments()

            self.calendar.insert(tk.END, "Payments:\n")
            for t in transactions:
                if t["Status"] == "Planned":
                    self.calendar.insert(tk.END, f"{t['Date']}: {t['Description']} - ${t['Amount']:.2f}\n")

            self.calendar.insert(tk.END, "\nAppointments:\n")
            for a in appointments:
                self.calendar.insert(tk.END, f"{a['Date']} {a['Time']}: {a['Title']}\n")

            logger.debug("Updated calendar")
        except Exception as e:
            logger.error(f"Error updating calendar: {e}")
            messagebox.showerror("Error", f"Failed to update calendar: {e}")

    def setup_notifications(self):
        frame = self.tab_frames["Notifications"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Notifications", font=("Arial", 16, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=20)
        tk.Label(frame, text="No new notifications", font=("Arial", 12),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", padx=20)

    def setup_wallet(self):
        frame = self.tab_frames["Wallet"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Wallet", font=("Arial", 16, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=20)

        self.card_frames = []
        cards = self.wallet_manager.get_cards()
        for i, card in enumerate(cards):
            card_frame = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
            card_frame.pack(fill="x", padx=20, pady=2)
            label = tk.Label(card_frame, text=f"{card['Type']}: {card['Number'][-4:]}", font=("Arial", 12),
                            bg=self.themes[self.current_theme]["content_bg"],
                            fg=self.themes[self.current_theme]["fg"])
            label.pack(side="left")
            remove_btn = tk.Button(card_frame, text="Remove", command=lambda idx=i: self.remove_card(idx),
                                  bg=self.themes[self.current_theme]["button_bg"],
                                  fg=self.themes[self.current_theme]["button_fg"])
            remove_btn.pack(side="right")
            self.card_frames.append(card_frame)

        tk.Label(frame, text="Add Card", font=("Arial", 14, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", padx=20, pady=10)
        card_form = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        card_form.pack(fill="x", padx=20)

        tk.Label(card_form, text="Card Type:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=0, padx=5, pady=5)
        self.card_type_var = tk.StringVar()
        self.card_type_dropdown = ttk.Combobox(card_form, textvariable=self.card_type_var, values=["Credit Card", "Debit Card"], state="readonly")
        self.card_type_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.card_type_dropdown.set("Credit Card")

        tk.Label(card_form, text="Card Number:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=1, column=0, padx=5, pady=5)
        self.entry_card_number = tk.Entry(card_form)
        self.entry_card_number.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(card_form, text="Add Card", command=self.add_card,
                  bg=self.themes[self.current_theme]["button_bg"],
                  fg=self.themes[self.current_theme]["button_fg"]).grid(row=2, column=0, columnspan=2, pady=5)

    def add_card(self):
        try:
            card_type = self.card_type_var.get()
            card_number = self.entry_card_number.get()
            if not card_number:
                messagebox.showerror("Error", "Card number cannot be empty")
                return

            self.wallet_manager.cards.append({"Type": card_type, "Number": card_number})
            self.wallet_manager.save_cards()
            self.setup_wallet()
            self.update_dashboard()
            messagebox.showinfo("Success", "Card added successfully")
        except Exception as e:
            logger.error(f"Error adding card: {e}")
            messagebox.showerror("Error", f"Failed to add card: {e}")

    def remove_card(self, index):
        try:
            self.wallet_manager.cards.pop(index)
            self.wallet_manager.save_cards()
            self.setup_wallet()
            self.update_dashboard()
            messagebox.showinfo("Success", "Card removed successfully")
        except Exception as e:
            logger.error(f"Error removing card: {e}")
            messagebox.showerror("Error", f"Failed to remove card: {e}")

    def setup_settings(self):
        frame = self.tab_frames["Settings"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Settings", font=("Arial", 16, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=20)

        tk.Label(frame, text="Select Theme:", font=("Arial", 12),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", padx=20)
        theme_var = tk.StringVar(value=self.current_theme)
        theme_dropdown = ttk.Combobox(frame, textvariable=theme_var, values=["Light", "Dark"], state="readonly")
        theme_dropdown.pack(anchor="w", padx=20, pady=5)

        def apply_theme():
            self.current_theme = theme_var.get()
            self.update_theme()

        tk.Button(frame, text="Apply Theme", command=apply_theme,
                  bg=self.themes[self.current_theme]["button_bg"],
                  fg=self.themes[self.current_theme]["button_fg"]).pack(anchor="w", padx=20, pady=5)

    def setup_payment(self):
        logger.debug("Starting setup_payment")
        frame = self.tab_frames["Payment"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Payment Methods", font=("Arial", 16, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", pady=10, padx=20)

        self.method_frames = []
        methods = self.transaction_manager.get_payment_methods()
        logger.debug(f"Loaded payment methods: {methods}")
        for i, method in enumerate(methods):
            method_frame = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
            method_frame.pack(fill="x", padx=20, pady=2)
            label = tk.Label(method_frame, text=method, font=("Arial", 12),
                            bg=self.themes[self.current_theme]["content_bg"],
                            fg=self.themes[self.current_theme]["fg"])
            label.pack(side="left")
            remove_btn = tk.Button(method_frame, text="Remove", command=lambda m=method: self.remove_payment_method(m),
                                  bg=self.themes[self.current_theme]["button_bg"],
                                  fg=self.themes[self.current_theme]["button_fg"])
            remove_btn.pack(side="right")
            self.method_frames.append(method_frame)

        tk.Label(frame, text="Add Payment Method", font=("Arial", 14, "bold"),
                 bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).pack(anchor="w", padx=20, pady=10)
        add_form = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        add_form.pack(fill="x", padx=20)

        tk.Label(add_form, text="Method Name:", bg=self.themes[self.current_theme]["content_bg"],
                 fg=self.themes[self.current_theme]["fg"]).grid(row=0, column=0, padx=5, pady=5)
        self.entry_payment_method = tk.Entry(add_form)
        self.entry_payment_method.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(add_form, text="Add Method", command=self.add_payment_method,
                  bg=self.themes[self.current_theme]["button_bg"],
                  fg=self.themes[self.current_theme]["button_fg"]).grid(row=1, column=0, columnspan=2, pady=5)
        logger.debug("Completed setup_payment")

    def add_payment_method(self):
        try:
            method_name = self.entry_payment_method.get().strip()
            if not method_name:
                messagebox.showerror("Error", "Payment method name cannot be empty")
                return

            if self.transaction_manager.add_payment_method(method_name):
                self.setup_payment()
                self.setup_transactions()
                self.setup_calendar()
                messagebox.showinfo("Success", "Payment method added successfully")
            else:
                messagebox.showerror("Error", "Payment method already exists or is invalid")
        except Exception as e:
            logger.error(f"Error adding payment method: {e}")
            messagebox.showerror("Error", f"Failed to add payment method: {e}")

    def remove_payment_method(self, method):
        try:
            transactions = self.transaction_manager.get_transactions()
            used_in_transactions = any(t["PaymentMethod"] == method for t in transactions)

            if used_in_transactions:
                available_methods = [m for m in self.transaction_manager.get_payment_methods() if m != method]
                if not available_methods:
                    messagebox.showerror("Error", "Cannot remove this payment method: no other payment methods available to reassign transactions to")
                    return

                reassign_window = tk.Toplevel(self.root)
                reassign_window.title("Reassign Payment Method")
                reassign_window.geometry("400x200")

                tk.Label(reassign_window, text=f"The payment method '{method}' is used in transactions.", wraplength=350).pack(pady=10)
                tk.Label(reassign_window, text="Please select a new payment method to reassign these transactions to:").pack(pady=5)

                new_method_var = tk.StringVar(value=available_methods[0])
                method_dropdown = ttk.Combobox(reassign_window, textvariable=new_method_var, values=available_methods, state="readonly")
                method_dropdown.pack(pady=5)

                def confirm_reassignment():
                    new_method = new_method_var.get()
                    if self.transaction_manager.reassign_payment_method(method, new_method):
                        if self.transaction_manager.remove_payment_method(method):
                            self.setup_payment()
                            self.setup_transactions()
                            self.setup_calendar()
                            reassign_window.destroy()
                            messagebox.showinfo("Success", f"Transactions reassigned to '{new_method}' and payment method '{method}' removed successfully")
                        else:
                            reassign_window.destroy()
                            messagebox.showerror("Error", "Failed to remove payment method after reassignment")
                    else:
                        reassign_window.destroy()
                        messagebox.showerror("Error", "Failed to reassign transactions")

                tk.Button(reassign_window, text="Confirm", command=confirm_reassignment,
                          bg=self.themes[self.current_theme]["button_bg"],
                          fg=self.themes[self.current_theme]["button_fg"]).pack(pady=10)

                tk.Button(reassign_window, text="Cancel", command=reassign_window.destroy,
                          bg=self.themes[self.current_theme]["button_bg"],
                          fg=self.themes[self.current_theme]["button_fg"]).pack(pady=5)
            else:
                if self.transaction_manager.remove_payment_method(method):
                    self.setup_payment()
                    self.setup_transactions()
                    self.setup_calendar()
                    messagebox.showinfo("Success", "Payment method removed successfully")
                else:
                    messagebox.showerror("Error", "Failed to remove payment method")
        except Exception as e:
            logger.error(f"Error removing payment method: {e}")
            messagebox.showerror("Error", f"Failed to remove payment method: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TransactionGUI(root)
    root.mainloop()