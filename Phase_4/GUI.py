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

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('debug.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TransactionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Transaction Tracker")
        self.root.geometry("1000x700")
        self.transaction_manager = TransactionManager()
        self.account_manager = AccountManager()
        self.calendar_manager = CalendarManager()
        self.wallet_manager = WalletManager()
        self.stats_manager = StatsManager(self.transaction_manager.get_transactions())
        self.selected_index = None
        self.image_ref = None
        self.style = ttk.Style()
        self.themes = {
            "Default": {
                "sidebar_bg": "#d9e1e8",
                "active_tab": "#3498db",
                "content_bg": "#ffffff",
                "text_fg": "#000000",
                "button_bg": "#3498db",
                "button_fg": "#ffffff"
            },
            "Dark": {
                "sidebar_bg": "#2c3e50",
                "active_tab": "#2980b9",
                "content_bg": "#34495e",
                "text_fg": "#ecf0f1",
                "button_bg": "#2980b9",
                "button_fg": "#ecf0f1"
            },
            "Light": {
                "sidebar_bg": "#f0f4f8",
                "active_tab": "#95a5a6",
                "content_bg": "#ffffff",
                "text_fg": "#2c3e50",
                "button_bg": "#95a5a6",
                "button_fg": "#ffffff"
            }
        }
        self.current_theme = "Default"
        self.setup_styles()
        self.setup_gui()
        self.generate_reflection_report()
        logger.debug("TransactionGUI initialized")

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

    def apply_theme(self):
        """Apply the current theme to all widgets."""
        theme = self.themes[self.current_theme]
        self.setup_styles()
        self.sidebar.configure(bg=theme["sidebar_bg"])
        self.content.configure(bg=theme["content_bg"])
        for name, btn in self.nav_buttons.items():
            btn.configure(bg=theme["active_tab"] if name == self.current_tab else theme["sidebar_bg"], fg=theme["text_fg"])
        # Rebuild the current tab to apply styles
        setup_func = {
            "Dashboard": self.setup_dashboard,
            "Transactions": self.setup_transactions,
            "Account Information": self.setup_account,
            "Statistics": self.setup_stats,
            "Calendar": self.setup_calendar,
            "Notifications": self.setup_notifications,
            "Wallet": self.setup_wallet,
            "Settings": self.setup_settings,
            "Payment": self.setup_payment
        }.get(self.current_tab, self.setup_dashboard)
        self.switch_tab(self.current_tab, setup_func)
        logger.debug(f"Applied theme: {self.current_theme}")

    def setup_gui(self):
        # Main layout: sidebar and content area
        self.sidebar = tk.Frame(self.root, bg=self.themes[self.current_theme]["sidebar_bg"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.content = tk.Frame(self.root, bg=self.themes[self.current_theme]["content_bg"])
        self.content.pack(side="left", expand=True, fill="both")

        # Sidebar navigation
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
                self.sidebar, text=tab_name, font=("Arial", 12), bg=self.themes[self.current_theme]["sidebar_bg"], fg=self.themes[self.current_theme]["text_fg"], bd=0,
                command=lambda name=tab_name, func=setup_func: self.switch_tab(name, func)
            )
            btn.pack(fill="x", pady=5)
            self.nav_buttons[tab_name] = btn

        # Default to Dashboard
        self.switch_tab("Dashboard", self.setup_dashboard)

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

        # Transaction Lists
        for frame, category in [
            (self.all_frame, None),
            (self.invoices_frame, "Invoice"),
            (self.deposits_frame, "Deposit"),
            (self.transfers_frame, "Transfer")
        ]:
            tree = ttk.Treeview(
                frame, columns=("Amount", "Status", "Recipient", "Date", "PaymentMethod"), show="headings"
            )
            tree.heading("Amount", text="Amount")
            tree.heading("Status", text="Status")
            tree.heading("Recipient", text="Recipient")
            tree.heading("Date", text="Date")
            tree.heading("PaymentMethod", text="Payment Method")
            tree.pack(expand=True, fill="both", padx=10, pady=5)
            tree.bind("<<TreeviewSelect>>", lambda e, f=frame: self.select_transaction(e, f))
            setattr(self, f"tree_{frame.winfo_name()}", tree)

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
        self.line_color = self.stats_manager.default_colors['line']
        self.zoom_levels = {
            "pie": 1.0,
            "bar": 1.0,
            "scatter": 1.0,
            "line": 1.0
        }

        # Pie Chart
        control_frame = tk.Frame(self.pie_frame, bg=self.themes[self.current_theme]["content_bg"])
        control_frame.pack(fill="x", pady=5)
        tk.Button(control_frame, text="Change Colors", command=self.change_pie_colors, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        self.pie_canvas, self.pie_fig = self.stats_manager.get_pie_chart(self.pie_frame, colors=self.pie_colors)
        self.pie_canvas.get_tk_widget().pack(expand=True, fill="both")

        # Bar Graph
        control_frame = tk.Frame(self.bar_frame, bg=self.themes[self.current_theme]["content_bg"])
        control_frame.pack(fill="x", pady=5)
        tk.Button(control_frame, text="Change Color", command=self.change_bar_color, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom In", command=lambda: self.zoom_graph("bar", 1.2), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom Out", command=lambda: self.zoom_graph("bar", 0.8), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        self.bar_canvas, self.bar_fig = self.stats_manager.get_bar_chart(self.bar_frame, color=self.bar_color, zoom=self.zoom_levels["bar"])
        self.bar_canvas.get_tk_widget().pack(expand=True, fill="both")

        # Scatter Plot
        control_frame = tk.Frame(self.scatter_frame, bg=self.themes[self.current_theme]["content_bg"])
        control_frame.pack(fill="x", pady=5)
        tk.Button(control_frame, text="Change Scatter Color", command=self.change_scatter_color, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Change Line Color", command=self.change_scatter_line_color, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom In", command=lambda: self.zoom_graph("scatter", 1.2), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom Out", command=lambda: self.zoom_graph("scatter", 0.8), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        self.scatter_canvas, self.scatter_fig = self.stats_manager.get_scatter_plot(self.scatter_frame, scatter_color=self.scatter_color, line_color=self.scatter_line_color, zoom=self.zoom_levels["scatter"])
        self.scatter_canvas.get_tk_widget().pack(expand=True, fill="both")

        # Line Graph
        control_frame = tk.Frame(self.line_frame, bg=self.themes[self.current_theme]["content_bg"])
        control_frame.pack(fill="x", pady=5)
        tk.Button(control_frame, text="Change Color", command=self.change_line_color, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom In", command=lambda: self.zoom_graph("line", 1.2), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        tk.Button(control_frame, text="Zoom Out", command=lambda: self.zoom_graph("line", 0.8), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(side="left", padx=5)
        self.line_canvas, self.line_fig = self.stats_manager.get_line_graph(self.line_frame, color=self.line_color, zoom=self.zoom_levels["line"])
        self.line_canvas.get_tk_widget().pack(expand=True, fill="both")

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
        colors = []
        for i in range(4):  # Assuming up to 4 categories
            color = colorchooser.askcolor(title=f"Select Color for Category {i+1}")[1]
            if color:
                colors.append(color)
        if colors:
            self.pie_colors = colors
            self.pie_canvas.get_tk_widget().destroy()
            self.pie_fig.close()
            self.pie_canvas, self.pie_fig = self.stats_manager.get_pie_chart(self.pie_frame, colors=self.pie_colors)
            self.pie_canvas.get_tk_widget().pack(expand=True, fill="both")
            logger.debug("Updated pie chart colors")

    def change_bar_color(self):
        color = colorchooser.askcolor(title="Select Bar Color")[1]
        if color:
            self.bar_color = color
            self.bar_canvas.get_tk_widget().destroy()
            self.bar_fig.close()
            self.bar_canvas, self.bar_fig = self.stats_manager.get_bar_chart(self.bar_frame, color=self.bar_color, zoom=self.zoom_levels["bar"])
            self.bar_canvas.get_tk_widget().pack(expand=True, fill="both")
            logger.debug("Updated bar chart color")

    def change_scatter_color(self):
        color = colorchooser.askcolor(title="Select Scatter Color")[1]
        if color:
            self.scatter_color = color
            self.scatter_canvas.get_tk_widget().destroy()
            self.scatter_fig.close()
            self.scatter_canvas, self.scatter_fig = self.stats_manager.get_scatter_plot(self.scatter_frame, scatter_color=self.scatter_color, line_color=self.scatter_line_color, zoom=self.zoom_levels["scatter"])
            self.scatter_canvas.get_tk_widget().pack(expand=True, fill="both")
            logger.debug("Updated scatter plot color")

    def change_scatter_line_color(self):
        color = colorchooser.askcolor(title="Select Line Color")[1]
        if color:
            self.scatter_line_color = color
            self.scatter_canvas.get_tk_widget().destroy()
            self.scatter_fig.close()
            self.scatter_canvas, self.scatter_fig = self.stats_manager.get_scatter_plot(self.scatter_frame, scatter_color=self.scatter_color, line_color=self.scatter_line_color, zoom=self.zoom_levels["scatter"])
            self.scatter_canvas.get_tk_widget().pack(expand=True, fill="both")
            logger.debug("Updated scatter plot line color")

    def change_line_color(self):
        color = colorchooser.askcolor(title="Select Line Color")[1]
        if color:
            self.line_color = color
            self.line_canvas.get_tk_widget().destroy()
            self.line_fig.close()
            self.line_canvas, self.line_fig = self.stats_manager.get_line_graph(self.line_frame, color=self.line_color, zoom=self.zoom_levels["line"])
            self.line_canvas.get_tk_widget().pack(expand=True, fill="both")
            logger.debug("Updated line graph color")

    def zoom_graph(self, graph_type, factor):
        self.zoom_levels[graph_type] *= factor
        if self.zoom_levels[graph_type] < 0.5:
            self.zoom_levels[graph_type] = 0.5
        elif self.zoom_levels[graph_type] > 2.0:
            self.zoom_levels[graph_type] = 2.0
        if graph_type == "bar":
            self.bar_canvas.get_tk_widget().destroy()
            self.bar_fig.close()
            self.bar_canvas, self.bar_fig = self.stats_manager.get_bar_chart(self.bar_frame, color=self.bar_color, zoom=self.zoom_levels["bar"])
            self.bar_canvas.get_tk_widget().pack(expand=True, fill="both")
        elif graph_type == "scatter":
            self.scatter_canvas.get_tk_widget().destroy()
            self.scatter_fig.close()
            self.scatter_canvas, self.scatter_fig = self.stats_manager.get_scatter_plot(self.scatter_frame, scatter_color=self.scatter_color, line_color=self.scatter_line_color, zoom=self.zoom_levels["scatter"])
            self.scatter_canvas.get_tk_widget().pack(expand=True, fill="both")
        elif graph_type == "line":
            self.line_canvas.get_tk_widget().destroy()
            self.line_fig.close()
            self.line_canvas, self.line_fig = self.stats_manager.get_line_graph(self.line_frame, color=self.line_color, zoom=self.zoom_levels["line"])
            self.line_canvas.get_tk_widget().pack(expand=True, fill="both")
        logger.debug(f"Zoomed {graph_type} graph: level={self.zoom_levels[graph_type]}")

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
        form = tk.Frame(self.planned_frame, bg=self.themes[self.current_theme]["content_bg"])
        form.pack(fill="x", padx=10)
        tk.Label(form, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_plan_amount = tk.Entry(form)
        self.entry_plan_amount.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_plan_date = tk.Entry(form)
        self.entry_plan_date.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Recipient:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_plan_recipient = tk.Entry(form)
        self.entry_plan_recipient.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form, text="Payment Method:").grid(row=3, column=0, padx=5, pady=5)
        self.plan_payment_var = tk.StringVar()
        self.plan_payment_dropdown = ttk.Combobox(
            form, textvariable=self.plan_payment_var, values=self.transaction_manager.get_payment_methods(), state="readonly"
        )
        self.plan_payment_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.plan_payment_dropdown.set(self.transaction_manager.get_payment_methods()[0])

        tk.Button(form, text="Add Planned Payment", command=self.add_planned_payment, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).grid(row=4, column=0, columnspan=2, pady=5)

        # Appointment Form
        tk.Label(self.appointments_frame, text="Add Appointment", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        appt_form = tk.Frame(self.appointments_frame, bg=self.themes[self.current_theme]["content_bg"])
        appt_form.pack(fill="x", padx=10)
        tk.Label(appt_form, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_appointment_title = tk.Entry(appt_form)
        self.entry_appointment_title.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(appt_form, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_appointment_date = tk.Entry(appt_form)
        self.entry_appointment_date.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(appt_form, text="Time (HH:MM):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_appointment_time = tk.Entry(appt_form)
        self.entry_appointment_time.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(appt_form, text="Add Appointment", command=self.add_appointment, bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).grid(row=3, column=0, columnspan=2, pady=5)

        self.update_calendar()

    def setup_notifications(self):
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="Notifications", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)

        # Upcoming Payments
        tk.Label(frame, text="Upcoming Payments", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.notifications_payments = ttk.Treeview(
            frame, columns=("Amount", "Recipient", "Date", "PaymentMethod"), show="headings", height=5
        )
        self.notifications_payments.heading("Amount", text="Amount")
        self.notifications_payments.heading("Recipient", text="Recipient")
        self.notifications_payments.heading("Date", text="Date")
        self.notifications_payments.heading("PaymentMethod", text="Payment Method")
        self.notifications_payments.pack(fill="x", pady=5)

        # Upcoming Appointments
        tk.Label(frame, text="Upcoming Appointments", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        self.notifications_appointments = ttk.Treeview(
            frame, columns=("Title", "Date", "Time"), show="headings", height=5
        )
        self.notifications_appointments.heading("Title", text="Title")
        self.notifications_appointments.heading("Date", text="Date")
        self.notifications_appointments.heading("Time", text="Time")
        self.notifications_appointments.pack(fill="x", pady=5)

        self.update_notifications()

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

    def change_theme(self):
        new_theme = self.theme_var.get()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_theme()
            logger.info(f"Changed theme to {self.current_theme}")

    def setup_payment(self):
        frame = tk.Frame(self.content, bg=self.themes[self.current_theme]["content_bg"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="Billing Details", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)

        # Current Subscription
        sub_frame = tk.Frame(frame, bg=self.themes[self.current_theme]["button_bg"], relief="raised", bd=2)
        sub_frame.pack(fill="x", pady=10)
        tk.Label(sub_frame, text="Current Subscription Plan", font=("Arial", 12), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(anchor="w", padx=10, pady=5)
        tk.Label(sub_frame, text="$25.00", font=("Arial", 16, "bold"), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(anchor="w", padx=10)
        tk.Label(sub_frame, text="Company Plus", font=("Arial", 10), bg=self.themes[self.current_theme]["button_bg"], fg=self.themes[self.current_theme]["button_fg"]).pack(anchor="w", padx=10)
        tk.Button(sub_frame, text="Change Plan", command=lambda: messagebox.showinfo("Info", "Change plan functionality not implemented"), bg=self.themes[self.current_theme]["content_bg"], fg=self.themes[self.current_theme]["button_bg"]).pack(anchor="w", padx=10, pady=5)

        # Next Payment
        tk.Label(frame, text="Next Payment", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        tk.Label(frame, text="$50.00 on May 15, 2025", font=("Arial", 10)).pack(anchor="w", padx=10)

        # Payment History
        tk.Label(frame, text="Payment History", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        payment_tree = ttk.Treeview(frame, columns=("Amount", "Status", "Recipient", "Date", "PaymentMethod"), show="headings")
        payment_tree.heading("Amount", text="Amount")
        payment_tree.heading("Status", text="Status")
        payment_tree.heading("Recipient", text="Recipient")
        payment_tree.heading("Date", text="Date")
        payment_tree.heading("PaymentMethod", text="Payment Method")
        payment_tree.pack(fill="x", padx=10, pady=5)
        for t in sorted(self.transaction_manager.get_transactions(), key=lambda x: x["Date"], reverse=True)[:3]:
            payment_tree.insert("", "end", values=(
                f"${t['Amount']:.2f}", t["Status"], t["Recipient"], t["Date"], t["PaymentMethod"]
            ))

    def update_balance(self):
        try:
            balance = sum(t["Amount"] for t in self.transaction_manager.get_transactions())
            self.balance_value.config(text=f"${balance:,.2f}")
            logger.debug(f"Updated balance: ${balance:,.2f}")
        except Exception as e:
            logger.error(f"Error updating balance: {e}")

    def update_dashboard(self):
        try:
            for row in self.recent_payments.get_children():
                self.recent_payments.delete(row)
            recent = sorted(
                self.transaction_manager.get_transactions(),
                key=lambda x: x["Date"],
                reverse=True
            )[:3]
            for t in recent:
                self.recent_payments.insert("", "end", values=(f"${t['Amount']:.2f}", t["Recipient"], t["Date"]))

            summary = self.transaction_manager.get_summary()
            self.summary_label.config(
                text=f"Income: ${summary['income']:,.2f} | Expenses: ${summary['expenses']:,.2f} | Net: ${summary['net']:,.2f}"
            )

            for widget in self.wallet_preview.winfo_children():
                widget.destroy()
            cards = self.wallet_manager.get_cards()
            if cards:
                main_card = cards[-1]
                card_frame = tk.Frame(self.wallet_preview, bg="#000000", relief="raised", bd=2)
                card_frame.pack(fill="x", pady=5)
                tk.Label(card_frame, text=f"{main_card['Type']} ending in {main_card['Number'][-4:]}", font=("Arial", 10), bg="#000000", fg="#ffffff").pack(pady=5)
                for card in reversed(cards[:-1][:3]):
                    card_frame = tk.Frame(self.wallet_preview, bg="#000000", relief="sunken", bd=1)
                    card_frame.pack(fill="x", pady=2)
                    tk.Label(card_frame, text=f"{card['Type']} ending in {card['Number'][-4:]}", font=("Arial", 8), bg="#000000", fg="#ffffff").pack()

            logger.debug("Updated dashboard")
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

    def update_transaction_lists(self, event=None):
        try:
            category_filter = self.filter_category_var.get()
            type_filter = self.filter_type_var.get()
            start_date = self.start_date_var.get().strip()
            end_date = self.end_date_var.get().strip()
            recipient = self.recipient_var.get().strip()
            if not start_date or not end_date:
                start_date = end_date = None
            trees = [
                (self.tree_all_frame, category_filter, type_filter),
                (self.tree_invoices_frame, "Invoice", None),
                (self.tree_deposits_frame, "Deposit", None),
                (self.tree_transfers_frame, "Transfer", None)
            ]
            for tree, cat, t_type in trees:
                for row in tree.get_children():
                    tree.delete(row)
                transactions = self.transaction_manager.get_transactions(
                    category=cat, transaction_type=t_type, start_date=start_date, end_date=end_date, recipient=recipient
                )
                for t in transactions:
                    tree.insert("", "end", values=(
                        f"${t['Amount']:.2f}", t["Status"], t["Recipient"], t["Date"], t["PaymentMethod"]
                    ))
            logger.debug("Updated transaction lists")
        except Exception as e:
            logger.error(f"Error updating transaction lists: {e}")
            messagebox.showerror("Error", str(e))

    def add_transaction(self):
        try:
            description = self.entry_description.get().strip()
            amount = self.entry_amount.get().strip()
            category = self.category_var.get()
            recipient = self.entry_recipient.get().strip()
            payment_method = self.payment_var.get()
            status = self.status_var.get()
            if not amount.replace(".", "", 1).isdigit():
                raise ValueError("Amount must be a valid number")
            amount = float(amount)
            self.transaction_manager.add_transaction(description, amount, category, recipient, payment_method, status)
            self.update_transaction_lists()
            self.update_balance()
            self.update_dashboard()
            self.stats_manager.update_transactions(self.transaction_manager.get_transactions())
            self.clear_transaction_form()
            messagebox.showinfo("Success", "Transaction added!")
            logger.info("Transaction added")
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            messagebox.showerror("Error", str(e))

    def edit_transaction(self):
        try:
            if self.selected_index is None:
                raise ValueError("No transaction selected")
            description = self.entry_description.get().strip()
            amount = self.entry_amount.get().strip()
            category = self.category_var.get()
            recipient = self.entry_recipient.get().strip()
            payment_method = self.payment_var.get()
            status = self.status_var.get()
            if not amount.replace(".", "", 1).isdigit():
                raise ValueError("Amount must be a valid number")
            amount = float(amount)
            self.transaction_manager.edit_transaction(
                self.selected_index, description, amount, category, recipient, payment_method, status
            )
            self.update_transaction_lists()
            self.update_balance()
            self.update_dashboard()
            self.stats_manager.update_transactions(self.transaction_manager.get_transactions())
            self.clear_transaction_form()
            self.selected_index = None
            messagebox.showinfo("Success", "Transaction updated!")
            logger.info(f"Transaction edited at index {self.selected_index}")
        except Exception as e:
            logger.error(f"Error editing transaction: {e}")
            messagebox.showerror("Error", str(e))

    def delete_transaction(self):
        try:
            if self.selected_index is None:
                raise ValueError("No transaction selected")
            if messagebox.askyesno("Confirm", "Delete this transaction?"):
                self.transaction_manager.delete_transaction(self.selected_index)
                self.update_transaction_lists()
                self.update_balance()
                self.update_dashboard()
                self.stats_manager.update_transactions(self.transaction_manager.get_transactions())
                self.clear_transaction_form()
                self.selected_index = None
                messagebox.showinfo("Success", "Transaction deleted!")
                logger.info("Transaction deleted")
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            messagebox.showerror("Error", str(e))

    def select_transaction(self, event, frame):
        try:
            tree = getattr(self, f"tree_{frame.winfo_name()}")
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

    def clear_transaction_form(self):
        self.entry_description.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_recipient.delete(0, tk.END)
        self.category_var.set(self.transaction_manager.get_categories()[0])
        self.payment_var.set(self.transaction_manager.get_payment_methods()[0])
        self.status_var.set("Pending")
        logger.debug("Cleared transaction form")

    def load_account(self):
        try:
            account = self.account_manager.get_account()
            self.entry_name.delete(0, tk.END)
            self.entry_emails.delete(0, tk.END)
            self.entry_phones.delete(0, tk.END)
            self.entry_ssn.delete(0, tk.END)
            self.cards_text.delete(1.0, tk.END)
            self.entry_name.insert(0, account["Name"])
            self.entry_emails.insert(0, ",".join(account["Emails"]))
            self.entry_phones.insert(0, ",".join(account["PhoneNumbers"]))
            self.entry_ssn.insert(0, account["SSN"])
            for card in self.wallet_manager.get_cards():
                self.cards_text.insert(tk.END, f"{card['Type']} ending in {card['Number'][-4:]}\n")
            if account["ImagePath"]:
                img = Image.open(account["ImagePath"]).resize((100, 100))
                self.image_ref = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.image_ref)
            logger.debug("Loaded account details")
        except Exception as e:
            logger.error(f"Error loading account: {e}")

    def save_account(self):
        try:
            name = self.entry_name.get().strip()
            emails = [e.strip() for e in self.entry_emails.get().split(",") if e.strip()]
            phones = [p.strip() for p in self.entry_phones.get().split(",") if p.strip()]
            ssn = self.entry_ssn.get().strip()
            image_path = self.account_manager.get_account().get("ImagePath", "")
            self.account_manager.update_account(name, emails, phones, ssn, image_path)
            messagebox.showinfo("Success", "Account updated!")
            logger.info("Account updated")
        except Exception as e:
            logger.error(f"Error saving account: {e}")
            messagebox.showerror("Error", str(e))

    def upload_image(self):
        try:
            file = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
            if file:
                self.account_manager.update_account(
                    self.account_manager.get_account()["Name"],
                    self.account_manager.get_account()["Emails"],
                    self.account_manager.get_account()["PhoneNumbers"],
                    self.account_manager.get_account()["SSN"],
                    file
                )
                img = Image.open(file).resize((100, 100))
                self.image_ref = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.image_ref)
                logger.info(f"Uploaded image: {file}")
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            messagebox.showerror("Error", str(e))

    def update_stats(self):
        try:
            percentages = self.stats_manager.get_recipient_percentages()
            self.recipient_text.delete(1.0, tk.END)
            for rec, perc in percentages.items():
                self.recipient_text.insert(tk.END, f"{rec}: {perc:.1f}%\n")
            logger.debug("Updated statistics")
        except Exception as e:
            logger.error(f"Error updating stats: {e}")

    def show_yearly_spending(self):
        try:
            year = self.entry_year.get().strip()
            if not year.isdigit():
                raise ValueError("Year must be a number")
            spending = self.stats_manager.get_yearly_spending(int(year))
            self.yearly_label.config(text=f"Yearly Spending: ${spending:,.2f}")
            logger.info(f"Calculated yearly spending for {year}: ${spending:,.2f}")
        except Exception as e:
            logger.error(f"Error showing yearly spending: {e}")
            messagebox.showerror("Error", str(e))

    def add_planned_payment(self):
        try:
            amount = self.entry_plan_amount.get().strip()
            date = self.entry_plan_date.get().strip()
            recipient = self.entry_plan_recipient.get().strip()
            payment_method = self.plan_payment_var.get()
            if not amount.replace(".", "", 1).isdigit():
                raise ValueError("Amount must be a valid number")
            self.calendar_manager.add_planned_payment(float(amount), date, recipient, payment_method)
            self.update_calendar()
            self.update_notifications()
            messagebox.showinfo("Success", "Planned payment added!")
            logger.info("Planned payment added")
        except Exception as e:
            logger.error(f"Error adding planned payment: {e}")
            messagebox.showerror("Error", str(e))

    def add_appointment(self):
        try:
            title = self.entry_appointment_title.get().strip()
            date = self.entry_appointment_date.get().strip()
            time = self.entry_appointment_time.get().strip()
            self.calendar_manager.add_appointment(title, date, time)
            self.update_calendar()
            self.update_notifications()
            messagebox.showinfo("Success", "Appointment added!")
            logger.info("Appointment added")
        except Exception as e:
            logger.error(f"Error adding appointment: {e}")
            messagebox.showerror("Error", str(e))

    def update_calendar(self):
        try:
            # Payments Tab: Display past transactions
            payments_tree = ttk.Treeview(
                self.payments_frame, columns=("Amount", "Recipient", "Date", "PaymentMethod"), show="headings"
            )
            payments_tree.heading("Amount", text="Amount")
            payments_tree.heading("Recipient", text="Recipient")
            payments_tree.heading("Date", text="Date")
            payments_tree.heading("PaymentMethod", text="Payment Method")
            for widget in self.payments_frame.winfo_children():
                widget.destroy()
            payments_tree.pack(expand=True, fill="both", padx=10, pady=5)
            for t in self.transaction_manager.get_transactions():
                payments_tree.insert("", "end", values=(
                    f"${t['Amount']:.2f}", t["Recipient"], t["Date"], t["PaymentMethod"]
                ))

            # Planned Payments Tab: Display planned payments below the form
            planned_tree = ttk.Treeview(
                self.planned_frame, columns=("Amount", "Recipient", "Date", "PaymentMethod"), show="headings"
            )
            planned_tree.heading("Amount", text="Amount")
            planned_tree.heading("Recipient", text="Recipient")
            planned_tree.heading("Date", text="Date")
            planned_tree.heading("PaymentMethod", text="Payment Method")
            for widget in self.planned_frame.winfo_children():
                widget.grid_forget()
            tk.Label(self.planned_frame, text="Add Planned Payment", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
            form = self.planned_frame.winfo_children()[1]
            form.pack(fill="x", padx=10)
            planned_tree.pack(expand=True, fill="both", padx=10, pady=5)
            for p in self.calendar_manager.get_planned_payments():
                planned_tree.insert("", "end", values=(
                    f"${p['Amount']:.2f}", p["Recipient"], p["Date"], p["PaymentMethod"]
                ))

            # Appointments Tab: Display appointments below the form
            appt_tree = ttk.Treeview(
                self.appointments_frame, columns=("Title", "Date", "Time"), show="headings"
            )
            appt_tree.heading("Title", text="Title")
            appt_tree.heading("Date", text="Date")
            appt_tree.heading("Time", text="Time")
            for widget in self.appointments_frame.winfo_children():
                widget.grid_forget()
            tk.Label(self.appointments_frame, text="Add Appointment", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
            appt_form = self.appointments_frame.winfo_children()[1]
            appt_form.pack(fill="x", padx=10)
            appt_tree.pack(expand=True, fill="both", padx=10, pady=5)
            for a in self.calendar_manager.get_appointments():
                appt_tree.insert("", "end", values=(a["Title"], a["Date"], a["Time"]))

            logger.debug("Updated calendar displays")
        except Exception as e:
            logger.error(f"Error updating calendar: {e}")

    def update_notifications(self):
        try:
            for row in self.notifications_payments.get_children():
                self.notifications_payments.delete(row)
            for p in self.calendar_manager.get_upcoming_payments():
                self.notifications_payments.insert("", "end", values=(
                    f"${p['Amount']:.2f}", p["Recipient"], p["Date"], p["PaymentMethod"]
                ))

            for row in self.notifications_appointments.get_children():
                self.notifications_appointments.delete(row)
            for a in self.calendar_manager.get_upcoming_appointments():
                self.notifications_appointments.insert("", "end", values=(
                    a["Title"], a["Date"], a["Time"]
                ))
            logger.debug("Updated notifications")
        except Exception as e:
            logger.error(f"Error updating notifications: {e}")

    def upload_card_image(self):
        try:
            file = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
            if file:
                self.temp_card_image = file
                logger.info(f"Uploaded card image: {file}")
            else:
                self.temp_card_image = ""
        except Exception as e:
            logger.error(f"Error uploading card image: {e}")
            messagebox.showerror("Error", str(e))

    def update_wallet(self):
        try:
            for widget in self.card_frame.winfo_children():
                widget.destroy()
            cards = self.wallet_manager.get_cards()
            if cards:
                main_card = cards[-1]
                frame = tk.Frame(self.card_frame, bg="#000000", relief="raised", bd=2)
                frame.pack(fill="x", pady=5)
                tk.Label(frame, text=f"{main_card['Type']} ending in {main_card['Number'][-4:]}", font=("Arial", 10), bg="#000000", fg="#ffffff").pack(pady=5)
                if main_card["ImagePath"]:
                    img = Image.open(main_card["ImagePath"]).resize((150, 100))
                    photo = ImageTk.PhotoImage(img)
                    tk.Label(frame, image=photo, bg="#000000").pack()
                    frame.image = photo
                for card in reversed(cards[:-1][:3]):
                    frame = tk.Frame(self.card_frame, bg="#000000", relief="sunken", bd=1)
                    frame.pack(fill="x", pady=2)
                    tk.Label(frame, text=f"{card['Type']} ending in {card['Number'][-4:]}", font=("Arial", 8), bg="#000000", fg="#ffffff").pack()
            logger.debug("Updated wallet display")
        except Exception as e:
            logger.error(f"Error updating wallet: {e}")

    def add_card(self):
        try:
            number = self.entry_card_number.get().strip()
            card_type = self.card_type_var.get()
            if not number:
                raise ValueError("Card number cannot be empty")
            # Use the temporary image path if available, otherwise default to empty string
            image_path = getattr(self, 'temp_card_image', "")
            self.wallet_manager.add_card(number, card_type, image_path)
            self.update_wallet()
            self.entry_card_number.delete(0, tk.END)
            self.card_type_var.set("Visa")
            self.temp_card_image = ""  # Reset the temporary image path
            messagebox.showinfo("Success", "Card added!")
            logger.info("Card added to wallet")
        except Exception as e:
            logger.error(f"Error adding card: {e}")
            messagebox.showerror("Error", str(e))

    def generate_reflection_report(self):
        # Placeholder for reflection report generation
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TransactionGUI(root)
    root.mainloop()