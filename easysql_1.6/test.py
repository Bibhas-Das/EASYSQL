# from prompt_toolkit import PromptSession
# from prompt_toolkit.validation import Validator
# from prompt_toolkit.key_binding import KeyBindings

# # Custom key bindings for real-time modification
# bindings = KeyBindings()

# @bindings.add(' ')
# def auto_uppercase(event):
#     buffer = event.app.current_buffer
#     text = buffer.text.lower()
#     keywords = ['select', 'from', 'where', 'insert', 'update', 'delete']
#     words = text.split()
    
#     if words:
#         last_word = words[-1]
#         if last_word in keywords:
#             new_text = ' '.join(words[:-1] + [last_word.upper()]) + ' '
#             print(f"Before: {buffer.text}")
#             print(f"Cursor Position: {buffer.cursor_position}")
#             buffer.text = new_text
#             buffer.cursor_position = len(new_text)
#             print(f"After: {buffer.text}")
#             print(f"Cursor Position: {buffer.cursor_position}")

# # Validator for basic SQL syntax
# sql_validator = Validator.from_callable(
#     lambda text: any(text.upper().startswith(kw) for kw in ('SELECT', 'INSERT', 'UPDATE', 'DELETE')),
#     error_message='Must start with SELECT/INSERT/UPDATE/DELETE',
#     move_cursor_to_end=True
# )

# # Create prompt session
# session = PromptSession(
#     key_bindings=bindings,
#     #validator=sql_validator,
#     #validate_while_typing=True
# )

# def main():
#     while True:
#         try:
#             query = session.prompt('SQL> ')
#             print(f"Final query: {query}")

#         except KeyboardInterrupt:
#             break

# if __name__ == "__main__":
#     main()





# from prompt_toolkit import PromptSession
# from prompt_toolkit.key_binding import KeyBindings

# # Custom key bindings for real-time modification
# bindings = KeyBindings()


# @bindings.add('(')
# def add_space_after_open_paren(event):
#     """Add a space after '('"""
#     buffer = event.app.current_buffer
#     buffer.insert_text('(')
#     buffer.insert_text(' ')
#     buffer.cursor_position = len(buffer.text)


# # Create prompt session
# session = PromptSession(key_bindings=bindings)

# def main():
#     while True:
#         try:
#             query = session.prompt('SQL> ')
#             print(f"Final query: {query}")

#         except KeyboardInterrupt:
#             break

# if __name__ == "__main__":
    # main()











# import re
# from prompt_toolkit import prompt
# from prompt_toolkit.key_binding import KeyBindings
# from prompt_toolkit.completion import Completer, Completion
# from prompt_toolkit.styles import Style
# from prompt_toolkit.history import FileHistory
# from prompt_toolkit.validation import Validator
# from prompt_toolkit.key_binding import KeyBindings
# from prompt_toolkit.shortcuts import CompleteStyle

# # Custom SQL keywords
# sql_keywords = {
#     "ADD", "ALL", "ALTER", "AND", "ANY", "AS", "ASC", "BACKUP", "BETWEEN", "CASE", "CHECK", "COLUMN",
#     "CONSTRAINT", "CREATE", "DATABASE", "DEFAULT", "DELETE", "DESC", "DISTINCT", "DROP", "EXEC", "EXISTS", "FOREIGN",
#     "FROM", "FULL", "GROUP", "HAVING", "IN", "INDEX", "INNER", "INSERT", "INTO", "IS", "JOIN", "KEY", "LEFT", "LIKE",
#     "LIMIT", "NOT", "NULL", "OR", "ORDER", "OUTER", "PRIMARY", "PROCEDURE", "RIGHT", "ROWNUM", "SELECT", "SET", 
#     "TABLE", "TOP", "TRUNCATE", "UNION", "UNIQUE", "UPDATE", "VALUES", "VIEW", "WHERE"
# }

# def is_keywords(token: str) -> bool:
#     """Returns True if the token is an SQL reserved keyword."""
#     return token.upper() in sql_keywords

# # Key bindings for handling spaces after keywords and parentheses
# bindings = KeyBindings()

# @bindings.add('(')
# def add_space_after_open_paren(event):
#     """Automatically add a space after the opening parenthesis."""
#     buffer = event.app.current_buffer
#     # Get the last word before the '(' to check if it's a SQL keyword or function
#     text_before_paren = buffer.document.text_before_cursor.strip()
#     if text_before_paren and (is_keywords(text_before_paren) or text_before_paren[-1] == '('):
#         # Insert a space after the opening parenthesis
#         buffer.insert_text(' ( ')
#     else:
#         buffer.insert_text('(')
#     buffer.cursor_position = len(buffer.text)  # Move the cursor to the end

