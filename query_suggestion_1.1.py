from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
from termcolor import colored
from serverConnect import fetch_database_structure

def read_queries(file_path):
    with open(file_path, 'r') as f:
        queries = [query.strip().upper() for query in f.read().split("\n") if query.strip()]
    return queries

def tokenize_queries(queries):
    tokenized_queries = []
    for query in queries:
        tokens = query.split()
        tokenized_queries.append(tokens)
    return tokenized_queries

def find_suggestions(tokenized_queries, completed_tokens, current_word):
    suggestions = set()
    current_word = current_word.upper()
    for tokens in tokenized_queries:
        if len(tokens) > len(completed_tokens):
            if tokens[:len(completed_tokens)] == completed_tokens:
                next_token = tokens[len(completed_tokens)]
                if next_token.startswith(current_word):
                    suggestions.add(next_token)
    return list(suggestions)

class SQLCompleter(Completer):
    def __init__(self, tokenized_queries):
        self.tokenized_queries = tokenized_queries

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor.upper()
        
        last_space_pos = text_before_cursor.rfind(' ')
        if last_space_pos == -1:
            completed_tokens = []
            current_word = text_before_cursor
        else:
            completed_part = text_before_cursor[:last_space_pos]
            completed_tokens = completed_part.split()
            current_word = text_before_cursor[last_space_pos+1:]
        
        suggestions = find_suggestions(self.tokenized_queries, completed_tokens, current_word)
        
        for suggestion in suggestions[:5]:
            yield Completion(suggestion, start_position=-len(current_word))

def main():
    queries = read_queries("generalize_queries.txt")
    tokenized_queries = tokenize_queries(queries)
    
    print("Start typing your SQL query (Ctrl+C to exit):")
    while True:
        try:
            user_input = prompt(
                "> ",
                completer=SQLCompleter(tokenized_queries),
                complete_style=CompleteStyle.MULTI_COLUMN,
            )
            print(f"You typed: {user_input}")
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
    
if __name__ == "__main__":
    main()