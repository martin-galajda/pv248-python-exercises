from scorelib import load
import sys

if len(sys.argv) != 2:
  raise ValueError("Program expects 2 arguments")

filename = sys.argv[1]
print_instances = load(filename)

for print_instance in print_instances:
  print_instance.format()
  print("")
