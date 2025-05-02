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
    if len(token)>1 and token[0]=='(':
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
    if '[TABLE]' in suggestions:
        suggestions.extend(tables)
        suggestions.remove('[TABLE]')
    return suggestions if suggestions else []
    ...

def suggestActualFields(suggestions:list[str],fields:dict[str:list[str]])->list[str]:
    if '[FIELD]' in suggestions:
        for table, _fields in fields.items():
            suggestions.extend(_fields)
        suggestions.remove('[FIELD]')
    return suggestions if suggestions else []
    ...


def getComparisonOperators(suggestions:list[str])->list[str]:
    List = ['=','<','>','<>','<=','>=']
    if '[COMPARISON]' in suggestions:
        suggestions.extend(List)
        suggestions.remove('[COMPARISON]')
    return suggestions
    ...

def getArithmeticOperators(suggestions:list[str])->list[str]:
    List = ['+','-','*','/']
    if '[ARITHMETIC]' in suggestions:
        suggestions.extend(List)
        suggestions.remove('[ARITHMETIC]')
    return suggestions
    ...


def getLogicalOperators(suggestions:list[str])->list[str]:
    List = ['AND','OR','NOT']
    if '[LOGICAL]' in suggestions:
        suggestions.extend(List)
        suggestions.remove('[LOGICAL]')
    return suggestions
    ...


def suggestSubqueries(suggestions:list[str])->list[str]:
    if any(bool(re.search(r'\[VALUE\]\S*', word)) or word == 'VALUES' or bool(re.search(r'\[FIELD\]\S*', word)) or bool(re.search(r'\[TABLE\]\S*', word)) for word in suggestions):
        suggestions.append('( SELECT')
    return suggestions
    ...


def remove_immidiate_used_token_from_suggestion(completed_tokens:list[str],suggestions:list[str])->list[str]:
    if completed_tokens and completed_tokens[-1] in suggestions:
        suggestions.remove(completed_tokens[-1])
    return suggestions if suggestions else []
    ...

def is_token_matched_without_variables(tokens:list[str],completed_tokens:list[str])->bool:
    index = 0
    for token in tokens[:len(completed_tokens)]:
        if is_placeholder(token) and not is_keywords(completed_tokens[index].upper()):
            index+=1
            continue
        if token != completed_tokens[index].upper():
            return False
        index+=1
    return True

def process_tokens(tokens: list[str]) -> list[str]:
    i = 0
    while i < len(tokens):
        if tokens[i].endswith(','):
            j = i
            while j < len(tokens) and tokens[j].endswith(','):
                j += 1
            if j < len(tokens):
                tokens[i:j + 1] = [tokens[j]]
            else:
                tokens[i:j] = []
        else:
            i += 1
    return tokens

def remove_token_sequences(complete_tokens, remove_list):
    if not all(isinstance(item, list) for item in remove_list):
        remove_list = [ [item] if not isinstance(item, list) else item for item in remove_list ]
    
    for pattern in remove_list:
        n = len(pattern)
        m = len(complete_tokens)
        for i in range(m - n + 1):
            if complete_tokens[i:i+n] == pattern:
                complete_tokens = complete_tokens[:i] + complete_tokens[i+n:]
                break
    return complete_tokens

