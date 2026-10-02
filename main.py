import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import defaultdict
import csv

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from expense_manager import (
    save_expenses,
    load_expenses,
    calculate_total,
    category_summary,
    create_expense,
    filter_expenses,
    save_settings,
    load_settings
)

expenses = load_expenses()
settings = load_settings()
monthly_budget = settings.get("monthly_budget", 2000)

editing_index = None
displayed_indices =[]


window = tk.Tk()

style = ttk.Style()
style.theme_use("clam")


# PET COLOR SYSTEM
BG = "#F7F8FA"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"
ACCENT = "#16A34A"
ACCENT_DARK = "#15803D"
DANGER = "#DC2626"

LIGHT_THEME = {
    "BG": "#F7F8FA",
    "CARD": "#FFFFFF",
    "TEXT": "#111827",
    "MUTED": "#6B7280",
    "BORDER": "#E5E7EB",
    "ACCENT": "#16A34A",
    "ACCENT_DARK": "#15803D",
    "DANGER": "#DC2626"
}

DARK_THEME = {
    "BG": "#111827",
    "CARD": "#1F2937",
    "TEXT": "#F9FAFB",
    "MUTED": "#9CA3AF",
    "BORDER": "#374151",
    "ACCENT": "#22C55E",
    "ACCENT_DARK": "#16A34A",
    "DANGER": "#F87171"
}

dark_mode = settings.get("dark_mode", False)

window.configure(bg=BG)


# GENERAL
style.configure(
    "TFrame",
    background=BG
)

style.configure(
    "TLabel",
    background=BG,
    foreground=TEXT,
    font=("Segoe UI", 10)
)

style.configure(
    "Title.TLabel",
    background=BG,
    foreground=TEXT,
    font=("Segoe UI", 28, "bold")
)

style.configure(
    "Subtitle.TLabel",
    background=BG,
    foreground=MUTED,
    font=("Segoe UI", 11)
)

style.configure(
    "Section.TLabel",
    background=BG,
    foreground=TEXT,
    font=("Segoe UI", 15, "bold")
)

style.configure(
    "Muted.TLabel",
    background=BG,
    foreground=MUTED,
    font=("Segoe UI", 10)
)


# BUTTONS
style.configure(
    "TButton",
    font=("Segoe UI", 10, "bold"),
    padding=(14, 9),
    borderwidth=0
)

style.map(
    "TButton",
    background=[
        ("active", "#E5E7EB"),
        ("pressed", "#D1D5DB")
    ]
)

style.configure(
    "Accent.TButton",
    background=ACCENT,
    foreground="white",
    font=("Segoe UI", 10, "bold"),
    padding=(16, 10),
    borderwidth=0
)

style.map(
    "Accent.TButton",
    background=[
        ("active", ACCENT_DARK),
        ("pressed", ACCENT_DARK)
    ]
)


# INPUTS
style.configure(
    "TEntry",
    padding=9,
    font=("Segoe UI", 10)
)

style.configure(
    "TCombobox",
    padding=8,
    font=("Segoe UI", 10)
)

style.configure(
    "Budget.Horizontal.TProgressbar",
    troughcolor=BORDER,
    background=ACCENT,
    thickness=14
)


# TRANSACTION TABLE
style.configure(
    "Treeview",
    background=CARD,
    foreground=TEXT,
    fieldbackground=CARD,
    rowheight=42,
    font=("Segoe UI", 10),
    borderwidth=0
)

style.configure(
    "Treeview.Heading",
    background=BG,
    foreground=MUTED,
    font=("Segoe UI", 9, "bold"),
    borderwidth=0
)

style.map(
    "Treeview",
    background=[
        ("selected", "#DCFCE7")
    ],
    foreground=[
        ("selected", TEXT)
    ]
)


# WINDOW
window.title("PET — Personal Expense Tracker")
window.geometry("1100x900")
window.minsize(900, 750)


#Page Containers
dashboard_page = ttk.Frame(window)
transactions_page = ttk.Frame(window)

# Scrollable Transactions Page
transactions_canvas = tk.Canvas(
    transactions_page,
    bg=BG,
    highlightthickness=0
)

