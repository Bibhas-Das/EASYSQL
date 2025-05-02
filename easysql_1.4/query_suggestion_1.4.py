from prompt_toolkit import prompt # is used to take user input with autocomplete suggestions.
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
import re # is used to match regular expressions(like [table], [field]).

from serverConnect import fetch_database_structure,runQuery
from check_syntax import checkSyntax
from score_manage import score_manage

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

    return True if token in sql_keywords else False
    ...


def read_queries(file_path:str)->list[str]:
    with open(file_path, 'r') as f:
        queries = [query.strip().upper() for query in f.read().split("\n") if query.strip()]
    return queries if queries else ""

def tokenize_queries(queries:list[str])->list[list[str]]:
    """ Tokenizes queries into lists of words """
    tokenized_queries = []
    for query in queries:
        tokens = query.split()
        tokenized_queries.append(tokens)
    return tokenized_queries if tokenized_queries else []

def is_placeholder(word:str)->bool:
    """ Checks if a word is a placeholder (like [field1], [table], [value]) """
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
        print('fileds are added')
        #print(f"in the function {suggestions} {fields}")
        for table, _fields in fields.items():
            suggestions.extend(_fields)
        suggestions.remove('[FIELD]')
        return suggestions if suggestions else []
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
    for token in tokens[:len(completed_tokens)]:
        if is_placeholder(token) and not is_keywords(completed_tokens[index]):
            index+=1
            continue
        if token != completed_tokens[index]:
            return False
        index+=1
    return True


def find_suggestions(tokenized_queries: list[list[str]], completed_tokens: list[str], current_word: str, database_schema: dict[str, dict[str, list[str]]]) -> list[str]:
    """ Finds next possible words for autocompletion """

    #creating object of score_manager.py file
    score = score_manage()

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
    suggestionss = suggestActualTable(suggestions, database_schema.keys())

    # Ensure we get actal fileds name instead of [FILED]
    #first we need to make it in form : dict[str:list[str]] from dict[str:dict[str:list[str]]]
    new_schema = { _table: list(_field.keys()) for _table, _field in database_schema.items() }
    #suggestionss = suggestActualFields(suggestions, new_schema)                             

    #rearranging accorind thier score of  most uses
    #suggestions = score.arrangeSuggestions(suggestions)

    return suggestions if suggestions else []





class SQLCompleter(Completer):
    def __init__(self, tokenized_queries:list[list[str]],database_scema)->None:
        self.tokenized_queries = tokenized_queries
        self.database_scema = database_scema

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

        suggestions = find_suggestions(self.tokenized_queries, completed_tokens, current_word,self.database_scema)
        #print(f"\n{suggestions}")

        for suggestion in suggestions:  # Limit suggestions
            yield Completion(suggestion, start_position=-len(current_word))

def main()->None:
    database_scema = fetch_database_structure()
    
    for table,desc in database_scema.items():
        print(f"\n{table}: {desc}")
    
    queries = read_queries("generalize_queries.txt")
    tokenized_queries = tokenize_queries(queries)
    #print(tokenized_queries)

    print("\nStart typing your SQL query (Ctrl+C to exit):")
    while True:
        try:
            user_input = prompt(
                "User $ ",
                completer=SQLCompleter(tokenized_queries,database_scema),
                complete_style=CompleteStyle.MULTI_COLUMN,
            )
            print(f"You typed: {user_input}")
            final_query = checkSyntax(user_input)
            print(f"Output : {list(runQuery(final_query))}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main() 