def validate_data_types(text: str, database_schema: dict) -> tuple:
    """
    Validates if values match the expected data types and lengths in the database schema.
    Returns (is_valid, warning_message) tuple.
    """
    text_upper = text.upper()
    
    # Check for INSERT statement
    if text_upper.startswith("INSERT INTO"):
        try:
            # Extract table name
            parts = text.split()
            table_name = parts[2]
            
            # Check if table exists
            if table_name not in database_schema:
                return (True, "")  # Table validation will happen at execution
            
            # Extract values portion
            values_start = text_upper.find("VALUES(")
            if values_start == -1:
                return (True, "")  # Syntax error will be caught elsewhere
                
            values_str = text[values_start + 7:-1]  # Get content inside VALUES()
            values = [v.strip().strip("'") for v in values_str.split(",")]
            
            # Get table columns and their data types
            columns = list(database_schema[table_name].keys())
            
            # Validate each value against its corresponding column
            for i, (col, val) in enumerate(zip(columns, values)):
                col_info = database_schema[table_name][col]
                data_type = col_info['data_type'].upper()
                max_length = col_info.get('max_length')
                
                # Skip if column info not available
                if not data_type:
                    continue
                    
                # Validate based on data type
                if 'INT' in data_type and not val.isdigit():
                    return (False, f"Warning: Value '{val}' is not a valid integer for column '{col}'")
                    
                elif 'CHAR' in data_type or 'TEXT' in data_type:
                    if max_length and len(val) > max_length:
                        return (False, f"Warning: Value '{val}' exceeds max length ({max_length}) for column '{col}'")
                        
                elif 'DATE' in data_type and not re.match(r'\d{4}-\d{2}-\d{2}', val):
                    return (False, f"Warning: Value '{val}' is not a valid date (YYYY-MM-DD) for column '{col}'")
                    
                elif 'DECIMAL' in data_type or 'FLOAT' in data_type or 'DOUBLE' in data_type:
                    try:
                        float(val)
                    except ValueError:
                        return (False, f"Warning: Value '{val}' is not a valid decimal for column '{col}'")
        
        except Exception as e:
            # If any error occurs during validation, just continue (syntax checker will catch it)
            return (True, "")
    
    # Check for UPDATE statement
    elif text_upper.startswith("UPDATE"):
        try:
            # Extract table name
            parts = text.split()
            table_name = parts[1]
            
            # Check if table exists
            if table_name not in database_schema:
                return (True, "")  # Table validation will happen at execution
                
            # Find SET clause
            set_start = text_upper.find("SET ") + 4
            where_start = text_upper.find(" WHERE ")
            set_clause = text[set_start:where_start if where_start != -1 else None]
            
            # Parse each assignment in SET clause
            assignments = [a.strip() for a in set_clause.split(",")]
            for assignment in assignments:
                if not assignment:
                    continue
                    
                col, val = assignment.split("=", 1)
                col = col.strip()
                val = val.strip().strip("'")
                
                # Get column info
                if col not in database_schema[table_name]:
                    continue
                    
                col_info = database_schema[table_name][col]
                data_type = col_info['data_type'].upper()
                max_length = col_info.get('max_length')
                
                # Validate based on data type
                if 'INT' in data_type and not val.isdigit():
                    return (False, f"Warning: Value '{val}' is not a valid integer for column '{col}'")
                    
                elif 'CHAR' in data_type or 'TEXT' in data_type:
                    if max_length and len(val) > max_length:
                        return (False, f"Warning: Value '{val}' exceeds max length ({max_length}) for column '{col}'")
                        
                elif 'DATE' in data_type and not re.match(r'\d{4}-\d{2}-\d{2}', val):
                    return (False, f"Warning: Value '{val}' is not a valid date (YYYY-MM-DD) for column '{col}'")
                    
                elif 'DECIMAL' in data_type or 'FLOAT' in data_type or 'DOUBLE' in data_type:
                    try:
                        float(val)
                    except ValueError:
                        return (False, f"Warning: Value '{val}' is not a valid decimal for column '{col}'")
        
        except Exception as e:
            # If any error occurs during validation, just continue
            return (True, "")
    
    return (True, "")


