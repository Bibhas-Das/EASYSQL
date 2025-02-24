from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
from termcolor import colored
from serverConnect import fetch_database_structure

# Read queries from the file
def read_queries(file_path):
    with open(file_path, 'r') as f:
        queries = [query.strip().upper() for query in f.read().split("\n") if query.strip()]
    return queries

# Tokenize queries into parts
def tokenize_queries(queries):
    tokenized_queries = []
    for query in queries:
        # Split query into parts (words, symbols, etc.)
        tokens = query.split()
        tokenized_queries.append(tokens)
    return tokenized_queries

# Find suggestions for the next word or part
def find_suggestions(tokenized_queries, input_tokens):
    suggestions = set()
    for tokens in tokenized_queries:
        # Check if the input tokens match the beginning of the query
        if len(tokens) > len(input_tokens) and all(tokens[i] == input_tokens[i] for i in range(len(input_tokens))):
            suggestions.add(tokens[len(input_tokens)])
    return list(suggestions)

class SQLCompleter(Completer):
    """
    Custom completer for SQL query suggestions.
    """
    def __init__(self, tokenized_queries):
        self.tokenized_queries = tokenized_queries

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.upper()
        input_tokens = text.split()
        
        # Find suggestions for the next word or part
        suggestions = find_suggestions(self.tokenized_queries, input_tokens)
        
        # Display the top 5 suggestions
        for suggestion in suggestions[:5]:
            yield Completion(suggestion, start_position=-len(input_tokens[-1]) if input_tokens else 0)

def main():
    # Read and tokenize queries
    queries = read_queries("queries.txt")
    tokenized_queries = tokenize_queries(queries)
    
   
    print("Start typing your SQL query (Ctrl+C to exit):")
    while True:
        try:
            # Use prompt_toolkit to capture input with real-time suggestions
            user_input = prompt(
                "> ",
                completer=SQLCompleter(tokenized_queries),
                complete_style=CompleteStyle.MULTI_COLUMN,
            )
            # Print the final input when Enter is pressed
            print(f"You typed: {user_input}")
            break
        except KeyboardInterrupt:
            # Exit gracefully on Ctrl+C
            print("\nExiting...")
            break
    
if __name__ == "__main__":
    main()