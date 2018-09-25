import sys
import re


if len(sys.argv) != 3:
  raise ValueError("Program expects 3 arguments")

filename = sys.argv[1]
option = sys.argv[2]

regexps = {
  'composer': re.compile(r'Composer:\s(.*)$'),
  'composition_year': re.compile(r'Composition Year:\s(\d+)'),
  'composer_extra_stuff_2': re.compile(r'\(.*\)'),
  'composer_extra_stuff_1': re.compile(r'Composer:\s'),
}

stats = {
  'composers': {

  },
  'century': {

  }
}

def safe_print_str(str):
  decoded = str

  if hasattr(decoded, 'encode'):
    decoded = decoded.encode('utf-8')

  print(repr(decoded))


def read_file():
  lines = []

  with open(filename, 'r', errors='ignore') as f:
    read = 0
    for line in f:
      read += 1
      lines += [line]


  return lines



def parse_composers(composers_line):
  str_composers = re.sub(regexps['composer_extra_stuff_1'], '', composers_line)
  clean_composers = []
  parsed_composers = re.sub(regexps['composer_extra_stuff_2'], '', str_composers).split(';')
  for parsed_composer in parsed_composers:
    if len(parsed_composer.strip()) > 0:
      clean_composers += [parsed_composer.strip()]

  return clean_composers

def century_from_year(year):
  return (year) // 100 + 1    # 1 because 2017 is 21st century, and 1989 = 20th century

def parse_composition_year(composition_year_line):
  composition_year = regexps['composition_year'].match(composition_year_line).group(1)

  return int(composition_year.strip())

lines = read_file()

for line in lines:
  match_composer = regexps['composer'].match(line)
  match_composition_year = regexps['composition_year'].match(line)

  if match_composer:
    composers = parse_composers(line)
    for composer in composers:

      if not composer in stats['composers'].keys():
        stats['composers'][composer] = 1
      else:
        stats['composers'][composer] += 1


  if match_composition_year:
    century = century_from_year(parse_composition_year(line))
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
