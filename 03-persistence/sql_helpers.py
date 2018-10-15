import os

def load_sql_schema_def(path_to_schema_def = './scorelib.sql'):
  sql_str = ""
  with open(path_to_schema_def) as file:
    for line in file:
      sql_str += line + os.linesep

  return sql_str