# # Function to condense multiple spaces to a single space
# def condense_spaces(text: str) -> str:
#     return re.sub(r'\s+', ' ', text)

# # Custom validator (if needed) to ensure valid SQL syntax while typing
# class SQLValidator(Validator):
#     def validate(self, document):
#         # Implement your validation logic here, for now we can keep it simple
#         pass

# # SQL Completer (you can customize it further)
# class SQLCompleter(Completer):
#     def get_completions(self, document, complete_event):
#         # Implement your SQL keyword completion logic here
#         return ['SELECT','FORM']
#         pass

# # Example of the style
# custom_style = Style.from_dict({
#     '': '#ff0066',
#     'rprompt': '#00ff00',
# })

# # Function to prompt and sanitize user input in real-time
# def get_sql_input():
#     user_input = prompt(
#         "╭─ SQL ➤ $ ",
#         rprompt=" " * 50,  # Padding on the right
#         completer=SQLCompleter(),  # Use the SQL completer
#         complete_style=CompleteStyle.MULTI_COLUMN,
#         complete_while_typing=True,  # Enable completions while typing
#         history=FileHistory("history.txt"),
#         style=custom_style,
#         validator=SQLValidator(),
#         validate_while_typing=True,
#         key_bindings=bindings
#     )

#     # Condense any multiple spaces to a single space
#     return condense_spaces(user_input)

# # Example usage
# if __name__ == "__main__":
#     result = get_sql_input()
#     print("Sanitized Input:", result)










# from prompt_toolkit import prompt
# from prompt_toolkit.key_binding import KeyBindings
# from prompt_toolkit.completion import Completer, Completion

# # List of previous queries (this could come from your database, file, or other sources)
# previous_queries = [
#     "SELECT * FROM users;",
#     "SELECT name, age FROM employees WHERE age > 30;",
#     "SELECT id, product_name FROM products ORDER BY price DESC;"
# ]

# # Create key bindings
# bindings = KeyBindings()

# # Custom Completer to suggest previous queries
# class QueryCompleter(Completer):
#     def get_completions(self, document, complete_event):
#         # If the document starts with "SELECT", suggest previous queries
#         if document.text.upper().startswith("SELECT"):
#             for query in previous_queries:
#                 yield Completion(query, start_position=-len(document.text))

# # Create the prompt with the custom completer
# def query_input():
#     query_completer = QueryCompleter()
    
#     user_input = prompt(
#         "Enter SQL query: ",
#         completer=query_completer,
#         key_bindings=bindings
#     )
    
#     print(f'You entered: {user_input}')
    
# # Handle key bindings for cursor movement when typing "SELECT"
# @bindings.add('space')  # We can monitor space or any other key, like backspace or enter
# def on_typing(event):
#     buffer = event.app.current_buffer
#     user_input = buffer.text.strip()  # Get the current input

#     # If the user types "SELECT", jump to the beginning of the query
#     if user_input.upper().endswith("SELECT"):
#         buffer.cursor_position = 0  # Move the cursor to the beginning

# # Call the function to start prompt
# query_input()













# from tabulate import tabulate
# from colorama import Fore, Back, Style, init

# # Initialize colorama
# init(autoreset=True)

# # Define the table data
# data = [
#     [Fore.GREEN + "Apple" + Style.RESET_ALL, Fore.RED + "Red" + Style.RESET_ALL, 10],
#     [Fore.YELLOW + "Banana" + Style.RESET_ALL, Fore.YELLOW + "Yellow" + Style.RESET_ALL, 5],
#     [Fore.BLUE + "Blueberry" + Style.RESET_ALL, Fore.BLUE + "Blue" + Style.RESET_ALL, 20],
#     [Fore.MAGENTA + "Grape" + Style.RESET_ALL, Fore.MAGENTA + "Purple" + Style.RESET_ALL, 15],
# ]

# # Define the table headers
# headers = [Fore.CYAN + "Fruit" + Style.RESET_ALL, Fore.CYAN + "Color" + Style.RESET_ALL, Fore.CYAN + "Quantity" + Style.RESET_ALL]

# # Create the table with colorful formatting
# table = tabulate(data, headers, tablefmt="grid", numalign="center", stralign="center")