def find_suggestions(tokenized_queries: list[list[str]], completed_tokens: list[str], current_word: str, database_schema: dict[str, dict[str, list[str]]]) -> list[str]:
    """ Finds next possible words for autocompletion """
    #print(" List : ",completed_tokens)
    #creating object of score_manager.py file
    score = score_manage(database_schema)

    suggestions = list()
    #current_word = current_word.upper()

    for tokens in tokenized_queries:
        next_token:str=''
        #token: each line [toknized]
        if len(tokens) > len(completed_tokens):

            completed_tokens = process_tokens(completed_tokens)
            #completed_tokens = [token[1:].upper() if len(token)>1 and token[0] == '(' else token for token in completed_tokens]
            #completed_tokens = [item for token in completed_tokens for item in (["(", token[1:].upper()] if token.startswith("(") and len(token) > 1 else [token])]

            #print("List",completed_tokens)
            #I will check if previous word is ending with ',' or not if yes then same types of sugestions hould show without increase index in search
            # if completed_tokens and completed_tokens[-1].endswith(','):
            #     no_mul_tokens:int = count_consecutive_tokens_ending_with_comma_from_end(completed_tokens)

            #     completed_tokens = completed_tokens[:len(completed_tokens)-no_mul_tokens]

                # if is_token_matched_without_variables(tokens,completed_tokens[:len(completed_tokens)-no_mul_tokens]):
                #     next_token:list[str] = tokens[len(completed_tokens)-no_mul_tokens]
                #     print(next_token)
                

            #here it should be modified...[filed1]...[value]..[table] should be ignore in tokenized_quries 
            #print(f"\n{is_token_matched_without_variables(tokens,completed_tokens)}")
            #if tokens[:len(completed_tokens)] == completed_tokens:
            if is_token_matched_without_variables(tokens, completed_tokens):
                next_token:str = tokens[len(completed_tokens)]

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
            if next_token.startswith(current_word.upper()) or is_placeholder(next_token):
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

    #print("Current : ",current_word)
    index=0
    for suggestion in suggestions:
        if suggestion and suggestion.startswith(current_word) or suggestion.startswith(current_word.upper()):
            suggestions[index]=suggestion
            index+=1



    return suggestions[:index] if suggestions else []
    


# def remove_token_sequences(complete_tokens, remove_list):
#     #print("function called")
#     #print("stack:",remove_list)
#     for pattern in remove_list:
#         #print("fucntion runiing..")
#         # Convert both lists to strings for easier pattern matching
#         tokens_str = ' '.join(complete_tokens)
#         pattern_str = ' '.join(pattern)
        
#         # Find the index of the pattern
#         index = tokens_str.find(pattern_str)
#         if index != -1:
#             # If found, split the string and reconstruct without the pattern
#             before = tokens_str[:index].strip()
#             after = tokens_str[index + len(pattern_str):].strip()
#             tokens_str = before + ' ' + after
#             # Convert back to list
#             complete_tokens = [token for token in tokens_str.split(' ') if token]
#     #print("function end")
#     return complete_tokens