transactions_scrollbar = ttk.Scrollbar(
    transactions_page,
    orient="vertical",
    command=transactions_canvas.yview
)

transactions_content = ttk.Frame(
    transactions_canvas
)

transactions_content.bind(
    "<Configure>",
    lambda event: transactions_canvas.configure(
        scrollregion=transactions_canvas.bbox("all")
    )
)

transactions_window = transactions_canvas.create_window(
    (0, 0),
    window=transactions_content,
    anchor="nw"
)

transactions_canvas.configure(
    yscrollcommand=transactions_scrollbar.set
)

transactions_canvas.pack(
    side="left",
    fill="both",
    expand=True
)

transactions_scrollbar.pack(
    side="right",
    fill="y"
)

def scroll_transactions(event):
    transactions_canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )

transactions_canvas.bind_all(
    "<MouseWheel>",
    scroll_transactions
)

def resize_transactions_content(event):
    transactions_canvas.itemconfigure(
        transactions_window,
        width=event.width
    )

transactions_canvas.bind(
    "<Configure>",
    resize_transactions_content
)

#Page Switching
def show_dashboard():
    transactions_page.pack_forget()
    dashboard_page.pack(
        fill="both",
        expand=True
    )

def show_transactions():
    dashboard_page.pack_forget()
    transactions_page.pack(
        fill="both",
        expand=True
    )

def toggle_theme():
    global dark_mode

    dark_mode = not dark_mode

    settings["dark_mode"] = dark_mode
    save_settings(settings)

    apply_theme()

# NAVIGATION
navigation_frame = ttk.Frame(window)
navigation_frame.pack(
    fill="x",
    padx=40,
    pady=(25, 5)
)

brand_label = ttk.Label(
    navigation_frame,
    text="PET",
    font=("Segoe UI", 18, "bold")
)
brand_label.pack(side="left")

nav_right = ttk.Frame(navigation_frame)
nav_right.pack(side="right")

dashboard_button = ttk.Button(
    nav_right,
    text="Dashboard",
    command=show_dashboard
)
dashboard_button.pack(side="left", padx=4)

transactions_button = ttk.Button(
    nav_right,
    text="Transactions",
    command=show_transactions
)
transactions_button.pack(side="left", padx=4)

theme_button = ttk.Button(
    nav_right,
    text="🌙 Dark Mode",
    command=toggle_theme
)
theme_button.pack(side="left", padx=(12, 4))

dashboard_page.pack(
    fill="both",
    expand=True
)

transactions_page.pack_forget()


#Title
title_label = ttk.Label(
    dashboard_page,
    text="",
    style="Title.TLabel"
)
title_label.pack(anchor="w", padx=40, pady=(25, 2))

subtitle_label = ttk.Label(
    dashboard_page,
    text="Here's your spending overview.",
    style="Subtitle.TLabel"
)
subtitle_label.pack(anchor="w", padx=40, pady=(0, 25))

def update_greeting():
    hour = datetime.now().hour

    if hour < 12:
        greeting = "Good morning."
    elif hour < 18:
        greeting = "Good afternoon."
    else:
        greeting = "Good evening."

    title_label.config(text=greeting)
    window.after(60000, update_greeting)

update_greeting()


#Input Section
ttk.Label(
    transactions_content,
    text="Add expense",
    style="Section.TLabel"
).pack(
    anchor="w",
    padx=40,
    pady=(25, 0)
)

input_frame = ttk.Frame(transactions_content)
input_frame.pack(
    fill="x",
    padx=40,
    pady=(15, 20)
)

date_label = ttk.Label(input_frame, text="Date:")
date_label.grid(row=0, column=0, padx=8, pady=8, sticky="w")

date_entry = ttk.Entry(input_frame, width=30)
date_entry.grid(row=0, column=1, padx=8, pady=8)
date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

amount_label = ttk.Label(input_frame, text="Amount:")
amount_label.grid(row=0, column=2, padx=8, pady=8, sticky="w")

amount_entry = ttk.Entry(input_frame, width=30)
amount_entry.grid(row=0, column=3, padx=8, pady=8)

category_label = ttk.Label(input_frame, text="Category:")
category_label.grid(row=1, column=0, padx=8, pady=8, sticky="w")

category_var = tk.StringVar()

