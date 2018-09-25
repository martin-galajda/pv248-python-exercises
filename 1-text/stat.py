import sys
import re

if len(sys.argv) != 3:
  raise ValueError("Program expects 3 arguments")

filename = sys.argv[1]
option = sys.argv[2]

regexps = {
  # Determine if current line is line for composer
  'composer': re.compile(r'Composer:\s(.*)$'),

  # Determine if current line is composition year
  # and if composition year contains value (expecting at least one number after first white space)
  'composition_year': re.compile(r'Composition Year:\s(\d+)'),

  # Possibly match exact century stated in composition year (e.g. "Composition Year: 17th century")
  'composition_year_explicit_century': re.compile(r'Composition Year:\s([\d]{1,4})th'),

  # Removing "dd. mm. " from "Composition Year: dd. mm. yyyy"
  'composition_year_extra_stuff': re.compile(r'[\d]{1,2}\.\s'),

  # Removing "(<stuff_inside_parentheses>)" from "Composer: Name (YYYY-YYYY); Name2 (YYYY-YYYY)"
  'composer_extra_stuff_2': re.compile(r'\(.*?\)'),

  # Removing "Composer " line containing composer name(s)
  'composer_extra_stuff_1': re.compile(r'Composer:\s'),
}

# Initialize empty stats
stats = {
  'composers': {},
  'century': {}
}

# Solve problems with encoding unicode characters in python 3.6.4 when printing to console
def safe_print_str(str):
  decoded = str

  if hasattr(decoded, 'encode'):
    decoded = decoded.encode('utf-8')

  print(repr(decoded))

# Read whole file inside array
def read_file():
  lines = []

  with open(filename, 'r') as f:
    read = 0
    for line in f:
      read += 1
      lines += [line]

  return lines

# Parse line containing info about composers into array
def parse_composers(composers_line):
  # Remove "Composer: " from line
  str_composers = re.sub(regexps['composer_extra_stuff_1'], '', composers_line)
  clean_composers = []

  # Remove parentheses with text inside them from the line and split it by ";"
  parsed_composers = re.sub(regexps['composer_extra_stuff_2'], '', str_composers).split(';')

  for parsed_composer in parsed_composers:
    if len(parsed_composer.strip()) > 0:
      clean_composers += [parsed_composer.strip()]

  return clean_composers

# Convert year to century
def century_from_year(year):
  return (year) // 100 + 1    # 1 because 2017 is 21st century, and 1989 = 20th century

def parse_composition_century(composition_year_line):
  # remove days & months from line if it contains it ("dd. mm. YYYY" -> "YYYY")
  preprocessed_year_line = regexps['composition_year_extra_stuff'].sub('', composition_year_line)

  explicit_century_match = regexps['composition_year_explicit_century'].match(preprocessed_year_line)
  if explicit_century_match:
    return int(explicit_century_match.group(1))

  composition_year = regexps['composition_year'].match(preprocessed_year_line).group(1)
  year = int(composition_year.strip())
  return century_from_year(year)

lines = read_file()

for line in lines:
  matches_composer_line = regexps['composer'].match(line)
  matches_composition_year_line = regexps['composition_year'].match(line)

  if matches_composer_line:
    composers = parse_composers(line)
    for composer in composers:
      if not composer in stats['composers'].keys():
        stats['composers'][composer] = 1
      else:
        stats['composers'][composer] += 1


  if matches_composition_year_line:
    century = parse_composition_century(line)
    if not century in stats['century'].keys():
      stats['century'][century] = 1
    else:
      stats['century'][century] += 1

if option == "century":
  for k, v in stats['century'].items():
    print("%dth century: %d" % (k, v))

if option == "composer":
  for k, v in stats['composers'].items():
    print(k + ": " + str(v))