class SQLCompleter(Completer):
    def __init__(self, tokenized_queries:list[list[str]],database_schema)->None:
        self.tokenized_queries = tokenized_queries
        self.database_schema = database_schema
        self.show_all_tables = True
        self.show_all_fields = True
        self.show_all_functions = True
        self.context_stack = []
        self.stack_item = -1
        self.query_type = 'UNKNOWN'
    
    def format_suggestions(self,label, items):
        if not items:
            return None
        suggestion_text = f"{label}: " + " ".join(f"[{item}]" for item in items)
        return suggestion_text[:terminal_width]

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        last_space_pos = text_before_cursor.rfind(' ')
        
        if last_space_pos == -1:
            completed_tokens = []
            current_word = text_before_cursor
        else:
            completed_part = text_before_cursor[:last_space_pos]
            completed_tokens = completed_part.split()
            current_word = text_before_cursor[last_space_pos+1:]

        completed_tokens = [item for token in completed_tokens for item in (["(", token[1:].upper()] if token.startswith("(") and len(token) > 1 else [token])]

        if self.stack_item > -1:
            completed_tokens = remove_token_sequences(completed_tokens,self.context_stack[:self.stack_item+1])
        elif self.context_stack:
            completed_tokens = self.context_stack[0] + remove_token_sequences(completed_tokens,self.context_stack)
            ...

        if completed_tokens:
            first_token = completed_tokens[0].upper()
            if first_token == 'SELECT':
                self.query_type = 'DQL'
            elif first_token in ('DELETE', 'UPDATE', 'INSERT'):
                self.query_type = 'DML'
            else:
                self.query_type = 'UNKNOWN'
        else:
            self.query_type = 'UNKNOWN'

        if len(completed_tokens)>=2:
            if '(' in completed_tokens[-2] and 'SELECT' in completed_tokens[-1]:
                self.context_stack.append(completed_tokens[:-1])
                self.stack_item += 1
                completed_tokens = [completed_tokens[-1]]

        if ')' in completed_tokens and self.context_stack and self.stack_item > -1:
            current_query = completed_tokens
            completed_tokens = self.context_stack[self.stack_item]
            self.stack_item -= 1
            self.context_stack.append(current_query)

        suggestions = find_suggestions(self.tokenized_queries, completed_tokens, current_word,self.database_schema)
        
        tables = []
        fields = []
        functions = []

        for suggestion in suggestions:
            if suggestion in self.database_schema:
                tables.append(suggestion)
            elif any(suggestion in columns for columns in self.database_schema.values()):
                fields.append(suggestion)
            else:
                functions.append(suggestion)

        score = score_manage(self.database_schema)

        if tables or fields or functions:
            if tables:
                if self.show_all_tables:
                    for table in score.arrangeSuggestions(tables):
                        yield Completion(table, start_position=-len(current_word), style="bg:lightpink", selected_style="fg:white bg:blue", display_meta="Table",)
                else:
                    for table in score.arrangeSuggestions(tables)[:8]:
                        yield Completion(table,start_position=-len(current_word),style="bg:lightpink",selected_style="fg:white bg:blue",display_meta="Table")
                    yield Completion(text="[More]",start_position=-len(current_word),style="bg:lightpink",selected_style="fg:white bg:blue",display_meta="More Tables")
            
            if fields:
                if self.show_all_fields:
                    for field in score.arrangeSuggestions(fields):
                        yield Completion(field, start_position=-len(current_word), style="bg:lightblue", selected_style="fg:white bg:blue", display_meta="Field",)
                else:
                    for field in score.arrangeSuggestions(fields)[:8]:
                        yield Completion(field,start_position=-len(current_word),style="bg:lightblue",selected_style="fg:white bg:blue",display_meta="Field")
                    yield Completion(text="[More]",start_position=-len(current_word),style="bg:lightblue",selected_style="fg:white bg:blue",display_meta="More Fileds")
            
            if functions:
                if self.show_all_functions:
                    for function in score.arrangeSuggestions(functions):
                        yield Completion(function, start_position=-len(current_word), style="bg:lightgreen", selected_style="fg:white bg:blue", display_meta="Function",)
                else:
                    for function in score.arrangeSuggestions(functions)[:8]:
                        yield Completion(function,start_position=-len(current_word),style="bg:lightgreen",selected_style="fg:white bg:blue",display_meta="Function")
                    yield Completion(text="[More]",start_position=-len(current_word),style="bg:lightgreen",selected_style="fg:white bg:blue",display_meta="More functions")
        else:
            for suggestion in suggestions:
                yield Completion(suggestion, start_position=-len(current_word))

def runtime_monitor(text,completer:SQLCompleter)->bool:
    response=False
    
    if '[More]' in text:
        if completer.show_all_tables == False:
            completer.show_all_tables = True
        elif completer.show_all_fields == False:
            completer.show_all_fields = True
        elif completer.show_all_functions == False:
            completer.show_all_functions = True
    else:
        if completer.show_all_tables == True:
            completer.show_all_tables = False
        elif completer.show_all_fields == True:
            completer.show_all_fields = False
        elif completer.show_all_functions == True:
            completer.show_all_functions = False
    
    # Check if the query starts with a valid keyword
    valid_keywords = ['!', 'SELECT', 'INSERT', 'UPDATE', 'DELETE','CREATE','ALTER','DROP','TRUNCATE','COMMIT','EXIT']
    return any(text.upper().startswith(kw) for kw in valid_keywords)

