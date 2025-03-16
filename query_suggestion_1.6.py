from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator
from prompt_toolkit.key_binding import KeyBindings

import re
import shutil
import os

from serverConnect import serverConnect
from check_syntax import checkSyntax
from score_manage import score_manage
from getChracter import getChracter
from showOutput import showOutput


TABLE_USED:list[str]=[]


# Get terminal width dynamically
terminal_width = shutil.get_terminal_size().columns


def remove_duplicates(List):
    seen = set()
    return [x for x in List if not (x in seen or seen.add(x))]

def is_keywords(token:str)->bool:
    #if token is belongs from sql reserv keywords then retun true else flase
    sql_keywords = {
    "ADD", "ALL", "ALTER", "AND", "ANY", "AS", "ASC", "BACKUP", "BETWEEN", "CASE", "CHECK", "COLUMN",
    "CONSTRAINT", "CREATE", "DATABASE", "DEFAULT", "DELETE", "DESC", "DISTINCT", "DROP", "EXEC", "EXISTS", "FOREIGN",
    "FROM", "FULL", "GROUP", "HAVING", "IN", "INDEX", "INNER", "INSERT", "INTO", "IS", "JOIN", "KEY", "LEFT", "LIKE",
    "LIMIT", "NOT", "NULL", "OR", "ORDER", "OUTER", "PRIMARY", "PROCEDURE", "RIGHT", "ROWNUM", "SELECT", "SET", 
    "TABLE", "TOP", "TRUNCATE", "UNION", "UNIQUE", "UPDATE", "VALUES", "VIEW", "WHERE"}

    token = token.strip()
    if token[0]=='(' and len(token)>1:
        #token = re.sub(r'(', '' ,token)
        token = token[1:]
        ...
    return True if token in sql_keywords else False
    ...


def read_queries(file_path:str)->list[str]:
    queries=""
    if os.path.exists(file_path):
        #read the text file 
        with open(file_path, 'r') as f:
            text = f.read()
        #Then remove all redundent symbols
        pattern = r'[;$#`\--]'
        text = re.sub(pattern, '', text)
        #then finaly break them all small token based on the space
        queries = [query.strip().upper() for query in text.split("\n") if query.strip()]
    return queries if queries else ""

def tokenize_queries(queries:list[str])->list[list[str]]:
    #Tokenizes queries into lists of words
    tokenized_queries = []
    for query in queries:
        tokens = query.split()
        tokenized_queries.append(tokens)
    return tokenized_queries if tokenized_queries else []

def is_placeholder(word:str)->bool:
    #Checks if a word is a placeholder (like [field1], [table], [value])
    return bool(re.match(r'\[.*?\]', word))  # Matches words enclosed in []

def is_field_required(word:str)->str:
    ...

def suggestActualTable(suggestions:list[str],tables:list[str])->list[str]:
    #print(f"in the function {suggestions} {tables}")
    if '[TABLE]' in suggestions:
        #print(f"in the function {suggestions} {tables}")
        suggestions.extend(tables)
        suggestions.remove('[TABLE]')
    return suggestions if suggestions else []
    ...

def suggestActualFields(suggestions:list[str],fields:dict[str:list[str]])->list[str]:
    #print(f"in the function {suggestions} {fields}")
    if '[FIELD]' in suggestions:
        #print('fileds are added')
        #print(f"in the function {suggestions} {fields}")
        for table, _fields in fields.items():
            suggestions.extend(_fields)
        suggestions.remove('[FIELD]')
    return suggestions if suggestions else []
    ...

def suggestSubqueries(suggestions:list[str])->list[str]:
    if any(re.search(r'\[VALUE\]\S*', word) or word == 'VALUES' for word in suggestions):
        #then here select subquery can be add
        suggestions.append('(SELECT')
    return suggestions
    ...


def remove_immidiate_used_token_from_suggestion(completed_tokens:list[str],suggestions:list[str])->list[str]:
    #print(f"completed tokens : {completed_tokens}")
    if completed_tokens and completed_tokens[-1] in suggestions:
        suggestions.remove(completed_tokens[-1])
    return suggestions if suggestions else []
    ...

