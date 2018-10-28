import sys
import  re
from to_pretty_json import to_pretty_json
import numpy as np
import numpy.linalg as linalg

if len(sys.argv) != 2:
  raise ValueError("Program expects 2 arguments")

equations_lines = []
filename = sys.argv[1]

with open(filename) as f:
  for line in f:
    if len(line.strip()) != 0:
      equations_lines += [line.strip()]


EQUATION_REGEXP = r'(.*)=(.*)'

parsed_equations = []
encountered_variables = 0
variable_name_to_idx = {}

for equations_line in equations_lines:
  matches = re.compile(EQUATION_REGEXP).match(equations_line)

  if matches is None:
    continue
  
  (left_side, right_side) = matches.groups()

  left_side = left_side.strip()
  right_side = right_side.strip()

  # get rid of multiple white spaces
  left_side = re.sub(r"\s+", ' ', left_side)

  # move `+` sign next to variable
  left_side = re.sub(r"\+\s+", '+', left_side)

  # move `-` sign next to variable
  left_side = re.sub(r'-\s+', '-', left_side)

  variables_with_coefficients = left_side.split(' ')
  eq_variables = {}
  
  for variable_with_coefficient in variables_with_coefficients:
    variable_with_coefficient = variable_with_coefficient.strip()
    regexp_variable = r'([+-]{1})?(\d+)?(.{1})'
    variable_match = re.match(regexp_variable, variable_with_coefficient)

    if variable_match is None:
      continue
    
    (sign, coefficient, regexp_variable_name) = variable_match.groups()

    sign = '+' if sign is None else sign
    coefficient = 1 if coefficient is None else int(coefficient)
    if sign == '-':
      coefficient *= -1

    if regexp_variable_name in eq_variables:
      curr_value = eq_variables[regexp_variable_name]['coefficient']
      new_value = coefficient + curr_value

      sign = '-' if new_value < 0 else '+'
      eq_variables[regexp_variable_name]['coefficient'] = new_value
      eq_variables[regexp_variable_name]['sign'] = sign
    else:
      eq_variables[regexp_variable_name] = {
        'name': regexp_variable_name,
        'sign': sign,
        'coefficient': int(coefficient),
      }

    if regexp_variable_name not in variable_name_to_idx:
      current_keys = list(variable_name_to_idx.keys())
      new_keys = current_keys + [regexp_variable_name]
      new_sorted_keys = sorted(new_keys)

      for idx, variable_name in enumerate(new_sorted_keys):
        variable_name_to_idx[variable_name] = idx

  constant = right_side.strip()
  constant = re.sub(r'\+\s+', '+', constant)
  constant = re.sub(r'-\s+', '-', constant)
  constant = int(constant)

  parsed_equations += [{
    'variables': eq_variables,
    'constant': constant
  }]

coefficient_matrix_for_equation = np.zeros((len(parsed_equations), len(variable_name_to_idx.keys())))
constants = np.zeros(len(parsed_equations))

for equation_idx, parsed_equation in enumerate(parsed_equations):
  for variable_name in variable_name_to_idx.keys():
    if variable_name in parsed_equation['variables']:
      variable = parsed_equation['variables'][variable_name]
      coefficient_matrix_for_equation[equation_idx][variable_name_to_idx[variable_name]] = variable['coefficient']


  constants[equation_idx] = parsed_equation['constant']

augmented_matrix = np.hstack((coefficient_matrix_for_equation, list(map(lambda c: [c], constants))))
augmented_rank = linalg.matrix_rank(augmented_matrix)
coeff_rank = linalg.matrix_rank(coefficient_matrix_for_equation)

rank_difference = augmented_rank - coeff_rank


number_of_variables = len(list(variable_name_to_idx.keys()))
if rank_difference != 0:
  print("no solution")
elif coeff_rank != number_of_variables:
  subspace_dimensions = number_of_variables - coeff_rank
  print("solution space dimension: " + str(subspace_dimensions))
else:
  coeff_results = linalg.solve(coefficient_matrix_for_equation, constants)

  variable_idx_to_name = {}

  for variable_name in variable_name_to_idx:
    variable_idx_to_name[variable_name_to_idx[variable_name]] = variable_name

  result_str = "solution: "
  for idx, coeff_result in enumerate(coeff_results):
    result_str += variable_idx_to_name[idx] + " = " + str(coeff_result) + ", "

  result_str = re.sub(r',\s$', '', result_str)

  print(result_str)