category_dropdown = ttk.Combobox(
    input_frame,
    textvariable=category_var,
    values=[
        "Food",
        "Transport",
        "Bills",
        "Shopping",
        "Investment",
        "Other"
    ],
    width=28,
    state="readonly"
)
category_dropdown.grid(row=1, column=1, padx=8, pady=8)

description_label = ttk.Label(input_frame, text="Description:")
description_label.grid(row=1, column=2, padx=8, pady=8, sticky="w")

description_entry = ttk.Entry(input_frame, width=30)
description_entry.grid(
    row=1,
    column=3,
    padx=8,
    pady=8,
    sticky="ew"
)

input_frame.columnconfigure(1, weight=1)
input_frame.columnconfigure(3, weight=1)


#Functions
def format_date(date_string):
    if not date_string:
        return "_"

    try:
        date_object = datetime.strptime(date_string, "%Y-%m-%d")
        return date_object.strftime("%b %d, %Y")
    except ValueError:
        return date_string

def refresh_expense_list(indices=None):
    global displayed_indices

    for item in expense_table.get_children():
        expense_table.delete(item)

    if indices is None:
        displayed_indices = list(range(len(expenses)))
    else:
        displayed_indices = indices

    for index in displayed_indices:
        expense = expenses[index]

        expense_table.insert(
            "",
            tk.END,
            iid=str(index),
            values=(
                format_date(expense.get("date")),
                expense["category"],
                expense["description"],
                f"GHS {expense['amount']:,.2f}"
            )
        )

    total_label.config(
        text=f"Total: GHS {calculate_total(expenses):,.2f}"
    )

    update_dashboard()

def auto_save():
    save_expenses(expenses)

def add_expense():
    global editing_index

    expense_date = date_entry.get().strip()
    amount = amount_entry.get().strip()
    category = category_var.get()
    description = description_entry.get().strip()

    if not amount or not category or not description:
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all fields."
        )
        return

    expense = create_expense(
        amount,
        category,
        description,
        expense_date
    )

    if expense is None:
        messagebox.showerror(
            "Invalid Expense",
            "Enter a valid amount and date (YYYY-MM-DD). Future dates are not allowed."
        )
        return

    if editing_index is not None:
        expenses[editing_index] = expense
        editing_index = None

        add_button.config(text="Add Expense")

        messagebox.showinfo(
            "Updated",
            "Expense updated successfully"
        )
    else:
        expenses.append(expense)

    refresh_expense_list()
    auto_save()

    date_entry.delete(0, tk.END)
    date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    category_var.set("")

def delete_expense():
    selected = expense_table.selection()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Select an expense first."
        )
        return

    index = int(selected[0])

    confirm = messagebox.askyesno(
        "Delete Expense",
        "Are you sure you want to delete this expense?"
    )

    if not confirm:
        return

    expenses.pop(index)

    refresh_expense_list()
    auto_save()

    messagebox.showinfo(
        "Deleted",
        "Expense deleted successfully."
    )

def edit_expense():
    global editing_index

    selected = expense_table.selection()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Select an expense to edit."
        )
        return

    editing_index = int(selected[0])

    expense = expenses[editing_index]

    date_entry.delete(0, tk.END)
    date_entry.insert(0, expense.get("date", ""))

    amount_entry.delete(0, tk.END)
    amount_entry.insert(0, str(expense["amount"]))

    category_var.set(expense["category"])

    description_entry.delete(0, tk.END)
    description_entry.insert(0, expense["description"])

    add_button.config(text="Update Expense")

