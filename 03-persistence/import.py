from scorelib import load
from sql_helpers import load_sql_schema_def
from sql import SELECT_SCORE_QUERY, INSERT_SCORE_STATEMENT, find_composition
import sqlite3
import sys
from db.conn import DbConnection

if len(sys.argv) != 3:
  raise ValueError("Program expects 3 arguments")

filename = sys.argv[1]
output_filename = sys.argv[2]
print_instances = load(filename)

def persist_print_instance(print_instance):
  print_instance.save_to_db()
  pass


# pylint: disable=E1101
conn = DbConnection.instance()
schema_sql = load_sql_schema_def()
conn.executescript(schema_sql)

for print_instance in print_instances:
  persist_print_instance(print_instance)

conn.close()
