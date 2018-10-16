from db.conn import DbConnection
import re
print_empty_lines = True

# -- Auxiliary table. See 'edition'.
# create table edition_author( id integer primary key not null,
#                              edition integer references edition( id ) not null,
#                              editor integer references person( id ) not null );


# -- Multiple editions of a given score may exist, and any given edition could
# -- have multiple editors. Like with score -- author relationship, this is M:N
# -- and stored in an auxiliary table, edition_author.
# create table edition ( id integer primary key not null,
#                        score integer references score( id ) not null,
#                        name varchar,
#                        year integer );

class Edition:
  db_conn = DbConnection.instance()
  def __init__(self, composition, authors = [], name = None):
    self.composition = composition
    self.authors = authors
    self.name = name
    self.year = None

  def print_composers(self):
    if len(self.composition.authors) > 0 or print_empty_lines:
      composers_str = "; ".join([composer.format() for composer in self.composition.authors])
      print("Composer: %s" % composers_str)
  def print_genre(self):
    if self.composition.genre is not None or print_empty_lines:
      print("Genre: %s" % (self.composition.genre if self.composition.genre is not None else ""))
  def print_key(self):
    if self.composition.key is not None or print_empty_lines:
      print("Key: %s" % (self.composition.key if self.composition.key is not None else ""))
  def print_composition_year(self):
    if self.composition.year is not None or print_empty_lines:
      print("Composition Year: %s" % (self.composition.year if self.composition.year is not None else "" ))
  def print_edition_name(self):
    if self.name is not None or print_empty_lines:
      print("Edition: %s" % (self.name if self.name is not None else ""))
  def print_editors(self):
    if len(self.authors) > 0 or print_empty_lines:
      editors_str = ', '.join([editor.format() for editor in self.authors])
      print("Editor: %s" % editors_str)
  def print_voices(self):
    self.composition.print_voices()
  def print_incipit(self):
    if self.composition.incipit or print_empty_lines:
      print("Incipit: %s" % (self.composition.incipit if self.composition.incipit is not None else ""))

  def print_composition_title(self):
    if self.composition.name or print_empty_lines:
      print("Title: %s" % (self.composition.name if self.composition.name is not None else ""))

  def find_from_db(self):
    SELECT_SQL = """
      SELECT id, score, name
      FROM edition
      WHERE name = ? AND score = ?;
    """

    values = ()
    if self.name is None:
      re.compile(r'name = \?').sub('name is NULL', SELECT_SQL)
    else:
      values += (self.name,)

    values += (self.composition.id, )

    data_from_db = self.db_conn.execute_and_fetch_one(SELECT_SQL, values)
    if data_from_db is not None:
      self.id = data_from_db[0]
    return data_from_db

  def has_different_authors(self, other_edition_id):
    SELECT_AUTHORS_FROM_DB = """
      SELECT person.id, person.name
      FROM person
      INNER JOIN edition_author ON edition_author.editor = person.id
      WHERE edition_author.edition = ?;
    """
    authors_from_db = self.db_conn.execute_and_fetch_all(SELECT_AUTHORS_FROM_DB, (other_edition_id,))

    matching_authors = 0
    total_author_rows = 0
    for author_row_from_db in authors_from_db:
      matches_author = any(map(lambda a: a.id == author_row_from_db[0], self.authors))
      if matches_author:
        matching_authors += 1
      total_author_rows += 1

    has_different_authors = len(self.authors) != matching_authors or total_author_rows != len(self.authors)
    if has_different_authors:
      self.print_editors()

    return has_different_authors

  def insert(self):
    INSERT_SQL = """
      INSERT INTO edition (score, name, year)
      VALUES (?, ?, ?);
    """

    inserted_id = self.db_conn.insert(INSERT_SQL, (self.composition.id, self.name, self.year))
    self.id = inserted_id

    for author in self.authors:
      author.attach_to_edition(self.id)

  def upsert(self):
    for author in self.authors:
      author.upsert()

    self.composition.upsert()

    SELECT_EDITION_SQL = """
      SELECT id, name, score
      FROM edition
      WHERE name = ? AND score = ?;
    """

    edition_data_from_db = self.db_conn.execute_and_fetch_one(SELECT_EDITION_SQL, (self.name, self.composition.id))

    if edition_data_from_db is not None:
      if self.has_different_authors(edition_data_from_db[0]):
        self.insert()
      else:
        self.id = edition_data_from_db[0]
        print("Edition - using already found edition: " + str((self.id, self.name)))
    else:
      self.insert()


