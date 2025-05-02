import os
from datetime import datetime
import re

def clear():
    os.system('cls')

def add_datetime_to_line(line):
    """Add current date-time to a line if it doesn't already have one."""
    if not re.match(r'^\[\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2} [ap]m\]', line):
        current_time = datetime.now().strftime("[%d/%m/%Y %I:%M:%S %p]")
        line = f"{current_time} {line}"
    return line

def clean_query(query):
    """Clean the query by removing double spaces and fixing spaces inside []."""
    query = ' '.join(query.split())  # Remove double spaces
    
    # Replace invalid placeholders with [value]
    query = re.sub(r'\[\s*([^\]]+?)\s*\]', lambda match: f"[{match.group(1).lower()}]" if match.group(1).lower() in ['value', 'field', 'table', 'condition', 'alias'] else "[value]", query)
    
    return query.lower()

def extract_query(query_line):
    """Extract the actual query part without the datetime prefix."""
    return re.sub(r'^\[\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2} [ap]m\] ', '', query_line.lower())

def process_file(file):
    """Process the file to clean queries and preserve existing date-time."""
    if os.path.exists(file):
        with open(file, 'r') as f:
            lines = f.read().splitlines()
        
        processed_queries = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Check if the line starts with a date-time prefix
            datetime_match = re.match(r'^(\[\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2} [ap]m\])(.*)', line)
            if datetime_match:
                # Preserve the existing date-time and clean the query part
                dt_prefix = datetime_match.group(1)
                query_part = datetime_match.group(2).strip()
                cleaned_query = clean_query(query_part)
                processed_line = f"{dt_prefix} {cleaned_query}"
            else:
                # Clean the entire line and add new date-time
                cleaned_query = clean_query(line)
                processed_line = add_datetime_to_line(cleaned_query)
            processed_queries.append(processed_line)
        return processed_queries
    else:
        print(f"File '{file}' does not exist.")
        return []

def main():
    clear()
    file = 'generalize_queries.txt'
    queries = process_file(file)
    
    if queries:
        print("Existing queries with date-time (Sorted):\n")
        for query in sorted(queries, key=extract_query):
            print(query)
    
    while True:
        user_query = input("\nEnter a new query (or type 'exit' to quit): ")
        if not user_query.endswith(';'):
            print("\nQuery should ends with ';'")
            continue

        if len(user_query.split(';')) > 1:
            print("\nYour queries.......")
            index = 1
            for query in user_query.split(';'):
                if query:
                    print(f"\n [{index}] : {query.strip()};")
                    index += 1
            ch = input(f"\nTotal {index-1} queries correct ? (y/n) : ").lower()
            if ch != 'y':
                continue
            ...
        
        if user_query.lower() == 'exit':
            print("Exiting...")
            break
        
        if not user_query:
            print("Query cannot be empty. Please try again.")
            continue
        
        
        
        for query in user_query.split(';'):
            if query:
                print("\n[Query] : "+query+";")
                cleaned_user_query = clean_query(query+';')
                existing_queries_without_dt = [extract_query(q) for q in queries]
                
                # Check if the cleaned query (without date-time) already exists
                if extract_query(cleaned_user_query) in existing_queries_without_dt:
                    input("\n[Result] : This query already exists. It will not be added.")
                    continue
                else:
                    input("\n[Result] : This query is added.")

                
                # Add date-time to the new query
                final_query = add_datetime_to_line(cleaned_user_query)
                queries.append(final_query)



        # Write updated queries back to the file
        with open(file, 'w') as f:
            for query in sorted(queries, key=extract_query):
                f.write(query + "\n")
            
        clear()

        print("\nUpdated queries (Sorted):")
        for query in sorted(queries, key=extract_query):
            print(query)

if __name__ == "__main__":
    main()