#retuns true even the variables like r'\[.*?\]' present in the query
#return false if other tokens is not matched
def is_token_matched_without_variables(tokens:list[str],completed_tokens:list[str])->bool:
    index = 0
    # print(tokens[0])
    for token in tokens[:len(completed_tokens)]:
        if is_placeholder(token) and not is_keywords(completed_tokens[index].upper()):
            index+=1
            continue
        if token != completed_tokens[index].upper():
            return False
        index+=1
    return True


def find_suggestions(tokenized_queries: list[list[str]], completed_tokens: list[str], current_word: str, database_schema: dict[str, dict[str, list[str]]]) -> list[str]:
    """ Finds next possible words for autocompletion """

    #creating object of score_manager.py file
    score = score_manage(database_schema)

    suggestions = list()
    current_word = current_word.upper()

    for tokens in tokenized_queries:
        #token: each line [toknized]
        if len(tokens) > len(completed_tokens):
            #here it should be modified...[filed1]...[value]..[table] should be ignore in tokenized_quries 
            #print(f"\n{is_token_matched_without_variables(tokens,completed_tokens)}")
            #if tokens[:len(completed_tokens)] == completed_tokens:
            if is_token_matched_without_variables(tokens, completed_tokens):
                next_token = tokens[len(completed_tokens)]

                # If it's a placeholder, allow user to type anything and still suggest the next keyword
                #if is_placeholder(next_token):
                #    next_token = "[value]"  # Show a generic placeholder instead

                
                '''
                if suggested_tables:
                    print(" Here")
                    # If suggestActualTable returns a list, add all valid items
                    if isinstance(suggested_tables, list):
                        for token in suggested_tables:
                            if isinstance(token, str) and (token.startswith(current_word) or is_placeholder(token)):
                                suggestions.add(token)
                    elif isinstance(suggested_tables, str):
                        if suggested_tables.startswith(current_word) or is_placeholder(suggested_tables):
                            suggestions.add(suggested_tables)
                '''

                # Suggest only if it starts with current_word
                if next_token.startswith(current_word) or is_placeholder(next_token):
                    suggestions.append(next_token)

                #if '[FIELD]' in suggestions and '[TABLE];' in suggestions and '[FIELD]' in suggestions:
                #    #print("THat is")
                #    print(f"\n{tokens}\n")    

    suggestions = remove_duplicates(suggestions)

    #if any token is alreay is completed then it can't be place imidiate after that
    #it will return rest suggestions
    # Remove immediate used tokens
    suggestions = remove_immidiate_used_token_from_suggestion(completed_tokens, suggestions)

    # Ensure we get actual table names instead of [TABLE]
    suggestions = suggestActualTable(suggestions, database_schema.keys())

    # Ensure we get actal fileds name instead of [FILED]
    #first we need to make it in form : dict[str:list[str]] from dict[str:dict[str:list[str]]]
    new_schema = { _table: list(_field.keys()) for _table, _field in database_schema.items() }
    suggestions = suggestActualFields(suggestions, new_schema)                             

    suggestions = suggestSubqueries(suggestions) #it will give suggestion of select .. starting sub queries...
    
    #rearranging accorind thier score of  most uses
    #suggestions = score.arrangeSuggestions(suggestions)

    #print(f"\nCompleted token list : {completed_tokens}")

    #print(f"\nCurrent word : {current_word}")
    if completed_tokens and not current_word: #and completed_tokens[-1] in suggestions:
        #print(f"last used token : {completed_tokens[-1]}")
        score.updateScore(completed_tokens[-1])

    return suggestions if suggestions else []











