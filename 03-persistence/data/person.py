from db.conn import DbConnection
import re

# -- A table that stores a person: could be either a composer or an editor.
# create table person ( id integer primary key not null,
#                       born integer,
#                       died integer,
#                       name varchar not null );

class Person:
  db_conn = DbConnection.instance()
  def __init__(self, name, born, died, id):
    self.id = id
    self.name = name

    self.born = int(born) if born is not None else None
    self.died = int(died) if died is not None else None

  def format(self):
    formatted_str = self.name

    if self.born is not None and self.died is not None:
      formatted_str += " (%d--%d)" % (self.born, self.died)
    elif self.born is not None:
      formatted_str += " (%d--)" % (self.born)
    elif self.died is not None:
      formatted_str += " (--%d)" % (self.died)

    return formatted_str

  def upsert(self):
    person_from_db = self.db_conn.execute_and_fetch_one("""
      SELECT id, name, born, died
      FROM person
      WHERE name = ?;
    """, (self.name,))

    created_new = False
    if person_from_db is not None and (self.born is not None or self.died is not None):
      self.id = person_from_db[0]

      UPDATE_SQL = """
        UPDATE person
        SET born = ?, died = ?, name = ?
        WHERE name = ?;
      """

      values = ()
      if self.born is None:
        UPDATE_SQL = re.compile(r'born = \?,').sub('', UPDATE_SQL)
      else:
        values += (self.born,)

      if self.died is None:
        UPDATE_SQL = re.compile(r'died = \?,').sub('', UPDATE_SQL)
      else:
        values += (self.died,)
      values += (self.name, self.name)

      self.db_conn.execute_and_fetch_one(UPDATE_SQL, values)
    elif person_from_db is None:
      new_id = self.db_conn.insert("""
        INSERT INTO person (name, born, died)
        VALUES (?, ?, ?)
      """, (self.name, self.born, self.died))
      created_new = True
      self.id = new_id
    elif person_from_db is not None:
      self.id = person_from_db[0]

    return created_new

  def attach_to_score(self, score_id):
    self.db_conn.execute_and_fetch_one("""
      INSERT INTO score_author (score, composer) VALUES (?, ?);
    """, (score_id, self.id))

  def attach_to_edition(self, edition_id):
    self.db_conn.execute_and_fetch_one("""
      INSERT INTO edition_author (edition, editor) VALUES (?, ?);
    """, (edition_id, self.id))
