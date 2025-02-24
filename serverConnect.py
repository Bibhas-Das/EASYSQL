import pymysql

def fetch_database_structure():
    try:
        # Connect to MySQL
        conn = pymysql.connect(
            host="localhost",
            user="t13",
            password="t13",
            database="SNU",
            charset="utf8mb4"
        )
        cursor = conn.cursor()

        # Fetch all tables
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        print("✅ Successfully connected to MySQL!")
        print("Tables in database SNU:")

        # Dictionary to store table structures
        database_structure = {}

        for table in tables:
            table_name = table[0]
            print(f"\n🔹 Table: {table_name}")
            
            # Fetch table schema
            cursor.execute(f"DESC {table_name};")
            columns = cursor.fetchall()

            #print("--------------------------------------------------------")
            #print("| Field Name     | Type            | Null | Key | Extra  |")
            #print("--------------------------------------------------------")

            # Dictionary to store column details
            column_details = {}

            for col in columns:
                field_name = col[0] if col[0] else ""
                field_type = col[1] if col[1] else ""
                is_nullable = col[2] if col[2] else ""
                key_type = col[3] if col[3] else ""  # Handle None
                extra = col[4] if col[4] else ""  # Handle None

                # Store column details in dictionary
                column_details[field_name] = [field_type, is_nullable, key_type, extra]

                # Print column details
                #print(f"| {field_name:<14} | {field_type:<15} | {is_nullable:<4} | {key_type:<3} | {extra:<6} |")

            #print("--------------------------------------------------------")

            # Store in main dictionary
            database_structure[table_name] = column_details

        # Print dictionary
        #print("\n📌 Database Structure as Dictionary:")
        #for table,disc in database_structure.items():
        #    print(f"{table}: {disc}\n")

        # Close connection
        cursor.close()
        conn.close()
        return database_structure

    except pymysql.MySQLError as e:
        print(f"❌ Error: {e}")


print(fetch_database_structure())