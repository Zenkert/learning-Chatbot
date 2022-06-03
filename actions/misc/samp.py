import main

database_name = "test"
collection_name = "mcqs"

conn = main.DatabaseConnection()
# conn = DatabaseConnection(database_name, collection_name)
c = conn.connection()
resss = main.get_subjects()
print(resss)

# print(c._conn__username)