def show_category_summary():
    summary = category_summary(expenses)

    summary_window = tk.Toplevel(window)
    summary_window.title("Category Summary")
    summary_window.geometry("400x400")
    summary_window.resizable(False, False)

    ttk.Label(
        summary_window,
        text="Spending by Category",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    if not summary:
        ttk.Label(
            summary_window,
            text="No expenses recorded yet."
        ).pack(pady=20)
        return

    summary_frame = ttk.Frame(summary_window)
    summary_frame.pack(fill="both", expand=True, padx=30)

    for category, amount in sorted(summary.items()):
        row = ttk.Frame(summary_frame)
        row.pack(fill="x", pady=6)

        ttk.Label(
            row,
            text=category,
            font=("Arial", 11, "bold")
        ).pack(side="left")

        ttk.Label(
            row,
            text=f"GHS {amount:.2f}"
        ).pack(side="right")

    ttk.Separator(summary_window).pack(
        fill="x",
        padx=30,
        pady=10
    )

    ttk.Label(
        summary_window,
        text=f"Total: GHS {calculate_total(expenses):.2f}",
        font=("Arial", 13, "bold")
    ).pack(pady=10)

def search_expenses():
    search_text = search_entry.get()

    matching_indices = filter_expenses(
        expenses,
        search_text
    )
    refresh_expense_list(matching_indices)

def export_expenses():
    if not expenses:
        messagebox.showinfo(
            "Export",
            "There are no expenses to export."
        )
        return

    try:
        with open(
            "expenses_export.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Date",
                "Category",
                "Description",
                "Amount"
            ])

            for expense in expenses:
                writer.writerow([
                    expense.get("date", ""),
                    expense["category"],
                    expense["description"],
                    expense["amount"]
                ])

        messagebox.showinfo(
            "Export Complete",
            "Expenses exported to expenses_export.csv"
        )

    except OSError:
        messagebox.showerror(
            "Export Error",
            "Could not export expenses."
        )


#Keyboard Shortcuts
window.bind("<Return>", lambda event: add_expense())
window.bind("<Delete>", lambda event: delete_expense())


#Main Buttons
button_frame = ttk.Frame(transactions_content)
button_frame.pack(pady=10)

add_button = ttk.Button(
    button_frame,
    text="Add Expense",
    command=add_expense
)
add_button.grid(row=0, column=0, padx=6, pady=6)

edit_button = ttk.Button(
    button_frame,
    text="Edit Expense",
    command=edit_expense
)
edit_button.grid(row=0, column=1, padx=6, pady=6)

delete_button = ttk.Button(
    button_frame,
    text="Delete Selected",
    command=delete_expense
)
delete_button.grid(row=0, column=2, padx=6, pady=6)


#Search
search_frame = ttk.Frame(transactions_content)
search_frame.pack(pady=10)

search_label = ttk.Label(search_frame, text="Search:")
search_label.grid(row=0, column=0, padx=5)

search_entry = ttk.Entry(search_frame, width=40)
search_entry.grid(row=0, column=1, padx=5)

search_entry.bind("<KeyRelease>", lambda event: search_expenses())


#Expense Table
ttk.Label(
    transactions_content,
    text="Transactions",
    style="Section.TLabel"
).pack(
    anchor="w",
    padx=40,
    pady=(25, 10)
)

expense_frame = ttk.Frame(
    transactions_content
)

expense_frame.pack(
    fill="both",
    padx=40,
    pady=(0, 10)
)

table_container = ttk.Frame(expense_frame)
table_container.pack(
    fill="x",
    expand=True
)

columns = ("date", "category", "description", "amount")

expense_table = ttk.Treeview(
    table_container,
    columns=columns,
    show="headings",
    selectmode="browse",
    height=5
)

expense_table.heading("date", text="DATE")
expense_table.heading("category", text="CATEGORY")
expense_table.heading("description", text="DESCRIPTION")
expense_table.heading("amount", text="AMOUNT")

expense_table.column("date", width=130, anchor="w")
expense_table.column("category", width=130, anchor="w")
expense_table.column("description", width=180, anchor="w")
expense_table.column("amount", width=140, anchor="e")

expense_table.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar = ttk.Scrollbar(
    table_container,
    orient="vertical",
    command=expense_table.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)

expense_table.configure(
    yscrollcommand=scrollbar.set
)


#Total
total_label = ttk.Label(
    transactions_content,
    text="Total: GHS 0.00",
    font=("Segoe UI", 16, "bold"),
    foreground=ACCENT,
    background=BG
)
total_label.pack(pady=10)


# Bottom Actions
action_frame = ttk.Frame(transactions_content)
action_frame.pack(
    fill="x",
    padx=40,
    pady=(5, 25)
)

summary_button = ttk.Button(
    action_frame,
    text="View Category Summary",
    command=show_category_summary
)