# # Add some margin around the table
# margin = " " * 4
# table_with_margin = "\n".join(margin + line for line in table.split("\n"))

# # Print the colorful table
# print(table_with_margin)









# from rich.console import Console
# from rich.table import Table

# # Initialize a Console object
# console = Console()

# # Create a Table object
# table = Table(title="A Fancy Table", show_header=True, header_style="bold magenta")

# # Add columns
# table.add_column("Company", style="cyan", justify="left")
# table.add_column("Contact", style="cyan", justify="left")
# table.add_column("Country", style="cyan", justify="left")

# # Add rows with different background colors
# table.add_row("Alfreds Futterkiste", "Maria Anders", "Germany", style="on bright_blue")
# table.add_row("Berglunds snabbköp", "Christina Berglund", "Sweden", style="on bright_green")
# table.add_row("Centro comercial Moctezuma", "Francisco Chang", "Mexico", style="on bright_yellow")
# table.add_row("Ernst Handel", "Roland Mendel", "Austria", style="on bright_magenta")
# table.add_row("Island Trading", "Helen Bennett", "UK", style="on bright_cyan")
# table.add_row("Königlich Essen", "Philip Cramer", "Germany", style="on bright_red")
# table.add_row("Laughing Bacchus Winecellars", "Yoshi Tannamuri", "Canada", style="on bright_white")
# table.add_row("Magazzini Alimentari Riuniti", "Giovanni Rovelli", "Italy", style="on bright_black")
# table.add_row("North/South", "Simon Crowther", "UK", style="on bright_blue")
# table.add_row("Paris spécialités", "Marie Bertrand", "France", style="on bright_green")

# # Print the table to the console
# console.print(table)















# from rich.console import Console
# from rich.table import Table

# console = Console()

# # Create a table
# table = Table(title="A Fancy Table", show_header=True, header_style="bold green")

# # Add columns
# table.add_column("Company", style="cyan")
# table.add_column("Contact", style="magenta")
# table.add_column("Country", style="yellow")

# # Add rows
# table.add_row("Alfreds Futterkiste", "Maria Anders", "Germany")
# table.add_row("Berglunds snabbköp", "Christina Berglund", "Sweden")
# table.add_row("Centro comercial Moctezuma", "Francisco Chang", "Mexico")
# table.add_row("Ernst Handel", "Roland Mendel", "Austria")
# table.add_row("Island Trading", "Helen Bennett", "UK")
# table.add_row("Königlich Essen", "Philip Cramer", "Germany")
# table.add_row("Laughing Bacchus Winecellars", "Yoshi Tannamuri", "Canada")
# table.add_row("Magazzini Alimentari Riuniti", "Giovanni Rovelli", "Italy")
# table.add_row("North/South", "Simon Crowther", "UK")
# table.add_row("Paris spécialités", "Marie Bertrand", "France")

# # Print the table
# console.print(table)
















# from rich.console import Console
# from rich.table import Table

# # Initialize a Console object
# console = Console()

# # Create a Table object
# table = Table(title="Output", show_header=True, header_style="black on bright_yellow")

# # Add columns with styling
# table.add_column("Company", style="bold cyan", justify="left")
# table.add_column("Contact", style="bold magenta", justify="left")
# table.add_column("Country", style="bold yellow", justify="left")

# # Add rows with alternating background colors
# rows = [
#     ("Alfreds Futterkiste", "Maria Anders", "Germany"),
#     ("Berglunds snabbköp", "Christina Berglund", "Sweden"),
#     ("Centro comercial Moctezuma", "Francisco Chang", "Mexico"),
#     ("Ernst Handel", "Roland Mendel", "Austria"),
#     ("Island Trading", "Helen Bennett", "UK"),
#     ("Königlich Essen", "Philip Cramer", "Germany"),
#     ("Laughing Bacchus Winecellars", "Yoshi Tannamuri", "Canada"),
#     ("Magazzini Alimentari Riuniti", "Giovanni Rovelli", "Italy"),
#     ("North/South", "Simon Crowther", "UK"),
#     ("Paris spécialités", "Marie Bertrand", "France"),
# ]

# # Add rows with alternating background colors
# for i, row in enumerate(rows):
#     if i % 2 == 0:
#         # Even rows: white background with black text
#         table.add_row(*row, style="black on white")
#     else:
#         # Odd rows: light black background with white text
#         table.add_row(*row, style="white on grey23")  # grey23 is a light black color

# # Print the table to the console
# console.print(table)






