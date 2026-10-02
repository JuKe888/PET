import json
from datetime import date, datetime

def save_expenses(expenses):
    with open("expenses.json", "w") as f:
        json.dump(expenses, f, indent=4)


def load_expenses():
    try:
        with open("expenses.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def create_expense(amount, category, description, expense_date=None):
    if not amount or not category or not description:
        return None

    try:
        amount = float(amount)
    except ValueError:
        return None

    if amount <= 0:
        return None

    if not expense_date:
        expense_date = date.today().isoformat()

    try:
        entered_date = datetime.strptime(
            expense_date,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return None

    if entered_date > date.today():
        return None

    return {
        "amount": amount,
        "category": category,
        "description": description,
        "date": expense_date
    }


def calculate_total(expenses):
    total = 0

    for expense in expenses:
        total += expense["amount"]

    return total


def category_summary(expenses):
    summary = {}

    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]

        if category in summary:
            summary[category] += amount
        else:
            summary[category] = amount

    return summary


def filter_expenses(expenses, search_text):
    search_text = search_text.strip().lower()

    if not search_text:
        return list(range(len(expenses)))

    matching_indices = []

    for index, expense in enumerate(expenses):
        if (
            search_text in expense["category"].lower()
            or search_text in expense["description"].lower()
        ):
            matching_indices.append(index)

    return matching_indices


def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)


def load_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "monthly_budget": 2000
        }