summary_button.pack(
    side="left",
    expand=True,
    fill="x",
    padx=(0, 8),
    ipady=5
)

export_button = ttk.Button(
    action_frame,
    text="Export to CSV",
    command=export_expenses
)

export_button.pack(
    side="left",
    expand=True,
    fill="x",
    padx=(8, 0),
    ipady=5
)


# KPI SUMMARY
kpi_frame = ttk.Frame(dashboard_page)
kpi_frame.pack(
    fill="x",
    padx=40,
    pady=(0, 30)
)

def create_kpi(parent, title, value):
    frame = tk.Frame(
        parent,
        bg=BG
    )

    kpi_title_label = tk.Label(
        frame,
        text=title.upper(),
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 9, "bold")
    )
    kpi_title_label.pack(anchor="w")

    value_label = tk.Label(
        frame,
        text=value,
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 22, "bold")
    )
    value_label.pack(
        anchor="w",
        pady=(5, 0)
    )

    return kpi_title_label, value_label


total_spent_title, total_spent_label = create_kpi(
    kpi_frame,
    "Total spent",
    "GHS 0.00"
)

monthly_title, monthly_label = create_kpi(
    kpi_frame,
    "This month",
    "GHS 0.00"
)

budget_left_title, budget_left_label = create_kpi(
    kpi_frame,
    "Budget left",
    "GHS 0.00"
)

transaction_count_title, transaction_count_label = create_kpi(
    kpi_frame,
    "Transactions",
    "0"
)

for column in range(4):
    kpi_frame.columnconfigure(
        column,
        weight=1
    )

total_spent_title.master.grid(
    row=0,
    column=0,
    sticky="w"
)

monthly_title.master.grid(
    row=0,
    column=1,
    sticky="w"
)

budget_left_title.master.grid(
    row=0,
    column=2,
    sticky="w"
)

transaction_count_title.master.grid(
    row=0,
    column=3,
    sticky="w"
)

budget_control = ttk.Frame(dashboard_page)
budget_control.pack(
    fill="x",
    padx=40,
    pady=(0, 25)
)

budget_info = ttk.Label(
    budget_control,
    text=f"Monthly budget: GHS {monthly_budget:,.2f}",
    style="Muted.TLabel"
)
budget_info.pack(side="left")

budget_progress = ttk.Progressbar(
    dashboard_page,
    style="Budget.Horizontal.TProgressbar",
    orient="horizontal",
    mode="determinate",
    maximum=100
)

budget_progress.pack(fill="x", padx=40, pady=(0, 5))

budget_percentage_label = ttk.Label(
    dashboard_page,
    text="0% used",
    style="Muted.TLabel"
)

budget_percentage_label.pack(
    anchor="e",
    padx=40,
    pady=(0, 20)
)


def open_budget_editor():
    global monthly_budget

    budget_window = tk.Toplevel(window)
    budget_window.title("Monthly Budget")
    budget_window.geometry("360x220")
    budget_window.resizable(False, False)
    budget_window.configure(bg=BG)

    ttk.Label(
        budget_window,
        text="Monthly budget",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(25, 5))

    ttk.Label(
        budget_window,
        text="Set the amount you want to spend each month.",
        style="Muted.TLabel"
    ).pack(pady=(0, 15))

    entry = ttk.Entry(
        budget_window,
        width=22
    )
    entry.insert(0, str(monthly_budget))
    entry.pack()

    def save_budget():
        global monthly_budget

        try:
            value = float(entry.get().strip())
        except ValueError:
            messagebox.showerror(
                "Invalid Budget",
                "Enter a valid amount."
            )
            return

        if value <= 0:
            messagebox.showerror(
                "Invalid Budget",
                "Budget must be greater than 0."
            )
            return

        monthly_budget = value
        settings["monthly_budget"] = value
        save_settings(settings)

        budget_info.config(
            text=f"Monthly budget: GHS {monthly_budget:,.2f}"
        )

        update_dashboard()
        budget_window.destroy()

    ttk.Button(
        budget_window,
        text="Save Budget",
        style="Accent.TButton",
        command=save_budget
    ).pack(pady=15)

ttk.Button(
    budget_control,
    text="Edit",
    command=open_budget_editor
).pack(side="left", padx=10)