class SQLCompleter(Completer):
    def __init__(self, tokenized_queries:list[list[str]],database_schema)->None:
        self.tokenized_queries = tokenized_queries
        self.database_schema = database_schema
        self.show_all_tables = False  # Track whether to show all tables
        self.show_all_fields = False  # Track whether to show all fields
        self.show_all_functions = False  # Track whether to show all functions
        self.query_type = 'UNKNOWN' #DDL: create drop,  DML: insert update delete, DQL: select, TCL: grant revoke
    
    
    # Function to format suggestions within terminal width
    def format_suggestions(self,label, items):
        if not items:
            return None
        suggestion_text = f"{label}: " + " ".join(f"[{item}]" for item in items)
        return suggestion_text[:terminal_width]  # Trim if exceeding width

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
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

        #detect which type of query is tyeping by user
        if completed_tokens:
            first_token = completed_tokens[0].upper()
            if first_token == 'SELECT':
                self.query_type = 'DQL'  # Data Query Language
            elif first_token in ('DELETE', 'UPDATE', 'INSERT'):
                self.query_type = 'DML'  # Data Manipulation Language
            #elif first_token in ('CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'COMMENT', 'RENAME'):
            #    self.query_type = 'DDL'  # Data Definition Language
            #elif first_token in ('GRANT', 'REVOKE'):
            #    self.query_type = 'DCL'  # Data Control Language
            #elif first_token in ('COMMIT', 'ROLLBACK', 'SAVEPOINT', 'SET TRANSACTION'):
            #    self.query_type = 'TCL'  # Transaction Control Language
            else:
                self.query_type = 'UNKNOWN'  # For any unclassified or incorrect commands
        else:
            self.query_type = 'UNKNOWN'
        #print(self.query_type)


        suggestions = find_suggestions(self.tokenized_queries, completed_tokens, current_word,self.database_schema)
        
        
        #print(f"\n{suggestions}")

        #for suggestion in suggestions:  # Limit suggestions
        #    yield Completion(suggestion, start_position=-len(current_word))




        #########################################################################################################################################################

        # tables = []
        # fields = []
        # functions = []
        
        # for suggestion in suggestions:
        #     if suggestion in self.database_schema:  # If it's a table name
        #         tables.append(suggestion)
        #     elif any(suggestion in columns for columns in self.database_schema.values()):  # If it's a field name
        #         fields.append(suggestion)
        #     else:  # Otherwise, assume it's a function
        #         functions.append(suggestion)

        # # If there are any categorized suggestions, display only those
        # if tables or fields or functions:
        #     if tables:
        #         yield Completion(f"TBL: {' '.join(f'[{t}]' for t in tables[:6])}", start_position=-len(current_word), display_meta="Category")
        #     if fields:
        #         yield Completion(f"FLD: {' '.join(f'[{f}]' for f in fields[:6])}", start_position=-len(current_word), display_meta="Category")
        #     if functions:
        #         yield Completion(self.format_suggestions("FUN", functions[:6]), start_position=-len(current_word), display_meta="Category")
        #         #yield Completion(f"FUN: {' '.join(f'[{func}]' for func in functions)}", start_position=-len(current_word), display_meta="Category")
        # else:
        #     # If no category is needed, yield individual suggestions
        #     for suggestion in suggestions:
        #         yield Completion(suggestion, start_position=-len(current_word))

        #########################################################################################################################################################

        tables = []
        fields = []
        functions = []

        for suggestion in suggestions:
            if suggestion in self.database_schema:  # If it's a table name
                tables.append(suggestion)
            elif any(suggestion in columns for columns in self.database_schema.values()):  # If it's a field name
                fields.append(suggestion)
            else:  # Otherwise, assume it's a function
                functions.append(suggestion)

        score = score_manage(self.database_schema)

        # If there are any categorized suggestions, display only those
        if tables or fields or functions:
            if tables:
                #for table in score.arrangeSuggestions(tables)[:8]:
                #    yield Completion(table, start_position=-len(current_word), style="bg:lightpink", selected_style="fg:white bg:blue", display_meta="Table")
                #yield Completion(text="[More]", style="bg:lightpink", selected_style="fg:white bg:blue", display_meta="More Tables") 


                if self.show_all_tables:
                    # Show all tables if "More" was selected
                    for table in score.arrangeSuggestions(tables):
                        yield Completion(table, start_position=-len(current_word), style="bg:lightpink", selected_style="fg:white bg:blue", display_meta="Table",)
                else:
                    # Show only the first 8 tables
                    for table in score.arrangeSuggestions(tables)[:8]:
                        yield Completion(table,start_position=-len(current_word),style="bg:lightpink",selected_style="fg:white bg:blue",display_meta="Table")
                    # Add "[More]" option
                    yield Completion(text="[More]",start_position=-len(current_word),style="bg:lightpink",selected_style="fg:white bg:blue",display_meta="More Tables")
            
            if fields:
                #for field in score.arrangeSuggestions(fields)[:8]:
                #    yield Completion(field, start_position=-len(current_word), style="bg:lightblue", selected_style="fg:white bg:blue", display_meta="Field" )
                #yield Completion(text="[More]", style="bg:lightblue", selected_style="fg:white bg:blue", display_meta="More Fields") 

                if self.show_all_fields:
                    # Show all tables if "More" was selected
                    for field in score.arrangeSuggestions(fields):
                        yield Completion(field, start_position=-len(current_word), style="bg:lightblue", selected_style="fg:white bg:blue", display_meta="Field",)
                else:
                    # Show only the first 8 tables
                    for field in score.arrangeSuggestions(fields)[:8]:
                        yield Completion(field,start_position=-len(current_word),style="bg:lightblue",selected_style="fg:white bg:blue",display_meta="Field")
                    # Add "[More]" option
                    yield Completion(text="[More]",start_position=-len(current_word),style="bg:lightblue",selected_style="fg:white bg:blue",display_meta="More Fileds")
            
            
            
            if functions:
                #for func in score.arrangeSuggestions(functions)[:8]:
                #    yield Completion(func, start_position=-len(current_word), style="bg:lightgreen",selected_style="fg:white bg:blue", display_meta="Function" )
                #yield Completion(text="[More]", style="bg:lightgreen", selected_style="fg:white bg:blue", display_meta="More Functions") 
                if self.show_all_functions:
                    for function in score.arrangeSuggestions(functions):
                        yield Completion(function, start_position=-len(current_word), style="bg:lightgreen", selected_style="fg:white bg:blue", display_meta="Function",)
                else:
                    # Show only the first 8 tables
                    for function in score.arrangeSuggestions(functions)[:8]:
                        yield Completion(function,start_position=-len(current_word),style="bg:lightgreen",selected_style="fg:white bg:blue",display_meta="Function")
                    # Add "[More]" option
                    yield Completion(text="[More]",start_position=-len(current_word),style="bg:lightgreen",selected_style="fg:white bg:blue",display_meta="More functions")
            
        else:
            # If no category is needed, yield individual suggestions
            for suggestion in suggestions:
                yield Completion(suggestion, start_position=-len(current_word))
                
        #########################################################################################################################################################
























