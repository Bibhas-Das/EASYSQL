import tkinter as tk
from tkinter import ttk

# Predefined SQL suggestions
sql_suggestions = {
    "SELECT * FROM": ["SELECT * FROM users WHERE age > 25;", "SELECT * FROM employees ORDER BY name ASC;"],
    "SELECT name FROM": ["SELECT name FROM employees WHERE department = 'HR';"],
    "INSERT INTO": ["INSERT INTO users (id, name) VALUES (1, 'John');"],
    "DELETE FROM": ["DELETE FROM users WHERE id = 1;"],
    "UPDATE": ["UPDATE users SET age = 30 WHERE id = 1;"]
}

def get_query_length(query: str) -> int:
    """Returns the length of the given SQL query."""
    return len(query)

def update_suggestions(event):
    """Updates the dropdown menu based on user input."""
    user_query = query_input.get()
    half_length = len(user_query) // 2
    query_half = user_query[:half_length]

    dropdown_menu["values"] = []  # Clear previous suggestions

    for key in sql_suggestions:
        if query_half.strip().startswith(key):
            dropdown_menu["values"] = sql_suggestions[key]  # Update suggestions

def apply_suggestion(event):
    """Inserts the selected suggestion into the input field."""
    query_input.delete(0, tk.END)
    query_input.insert(0, dropdown_menu.get())

# GUI Window
root = tk.Tk()
root.title("SQL Autocomplete Tool")
root.geometry("600x200")

# Input Field
query_input = tk.Entry(root, width=60, font=("Arial", 12))
query_input.pack(pady=20)
query_input.bind("<KeyRelease>", update_suggestions)  # Update dropdown on typing

# Dropdown Menu
dropdown_menu = ttk.Combobox(root, width=80)
dropdown_menu.pack(pady=10)
dropdown_menu.bind("<<ComboboxSelected>>", apply_suggestion)

# Run GUI
root.mainloop()
