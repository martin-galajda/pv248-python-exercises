import sys
from enums import DataFrameEnums, ModeEnums
from build_dataframe import build_dataframe
import re 
import numpy as np
import json

def default(o):
  if isinstance(o, np.int64): return int(o)
  if isinstance(o, np.float64): return float(o)
  if isinstance(o, np.int32): return int(o)
  if isinstance(o, np.float32): return float(o)

  raise TypeError


def get_mode_prefix(mode):
  if mode == ModeEnums.DATES:
    return DataFrameEnums.DATE_PREFIX

  if mode == ModeEnums.DEADLINES:
    return DataFrameEnums.DEADLINES_PREFIX

  if mode == ModeEnums.EXERCISES:
    return DataFrameEnums.EXERCISES_PREFIX

  raise Exception("Invalid mode: '%s'" % mode)

def main(args):
  filename, mode = args
  mode_prefix = get_mode_prefix(mode)

  students_df = build_dataframe(filename, with_average_student=False)
  regexp_extract_key = r"%s(.*)"

  new_cols_flags = [re.match(pattern=regexp_extract_key % mode_prefix, string = new_col) is not None for new_col in students_df.columns]
  new_cols = students_df.columns[new_cols_flags]


  dict_res = {}
  for new_col in new_cols:
    new_col_key_match = re.match(pattern = regexp_extract_key % mode_prefix, string = new_col)

    key = new_col_key_match.groups()[0]
    dict_res[key] = {
      'mean': students_df[new_col].mean(),
      'median': students_df[new_col].median(),
      'first': students_df[new_col].quantile(q = 0.25),
      'last': students_df[new_col].quantile(q = 0.75),
      'passed': np.sum(students_df[new_col] > 0)
    }
  
  print(json.dumps(dict_res, indent=2, default=default))



if __name__ == "__main__":
  main(sys.argv[1:])
