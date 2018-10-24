from data.person import Person
from data.voice import Voice
import re
from db.conn import DbConnection

# -- Auxiliary table. See 'score'.
# create table score_author( id integer primary key not null,
#                            score integer references score( id ) not null,
#                            composer integer references person( id ) not null );


# -- Stores info about a single score. Since some of the scores in the library
# -- have multiple compositions in them, author data is stored in a separate
# -- table (score_author). The relationship between authors and scores is M:N
# -- since most composers have more than one composition to their name. Year in
# -- this table refers to the field 'Composition Year' in the text file.
# create table score ( id integer primary key not null,
#                      name varchar,
#                      genre varchar,
#                      key varchar,
#                      incipit varchar,
#                      year integer );

class Score():
  db_conn = DbConnection.instance()

  def __init__(self, name = None, incipit = None, key = None, genre = None, year = None, voices = [], authors = [], id = None):
    self.id = id
    self.name = name
    self.incipit = incipit
    self.key = key
    self.genre = genre
    self.year = year
    self.voices = voices
    self.authors = authors

  def print_voices(self):
    for voice_idx in range(len(self.voices)):
      voice = self.voices[voice_idx]
      print("Voice %d: %s" % (voice.number, voice.format()))

  def load_authors_from_db(self):
    results = self.db_conn.execute_and_fetch_one("""
      SELECT person.id, person.name, person.born, person.died
      FROM score
      INNER JOIN score_author ON score_author.score = score.id
      INNER JOIN person ON person.id = score_author.composer
      WHERE score.id = ?;
    """, (self.id,))
    authors = []

    for result in results:
      (person_id, person_name, person_born, person_died) = result
      authors += [Person(name = person_name, born = person_born, died = person_died, id = person_id)]

    self.authors = authors

  def load_voices_from_db(self):
    results = self.db_conn.execute_and_fetch_one("""
      SELECT voice.id, voice.number, voice.score, voice.range, voice.name
      FROM voice
      WHERE voice.score = ?;
    """, (self.id,))
    voices_dict = {}
    voices = []

    for result in results:
      (voice_id, voice_number, voice_score, voice_range, voice_name) = result
      voices_dict[voice_number] = Voice(name = voice_name, range = voice_range, score = voice_score, id = voice_id, number = voice_number)
      voices += [None]

    for idx in voices_dict.keys():
      voices[idx] = voices_dict[idx]

    self.voices = voices

  def insert(self):
    new_id = self.db_conn.insert("""
      INSERT INTO score (name, genre, key, incipit, year)
      VALUES (?, ?, ?, ?, ?);
    """, (self.name, self.genre, self.key, self.incipit, self.year))
    new_score_data = (new_id, self.name, self.genre, self.key, self.incipit, self.year)
    self.id = new_id

    for voice in self.voices:
      voice.score = self.id
      voice.insert()

    for author in self.authors:
      author.attach_to_score(self.id)

    return new_score_data

  def print_authors(self):
    print("Authors: %s" % ','.join(map(lambda a: str((a.id, a.name)), self.authors)))

  def has_different_authors_or_voices(self, other_score_id):
    SELECT_AUTHORS_FROM_DB = """
      SELECT person.id, person.name
      FROM person
      INNER JOIN score_author ON score_author.composer = person.id
      WHERE score_author.score = ?;
    """
    authors_from_db = self.db_conn.execute_and_fetch_all(SELECT_AUTHORS_FROM_DB, (other_score_id,))

    matching_authors = 0
    total_author_rows = 0
    for author_row_from_db in authors_from_db:
      matches_author = any(map(lambda a: a.id == author_row_from_db[0], self.authors))
      if matches_author:
        matching_authors += 1
      total_author_rows += 1

    has_different_authors = len(self.authors) != matching_authors or total_author_rows != len(self.authors)
    if has_different_authors:
      return True

    SELECT_VOICES_FROM_DB = """
      SELECT voice.id, voice.number, voice.name, voice.range
      FROM voice
      WHERE voice.score = ?;
    """
    voices_from_db = self.db_conn.execute_and_fetch_all(SELECT_VOICES_FROM_DB, (other_score_id,))

    matching_voices = 0
    total_voices_from_db = 0
    for voice_row_from_db in voices_from_db:
      total_voices_from_db += 1

      (voice_from_db_id, voice_from_db_number, voice_from_db_name, voice_from_db_range) = voice_row_from_db
      if len(self.voices) >= voice_from_db_number:
        curr_voice = self.voices[voice_from_db_number-1]
        if curr_voice.name == voice_from_db_name and curr_voice.range == voice_from_db_range:
          matching_voices += 1

    has_different_voices = len(self.voices) != matching_voices or total_voices_from_db != len(self.voices)

    return has_different_voices


  def upsert(self):
    for idx, author in enumerate(self.authors):
      self.authors[idx].upsert()

      if self.authors[idx].id is None:
        print("Id for author is none!!!")

    for idx, voice in enumerate(self.voices):
      self.voices[idx].number = idx + 1

    sql_str  = """
      SELECT score.id, score.name, genre, key, incipit, score.year
      FROM score
      WHERE name = ? AND genre = ? AND key = ? AND incipit = ? AND year = ?
    """
    values = (self.name, )

    if self.genre is not None:
      values += (self.genre,)
    else:
      sql_str = re.compile(r' AND genre = \?').sub(' AND GENRE is NULL', sql_str)

    if self.key is not None:
      values += (self.key,)
    else:
      sql_str = re.compile(r' AND key = \?').sub(' AND key is NULL', sql_str)

    if self.incipit is not None:
      values += (self.incipit,)
    else:
      sql_str = re.compile(r' AND incipit = \?').sub(' AND incipit is NULL', sql_str)

    if self.year is not None:
      values += (self.year,)
    else:
      sql_str = re.compile(r' AND year = \?').sub(' AND year is NULL', sql_str)

    score_data_from_db = self.db_conn.execute_and_fetch_one(sql_str, values)

    created_new_score = False
    if score_data_from_db is not None:
      other_score_id = score_data_from_db[0]
      if self.has_different_authors_or_voices(other_score_id):
        self.insert()
        created_new_score = True
      else:
        print("Using already found score: " + str((score_data_from_db[0], score_data_from_db[1])))
        self.id = score_data_from_db[0] 
    elif score_data_from_db is None:
      score_data_from_db = self.insert()
      created_new_score = True

    return created_new_score
