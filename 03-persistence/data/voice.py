from db.conn import DbConnection
import re

# -- Information about the voices in a particular score. Scores often contain
# -- multiple voices, hence a separate table. The relationship is 1:N (each row
# -- in the voice table belongs to exactly one score). The 'number' column
# -- refers to the voice number, i.e. it's 1 for a line starting 'Voice 1:'.
# create table voice ( id integer primary key not null,
#                      number integer not null, -- which voice this is
#                      score integer references score( id ) not null,
#                      range varchar,
#                      name varchar );



class Voice:
  db_conn = DbConnection.instance()
  def __init__(self, name, range = None, id = None, score = None, number = None):
    self.id = id
    self.score = score
    self.name = name
    self.range = range
    self.number = number
  
  def format(self):
    formatted_str = ""

    if self.range:
      formatted_str += self.range + ", "

    return formatted_str + self.name

  def find_in_db(self):
    SELECT_SQL = """
      SELECT id, score, number, range, name
      FROM voice
      WHERE number = ? AND range = ? AND name = ?;
    """

    values = ()
    if self.number is None:
      SELECT_SQL = re.compile(r'number = \?').sub('number IS NULL', SELECT_SQL)
    else:
      values += (self.number,)

    if self.range is None:
      SELECT_SQL = re.compile(r'range = \?').sub('range IS NULL', SELECT_SQL)
    else:
      values += (self.range,)

    values += (self.name,)

    voice_from_db_data = self.db_conn.execute_and_fetch_one(SELECT_SQL, values)

    return voice_from_db_data

  def insert(self):
    inserted_id = self.db_conn.insert("""
      INSERT INTO voice (score, number, range, name) VALUES (?, ?, ?, ?);
    """, (self.score, self.number, self.range, self.name))
    self.id = inserted_id

  def upsert(self):
    voice_from_db_data = self.find_in_db()

    created_new = False
    if voice_from_db_data is None:
      created_new = True
      inserted_id = self.db_conn.insert("""
        INSERT INTO voice (number, range, name) VALUES (?, ?, ?);
      """, (self.number, self.range, self.name))
      self.id = inserted_id
    else:
      self.id = voice_from_db_data[0]
      self.score = voice_from_db_data[1]

    return created_new


  def attach_to_score(self, score_id):
    self.db_conn.execute_and_fetch_one("""
      UPDATE voice
      SET score = ?
      WHERE id = ?;
    """, (score_id, self.id))

    self.score = score_id
