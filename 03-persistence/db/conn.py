import sqlite3
from decorators.singleton import Singleton

def get_db_conn(filename = 'scorelib.dat'):
  conn = sqlite3.connect(filename)

  return conn

@Singleton
class DbConnection():

  def __init__(self):
    self._conn = get_db_conn()
    self._cursor = self._conn.cursor()

  def insert(self, sql, values):
    self._cursor.execute(sql, values)
    
    return self._cursor.lastrowid

  def execute_and_fetch_one(self, sql, values):
    self._cursor.execute(sql, values)

    return self._cursor.fetchone()
  
  def execute_and_fetch_many(self, sql, values):
    self._cursor.execute(sql, values)

    return self._cursor.fetchmany()

  def execute_and_fetch_all(self, sql, values):
    self._cursor.execute(sql, values)

    return self._cursor.fetchall()

  def executescript(self, sql):
    self._cursor.executescript(sql)

  def close(self):
    self._cursor.close()
    self._conn.commit()
    self._conn.close()
