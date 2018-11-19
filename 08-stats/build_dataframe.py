import pandas
from enums import DataFrameEnums
import numpy as np
import re

def with_aggregated_columns(students_dataframe, columns_without_student_col):
  column_regexp = r'([\d]{4}-[\d]{1,2}-[\d]{1,2})\/([\d]{1,2})'

  enhanced_students_dataframe = students_dataframe.copy()
  curr_values = np.zeros(students_dataframe.shape[0])
  for orig_col in sorted(columns_without_student_col):

    orig_col_date, orig_col_exercise = re.match(pattern=column_regexp, string=orig_col).groups()
    
    new_col_date = DataFrameEnums.DATE_PREFIX + orig_col_date
    new_col_exercise = DataFrameEnums.EXERCISES_PREFIX + orig_col_exercise
    new_col_orig = DataFrameEnums.DEADLINES_PREFIX + orig_col

    curr_values += students_dataframe[orig_col]
    
    if not new_col_date in enhanced_students_dataframe:
      enhanced_students_dataframe[new_col_date] = students_dataframe[orig_col]
    else:
      enhanced_students_dataframe[new_col_date] += students_dataframe[orig_col]
    
    if not new_col_exercise in enhanced_students_dataframe:
      enhanced_students_dataframe[new_col_exercise] = students_dataframe[orig_col]
    else:
      enhanced_students_dataframe[new_col_exercise] += students_dataframe[orig_col]

    enhanced_students_dataframe[new_col_orig] = students_dataframe[orig_col]
    enhanced_students_dataframe[DataFrameEnums.AGGREGATED_PREFIX + new_col_date] = curr_values
    enhanced_students_dataframe[DataFrameEnums.AGGREGATED_PREFIX + new_col_exercise] = curr_values


  # append values for average student as last row
  avg_student_row_idx = enhanced_students_dataframe.shape[0]
  enhanced_students_dataframe.loc[avg_student_row_idx] = np.zeros(enhanced_students_dataframe.shape[1])
  enhanced_students_dataframe.loc[avg_student_row_idx][DataFrameEnums.STUDENT_COL_NAME] = DataFrameEnums.SPECIAL_AVERAGE_STUDENT_ROW_ID

  curr_value = 0
  for orig_col in sorted(columns_without_student_col):
    orig_col_date, orig_col_exercise = re.match(pattern=column_regexp, string=orig_col).groups()

    new_col_date = DataFrameEnums.DATE_PREFIX + orig_col_date
    new_col_exercise = DataFrameEnums.EXERCISES_PREFIX + orig_col_exercise
    new_col_orig = DataFrameEnums.DEADLINES_PREFIX + orig_col
    
    curr_value += enhanced_students_dataframe[orig_col].mean()

    enhanced_students_dataframe.loc[avg_student_row_idx][orig_col] = enhanced_students_dataframe[orig_col].mean()
    enhanced_students_dataframe.loc[avg_student_row_idx][new_col_orig] = enhanced_students_dataframe[orig_col].mean()

    select_avg_student_row_flags = enhanced_students_dataframe.index.isin([avg_student_row_idx])

    enhanced_students_dataframe.loc[avg_student_row_idx][new_col_date] = enhanced_students_dataframe[~select_avg_student_row_flags][new_col_date].mean()
    enhanced_students_dataframe.loc[avg_student_row_idx][new_col_exercise] = enhanced_students_dataframe.loc[~select_avg_student_row_flags][new_col_exercise].mean()

    enhanced_students_dataframe.loc[avg_student_row_idx][DataFrameEnums.AGGREGATED_PREFIX + new_col_date] = curr_value
    enhanced_students_dataframe.loc[avg_student_row_idx][DataFrameEnums.AGGREGATED_PREFIX + new_col_exercise] = curr_value

  return enhanced_students_dataframe



def build_dataframe(filename):
  with open(filename, 'r') as file:
    students_dataframe = pandas.read_csv(file)
      
  columns_without_student_col = students_dataframe.columns[students_dataframe.columns != DataFrameEnums.STUDENT_COL_NAME]
  columns_without_student_col = sorted(columns_without_student_col)

  return with_aggregated_columns(students_dataframe, columns_without_student_col)

