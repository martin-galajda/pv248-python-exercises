
from db.conn import DbConnection

# -- Information about a printed score. This is always of a particular edition,
# -- so we refer to that. The partiture column describes whether a partiture is
# -- part of the print. In all the above tables, 'id' is an auto-generated
# -- primary key. For print, however, this is the value of the 'Print Number'
# -- field from the text file.
# create table print ( id integer primary key not null,
#                      partiture char(1) default 'N' not null, -- N = No, Y = Yes, P = Partial
#                      edition integer references edition( id ) );
class Print:
  db_conn = DbConnection.instance()

  def __init__(self, edition = None, print_id = None, partiture = None, id = None):
    self.edition = edition
    self.print_id = print_id
    self.partiture = partiture

  def format(self):
    print("Print Number: %d" % self.print_id)
    self.edition.print_composers()
    self.edition.print_composition_title()
    self.edition.print_genre()
    self.edition.print_key()
    self.edition.print_composition_year()
    self.edition.print_edition_name()
    self.edition.print_editors()
    self.edition.print_voices()
    print("Partiture: %s" % ("yes" if self.partiture == True else "no"))
    self.edition.print_incipit()

  def composition(self):
    return self.edition.composition

  def save_to_db(self):
    self.edition.upsert()

    INSERT_INTO_DB_SQL = """
      INSERT INTO print (id, partiture, edition)
      VALUES (?, ?, ?);
    """
    self.db_conn.insert(INSERT_INTO_DB_SQL, (self.print_id, ("Y" if self.partiture else "N"), self.edition.id))