def validate_input(text: str, database_schema: dict) -> tuple:
    """
    Validates user input against database schema and returns (is_valid, warning_message).
    """
    # First check basic SQL syntax
    if not runtime_monitor(text, None):
        return (False, "Must start with !/SELECT/INSERT/UPDATE/DELETE/DROP/TRUNCATE/CREATE/ALTER/COMMIT")
    
    # Then check data types and lengths if applicable
    is_valid, warning = validate_data_types(text, database_schema)
    if not is_valid:
        return (is_valid, warning)
    
    return (True, "")

# Custom key bindings for real-time modification    
bindings = KeyBindings()

@bindings.add('(')
def add_space_after_open_paren(event):
    """Add a space after '('"""
    buffer = event.app.current_buffer
    if len(buffer.text)>=2 and buffer.text[-1] == ' ' and buffer.text[-2] == '=':         
        buffer.insert_text('(')
    elif len(buffer.text)>=1 and buffer.text[-1] == '=':   
        buffer.insert_text(' ')
        buffer.insert_text('(')
    else:
        buffer.insert_text('(')
    buffer.cursor_position = len(buffer.text)

@bindings.add(' ')
def prevent_repeated_spaces(event):
    buffer = event.app.current_buffer
    if buffer.text and buffer.text[-1] == ' ':
        return
    buffer.insert_text(' ')
    buffer.cursor_position = len(buffer.text)

@bindings.add(',')
def remove_space_before_coma(event):
    """Add a space after '('"""
    buffer = event.app.current_buffer
    if buffer.text and buffer.text[-1] == ' ': 
        buffer.delete_before_cursor(1)
        buffer.insert_text(',')
    else:
        buffer.insert_text(',')
    buffer.cursor_position = len(buffer.text)

@bindings.add('enter')
def check_before_hit_enter(event):
    buffer = event.app.current_buffer
    if buffer.text and buffer.text[-1] != ';':
        buffer.insert_text(';')
    buffer.validate_and_handle()

def main()->None:
    dobj=serverConnect()
    database_schema = dobj.fetch_database_structure()
    
    #Optional
    for table,desc in database_schema.items():
       print(f"\n{table}: {desc}")
    
    queries = read_queries("generalize_queries2.txt")
    tokenized_queries = tokenize_queries(queries)

    completer = SQLCompleter(tokenized_queries,database_schema)

    custom_style = Style.from_dict({
        "prompt": "bg:#1e1e1e #06989a",
    })

    # Create validator with both syntax and data type validation
    sql_validator = Validator.from_callable(
        lambda text: validate_input(text, database_schema)[0],
        error_message=lambda: validate_input(text, database_schema)[1] or "Invalid SQL syntax",
        move_cursor_to_end=True
    )
    
    cobj = getChracter()

    while True:
        try:
            user_input = prompt(
                "╭─"+ cobj.chracter() + dobj.host+'@'+dobj.user + "\n╰─➤ $ ",
                rprompt=" " * 50,
                completer= completer,
                complete_style=CompleteStyle.MULTI_COLUMN,
                complete_while_typing=True,
                history=FileHistory("history.txt"),
                style=custom_style,
                validator=sql_validator,
                validate_while_typing=True,
                key_bindings=bindings
            )

            if user_input.startswith('!'):
                os.system(user_input[1:])
                print()
                continue

            if user_input.lower() == 'exit;':
                break

            print(f"You typed: {user_input}")
            final_query = checkSyntax(user_input)
            if final_query is None:
                print("Syntax check failed. Query is None.")
                continue
            print(f"Final : {final_query}")

            out = showOutput(dobj.runQuery(final_query))                
            out.display()
            
            # Show any validation warnings that might have been bypassed
            is_valid, warning = validate_data_types(user_input, database_schema)
            if not is_valid:
                print(f"\nWarning: {warning}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()