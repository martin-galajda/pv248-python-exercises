import sqlite3
import sys
from db.conn import DbConnection
from data.edition import Edition
from data.score import Score
from data.voice import Voice
from data.print import Print
from data.person import Person
import json
from to_pretty_json import to_pretty_json

if len(sys.argv) != 2:
  raise ValueError("Program expects 2 arguments")
DB_NAME = 'scorelib.dat'

printIdArg = sys.argv[1]

# pylint: disable=E1101
conn = DbConnection.instance()
conn.init(DB_NAME)

SQL_SELECT_ALL_PRINTS = """
  SELECT print.id, print.partiture, 
    edition.id as editionId, edition.name as editionName, edition.year as publicationYear,
    score.id as scoreId, score.name as compositionName, score.genre as scoreGenre, score.key as scoreKey,
    score.incipit as scoreIncipit, score.year as compositionYear
  FROM print
  INNER JOIN edition ON print.edition = edition.id
  INNER JOIN score ON edition.score = score.id
  WHERE print.id = ?;
"""

SQL_SELECT_AUTHORS_FOR_SCORE = """
  SELECT person.id, person.name, person.born, person.died
  FROM person
  INNER JOIN score_author ON score_author.composer = person.id
  INNER JOIN score ON score_author.score = score.id
  WHERE score.id = ?;
"""


all_prints = conn.execute_and_fetch_all(SQL_SELECT_ALL_PRINTS, (printIdArg,))

composers = []
for print_db in all_prints:
  (printId, printPartiture, editionId, editionName, publicationYear, scoreId, scoreName, scoreGenre, scoreKey, scoreIncipit, scoreYear) = print_db

  composers = []
  all_composers_db = conn.execute_and_fetch_all(SQL_SELECT_AUTHORS_FOR_SCORE, (scoreId,))
  for composer_db in all_composers_db:
    (personId, personName, personBorn, personDied) = composer_db
    composers += [Person(id = personId, name = personName, born = personBorn, died = personDied)]

conn.close()

print(to_pretty_json(composers))
