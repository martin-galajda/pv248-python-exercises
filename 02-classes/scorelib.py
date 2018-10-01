import re

print_empty_lines = True

class Voice:
  def __init__(self, name, range = None):
    self.name = name
    self.range = range
  
  def format(self):
    formatted_str = ""

    if self.range:
      formatted_str += self.range + ", "

    return formatted_str + self.name

class Person:
  def __init__(self, name, born, died):
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

class Composition:
  def __init__(self, name = None, incipit = None, key = None, genre = None, year = None, voices = [], authors = []):
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
      print("Voice %d: %s" % (voice_idx + 1, voice.format()))

class Edition:
  def __init__(self, composition, authors = [], name = None):
    self.composition = composition
    self.authors = authors
    self.name = name

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
      editors_str = ','.join([editor.format() for editor in self.authors])
      print("Editor: %s" % editors_str)
  def print_voices(self):
    self.composition.print_voices()
  def print_incipit(self):
    if self.composition.incipit or print_empty_lines:
      print("Incipit: %s" % (self.composition.incipit if self.composition.incipit is not None else ""))

  def print_composition_title(self):
    if self.composition.name or print_empty_lines:
      print("Title: %s" % (self.composition.name if self.composition.name is not None else ""))


class Print:
  def __init__(self, edition, print_id, partiture):
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

def parse_composition_name(print_instance, title_str):
  print_instance.composition().name = title_str.strip()

def parse_print_number(print_instance, number_str):
  print_instance.print_id = int(number_str.strip())

def parse_composition_year(print_instance, composition_year_str):
  regexp_extract = re.compile(r'(\d+)--(\d+)|.*(\d{4})')
  valid_match = regexp_extract.match(composition_year_str)
  if valid_match is not None:
    _, __, group3 = valid_match.groups()
    print_instance.composition().year = int(group3) if group3 is not None else None

def parse_voice(print_instace, voice_str):
  range_voice_regexp = r'(.*--.*?)[,;]\s(.+)'

  match_range_voice = re.compile(range_voice_regexp).match(voice_str)
  voice = None
  if match_range_voice is not None:
    matched_groups = match_range_voice.groups()
    range = matched_groups[0]
    voice_name = matched_groups[1]

    voice = Voice(range=range, name=voice_name)
  else:
    voice = Voice(name=voice_str)

  if voice is not None:
    print_instace.edition.composition.voices += [voice]

def parse_key(print_instance, key_str):
  print_instance.edition.composition.key = key_str.strip()

def parse_genre(print_instance, genre_str):
  print_instance.edition.composition.genre = genre_str.strip()

def parse_edition_name(print_instance, name_str):
  print_instance.edition.name = name_str.strip()

def parse_partiture(print_instance, partiture_str):

  if re.search(r'yes', partiture_str) is not None:
    print_instance.partiture = True
  else:
    print_instance.partiture = False

def parse_incipit(print_instance, incipit_str):
  if print_instance.edition.composition.incipit is None:
    print_instance.edition.composition.incipit = incipit_str.strip()

def parse_composers(print_instance, composer_line):
  regexps_years = r'\((\d{4})-{1,2}(\d{4})\)|\(\+(\d{4})\)|\(\*(\d{4})\)|\(.*-{1,2}(\d{4})\)|\((\d{4})-{1,2}.*\)'
  composers = composer_line.split(';')

  composer_people = []
  for composer_str in composers:
    years_match = re.search(regexps_years, composer_str)
    born = None
    died = None
    if years_match is not None:
      born1, died1, died2, born2, died3, born3 = years_match.groups()

      born = born1 or born2 or born3
      died = died1 or died2 or died3

    composer_name = re.sub(regexps_years, "", composer_str).strip()

    composer_people += [Person(name=composer_name, born = born, died = died)]

  print_instance.edition.composition.authors = composer_people


def parse_editors(print_instance, editor_str):
  editor_str = editor_str.strip()
  token_names = editor_str.split(',')

  invalid_part_regex_1 = r'continuo\sby\s'
  invalid_part_regex_2 = r'continuo:\s'
  names = []

  if len(token_names) > 2:
    if len(token_names) % 2 == 1:
      print("Invalid !!!")
    for i in range(len(token_names)):
      if i % 2 == 1:
        names += [token_names[i-1] + token_names[i]]
  elif len(token_names) == 2:
    first_token_name = token_names[0]
    snd_token_name = token_names[1]

    if len(first_token_name.strip().split(' ')) > 1 or len(snd_token_name.strip().split(' ')) > 1:
      names += [(token_names[0]).strip()]
      names += [(token_names[1]).strip()]

    else:
      names += [editor_str.strip()]
  else:
    names += [editor_str.strip()]
    
  people = []
  for name in names:
    fixed_name = re.sub(invalid_part_regex_1, "", name)
    fixed_name = re.sub(invalid_part_regex_2, "", fixed_name)
    people += [Person(name=fixed_name, born = None, died = None)]

  print_instance.edition.authors = people

REGEXPS = [
  (parse_print_number, r'Print Number:\s(.+)$'),
  (parse_genre, r'Genre:\s(.+)$'),
  (parse_key, r'Key:\s(.+)$'),
  (parse_edition_name, r'Edition:\s(.+)$'),
  (parse_voice, r'Voice [\d]+:\s(.+)$'),
  (parse_partiture, r'Partiture:\s(.+)$'),
  (parse_incipit, r'Incipit:\s(.+)$'),
  (parse_composers, r'Composer:\s(.+)$'),
  (parse_composition_name, r'Title:\s(.+)$'),
  (parse_composition_year, r'Composition Year:\s(.+)$'),
  (parse_editors, r'Editor:\s(.+)$')
]

class ScoreLibParser:
  def __init__(self, filename = "./scorelib.txt"):
    self.filename = filename
    self.print_blocks = []

  def load_print_blocks(self):
    self.print_blocks = []
    new_print_block = []
    with open(self.filename) as f:
      for line in f:
        if len(line.strip()) == 0:
          if len(new_print_block) >=1:
            self.print_blocks += [new_print_block]
          new_print_block = []
        else:
          new_print_block += [line]
    self.print_blocks += [new_print_block]


  def parse_prints(self):
    self.load_print_blocks()

    prints = []
    for print_block_lines in self.print_blocks:
      prints += [self.parse_print_block(print_block_lines)]

    return prints

  def parse_print_block(self, print_block_lines):
    composition = Composition(voices=[])
    edition = Edition(composition = composition)
    print_instance = Print(edition = edition, print_id = None, partiture = None)

    for line in print_block_lines:
      for regexp_config in REGEXPS:
        parse_method, regexp = regexp_config

        regex_match = re.match(regexp, line)
        if regex_match is not None:
          parse_method(print_instance, regex_match.group(1))

    return print_instance


def load(filename):
  parser = ScoreLibParser(filename = filename)

  return parser.parse_prints()
