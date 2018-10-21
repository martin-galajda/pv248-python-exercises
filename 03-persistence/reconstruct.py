from scorelib import load
from sql_helpers import load_sql_schema_def
import sqlite3
import sys
from db.conn import DbConnection
from data.edition import Edition
from data.score import Score
from data.voice import Voice
from data.print import Print
from data.person import Person

if len(sys.argv) != 3:
  raise ValueError("Program expects 3 arguments")

db_filename = sys.argv[1]
output_filename = sys.argv[2]

# pylint: disable=E1101
conn = DbConnection.instance()
conn.init(db_filename)

SQL_SELECT_ALL_PRINTS = """
  SELECT print.id, print.partiture, 
    edition.id as editionId, edition.name as editionName, edition.year as publicationYear,
    score.id as scoreId, score.name as compositionName, score.genre as scoreGenre, score.key as scoreKey,
    score.incipit as scoreIncipit, score.year as compositionYear
  FROM print
  INNER JOIN edition ON print.edition = edition.id
  INNER JOIN score ON edition.score = score.id;
"""

SQL_SELECT_VOICES_FOR_SCORE = """
  SELECT voice.id, voice.number, voice.range, voice.name
  FROM voice
  WHERE voice.score = ?;
"""

SQL_SELECT_AUTHORS_FOR_EDITION = """
  SELECT person.id, person.name, person.born, person.died
  FROM person
  INNER JOIN edition_author ON edition_author.editor = person.id
  INNER JOIN edition ON edition_author.edition = edition.id
  WHERE edition.id = ?;
"""

SQL_SELECT_AUTHORS_FOR_SCORE = """
  SELECT person.id, person.name, person.born, person.died
  FROM person
  INNER JOIN score_author ON score_author.composer = person.id
  INNER JOIN score ON score_author.score = score.id
  WHERE score.id = ?;
"""


all_prints = conn.execute_and_fetch_all(SQL_SELECT_ALL_PRINTS, ())

print_instances = []

for print_db in all_prints:
  (printId, printPartiture, editionId, editionName, publicationYear, scoreId, scoreName, scoreGenre, scoreKey, scoreIncipit, scoreYear) = print_db

  editors = []

  all_editors_db = conn.execute_and_fetch_all(SQL_SELECT_AUTHORS_FOR_EDITION, (editionId,))
  for editor_db in all_editors_db:
    (personId, personName, personBorn, personDied) = editor_db
    editors += [Person(id = personId, name = personName, born = personBorn, died = personDied)]


  composers = []
  all_composers_db = conn.execute_and_fetch_all(SQL_SELECT_AUTHORS_FOR_SCORE, (scoreId,))
  for composer_db in all_composers_db:
    (personId, personName, personBorn, personDied) = composer_db
    composers += [Person(id = personId, name = personName, born = personBorn, died = personDied)]


  voices_db = conn.execute_and_fetch_all(SQL_SELECT_VOICES_FOR_SCORE, (scoreId,))

  voices = list(range(len(voices_db)))
  for voice_db in voices_db:
    (voiceId, voiceNumber, voiceRange, voiceName) = voice_db
    voices[voiceNumber-1] = Voice(id = voiceId, name = voiceName, range = voiceRange, number = voiceNumber)


  score = Score(id = scoreId, name = scoreName, incipit=scoreIncipit, key = scoreKey, genre = scoreGenre, year = scoreYear, voices = voices, authors=composers)
  edition = Edition(composition=score, authors = editors, name = editionName)
  print_instance = Print(edition=edition, print_id = printId, partiture=(True if printPartiture == 'Y' else False))

  print_instances += [print_instance]

conn.close()

for print_instance in print_instances:
  print_instance.format()
  print("")
