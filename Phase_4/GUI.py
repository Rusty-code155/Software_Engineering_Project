# Written by: Turner Miles Peeples

import tkinter as tk
from tkinter import messagebox, ttk, filedialog, colorchooser
from PIL import Image, ImageTk
import logging
from log import TransactionManager
from account import AccountManager
from stats import StatsManager
from cal_manager import CalendarManager
from wallet import WalletManager
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('debug.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TransactionGUI:
    def __init__(self, root):
        self.root = root  
        self.root.title("Transaction Manager")
        self.root.geometry("800x600")

        self.transaction_manager = TransactionManager()
        self.account_manager = AccountManager()
        self.stats_manager = StatsManager(self.transaction_manager.get_transactions())
        self.calendar_manager = CalendarManager()
        self.wallet_manager = WalletManager()

        self.themes = {
            "Light": {
                "sidebar_bg": "#f0f0f0",
                "content_bg": "#ffffff",
                "button_bg": "#e0e0e0",
                "button_fg": "#000000",
                "text_fg": "#000000",
                "active_tab": "#d0d0d0"
            },
            "Dark": {
                "sidebar_bg": "#333333",
                "content_bg": "#444444",
                "button_bg": "#555555",
                "button_fg": "#ffffff",
                "text_fg": "#ffffff",
                "active_tab": "#666666"
            }
        }
        self.current_theme = "Light"

        
        self.style = ttk.Style()
        self.tab_frames = {}  
        self.selected_index = None  

        self.setup_gui()
        self.generate_reflection_report()
        logger.debug("TransactionGUI initialized")

    def setup_gui(self):
        self.sidebar = tk.Frame(self.root, bg=self.themes[self.current_theme]["sidebar_bg"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.content = tk.Frame(self.root, bg=self.themes[self.current_theme]["content_bg"])
        self.content.pack(side="left", expand=True, fill="both")

        
        self.nav_buttons = {}
        self.current_tab = "Dashboard"
        tabs = [
            ("Dashboard", self.setup_dashboard),
            ("Transactions", self.setup_transactions),
            ("Account Information", self.setup_account),
            ("Statistics", self.setup_stats),
            ("Calendar", self.setup_calendar),
            ("Notifications", self.setup_notifications),
            ("Wallet", self.setup_wallet),
            ("Settings", self.setup_settings),
            ("Payment", self.setup_payment)
        ]
        for tab_name, setup_func in tabs:
            btn = tk.Button(
                self.sidebar, text=tab_name, font=("Arial", 12),
                bg=self.themes[self.current_theme]["sidebar_bg"],
                fg=self.themes[self.current_theme]["text_fg"], bd=0,
                command=lambda name=tab_name, func=setup_func: self.switch_tab(name, func)
            )
            btn.pack(fill="x", pady=5)
            self.nav_buttons[tab_name] = btn

        
        for tab_name, setup_func in tabs:
            frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
            self.tab_frames[tab_name] = frame
            setup_func()  

     
        self.switch_tab("Dashboard", self.setup_dashboard)
        
    def switch_tab(self, tab_name, setup_func):
        """Switch between tabs by showing/hiding frames."""
        self.current_tab = tab_name
        theme = self.themes[self.current_theme]
        for name, btn in self.nav_buttons.items():
            btn.config(bg=theme["active_tab"] if name == tab_name else theme["sidebar_bg"], fg=theme["text_fg"])

        # Hide all tab frames
        for frame in self.tab_frames.values():
            frame.pack_forget()

        # Show the selected tab frame
        if tab_name not in self.tab_frames:
            self.tab_frames[tab_name] = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
            setup_func()
        self.tab_frames[tab_name].pack(expand=True, fill="both")
        logger.debug(f"Switched to tab: {tab_name}")

    def apply_theme(self):
        """Apply the current theme to all widgets without destroying tabs."""
        theme = self.themes[self.current_theme]
        self.setup_styles()
        self.sidebar.configure(bg=theme["sidebar_bg"])
        self.content.configure(bg=theme["content_bg"])
        for name, btn in self.nav_buttons.items():
            btn.configure(bg=theme["active_tab"] if name == self.current_tab else theme["sidebar_bg"], fg=theme["text_fg"])

        # Update existing tab frames without destroying them
        for tab_name, frame in self.tab_frames.items():
            frame.configure(bg=theme["content_bg"])
            # Update child widgets recursively
            self._update_widget_tree(frame, theme)

        # Restore state by updating tabs
        if self.current_tab == "Dashboard":
            self.update_dashboard()
        elif self.current_tab == "Transactions":
            self.update_transaction_lists()
        elif self.current_tab == "Account Information":
            self.load_account()
        elif self.current_tab == "Statistics":
            self.update_stats()
        elif self.current_tab == "Calendar":
            self.update_calendar()
        elif self.current_tab == "Notifications":
            self.update_notifications()
        elif self.current_tab == "Wallet":
            self.update_wallet()
        elif self.current_tab == "Payment":
            self.update_payment()
        elif self.current_tab == "Settings":
            pass

        logger.debug(f"Applied theme: {self.current_theme}")

    def _update_widget_tree(self, widget, theme):
        """Recursively update the theme of a widget and its children."""
        try:
            # Update background and foreground colors
            if isinstance(widget, (tk.Frame, tk.Label, ttk.Frame, ttk.Label)):
                widget.configure(bg=theme["content_bg"])
                if isinstance(widget, (tk.Label, ttk.Label)):
                    widget.configure(fg=theme["text_fg"])
            elif isinstance(widget, (tk.Button, ttk.Button)):
                widget.configure(bg=theme["button_bg"], fg=theme["button_fg"])
            elif isinstance(widget, (ttk.Treeview, ttk.Combobox)):
                pass  # Styles are handled by setup_styles
            elif isinstance(widget, tk.Text):
                widget.configure(bg=theme["content_bg"], fg=theme["text_fg"])

            # Recursively update children
            for child in widget.winfo_children():
                self._update_widget_tree(child, theme)
        except Exception as e:
            logger.error(f"Error updating widget theme: {e}")

    def setup_styles(self):
        """Apply UI styles based on the current theme."""
        theme = self.themes[self.current_theme]
        self.style.configure("TNotebook", background=theme["content_bg"], tabposition="wn")
        self.style.configure("TNotebook.Tab", background=theme["sidebar_bg"], padding=[10, 5], font=("Arial", 10))
        self.style.map("TNotebook.Tab", background=[("selected", theme["active_tab"])])
        self.style.configure("TFrame", background=theme["content_bg"])
        self.style.configure("TLabel", background=theme["content_bg"], foreground=theme["text_fg"], font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10), background=theme["button_bg"], foreground=theme["button_fg"])
        self.style.configure("TCombobox", font=("Arial", 10))
        self.style.configure("Treeview", font=("Arial", 10), background=theme["content_bg"], foreground=theme["text_fg"])
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        logger.debug(f"Styles configured for theme: {self.current_theme}")

    

    def switch_tab(self, tab_name, setup_func):
        """Switch between tabs and highlight the active one."""
        self.current_tab = tab_name
        theme = self.themes[self.current_theme]
        for name, btn in self.nav_buttons.items():
            btn.config(bg=theme["active_tab"] if name == tab_name else theme["sidebar_bg"], fg=theme["text_fg"])
        for widget in self.content.winfo_children():
            widget.destroy()
        setup_func()
    
    def setup_dashboard(self):
        self.widgets = {}
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Current Balance
        balance_frame = tk.Frame(frame, bg=self.themes[self.current_theme]["button_bg"], relief="raised", bd=2)
        balance_frame.pack(fill="x", pady=10)
        tk.Label(balance_frame, text="Current Balance", font=("Arial", 14, "bold"), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(pady=5)
        self.balance_value = tk.Label(balance_frame, text="$0.00", font=("Arial", 16, "bold"), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"])
        self.balance_value.pack()

        # Recent Payments
        tk.Label(frame, text="Recent Payments", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.recent_payments = ttk.Treeview(
            frame, columns=("Amount", "Recipient", "Date"), show="headings", height=3
        )
        self.recent_payments.heading("Amount", text="Amount")
        self.recent_payments.heading("Recipient", text="Recipient")
        self.recent_payments.heading("Date", text="Date")
        self.recent_payments.pack(fill="x", pady=5)

        # Summary
        tk.Label(frame, text="Monthly Summary", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.summary_label = tk.Label(frame, text="Income: $0 | Expenses: $0 | Net: $0", font=("Arial", 10, "bold"))
        self.summary_label.pack(anchor="w")

        # Wallet Preview
        tk.Label(frame, text="Wallet", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.wallet_preview = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        self.wallet_preview.pack(fill="x")

        self.update_dashboard()

    def setup_transactions(self):
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.trans_notebook = ttk.Notebook(frame)
        self.trans_notebook.pack(expand=True, fill="both")

        self.form_frame = ttk.Frame(self.trans_notebook)
        self.all_frame = ttk.Frame(self.trans_notebook)
        self.invoices_frame = ttk.Frame(self.trans_notebook)
        self.deposits_frame = ttk.Frame(self.trans_notebook)
        self.transfers_frame = ttk.Frame(self.trans_notebook)

        self.trans_notebook.add(self.form_frame, text="New Transaction")
        self.trans_notebook.add(self.all_frame, text="All Transactions")
        self.trans_notebook.add(self.invoices_frame, text="Invoices")
        self.trans_notebook.add(self.deposits_frame, text="Deposits")
        self.trans_notebook.add(self.transfers_frame, text="Transfers")

        # Transaction Form
        tk.Label(self.form_frame, text="New Transaction", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        form = tk.Frame(self.form_frame, bg=self.themes[self.current_theme]["content_bg"])
        form.pack(fill="x", padx=10)
        tk.Label(form, text="Description:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_description = tk.Entry(form)
        self.entry_description.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_amount = tk.Entry(form)
        self.entry_amount.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Category:").grid(row=2, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            form, textvariable=self.category_var, values=self.transaction_manager.get_categories(), state="readonly"
        )
        self.category_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.category_dropdown.set(self.transaction_manager.get_categories()[0])

        tk.Label(form, text="Recipient:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_recipient = tk.Entry(form)
        self.entry_recipient.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Payment Method:").grid(row=4, column=0, padx=5, pady=5)
        self.payment_var = tk.StringVar()
        self.payment_dropdown = ttk.Combobox(
            form, textvariable=self.payment_var, values=self.transaction_manager.get_payment_methods(), state="readonly"
        )
        self.payment_dropdown.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.payment_dropdown.set(self.transaction_manager.get_payment_methods()[0])

        tk.Label(form, text="Status:").grid(row=5, column=0, padx=5, pady=5)
        self.status_var = tk.StringVar()
        self.status_dropdown = ttk.Combobox(
            form, textvariable=self.status_var, values=["Pending", "Completed", "Failed"], state="readonly"
        )
        self.status_dropdown.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.status_dropdown.set("Pending")

        btn_frame = tk.Frame(form, bg=self.themes[self.current_theme]["content_bg"])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Add", command=self.add_transaction, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit", command=self.edit_transaction, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_transaction, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)

        # All Transactions with Advanced Filters
        filter_frame = tk.Frame(self.all_frame, bg=self.themes[self.current_theme]["content_bg"])
        filter_frame.pack(fill="x", pady=5)
        tk.Label(filter_frame, text="Filter by Category:").pack(side="left", padx=5)
        self.filter_category_var = tk.StringVar()
        self.filter_category_dropdown = ttk.Combobox(
            filter_frame, textvariable=self.filter_category_var, values=self.transaction_manager.get_categories(), state="readonly"
        )
        self.filter_category_dropdown.pack(side="left", padx=5)
        self.filter_category_dropdown.set("All")
        self.filter_category_dropdown.bind("<<ComboboxSelected>>", self.update_transaction_lists)

        tk.Label(filter_frame, text="Filter by Type:").pack(side="left", padx=5)
        self.filter_type_var = tk.StringVar()
        self.filter_type_dropdown = ttk.Combobox(
            filter_frame, textvariable=self.filter_type_var, values=self.transaction_manager.get_transaction_types(), state="readonly"
        )
        self.filter_type_dropdown.pack(side="left", padx=5)
        self.filter_type_dropdown.set("All Transactions")
        self.filter_type_dropdown.bind("<<ComboboxSelected>>", self.update_transaction_lists)

        tk.Label(filter_frame, text="Start Date (YYYY-MM-DD):").pack(side="left", padx=5)
        self.start_date_var = tk.Entry(filter_frame, width=12)
        self.start_date_var.pack(side="left", padx=5)

        tk.Label(filter_frame, text="End Date (YYYY-MM-DD):").pack(side="left", padx=5)
        self.end_date_var = tk.Entry(filter_frame, width=12)
        self.end_date_var.pack(side="left", padx=5)

        tk.Label(filter_frame, text="Recipient:").pack(side="left", padx=5)
        self.recipient_var = tk.Entry(filter_frame, width=15)
        self.recipient_var.pack(side="left", padx=5)

        tk.Button(filter_frame, text="Apply Filters", command=self.update_transaction_lists, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)

        # Transaction Lists with explicit attribute names
        self.tree_all = ttk.Treeview(
            self.all_frame, columns=("Amount", "Status", "Recipient", "Date", "PaymentMethod"), show="headings"
        )
        self.tree_all.heading("Amount", text="Amount")
        self.tree_all.heading("Status", text="Status")
        self.tree_all.heading("Recipient", text="Recipient")
        self.tree_all.heading("Date", text="Date")
        self.tree_all.heading("PaymentMethod", text="Payment Method")
        self.tree_all.pack(expand=True, fill="both", padx=10, pady=5)
        self.tree_all.bind("<<TreeviewSelect>>", lambda e: self.select_transaction(e, self.all_frame))

        self.tree_invoices = ttk.Treeview(
            self.invoices_frame, columns=("Amount", "Status", "Recipient", "Date", "PaymentMethod"), show="headings"
        )
        self.tree_invoices.heading("Amount", text="Amount")
        self.tree_invoices.heading("Status", text="Status")
        self.tree_invoices.heading("Recipient", text="Recipient")
        self.tree_invoices.heading("Date", text="Date")
        self.tree_invoices.heading("PaymentMethod", text="Payment Method")
        self.tree_invoices.pack(expand=True, fill="both", padx=10, pady=5)
        self.tree_invoices.bind("<<TreeviewSelect>>", lambda e: self.select_transaction(e, self.invoices_frame))

        self.tree_deposits = ttk.Treeview(
            self.deposits_frame, columns=("Amount", "Status", "Recipient", "Date", "PaymentMethod"), show="headings"
        )
        self.tree_deposits.heading("Amount", text="Amount")
        self.tree_deposits.heading("Status", text="Status")
        self.tree_deposits.heading("Recipient", text="Recipient")
        self.tree_deposits.heading("Date", text="Date")
        self.tree_deposits.heading("PaymentMethod", text="Payment Method")
        self.tree_deposits.pack(expand=True, fill="both", padx=10, pady=5)
        self.tree_deposits.bind("<<TreeviewSelect>>", lambda e: self.select_transaction(e, self.deposits_frame))

        self.tree_transfers = ttk.Treeview(
            self.transfers_frame, columns=("Amount", "Status", "Recipient", "Date", "PaymentMethod"), show="headings"
        )
        self.tree_transfers.heading("Amount", text="Amount")
        self.tree_transfers.heading("Status", text="Status")
        self.tree_transfers.heading("Recipient", text="Recipient")
        self.tree_transfers.heading("Date", text="Date")
        self.tree_transfers.heading("PaymentMethod", text="Payment Method")
        self.tree_transfers.pack(expand=True, fill="both", padx=10, pady=5)
        self.tree_transfers.bind("<<TreeviewSelect>>", lambda e: self.select_transaction(e, self.transfers_frame))

        self.update_transaction_lists()

    def setup_account(self):
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="Account Information", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        form = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        form.pack(fill="x", padx=10)

        tk.Label(form, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_name = tk.Entry(form)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Emails (comma-separated):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_emails = tk.Entry(form)
        self.entry_emails.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Phone Numbers (comma-separated):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_phones = tk.Entry(form)
        self.entry_phones.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="SSN:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_ssn = tk.Entry(form)
        self.entry_ssn.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Image:").grid(row=4, column=0, padx=5, pady=5)
        self.image_label = tk.Label(form)
        self.image_label.grid(row=4, column=1, padx=5, pady=5)
        tk.Button(form, text="Upload Image", command=self.upload_image, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).grid(row=4, column=2, padx=5, pady=5)

        tk.Label(form, text="Cards:").grid(row=5, column=0, padx=5, pady=5)
        self.cards_text = tk.Text(form, height=3, width=30)
        self.cards_text.grid(row=5, column=1, padx=5, pady=5)

        tk.Button(form, text="Save", command=self.save_account, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).grid(row=6, column=0, columnspan=3, pady=10)

        self.load_account()

    def setup_stats(self):
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.stats_notebook = ttk.Notebook(frame)
        self.stats_notebook.pack(expand=True, fill="both")

        self.pie_frame = ttk.Frame(self.stats_notebook)
        self.bar_frame = ttk.Frame(self.stats_notebook)
        self.scatter_frame = ttk.Frame(self.stats_notebook)
        self.line_frame = ttk.Frame(self.stats_notebook)
        self.recipient_frame = ttk.Frame(self.stats_notebook)
        self.yearly_frame = ttk.Frame(self.stats_notebook)

        self.stats_notebook.add(self.pie_frame, text="Pie Chart")
        self.stats_notebook.add(self.bar_frame, text="Bar Graph")
        self.stats_notebook.add(self.scatter_frame, text="Scatter Plot")
        self.stats_notebook.add(self.line_frame, text="Line Graph")
        self.stats_notebook.add(self.recipient_frame, text="Recipient Percentages")
        self.stats_notebook.add(self.yearly_frame, text="Yearly Spending")

        # Graph customization states
        self.pie_colors = self.stats_manager.default_colors['pie']
        self.bar_color = self.stats_manager.default_colors['bar']
        self.scatter_color = self.stats_manager.default_colors['scatter']
        self.scatter_line_color = self.stats_manager.default_colors['scatter_line']
        self.line_color = self.stats_manager.default_colors['line']  # Fixed line
        self.zoom_levels = {
            "pie": 1.0,
            "bar": 1.0,
            "scatter": 1.0,
            "line": 1.0
        }
        # Initialize canvas attributes as None
        self.pie_canvas = None
        self.pie_fig = None
        self.bar_canvas = None
        self.bar_fig = None
        self.scatter_canvas = None
        self.scatter_fig = None
        self.line_canvas = None
        self.line_fig = None

        # Pie Chart
        control_frame = tk.Frame(self.pie_frame, bg=self.themes[self.current_theme]["content_bg"])
        control_frame.pack(fill="x", pady=5)
        tk.Button(control_frame, text="Change Colors", command=self.change_pie_colors, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        try:
            self.pie_canvas, self.pie_fig = self.stats_manager.get_pie_chart(self.pie_frame, colors=self.pie_colors)
            self.pie_canvas.get_tk_widget().pack(expand=True, fill="both")
        except Exception as e:
            logger.error(f"Failed to generate pie chart: {e}")
            tk.Label(self.pie_frame, text="Unable to generate pie chart", font=("Arial", 12)).pack(expand=True, fill="both")

        # Bar Graph
        control_frame = tk.Frame(self.bar_frame, bg=self.themes[self.current_theme]["content_bg"])
        control_frame.pack(fill="x", pady=5)
        tk.Button(control_frame, text="Change Color", command=self.change_bar_color, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom In", command=lambda: self.zoom_graph("bar", 1.2), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom Out", command=lambda: self.zoom_graph("bar", 0.8), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        try:
            self.bar_canvas, self.bar_fig = self.stats_manager.get_bar_chart(self.bar_frame, color=self.bar_color, zoom=self.zoom_levels["bar"])
            self.bar_canvas.get_tk_widget().pack(expand=True, fill="both")
        except Exception as e:
            logger.error(f"Failed to generate bar chart: {e}")
            tk.Label(self.bar_frame, text="Unable to generate bar chart", font=("Arial", 12)).pack(expand=True, fill="both")

        # Scatter Plot
        control_frame = tk.Frame(self.scatter_frame, bg=self.themes[self.current_theme]["content_bg"])
        control_frame.pack(fill="x", pady=5)
        tk.Button(control_frame, text="Change Scatter Color", command=self.change_scatter_color, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Change Line Color", command=self.change_scatter_line_color, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom In", command=lambda: self.zoom_graph("scatter", 1.2), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom Out", command=lambda: self.zoom_graph("scatter", 0.8), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        try:
            self.scatter_canvas, self.scatter_fig = self.stats_manager.get_scatter_plot(self.scatter_frame, scatter_color=self.scatter_color, line_color=self.scatter_line_color, zoom=self.zoom_levels["scatter"])
            self.scatter_canvas.get_tk_widget().pack(expand=True, fill="both")
        except Exception as e:
            logger.error(f"Failed to generate scatter plot: {e}")
            tk.Label(self.scatter_frame, text="Unable to generate scatter plot", font=("Arial", 12)).pack(expand=True, fill="both")

        # Line Graph
        control_frame = tk.Frame(self.line_frame, bg=self.themes[self.current_theme]["content_bg"])
        control_frame.pack(fill="x", pady=5)
        tk.Button(control_frame, text="Change Color", command=self.change_line_color, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom In", command=lambda: self.zoom_graph("line", 1.2), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom Out", command=lambda: self.zoom_graph("line", 0.8), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        try:
            self.line_canvas, self.line_fig = self.stats_manager.get_line_graph(self.line_frame, color=self.line_color, zoom=self.zoom_levels["line"])
            self.line_canvas.get_tk_widget().pack(expand=True, fill="both")
        except Exception as e:
            logger.error(f"Failed to generate line graph: {e}")
            tk.Label(self.line_frame, text="Unable to generate line graph", font=("Arial", 12)).pack(expand=True, fill="both")

        tk.Label(self.recipient_frame, text="Recipient Percentages:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.recipient_text = tk.Text(self.recipient_frame, height=5)
        self.recipient_text.pack(expand=True, fill="both", padx=10)

        tk.Label(self.yearly_frame, text="Year:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        year_frame = tk.Frame(self.yearly_frame, bg=self.themes[self.current_theme]["content_bg"])
        year_frame.pack(fill="x", padx=10)
        self.entry_year = tk.Entry(year_frame, width=10)
        self.entry_year.pack(side="left", padx=5)
        tk.Button(year_frame, text="Calculate", command=self.show_yearly_spending, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        self.yearly_label = tk.Label(self.yearly_frame, text="Yearly Spending: $0")
        self.yearly_label.pack(anchor="w", padx=10, pady=5)

        self.update_stats()
        
    def change_pie_colors(self):
        try:
            colors = []
            for i in range(4):  # Assuming up to 4 categories
                color = colorchooser.askcolor(title=f"Select Color for Category {i+1}")[1]
                if color:
                    colors.append(color)
            if colors:
                self.pie_colors = colors
                if self.pie_canvas is not None:
                    self.pie_canvas.get_tk_widget().destroy()
                if self.pie_fig is not None:
                    plt.close(self.pie_fig)
                self.pie_canvas, self.pie_fig = self.stats_manager.get_pie_chart(self.pie_frame, colors=self.pie_colors)
                self.pie_canvas.get_tk_widget().pack(expand=True, fill="both")
                logger.debug("Updated pie chart colors")
        except Exception as e:
            logger.error(f"Error changing pie chart colors: {e}")
            messagebox.showerror("Error", f"Failed to change pie chart colors: {e}")

    def change_bar_color(self):
        try:
            color = colorchooser.askcolor(title="Select Bar Color")[1]
            if color:
                self.bar_color = color
                if self.bar_canvas is not None:
                    self.bar_canvas.get_tk_widget().destroy()
                if self.bar_fig is not None:
                    plt.close(self.bar_fig)
                self.bar_canvas, self.bar_fig = self.stats_manager.get_bar_chart(self.bar_frame, color=self.bar_color, zoom=self.zoom_levels["bar"])
                self.bar_canvas.get_tk_widget().pack(expand=True, fill="both")
                logger.debug("Updated bar chart color")
        except Exception as e:
            logger.error(f"Error changing bar chart color: {e}")
            messagebox.showerror("Error", f"Failed to change bar chart color: {e}")
        
    def change_scatter_color(self):
        try:
            color = colorchooser.askcolor(title="Select Scatter Color")[1]
            if color:
                self.scatter_color = color
                if self.scatter_canvas is not None:
                    self.scatter_canvas.get_tk_widget().destroy()
                if self.scatter_fig is not None:
                    plt.close(self.scatter_fig)
                self.scatter_canvas, self.scatter_fig = self.stats_manager.get_scatter_plot(self.scatter_frame, scatter_color=self.scatter_color, line_color=self.scatter_line_color, zoom=self.zoom_levels["scatter"])
                self.scatter_canvas.get_tk_widget().pack(expand=True, fill="both")
                logger.debug("Updated scatter plot color")
        except Exception as e:
            logger.error(f"Error changing scatter plot color: {e}")
            messagebox.showerror("Error", f"Failed to change scatter plot color: {e}")

    def change_scatter_line_color(self):
        try:
            color = colorchooser.askcolor(title="Select Line Color")[1]
            if color:
                self.scatter_line_color = color
                if self.scatter_canvas is not None:
                    self.scatter_canvas.get_tk_widget().destroy()
                if self.scatter_fig is not None:
                    plt.close(self.scatter_fig)
                self.scatter_canvas, self.scatter_fig = self.stats_manager.get_scatter_plot(self.scatter_frame, scatter_color=self.scatter_color, line_color=self.scatter_line_color, zoom=self.zoom_levels["scatter"])
                self.scatter_canvas.get_tk_widget().pack(expand=True, fill="both")
                logger.debug("Updated scatter plot line color")
        except Exception as e:
            logger.error(f"Error changing scatter plot line color: {e}")
            messagebox.showerror("Error", f"Failed to change scatter plot line color: {e}")
            
    def change_line_color(self):
        try:
            color = colorchooser.askcolor(title="Select Line Color")[1]
            if color:
                self.line_color = color
                if self.line_canvas is not None:
                    self.line_canvas.get_tk_widget().destroy()
                if self.line_fig is not None:
                    plt.close(self.line_fig)
                self.line_canvas, self.line_fig = self.stats_manager.get_line_graph(self.line_frame, color=self.line_color, zoom=self.zoom_levels["line"])
                self.line_canvas.get_tk_widget().pack(expand=True, fill="both")
                logger.debug("Updated line graph color")
        except Exception as e:
            logger.error(f"Error changing line graph color: {e}")
            messagebox.showerror("Error", f"Failed to change line graph color: {e}")

    def zoom_graph(self, graph_type, factor):
        try:
            self.zoom_levels[graph_type] *= factor
            if self.zoom_levels[graph_type] < 0.5:
                self.zoom_levels[graph_type] = 0.5
            elif self.zoom_levels[graph_type] > 2.0:
                self.zoom_levels[graph_type] = 2.0

            if graph_type == "bar":
                if self.bar_canvas is None:
                    logger.debug("Bar canvas not initialized, skipping zoom")
                    messagebox.showwarning("Warning", "Bar chart not available for zooming")
                    return
                self.bar_canvas.get_tk_widget().destroy()
                plt.close(self.bar_fig)  # Fixed: Use plt.close()
                self.bar_canvas, self.bar_fig = self.stats_manager.get_bar_chart(self.bar_frame, color=self.bar_color, zoom=self.zoom_levels["bar"])
                self.bar_canvas.get_tk_widget().pack(expand=True, fill="both")
            elif graph_type == "scatter":
                if self.scatter_canvas is None:
                    logger.debug("Scatter canvas not initialized, skipping zoom")
                    messagebox.showwarning("Warning", "Scatter plot not available for zooming")
                    return
                self.scatter_canvas.get_tk_widget().destroy()
                plt.close(self.scatter_fig)  # Fixed: Use plt.close()
                self.scatter_canvas, self.scatter_fig = self.stats_manager.get_scatter_plot(self.scatter_frame, scatter_color=self.scatter_color, line_color=self.scatter_line_color, zoom=self.zoom_levels["scatter"])
                self.scatter_canvas.get_tk_widget().pack(expand=True, fill="both")
            elif graph_type == "line":
                if self.line_canvas is None:
                    logger.debug("Line canvas not initialized, skipping zoom")
                    messagebox.showwarning("Warning", "Line graph not available for zooming")
                    return
                self.line_canvas.get_tk_widget().destroy()
                plt.close(self.line_fig)  # Fixed: Use plt.close()
                self.line_canvas, self.line_fig = self.stats_manager.get_line_graph(self.line_frame, color=self.line_color, zoom=self.zoom_levels["line"])
                self.line_canvas.get_tk_widget().pack(expand=True, fill="both")
            logger.debug(f"Zoomed {graph_type} graph: level={self.zoom_levels[graph_type]}")
        except Exception as e:
            logger.error(f"Error zooming {graph_type} graph: {e}")
            messagebox.showerror("Error", f"Failed to zoom {graph_type} graph: {e}")

    def refresh_line_chart(self):
     try:
         if self.line_canvas is not None:
             self.line_canvas.get_tk_widget().destroy()
         if self.line_fig is not None:
             plt.close(self.line_fig)
         self.line_canvas, self.line_fig = self.stats_manager.get_line_graph(self.line_frame, color=self.line_color, zoom=self.zoom_levels["line"])
         self.line_canvas.get_tk_widget().pack(expand=True, fill="both")
         logger.debug("Refreshed line graph")
     except Exception as e:
         logger.error(f"Error refreshing line graph: {e}")
         messagebox.showerror("Error", f"Failed to refresh line graph: {e}")


    def setup_calendar(self):
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.cal_notebook = ttk.Notebook(frame)
        self.cal_notebook.pack(expand=True, fill="both")

        self.payments_frame = ttk.Frame(self.cal_notebook)
        self.planned_frame = ttk.Frame(self.cal_notebook)
        self.appointments_frame = ttk.Frame(self.cal_notebook)

        self.cal_notebook.add(self.payments_frame, text="Payments")
        self.cal_notebook.add(self.planned_frame, text="Planned Payments")
        self.cal_notebook.add(self.appointments_frame, text="Appointments")

        # Planned Payment Form
        tk.Label(self.planned_frame, text="Add Planned Payment", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        self.planned_form = tk.Frame(self.planned_frame, bg=self.themes[self.current_theme]["content_bg"])
        self.planned_form.pack(fill="x", padx=10)
        tk.Label(self.planned_form, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_plan_amount = tk.Entry(self.planned_form)
        self.entry_plan_amount.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.planned_form, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_plan_date = tk.Entry(self.planned_form)
        self.entry_plan_date.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.planned_form, text="Recipient:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_plan_recipient = tk.Entry(self.planned_form)
        self.entry_plan_recipient.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.planned_form, text="Payment Method:").grid(row=3, column=0, padx=5, pady=5)
        self.plan_payment_var = tk.StringVar()
        self.plan_payment_dropdown = ttk.Combobox(
            self.planned_form, textvariable=self.plan_payment_var, values=self.transaction_manager.get_payment_methods(), state="readonly"
        )
        self.plan_payment_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.plan_payment_dropdown.set(self.transaction_manager.get_payment_methods()[0])

        tk.Button(self.planned_form, text="Add Planned Payment", command=self.add_planned_payment, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).grid(row=4, column=0, columnspan=2, pady=5)

        # Appointment Form
        tk.Label(self.appointments_frame, text="Add Appointment", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        self.appointment_form = tk.Frame(self.appointments_frame, bg=self.themes[self.current_theme]["content_bg"])
        self.appointment_form.pack(fill="x", padx=10)
        tk.Label(self.appointment_form, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_appointment_title = tk.Entry(self.appointment_form)
        self.entry_appointment_title.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.appointment_form, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_appointment_date = tk.Entry(self.appointment_form)
        self.entry_appointment_date.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.appointment_form, text="Time (HH:MM):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_appointment_time = tk.Entry(self.appointment_form)
        self.entry_appointment_time.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(self.appointment_form, text="Add Appointment", command=self.add_appointment, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).grid(row=3, column=0, columnspan=2, pady=5)

        self.update_calendar()

    def setup_notifications(self):
        frame = self.tab_frames["Notifications"]
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Notifications", font=("Arial", 16, "bold")).pack(pady=10)

        # Upcoming Payments
        payments_frame = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        payments_frame.pack(expand=True, fill="both", padx=20, pady=5)
        tk.Label(payments_frame, text="Upcoming Payments", font=("Arial", 12, "bold")).pack(anchor="w")
        self.notifications_payments = ttk.Treeview(payments_frame, columns=("Amount", "Recipient", "Date", "Method"), show="headings", height=5)
        self.notifications_payments.heading("Amount", text="Amount")
        self.notifications_payments.heading("Recipient", text="Recipient")
        self.notifications_payments.heading("Date", text="Date")
        self.notifications_payments.heading("Method", text="Method")
        self.notifications_payments.pack(expand=True, fill="both")
        for col in ("Amount", "Recipient", "Date", "Method"):
            self.notifications_payments.column(col, anchor="center", width=100)

        # Upcoming Appointments
        appointments_frame = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        appointments_frame.pack(expand=True, fill="both", padx=20, pady=5)
        tk.Label(appointments_frame, text="Upcoming Appointments", font=("Arial", 12, "bold")).pack(anchor="w")
        self.notifications_appointments = ttk.Treeview(appointments_frame, columns=("Title", "Date", "Time"), show="headings", height=5)
        self.notifications_appointments.heading("Title", text="Title")
        self.notifications_appointments.heading("Date", text="Date")
        self.notifications_appointments.heading("Time", text="Time")
        self.notifications_appointments.pack(expand=True, fill="both")
        for col in ("Title", "Date", "Time"):
            self.notifications_appointments.column(col, anchor="center", width=100)

        self.update_notifications()
        logger.debug("Setup notifications tab")

    def setup_wallet(self):
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="Wallet", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        self.card_frame = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        self.card_frame.pack(fill="x")

        tk.Label(frame, text="Add Card", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        form = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        form.pack(fill="x", padx=10)
        tk.Label(form, text="Number:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_card_number = tk.Entry(form)
        self.entry_card_number.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Type:").grid(row=1, column=0, padx=5, pady=5)
        self.card_type_var = tk.StringVar()
        self.card_type_dropdown = ttk.Combobox(
            form, textvariable=self.card_type_var, values=["Visa", "MasterCard", "Amex"], state="readonly"
        )
        self.card_type_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.card_type_dropdown.set("Visa")

        tk.Button(form, text="Upload Card Image", command=self.upload_card_image, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(form, text="Add Card", command=self.add_card, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).grid(row=2, column=1, padx=5, pady=5)

        self.update_wallet()

    def setup_settings(self):
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="Settings", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)

        # Theme Selection
        tk.Label(frame, text="UI Theme", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        theme_frame = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        theme_frame.pack(fill="x", padx=10)
        tk.Label(theme_frame, text="Select Theme:").pack(side="left", padx=5)
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_dropdown = ttk.Combobox(
            theme_frame, textvariable=self.theme_var, values=list(self.themes.keys()), state="readonly"
        )
        theme_dropdown.pack(side="left", padx=5)
        tk.Button(theme_frame, text="Apply Theme", command=self.change_theme, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)

        tk.Label(frame, text="Profile", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        tk.Label(frame, text="Edit profile settings (Placeholder)", font=("Arial", 10)).pack(anchor="w", padx=10)

    def setup_payment(self):
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="Billing Details", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)

        # Current Subscription
        sub_frame = tk.Frame(frame, bg=self.themes[self.current_theme]["button_bg"], relief="raised", bd=2)
        sub_frame.pack(fill="x", pady=10)
        tk.Label(sub_frame, text="Current Subscription Plan", font=("Arial", 12, "bold"), 
                 bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(pady=5)
        self.plan_label = tk.Label(sub_frame, text="Free Plan", font=("Arial", 10), 
                                   bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"])
        self.plan_label.pack()

        # Billing Information Form
        tk.Label(frame, text="Update Billing Information", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        billing_form = tk.Frame(frame, bg=self.themes[self.current_theme]["content_bg"])
        billing_form.pack(fill="x", padx=10)

        tk.Label(billing_form, text="Card Number:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_billing_card = tk.Entry(billing_form)
        self.entry_billing_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(billing_form, text="Expiration Date (MM/YY):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_billing_expiry = tk.Entry(billing_form)
        self.entry_billing_expiry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(billing_form, text="CVV:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_billing_cvv = tk.Entry(billing_form)
        self.entry_billing_cvv.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(billing_form, text="Billing Address:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_billing_address = tk.Entry(billing_form)
        self.entry_billing_address.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Buttons
        btn_frame = tk.Frame(billing_form, bg=self.themes[self.current_theme]["content_bg"])
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Change Plan", command=self.change_plan, 
                  bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Billing", command=self.update_billing, 
                  bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)

    def change_plan(self):
        messagebox.showinfo("Info", "Change plan functionality not implemented")
        logger.debug("Attempted to change plan (not implemented)")

    def update_billing(self):
        messagebox.showinfo("Info", "Billing information updated (Placeholder)")
        logger.debug("Updated billing information (placeholder)")

    def change_theme(self):
        new_theme = self.theme_var.get()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_theme()
            logger.info(f"Changed theme to {self.current_theme}")

    def update_dashboard(self):
        try:
            # Check if Dashboard widgets exist
            if not all(hasattr(self, attr) and getattr(self, attr).winfo_exists() for attr in ['balance_value', 'summary_label', 'recent_payments', 'wallet_preview']):
                logger.debug("Dashboard widgets missing, recreating tab")
                self.tab_frames["Dashboard"].destroy()
                self.tab_frames["Dashboard"] = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
                self.setup_dashboard()

            transactions = self.transaction_manager.get_transactions()
            income = sum(t["Amount"] for t in transactions if t["Category"] == "Deposit")
            expenses = sum(t["Amount"] for t in transactions if t["Category"] in ["Expense", "Invoice"])
            net = income - expenses

            self.balance_value.config(text=f"${net:.2f}")
            self.summary_label.config(text=f"Income: ${income:.2f} | Expenses: ${expenses:.2f} | Net: ${net:.2f}")

            # Update recent_payments
            for row in self.recent_payments.get_children():
                self.recent_payments.delete(row)
            for t in transactions[-3:]:  # Last 3 transactions
                self.recent_payments.insert("", "end", values=(
                    f"${t['Amount']:.2f}", t["Recipient"], t["Date"]
                ))

            # Update wallet_preview
            for widget in self.wallet_preview.winfo_children():
                widget.destroy()
            cards = self.wallet_manager.get_cards()
            for card in cards[:2]:  # Show up to 2 cards
                tk.Label(self.wallet_preview, text=f"{card['Type']}: {card['Number'][-4:]}", font=("Arial", 10)).pack(anchor="w")

            logger.debug("Updated dashboard")
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            messagebox.showerror("Error", f"Failed to update dashboard: {e}")

    def update_transaction_lists(self):
        try:
            # Check if Transactions widget exists
            if not hasattr(self, 'transactions_list') or not self.transactions_list.winfo_exists():
                logger.debug("Transactions list widget missing, recreating tab")
                self.tab_frames["Transactions"].destroy()
                self.tab_frames["Transactions"] = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
                self.setup_transactions()

            for row in self.transactions_list.get_children():
                self.transactions_list.delete(row)
            transactions = self.transaction_manager.get_transactions()
            for t in transactions:
                self.transactions_list.insert("", "end", values=(
                    f"${t['Amount']:.2f}", t["Category"], t["Recipient"], t["Date"], t["PaymentMethod"]
                ))
            logger.debug("Updated transaction lists")
        except Exception as e:
            logger.error(f"Error updating transaction lists: {e}")
            messagebox.showerror("Error", f"Failed to update transaction lists: {e}")

    def select_transaction(self, event, frame):
        try:
            # Map frames to their corresponding Treeview widgets
            tree_map = {
                self.all_frame: self.tree_all,
                self.invoices_frame: self.tree_invoices,
                self.deposits_frame: self.tree_deposits,
                self.transfers_frame: self.tree_transfers
            }
            tree = tree_map[frame]
            selected = tree.selection()
            if not selected:
                return
            values = tree.item(selected, "values")
            for i, t in enumerate(self.transaction_manager.get_transactions()):
                if (f"${t['Amount']:.2f}" == values[0] and
                    t["Status"] == values[1] and
                    t["Recipient"] == values[2] and
                    t["Date"] == values[3]):
                    self.selected_index = i
                    break
            t = self.transaction_manager.get_transactions()[self.selected_index]
            self.entry_description.delete(0, tk.END)
            self.entry_amount.delete(0, tk.END)
            self.entry_recipient.delete(0, tk.END)
            self.entry_description.insert(0, t["Description"])
            self.entry_amount.insert(0, t["Amount"])
            self.entry_recipient.insert(0, t["Recipient"])
            self.category_var.set(t["Category"])
            self.payment_var.set(t["PaymentMethod"])
            self.status_var.set(t["Status"])
            self.trans_notebook.select(self.form_frame)
            logger.debug(f"Selected transaction: {t}")
        except Exception as e:
            logger.error(f"Error selecting transaction: {e}")

    def add_transaction(self):
        try:
            amount = float(self.entry_amount.get())
            category = self.category_var.get()
            recipient = self.entry_recipient.get()
            date = self.entry_date.get()
            payment_method = self.payment_method_var.get()
            self.transaction_manager.add_transaction(amount, category, recipient, date, payment_method)
            self.update_transaction_lists()
            self.load_account()
            self.update_dashboard()
            # Ensure the Notifications tab is properly set up before updating
            if not hasattr(self, 'notifications_payments') or not self.notifications_payments.winfo_exists():
                self.tab_frames["Notifications"].destroy()
                self.tab_frames["Notifications"] = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
                self.setup_notifications()
            self.update_notifications()
            self.update_stats()
            self.update_calendar()
            self.update_wallet()
            messagebox.showinfo("Success", "Transaction added successfully")
            logger.debug(f"Added transaction: {amount}, {category}, {recipient}, {date}")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid amount format")
            logger.error(f"Error adding transaction: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {e}")
            logger.error(f"Error adding transaction: {e}")
            
    def edit_transaction(self):
        if self.selected_index is None:
            messagebox.showerror("Error", "No transaction selected")
            return
        try:
            amount = float(self.entry_amount.get())
            description = self.entry_description.get()
            category = self.category_var.get()
            recipient = self.entry_recipient.get()
            payment_method = self.payment_var.get()
            status = self.status_var.get()
            self.transaction_manager.edit_transaction(
                self.selected_index, description, amount, category, recipient, payment_method, status
            )
            self.update_transaction_lists()
            self.update_dashboard()
            self.update_notifications()
            self.update_calendar()
            self.update_stats()
            messagebox.showinfo("Success", "Transaction updated successfully")
            logger.debug(f"Edited transaction at index {self.selected_index}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid amount: {e}")
            logger.error(f"Error editing transaction: {e}")

    def delete_transaction(self):
        if self.selected_index is None:
            messagebox.showerror("Error", "No transaction selected")
            return
        self.transaction_manager.delete_transaction(self.selected_index)
        self.selected_index = None
        self.update_transaction_lists()
        self.update_dashboard()
        self.update_notifications()
        self.update_calendar()
        self.update_stats()
        messagebox.showinfo("Success", "Transaction deleted successfully")
        logger.debug("Deleted transaction")

    def update_calendar(self):
        try:
            # Check if Calendar widget exists
            if not hasattr(self, 'calendar') or not self.calendar.winfo_exists():
                logger.debug("Calendar widget missing, recreating tab")
                self.tab_frames["Calendar"].destroy()
                self.tab_frames["Calendar"] = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
                self.setup_calendar()

            self.calendar.delete(1.0, tk.END)
            payments = self.calendar_manager.get_planned_payments()
            appointments = self.calendar_manager.get_appointments()
            self.calendar.insert(tk.END, "Planned Payments:\n")
            for p in payments:
                self.calendar.insert(tk.END, f"{p['Date']}: ${p['Amount']:.2f} to {p['Recipient']} via {p['PaymentMethod']}\n")
            self.calendar.insert(tk.END, "\nAppointments:\n")
            for a in appointments:
                self.calendar.insert(tk.END, f"{a['Date']} at {a['Time']}: {a['Title']}\n")
            logger.debug("Updated calendar")
        except Exception as e:
            logger.error(f"Error updating calendar: {e}")
            messagebox.showerror("Error", f"Failed to update calendar: {e}")

    def add_planned_payment(self):
        try:
            amount = float(self.entry_plan_amount.get())
            date = self.entry_plan_date.get()
            recipient = self.entry_plan_recipient.get()
            payment_method = self.plan_payment_var.get()
            self.calendar_manager.add_planned_payment(amount, date, recipient, payment_method)
            self.update_calendar()
            self.update_notifications()
            messagebox.showinfo("Success", "Planned payment added successfully")
            logger.debug(f"Added planned payment: {amount}, {date}, {recipient}, {payment_method}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid amount or date: {e}")
            logger.error(f"Error adding planned payment: {e}")

    def add_appointment(self):
        try:
            title = self.entry_appointment_title.get()
            date = self.entry_appointment_date.get()
            time = self.entry_appointment_time.get()
            self.calendar_manager.add_appointment(title, date, time)
            self.update_calendar()
            self.update_notifications()
            messagebox.showinfo("Success", "Appointment added successfully")
            logger.debug(f"Added appointment: {title}, {date}, {time}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date or time: {e}")
            logger.error(f"Error adding appointment: {e}")

    def update_notifications(self):
        try:
            # Check if the Treeview widgets exist and are valid
            if not hasattr(self, 'notifications_payments') or not self.notifications_payments.winfo_exists():
                logger.debug("Notifications payments Treeview missing, recreating tab")
                self.tab_frames["Notifications"].destroy()
                self.tab_frames["Notifications"] = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
                self.setup_notifications()

            if not hasattr(self, 'notifications_appointments') or not self.notifications_appointments.winfo_exists():
                logger.debug("Notifications appointments Treeview missing, recreating tab")
                self.tab_frames["Notifications"].destroy()
                self.tab_frames["Notifications"] = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
                self.setup_notifications()

            # Clear and update payments
            for row in self.notifications_payments.get_children():
                self.notifications_payments.delete(row)
            payments = self.calendar_manager.get_upcoming_payments()
            logger.debug(f"Retrieved upcoming payments: {len(payments)}")
            for p in payments:
                self.notifications_payments.insert("", "end", values=(
                    f"${p['Amount']:.2f}", p["Recipient"], p["Date"], p["PaymentMethod"]
                ))

            # Clear and update appointments
            for row in self.notifications_appointments.get_children():
                self.notifications_appointments.delete(row)
            appointments = self.calendar_manager.get_upcoming_appointments()
            logger.debug(f"Retrieved upcoming appointments: {len(appointments)}")
            for a in appointments:
                self.notifications_appointments.insert("", "end", values=(
                    a["Title"], a["Date"], a["Time"]
                ))
            logger.debug("Updated notifications")
        except Exception as e:
            logger.error(f"Error updating notifications: {e}")
            messagebox.showerror("Error", f"Failed to update notifications: {e}")

    def update_wallet(self):
        try:
            # Check if Wallet widget exists
            if not hasattr(self, 'card_frame') or not self.card_frame.winfo_exists():
                logger.debug("Card frame widget missing, recreating tab")
                self.tab_frames["Wallet"].destroy()
                self.tab_frames["Wallet"] = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
                self.setup_wallet()

            for widget in self.card_frame.winfo_children():
                widget.destroy()
            cards = self.wallet_manager.get_cards()
            for card in cards:
                card_frame = tk.Frame(self.card_frame, bg=self.themes[self.current_theme]["content_bg"])
                card_frame.pack(fill="x", pady=2)
                tk.Label(card_frame, text=f"{card['Type']}: {card['Number'][-4:]}", font=("Arial", 10)).pack(side="left")
                if card.get("ImagePath"):
                    try:
                        img = Image.open(card["ImagePath"]).resize((50, 30), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        tk.Label(card_frame, image=photo).pack(side="right")
                        card_frame.image = photo  # Keep reference
                    except Exception as e:
                        logger.error(f"Error loading card image {card['ImagePath']}: {e}")
            logger.debug("Updated wallet display")
        except Exception as e:
            logger.error(f"Error updating wallet: {e}")
            messagebox.showerror("Error", f"Failed to update wallet: {e}")

    def add_card(self):
        try:
            number = self.entry_card_number.get()
            card_type = self.card_type_var.get()
            image_path = getattr(self, "card_image_path", "")
            self.wallet_manager.add_card(number, card_type, image_path)
            self.update_wallet()
            self.load_account()  # Update account tab
            self.update_dashboard()
            messagebox.showinfo("Success", "Card added successfully")
            logger.debug(f"Added card: {card_type}, ending in {number[-4:]}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add card: {e}")
            logger.error(f"Error adding card: {e}")

    def upload_card_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.card_image_path = file_path
            messagebox.showinfo("Success", "Card image uploaded successfully")
            logger.debug(f"Uploaded card image: {file_path}")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            try:
                img = Image.open(file_path).resize((100, 100), Image.Resampling.LANCZOS)
                self.image_ref = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.image_ref)
                # Update account with new image path
                current_account = self.account_manager.get_account()
                self.account_manager.update_account(
                    current_account["Name"],
                    current_account["Emails"],
                    current_account["PhoneNumbers"],
                    current_account["SSN"],
                    file_path
                )
                messagebox.showinfo("Success", "Image uploaded successfully")
                logger.debug(f"Uploaded account image: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload image: {e}")
                logger.error(f"Error uploading image: {e}")
            
    def save_account(self):
        try:
            name = self.entry_name.get()
            emails = [email.strip() for email in self.entry_emails.get().split(",") if email.strip()]
            phones = [phone.strip() for phone in self.entry_phones.get().split(",") if phone.strip()]
            ssn = self.entry_ssn.get()
            image_path = self.account_manager.get_account().get("ImagePath", "")
            self.account_manager.update_account(name, emails, phones, ssn, image_path)
            messagebox.showinfo("Success", "Account details saved successfully")
            logger.debug(f"Saved account details: {name}, {emails}, {phones}, {ssn}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save account details: {e}")
            logger.error(f"Error saving account details: {e}")
        
    def load_account(self):
        details = self.account_manager.get_account()  # Changed from get_details to get_account
        logger.debug("Retrieved account details")
        cards = self.wallet_manager.get_cards()
        logger.debug("Retrieved cards")
        self.entry_name.delete(0, tk.END)
        self.entry_emails.delete(0, tk.END)
        self.entry_phones.delete(0, tk.END)
        self.entry_ssn.delete(0, tk.END)
        self.cards_text.delete(1.0, tk.END)

        self.entry_name.insert(0, details.get("Name", ""))
        self.entry_emails.insert(0, ", ".join(details.get("Emails", [])))
        self.entry_phones.insert(0, ", ".join(details.get("PhoneNumbers", [])))
        self.entry_ssn.insert(0, details.get("SSN", ""))
        for card in cards:
            self.cards_text.insert(tk.END, f"{card['Type']}: {card['Number']}\n")

        if details.get("ImagePath"):  # Changed from Image to ImagePath to match account.py
            img = Image.open(details["ImagePath"]).resize((100, 100), Image.Resampling.LANCZOS)
            self.image_ref = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.image_ref)
        logger.debug("Loaded account details")
    
    def update_stats(self):
        self.stats_manager.transactions = self.transaction_manager.get_transactions()
        try:
            percentages = self.stats_manager.get_recipient_percentages()
            self.recipient_text.delete(1.0, tk.END)
            for recipient, percentage in percentages.items():
                self.recipient_text.insert(tk.END, f"{recipient}: {percentage:.2f}%\n")
        except ValueError as e:
            self.recipient_text.delete(1.0, tk.END)
            self.recipient_text.insert(tk.END, "No transaction data available")

    def show_yearly_spending(self):
        year = self.entry_year.get()
        try:
            spending = self.stats_manager.get_yearly_spending(year)
            self.yearly_label.config(text=f"Yearly Spending: ${spending:.2f}")
        except ValueError as e:
            self.yearly_label.config(text="Yearly Spending: $0")
            messagebox.showerror("Error", str(e))

    def generate_reflection_report(self):
        transactions = self.transaction_manager.get_transactions()
        total_spent = sum(t["Amount"] for t in transactions if t["Category"] in ["Invoice", "Transfer"])
        total_received = sum(t["Amount"] for t in transactions if t["Category"] == "Deposit")
        report = f"Reflection Report\nTotal Spent: ${total_spent:.2f}\nTotal Received: ${total_received:.2f}\n"
        with open("reflection_report.txt", "w") as f:
            f.write(report)
        logger.debug("Generated reflection report")

if __name__ == "__main__":
    root = tk.Tk()
    app = TransactionGUI(root)
    root.mainloop()