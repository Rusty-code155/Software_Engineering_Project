# Written by: Turner Miles Peeples

import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('debug.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class StatsManager:
    def __init__(self, transactions):
        self.transactions = transactions
        self.default_colors = {
            'pie': ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f'],
            'bar': '#3498db',
            'scatter': '#3498db',
            'scatter_line': '#e74c3c',
            'line': '#2ecc71'
        }
        logger.debug("StatsManager initialized")

    def get_pie_chart(self, tk_parent, colors=None):
        try:
            categories = {}
            for t in self.transactions:
                cat = t["Category"]
                categories[cat] = categories.get(cat, 0) + t["Amount"]
            labels = list(categories.keys())
            sizes = list(categories.values())
            if not sizes:
                raise ValueError("No transaction data")
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors or self.default_colors['pie'])
            ax.set_title("Spending by Category")
            canvas = FigureCanvasTkAgg(fig, master=tk_parent)
            logger.debug("Generated pie chart")
            return canvas, fig
        except Exception as e:
            logger.error(f"Error generating pie chart: {e}")
            raise

    def get_bar_chart(self, tk_parent, color=None, zoom=1.0):
        try:
            monthly_spending = {}
            for t in self.transactions:
                if t["Category"] in ["Expense", "Invoice"]:
                    date = datetime.strptime(t["Date"], "%Y-%m-%d %H:%M:%S")
                    month = date.strftime("%Y-%m")
                    monthly_spending[month] = monthly_spending.get(month, 0) + t["Amount"]
            if not monthly_spending:
                raise ValueError("No spending data")
            months = list(monthly_spending.keys())
            amounts = list(monthly_spending.values())
            fig, ax = plt.subplots(figsize=(6 * zoom, 4 * zoom))
            bars = ax.bar(months, amounts, color=color or self.default_colors['bar'])
            ax.set_title("Monthly Spending")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount ($)")
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Panning setup
            ax.panning = False
            ax.press = None

            def on_press(event):
                if event.inaxes != ax:
                    return
                ax.panning = True
                ax.press = event.xdata, event.ydata

            def on_release(event):
                ax.panning = False
                ax.press = None

            def on_motion(event):
                if not ax.panning or event.inaxes != ax or ax.press is None:
                    return
                xpress, ypress = ax.press
                dx = event.xdata - xpress
                dy = event.ydata - ypress
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
                ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
                canvas.draw()

            # Tooltip setup
            annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)

            def update_annot(bar, month, amount):
                x, y = bar.get_x() + bar.get_width() / 2, bar.get_height()
                annot.xy = (x, y)
                text = f"Month: {month}\nAmount: ${amount:.2f}"
                annot.set_text(text)
                annot.set_visible(True)
                canvas.draw_idle()

            def on_hover(event):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    for bar, (month, amount) in zip(bars, zip(months, amounts)):
                        cont, _ = bar.contains(event)
                        if cont:
                            update_annot(bar, month, amount)
                            return
                if vis:
                    annot.set_visible(False)
                    canvas.draw_idle()

            canvas.mpl_connect("button_press_event", on_press)
            canvas.mpl_connect("button_release_event", on_release)
            canvas.mpl_connect("motion_notify_event", on_motion)
            canvas.mpl_connect("motion_notify_event", on_hover)

            canvas = FigureCanvasTkAgg(fig, master=tk_parent)
            logger.debug("Generated bar chart with panning and tooltips")
            return canvas, fig
        except Exception as e:
            logger.error(f"Error generating bar chart: {e}")
            raise

    def get_scatter_plot(self, tk_parent, scatter_color=None, line_color=None, zoom=1.0):
        try:
            dates = []
            amounts = []
            date_objects = []
            for t in self.transactions:
                if t["Category"] in ["Expense", "Invoice"]:
                    date = datetime.strptime(t["Date"], "%Y-%m-%d %H:%M:%S")
                    date_objects.append(date)
                    dates.append(date.timestamp())
                    amounts.append(t["Amount"])
            if not dates:
                raise ValueError("No spending data")
            fig, ax = plt.subplots(figsize=(6 * zoom, 4 * zoom))
            scatter = ax.scatter(dates, amounts, color=scatter_color or self.default_colors['scatter'], label="Spending")
            z = np.polyfit(dates, amounts, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(dates), color=line_color or self.default_colors['scatter_line'], label="Line of Best Fit")
            ax.set_title("Spending Over Time")
            ax.set_xlabel("Date")
            ax.set_ylabel("Amount ($)")
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Panning setup
            ax.panning = False
            ax.press = None

            def on_press(event):
                if event.inaxes != ax:
                    return
                ax.panning = True
                ax.press = event.xdata, event.ydata

            def on_release(event):
                ax.panning = False
                ax.press = None

            def on_motion(event):
                if not ax.panning or event.inaxes != ax or ax.press is None:
                    return
                xpress, ypress = ax.press
                dx = event.xdata - xpress
                dy = event.ydata - ypress
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
                ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
                canvas.draw()

            # Tooltip setup
            annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)

            def update_annot(ind):
                idx = ind["ind"][0]
                pos = scatter.get_offsets()[idx]
                annot.xy = pos
                date_str = date_objects[idx].strftime("%Y-%m-%d %H:%M:%S")
                text = f"Date: {date_str}\nAmount: ${amounts[idx]:.2f}"
                annot.set_text(text)
                annot.set_visible(True)
                canvas.draw_idle()

            def on_hover(event):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    cont, ind = scatter.contains(event)
                    if cont:
                        update_annot(ind)
                        return
                if vis:
                    annot.set_visible(False)
                    canvas.draw_idle()

            canvas = FigureCanvasTkAgg(fig, master=tk_parent)
            canvas.mpl_connect("button_press_event", on_press)
            canvas.mpl_connect("button_release_event", on_release)
            canvas.mpl_connect("motion_notify_event", on_motion)
            canvas.mpl_connect("motion_notify_event", on_hover)

            logger.debug("Generated scatter plot with panning and tooltips")
            return canvas, fig
        except Exception as e:
            logger.error(f"Error generating scatter plot: {e}")
            raise

    def get_line_graph(self, tk_parent, color=None, zoom=1.0):
        try:
            daily_spending = {}
            for t in self.transactions:
                if t["Category"] in ["Expense", "Invoice"]:
                    date = datetime.strptime(t["Date"], "%Y-%m-%d %H:%M:%S").date()
                    daily_spending[date] = daily_spending.get(date, 0) + t["Amount"]
            if not daily_spending:
                raise ValueError("No spending data")
            dates = sorted(daily_spending.keys())
            cumulative = []
            total = 0
            for date in dates:
                total += daily_spending[date]
                cumulative.append(total)
            fig, ax = plt.subplots(figsize=(6 * zoom, 4 * zoom))
            line, = ax.plot(dates, cumulative, color=color or self.default_colors['line'], label="Cumulative Spending")
            ax.set_title("Cumulative Spending Over Time")
            ax.set_xlabel("Date")
            ax.set_ylabel("Cumulative Amount ($)")
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Panning setup
            ax.panning = False
            ax.press = None

            def on_press(event):
                if event.inaxes != ax:
                    return
                ax.panning = True
                ax.press = event.xdata, event.ydata

            def on_release(event):
                ax.panning = False
                ax.press = None

            def on_motion(event):
                if not ax.panning or event.inaxes != ax or ax.press is None:
                    return
                xpress, ypress = ax.press
                dx = event.xdata - xpress
                dy = event.ydata - ypress
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
                ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
                canvas.draw()

            # Tooltip setup
            annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)

            def on_hover(event):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    x, y = event.xdata, event.ydata
                    # Convert xdata (mouse position) to index
                    x_data = [d.toordinal() for d in dates]
                    idx = np.argmin(np.abs(np.array(x_data) - x))
                    if abs(x_data[idx] - x) < 0.5:  # Threshold for proximity
                        annot.xy = (x_data[idx], cumulative[idx])
                        date_str = dates[idx].strftime("%Y-%m-%d")
                        text = f"Date: {date_str}\nCumulative: ${cumulative[idx]:.2f}"
                        annot.set_text(text)
                        annot.set_visible(True)
                        canvas.draw_idle()
                        return
                if vis:
                    annot.set_visible(False)
                    canvas.draw_idle()

            canvas = FigureCanvasTkAgg(fig, master=tk_parent)
            canvas.mpl_connect("button_press_event", on_press)
            canvas.mpl_connect("button_release_event", on_release)
            canvas.mpl_connect("motion_notify_event", on_motion)
            canvas.mpl_connect("motion_notify_event", on_hover)

            logger.debug("Generated line graph with panning and tooltips")
            return canvas, fig
        except Exception as e:
            logger.error(f"Error generating line graph: {e}")
            raise

    def get_recipient_percentages(self):
        try:
            total = sum(t["Amount"] for t in self.transactions)
            if total == 0:
                return {}
            recipients = {}
            for t in self.transactions:
                rec = t["Recipient"]
                recipients[rec] = recipients.get(rec, 0) + t["Amount"]
            return {k: (v / total * 100) for k, v in recipients.items()}
        except Exception as e:
            logger.error(f"Error calculating recipient percentages: {e}")
            raise

    def get_yearly_spending(self, year):
        try:
            yearly = [t for t in self.transactions if t["Date"].startswith(str(year))]
            return sum(t["Amount"] for t in yearly)
        except Exception as e:
            logger.error(f"Error calculating yearly spending: {e}")
            raise

    def update_transactions(self, transactions):
        self.transactions = transactions
        logger.debug("Updated transactions in StatsManager")