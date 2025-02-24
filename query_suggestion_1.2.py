from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
import re

def read_queries(file_path:str)->list[str]:
    with open(file_path, 'r') as f:
        queries = [query.strip().upper() for query in f.read().split("\n") if query.strip()]
    return queries

def tokenize_queries(queries:list[str])->list[list[str]]:
    """ Tokenizes queries into lists of words """
    tokenized_queries = []
    for query in queries:
        tokens = query.split()
        tokenized_queries.append(tokens)
    return tokenized_queries

def is_placeholder(word:str)->bool:
    """ Checks if a word is a placeholder (like [field1], [table], [value]) """
    return bool(re.match(r'\[.*?\]', word))  # Matches words enclosed in []

def find_suggestions(tokenized_queries:list[list[str]], completed_tokens:list[str], current_word:str)->list[str]:
    #print(f"\nCall : {completed_tokens}, {current_word}")
    """ Finds next possible words for autocompletion """
    suggestions = set()
    current_word = current_word.upper()

    for tokens in tokenized_queries:
        #token: each line [toknized]
        if len(tokens) > len(completed_tokens):
            #here it should be modified...[filed1]...[value]..[table] should be ignore in tokenized_quries 
        
            if tokens[:len(completed_tokens)] == completed_tokens:
                next_token = tokens[len(completed_tokens)]

                # If it's a placeholder, allow user to type anything and still suggest the next keyword
                if is_placeholder(next_token):
                    next_token = "[value]"  # Show a generic placeholder instead

                # Suggest only if it starts with current_word
                if next_token.startswith(current_word) or is_placeholder(next_token):
                    suggestions.add(next_token)

    return list(suggestions)

class SQLCompleter(Completer):
    def __init__(self, tokenized_queries:list[list[str]])->None:
        self.tokenized_queries = tokenized_queries

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor.upper()
        #print(f"({text_before_cursor})")

        last_space_pos = text_before_cursor.rfind(' ')
        #print(f"last_space : {last_space_pos}")

        if last_space_pos == -1:
            completed_tokens = []
            current_word = text_before_cursor
        else:
            completed_part = text_before_cursor[:last_space_pos]
            completed_tokens = completed_part.split()
            current_word = text_before_cursor[last_space_pos+1:]

        suggestions = find_suggestions(self.tokenized_queries, completed_tokens, current_word)
        #print(f"\n{suggestions}")

        for suggestion in suggestions:  # Limit suggestions
            yield Completion(suggestion, start_position=-len(current_word))

def main()->None:
    queries = read_queries("generalize_queries.txt")
    tokenized_queries = tokenize_queries(queries)
    #print(tokenized_queries)

    print("Start typing your SQL query (Ctrl+C to exit):")
    while True:
        try:
            user_input = prompt(
                "> ",
                completer=SQLCompleter(tokenized_queries),
                complete_style=CompleteStyle.MULTI_COLUMN,
            )
            print(f"You typed: {user_input}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