# Dashboard Charts
charts_frame = ttk.Frame(dashboard_page)
charts_frame.pack(
    fill="both",
    expand=True,
    padx=40,
    pady=10
)

category_frame = ttk.Frame(charts_frame)
category_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 20)
)

trend_frame = ttk.Frame(charts_frame)
trend_frame.pack(
    side="left",
    fill="both",
    expand=True
)

ttk.Label(
    category_frame,
    text="Spending by category",
    style="Section.TLabel"
).pack(
    anchor="w",
    pady=(0, 10)
)

ttk.Label(
    trend_frame,
    text="Spending trend",
    style="Section.TLabel"
).pack(
    anchor="w",
    pady=(0, 10)
)


category_figure = Figure(
    figsize=(5, 3),
    dpi=100
)

category_ax = category_figure.add_subplot(111)

category_canvas = FigureCanvasTkAgg(
    category_figure,
    master=category_frame
)

category_canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)


trend_figure = Figure(
    figsize=(5, 3),
    dpi=100
)

trend_ax = trend_figure.add_subplot(111)

trend_canvas = FigureCanvasTkAgg(
    trend_figure,
    master=trend_frame
)

trend_canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)

def update_dashboard_charts():
    category_ax.clear()
    trend_ax.clear()

    category_ax.set_facecolor(BG)
    trend_ax.set_facecolor(BG)

    category_figure.patch.set_facecolor(BG)
    trend_figure.patch.set_facecolor(BG)

    # Spending by Category
    summary = category_summary(expenses)

    if summary:
        categories = list(summary.keys())
        amounts = list(summary.values())

        category_ax.bar(
            categories,
            amounts
        )


        category_ax.set_ylabel("GHS")
        category_ax.tick_params(
            axis="x",
            rotation=30
        )

        category_ax.grid(
            axis="y",
            alpha=0.2
        )

    else:
        category_ax.text(
            0.5,
            0.5,
            "No spending data yet",
            ha="center",
            va="center"
        )



    # Spending Trend
    daily_spending = defaultdict(float)

    for expense in expenses:
        date_string = expense.get("date")

        if date_string:
            daily_spending[date_string] += expense["amount"]

    if daily_spending:
        dates = sorted(daily_spending.keys())
        amounts = [
            daily_spending[date]
            for date in dates
        ]

        trend_ax.plot(
            dates,
            amounts,
            marker="o",
            linewidth=2
        )


        trend_ax.set_ylabel("GHS")

        trend_ax.grid(
            axis="y",
            alpha=0.2
        )

        trend_ax.tick_params(
            axis="x",
            rotation=30
        )

    else:
        trend_ax.text(
            0.5,
            0.5,
            "No spending data yet",
            ha="center",
            va="center"
        )

    category_figure.tight_layout()
    trend_figure.tight_layout()

    for ax in [category_ax, trend_ax]:
        ax.tick_params(
            colors=MUTED,
            labelsize=9
        )

        ax.xaxis.label.set_color(MUTED)
        ax.yaxis.label.set_color(MUTED)

        ax.title.set_color(TEXT)

        ax.spines["left"].set_color(BORDER)
        ax.spines["bottom"].set_color(BORDER)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    category_canvas.draw()
    trend_canvas.draw()


