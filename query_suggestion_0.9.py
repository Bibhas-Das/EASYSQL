import tkinter as tk
from tkinter import ttk

# Predefined SQL queries
queries = [
    "SELECT * FROM students;",
    "SELECT name, age FROM students;",
    "SELECT * FROM students WHERE age > 18;",
    "INSERT INTO students (id, name, age) VALUES (1, 'Sayak', 22);",
    "UPDATE students SET age = 23 WHERE id = 1;",
    "DELETE FROM students WHERE id = 1;"
]

def check_partial_query(event):
    user_input = query_entry.get().strip().upper()
    
    # Detect if the user starts typing "SELECT * FROM"
    if user_input.startswith("SELECT * FROM") and len(user_input.split()) == 3:
        suggestion_menu["values"] = ["Write the table name here..."]
        query_var.set("Write the table name here...")
    else:
        suggestions = []
        for query in queries:
            query_upper = query.upper()
            
            # Check if the user has typed at least 50% of a query
            if len(user_input) >= len(query_upper) * 0.5 and user_input in query_upper:
                suggestions.append(query)

        # Update dropdown suggestions
        suggestion_menu["values"] = suggestions if suggestions else ["No suggestions"]
        if suggestions:
            query_var.set(suggestions[0])  # Auto-select first suggestion

def use_suggestion():
    query_entry.delete(0, tk.END)
    query_entry.insert(0, query_var.get())

# Create main window
root = tk.Tk()
root.title("SQL Query Helper")
root.geometry("600x300")

# Label
tk.Label(root, text="Type your SQL Query:", font=("Arial", 12)).pack(pady=10)

# Query Input Box
query_entry = tk.Entry(root, font=("Arial", 12), width=50)
query_entry.pack(pady=5)
query_entry.bind("<KeyRelease>", check_partial_query)  # Detect user input

# Suggestion Dropdown
query_var = tk.StringVar()
suggestion_menu = ttk.Combobox(root, textvariable=query_var, width=50)
suggestion_menu.pack(pady=5)

# Button to use suggestion
tk.Button(root, text="Use Suggestion", command=use_suggestion, font=("Arial", 10)).pack(pady=5)

# Run the GUI
root.mainloop()