#runtime correction 
def runtime_monitor(text,completer:SQLCompleter)->bool:
    response=False
    #print(f"Validating: {text}")  # Debugging: Print the input text
    
    # Check if '[More]' is typed
    if '[More]' in text:
        #print("state varibale can be change")
        #print(f"\nchanging state variables {completer.query_type}")
        # Update the state to show all suggestions
        if completer.show_all_tables == False:
            completer.show_all_tables = True
        elif completer.show_all_fields == False:
            completer.show_all_fields = True
        elif completer.show_all_functions == False:
            completer.show_all_functions = True
        #print(f"\nchanging state variables {completer.show_all_fields}")
        
    else:
         # Update the state to show all suggestions
        if completer.show_all_tables == True:
            completer.show_all_tables = False
        elif completer.show_all_fields == True:
            completer.show_all_fields = False
        elif completer.show_all_functions == True:
            completer.show_all_functions = False
        #print(f"\nchanging state variables {completer.show_all_fields}")
        
    
    # Check if the query starts with a valid keyword
    valid_keywords = ['!', 'SELECT', 'INSERT', 'UPDATE', 'DELETE','CREATE','ALTER','DROP','TRUNCATE','COMMIT','EXIT']
    return any(text.upper().startswith(kw) for kw in valid_keywords)




