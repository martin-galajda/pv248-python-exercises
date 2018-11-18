from datetime import datetime, timedelta
import re
import numpy as np
from enums import DataFrameEnums
import json
from build_dataframe import build_dataframe
import sys 

datetime_format = "%Y-%m-%d"
semester_start_date = '2018-09-17'

def default(o):
  if isinstance(o, np.int64): return int(o)
  if isinstance(o, np.float64): return float(o)
  if isinstance(o, np.int32): return int(o)
  if isinstance(o, np.float32): return float(o)

  raise TypeError


def days_between(d1, d2):
  if isinstance(d1, str):
    d1 = datetime.strptime(d1, datetime_format)
  if isinstance(d2, str):
    d2 = datetime.strptime(d2, datetime_format)
  return abs((d2 - d1).days)

def add_days(d1, num_of_days):
  d1 = datetime.strptime(d1, datetime_format)
  return d1 + timedelta(days=num_of_days)


def process_student(enhanced_students_dataframe, student):
  student_df = enhanced_students_dataframe.iloc[int(student)]
  
  regexp_extract_aggregated_date = r'%s%s(.*)' % (DataFrameEnums.AGGREGATED_PREFIX, DataFrameEnums.DATE_PREFIX)
  aggregated_cols_flags = [re.match(pattern=regexp_extract_aggregated_date, string = new_col) is not None for new_col in enhanced_students_dataframe.columns]
  aggregated_cols = enhanced_students_dataframe.columns[aggregated_cols_flags]
  
  aggregated_cols = sorted(aggregated_cols)
  dict_res = {}

  X = []
  y = []

  for aggregated_col in aggregated_cols:
    aggregated_col_key_match = re.match(pattern = regexp_extract_aggregated_date, string = aggregated_col)

    date = aggregated_col_key_match.groups()[0]
    curr_date_end = days_between(semester_start_date, date)
    
    X += [[curr_date_end]]
    y += [student_df[aggregated_col]]

  
  slope = "inf"
  if y[-1] > 0:
    slope, _, _, _ = np.linalg.lstsq(X, y)
    slope = slope[0]
    # print(X)
    # print(y)


#         print(list(zip(X, y)))

#         regressor = LinearRegression(fit_intercept=False).fit(X,y)
      
#         plt.plot(X, y, 'bo')
#         plt.plot(X, a * X, 'r-')
#         plt.show()
      #print(list(map(lambda x: x[0], X)))
      #print(len(list(map(lambda x: x[0], X))))
#         print(len(y))
      
#         print(y)
      
    date_for_16 = None
    date_for_20 = None

    i = 1
    while date_for_16 is None or date_for_20 is None:
      # value_predicted = regressor.predict([[i]])
      value_predicted = slope * i
      if value_predicted >= 16.0 and date_for_16 is None:
        date_for_16 = add_days(semester_start_date, i).strftime(datetime_format)

      if value_predicted >= 20.0 and date_for_20 is None:
        date_for_20 = add_days(semester_start_date, i).strftime(datetime_format)

      i += 1
          
  else:
    date_for_16 = "inf"
    date_for_20 = "inf"

  regexp_extract_aggregated_date = r'%s(.*)' % (DataFrameEnums.EXERCISES_PREFIX)
  exercise_cols_flags = [re.match(pattern=regexp_extract_aggregated_date, string = new_col) is not None for new_col in enhanced_students_dataframe.columns]
  exercise_cols = enhanced_students_dataframe.columns[exercise_cols_flags]

  dict_res = {
    'mean': student_df[exercise_cols].mean(),
    'median': np.median(student_df[exercise_cols]),
    'passed': np.sum(student_df[exercise_cols] > 0),
    'total': np.sum(student_df[exercise_cols]),
    'regression slope': slope,
    'date 16': date_for_16,
    'date 20': date_for_20,
  }

  print(json.dumps(dict_res, indent=2, default=default))


def main(args):
  filename, student = args
  # TODO: Add support for "average" STUDENT !!!
  # TODO: Also student is probably id which can be found in "student" column not its position!!! CHECK
  students_df = build_dataframe(filename)
  process_student(students_df, student)


if __name__ == "__main__":
  main(sys.argv[1:])
  # for i in range(0, 60):
  #   main([sys.argv[1], i])