def apply_theme():
    global BG, CARD, TEXT, MUTED, BORDER
    global ACCENT, ACCENT_DARK, DANGER

    theme = DARK_THEME if dark_mode else LIGHT_THEME

    BG = theme["BG"]
    CARD = theme["CARD"]
    TEXT = theme["TEXT"]
    MUTED = theme["MUTED"]
    BORDER = theme["BORDER"]
    ACCENT = theme["ACCENT"]
    ACCENT_DARK = theme["ACCENT_DARK"]
    DANGER = theme["DANGER"]

    window.configure(bg=BG)

    style.configure(
        "TFrame",
        background=BG
    )

    style.configure(
        "TLabel",
        background=BG,
        foreground=TEXT
    )

    style.configure(
        "Title.TLabel",
        background=BG,
        foreground=TEXT
    )

    style.configure(
        "Subtitle.TLabel",
        background=BG,
        foreground=MUTED
    )

    style.configure(
        "Section.TLabel",
        background=BG,
        foreground=TEXT
    )

    style.configure(
        "Muted.TLabel",
        background=BG,
        foreground=MUTED
    )

    style.configure(
        "TEntry",
        fieldbackground=CARD,
        foreground=TEXT
    )

    style.configure(
        "TCombobox",
        fieldbackground=CARD,
        foreground=TEXT
    )

    style.configure(
        "Treeview",
        background=CARD,
        foreground=TEXT,
        fieldbackground=CARD
    )

    style.configure(
        "Treeview.Heading",
        background=BG,
        foreground=MUTED
    )

    style.configure(
        "Budget.Horizontal.TProgressbar",
        troughcolor=BORDER,
        background=ACCENT
    )

    transactions_canvas.configure(bg=BG)

    total_label.configure(
        background=BG,
        foreground=ACCENT
    )

    for widget in kpi_frame.winfo_children():
        widget.configure(bg=BG)

        for child in widget.winfo_children():
            child.configure(bg=BG)

    total_spent_title.configure(
        bg=BG,
        fg=MUTED
    )
    total_spent_label.configure(
        bg=BG,
        fg=TEXT
    )

    monthly_title.configure(
        bg=BG,
        fg=MUTED
    )
    monthly_label.configure(
        bg=BG,
        fg=TEXT
    )

    budget_left_title.configure(
        bg=BG,
        fg=MUTED
    )
    budget_left_label.configure(
        bg=BG,
        fg=TEXT
    )

    transaction_count_title.configure(
        bg=BG,
        fg=MUTED
    )
    transaction_count_label.configure(
        bg=BG,
        fg=TEXT
    )

    for ax in [category_ax, trend_ax]:
        ax.set_facecolor(BG)
        ax.figure.patch.set_facecolor(BG)

        ax.tick_params(colors=MUTED)
        ax.xaxis.label.set_color(MUTED)
        ax.yaxis.label.set_color(MUTED)

        ax.spines["left"].set_color(BORDER)
        ax.spines["bottom"].set_color(BORDER)

    category_canvas.draw()
    trend_canvas.draw()

    theme_button.config(
        text="☀ Light Mode" if dark_mode else "🌙 Dark Mode"
    )

def animate_budget_progress(target_value, current_value=None):
    if current_value is None:
        current_value = budget_progress["value"]

    difference = target_value - current_value

    if abs(difference) < 1:
        budget_progress["value"] = target_value
        return

    step = current_value + (difference * 0.15)

    budget_progress["value"] = step

    window.after(
        15,
        lambda: animate_budget_progress(
            target_value,
            step
        )
    )

def update_dashboard():
    total = calculate_total(expenses)

    current_month = datetime.today().strftime("%Y-%m")

    monthly_total = sum(
        expense["amount"]
        for expense in expenses
        if expense.get("date", "").startswith(current_month)
    )

    budget_left = monthly_budget - monthly_total

    total_spent_label.config(
        text=f"GHS {total:,.2f}"
    )

    monthly_label.config(
        text=f"GHS {monthly_total:,.2f}"
    )

    transaction_count_label.config(
        text=str(len(expenses))
    )

    budget_left_label.config(
        text=f"GHS {budget_left:,.2f}"
    )

    #Budget Progress
    if monthly_budget > 0:
        budget_percentage = (
            monthly_total / monthly_budget
        ) * 100
    else:
        budget_percentage = 0

    displayed_percentage = min(
        budget_percentage,
        100
    )

    animate_budget_progress(displayed_percentage)

    budget_percentage_label.config(
        text=f"{budget_percentage:.0f}% used"
    )

    if budget_percentage >= 100:
        budget_percentage_label.config(
            text=f"{budget_percentage:.0f}% used — Budget exceeded",
            foreground=DANGER
        )

    elif budget_percentage >= 75:
        budget_percentage_label.config(
            text=f"{budget_percentage:.0f}% used — Approaching budget",
            foreground=MUTED
        )

    else:
        budget_percentage_label.config(
            text=f"{budget_percentage:.0f}% used",
            foreground=MUTED
        )

    update_dashboard_charts()


#Start App
refresh_expense_list()
apply_theme()

window.mainloop()