# Custom key bindings for real-time modification    
bindings = KeyBindings()

@bindings.add('(')
def add_space_after_open_paren(event):
    """Add a space after '('"""
    buffer = event.app.current_buffer
    #print(">" , buffer.cursor_position)
    if buffer.text and buffer.text[-1] == ' ': 
        buffer.insert_text('(')
        #buffer.insert_text(' ')
    else:
        buffer.insert_text(' ')
        buffer.insert_text('(')
        #buffer.insert_text(' ')

    buffer.cursor_position = len(buffer.text)


@bindings.add(' ')
def prevent_repeated_spaces(event):
    buffer = event.app.current_buffer
    # Check if the last character is already a space
    if buffer.text and buffer.text[-1] == ' ':
        # If the last character is a space, don't insert another space
        return
    # Otherwise, allow space to be inserted
    buffer.insert_text(' ')
    buffer.cursor_position = len(buffer.text)


@bindings.add('enter')
def check_before_hit_enter(event):
    buffer = event.app.current_buffer
    # Check if the last character is already a space
    if buffer.text and buffer.text[-1] != ';':
        buffer.insert_text(';')
    buffer.validate_and_handle()




def main()->None:

    dobj=serverConnect() #It should be first
    database_schema = dobj.fetch_database_structure() #It should be second
    
    #Optional
    for table,desc in database_schema.items():
       print(f"\n{table}: {desc}")
    
    queries = read_queries("generalize_queries.txt") #It shoud be third
    tokenized_queries = tokenize_queries(queries) #It should be forth
    #print(tokenized_queries)

    #print("\nStart typing your SQL query (Ctrl+C to exit):")

    completer = SQLCompleter(tokenized_queries,database_schema) #It should be Fifth




    # Define a custom style
    custom_style = Style.from_dict({
        # Customize the prompt appearance
        #"prompt": "bg:#008787 #eeeeee",  # Green background with white text
        "prompt": "bg:#1e1e1e #06989a",
        #"completion-menu.completion": "bg:#008800 #ffffff",  # Darker green for completions
        #"completion-menu.completion.current": "bg:#00ff00 #000000",  # Bright green for selected completion
        #"scrollbar.background": "bg:#00aa00",  # Green scrollbar background
        #"scrollbar.button": "bg:#00ff00",  # Bright green scrollbar button
    })

    # Validator for basic SQL syntax
    sql_validator = Validator.from_callable(
        lambda text: runtime_monitor(text, completer), 
        error_message='Must start with !/SELECT/INSERT/UPDATE/DELETE/DROP/TRUNCATE/CREATE/ALTER/COMMIT',
        move_cursor_to_end=True
    )
    #object of getChacater t get chracater on UI
    cobj = getChracter()




    while True:
        try:
            user_input = prompt(
                "╭─"+ cobj.chracter() + dobj.host+'@'+dobj.user + "\n╰─➤ $ ",
                rprompt=" " * 50,  # Add 10 spaces of padding on the right
                completer= completer,
                complete_style=CompleteStyle.MULTI_COLUMN,
                complete_while_typing=True,  # Enable completions while typing
                #multiline=True,
                #prompt_continuation=lambda width, line_number, is_soft_wrap: "... ",
                mouse_support=True,  # Enable mouse support
                history=FileHistory("history.txt"),
                style=custom_style,
                validator=sql_validator,
                validate_while_typing=True,
                key_bindings=bindings
                
            )

            #run os commands directly with ! Ex: !ls
            if user_input.startswith('!'):
                os.system(user_input[1:])
                print()
                continue

            #exit for exit
            if user_input.lower() == 'exit':
                break


            print(f"You typed: {user_input}")
            final_query = checkSyntax(user_input)
            if final_query is None:
                print("Syntax check failed. Query is None.")
                continue
            print(f"Final : {final_query}")

            showOutput(dobj.runQuery(final_query))                

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
    ... 
