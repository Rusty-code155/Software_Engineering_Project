# Written by: Turner Miles Peeples

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatsManager:
    def __init__(self, transaction_manager):
        self.transaction_manager = transaction_manager

    def get_pie_chart(self, frame):
        try:
            transactions = self.transaction_manager.get_transactions()
            categories = {}
            for t in transactions:
                if t["Category"] in ["Expense", "Invoice"]:
                    categories[t["Category"]] = categories.get(t["Category"], 0) + t["Amount"]

            if not categories:
                return None

            labels = list(categories.keys())
            sizes = list(categories.values())

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            logger.debug("Generated pie chart")
            return canvas, fig
        except Exception as e:
            logger.error(f"Error generating pie chart: {e}")
            return None

    def get_bar_chart(self, frame):
        try:
            transactions = self.transaction_manager.get_transactions()
            spending = {}
            for t in transactions:
                if t["Category"] in ["Expense", "Invoice"]:
                    date = t["Date"].split()[0]
                    spending[date] = spending.get(date, 0) + t["Amount"]

            if not spending:
                return None

            dates = list(spending.keys())
            amounts = list(spending.values())

            fig, ax = plt.subplots()
            ax.bar(dates, amounts)
            ax.set_xlabel("Date")
            ax.set_ylabel("Amount ($)")
            ax.set_title("Spending Over Time")
            plt.xticks(rotation=45)
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            logger.debug("Generated bar chart")
            return canvas, fig
        except Exception as e:
            logger.error(f"Error generating bar chart: {e}")
            return None

    def get_scatter_plot(self, frame):
        try:
            transactions = self.transaction_manager.get_transactions()
            amounts = []
            dates = []
            for t in transactions:
                if t["Category"] in ["Expense", "Invoice"]:
                    try:
                        # Try the full datetime format first
                        date = datetime.strptime(t["Date"], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            # Fallback to date-only format and add a default time
                            date = datetime.strptime(t["Date"], "%Y-%m-%d")
                        except ValueError:
                            logger.warning(f"Skipping transaction with invalid date format: {t['Date']}")
                            continue
                    amounts.append(t["Amount"])
                    dates.append(date)

            if not amounts or not dates:
                logger.debug("No data available for scatter plot")
                return None

            fig, ax = plt.subplots()
            ax.scatter(dates, amounts)
            ax.set_xlabel("Date")
            ax.set_ylabel("Amount ($)")
            ax.set_title("Spending Scatter Plot")
            plt.xticks(rotation=45)
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            logger.debug("Generated scatter plot")
            return canvas, fig
        except Exception as e:
            logger.error(f"Error generating scatter plot: {e}")
            return None

    def get_line_graph(self, frame):
        try:
            transactions = self.transaction_manager.get_transactions()
            spending = {}
            for t in transactions:
                if t["Category"] in ["Expense", "Invoice"]:
                    date = t["Date"].split()[0]
                    spending[date] = spending.get(date, 0) + t["Amount"]

            if not spending:
                return None

            dates = list(spending.keys())
            amounts = list(spending.values())

            fig, ax = plt.subplots()
            ax.plot(dates, amounts, marker='o')
            ax.set_xlabel("Date")
            ax.set_ylabel("Amount ($)")
            ax.set_title("Spending Trend Over Time")
            plt.xticks(rotation=45)
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            logger.debug("Generated line graph")
            return canvas, fig
        except Exception as e:
            logger.error(f"Error generating line graph: {e}")
            return None