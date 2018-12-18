import sys
from urllib import request, parse
import json
import os
from time import sleep
import re

PLAYER_MARKS = {
  0: '_',
  1: 'x',
  2: 'o'
}

def safely_parse_int(str):
  try:
    input = int(str)
    return input
  except Exception:
    return None

def parse_json_response(response):
  try:
    str_response = response.read().decode('utf-8')
    return json.loads(str_response)
  except Exception as e:
    print(e)
    return None

def get_list_of_games(server_address):
  response = request.urlopen(server_address + "/list")

  games = parse_json_response(response)

  return list(filter(lambda game: game['board_is_empty'] == True, games))

def get_game_status(server_address, game_id):
  response = request.urlopen(server_address + ("/status?game=%d" % (game_id,)))

  games = parse_json_response(response)
  return games

def create_new_game(server_address, game_name):
  response = request.urlopen(server_address + ("/start?name=%s" % (parse.quote(game_name),)))
  game = parse_json_response(response)
  return game

def make_move(server_address, game_id, player_idx, coordinates):
  try:
    x, y = coordinates
    url = server_address + ("/play?game=%d&x=%d&y=%d&player=%d" % (game_id,x,y, player_idx))
    response = request.urlopen(url)
    game = parse_json_response(response)
    return game
  except:
    print("invalid input")

def parse_make_move_input(player_mark):
  input_parsed = False
  while not input_parsed:
    input_parsed = True
    user_input = input("your turn (%s): " % (player_mark,))

    parts = user_input.strip().split(' ')

    if len(parts) != 2:
      input_parsed = False
      print("invalid input")
      continue

    x = safely_parse_int(parts[0].strip())
    y = safely_parse_int(parts[1].strip())

    if x == None or y == None:
      input_parsed = False
    elif x >= 3 or x < 0:
      input_parsed = False
    elif y >= 3 or y < 0:
      input_parsed = False


    if not input_parsed:
      x = None
      y = None
      print("invalid input")


  return (x, y)

def show_games(games):
  for game in games:
    print("%d %s" % (game['id'], game['name']))

  return games

def print_board(game_status):
  str = ""

  if 'board' in game_status:
    board = game_status['board']
    for row in board:
      for col in row:
        mark = PLAYER_MARKS[col]
        str += "%s" % (mark,)

      str += os.linesep
    print(str.strip(os.linesep))


def run_game_loop(server_address):
  games = get_list_of_games(server_address)
  games = show_games(games)

  allowed_game_ids = list(map(lambda x: x['id'], games))

  game_to_join = None
  game_joined = None
  while not game_joined:
    game_to_join = input("Enter 'id' of the game you would like to join or type 'new' for starting new one:\n")

    if game_to_join.strip().startswith('new'):
      new_game_name = re.sub('new', '', game_to_join).strip()
      game_joined = create_new_game(server_address, new_game_name)
      player_idx = 1
      player_mark = PLAYER_MARKS[player_idx]
    else:
      game_to_join = safely_parse_int(game_to_join.strip())

      valid_input = False
      for allowed_game_id in allowed_game_ids:
        if allowed_game_id == game_to_join:
          valid_input = True

      if not valid_input:
        game_to_join = None
        print("invalid input")
        continue

      game_joined = {
        'id': game_to_join
      }
      player_idx = 2
      player_mark = PLAYER_MARKS[player_idx]

  game_status = get_game_status(server_address, game_joined['id'])
  waiting_for_other_played_logged = False
  while 'winner' not in game_status:
    if game_status['next'] != player_idx and not waiting_for_other_played_logged:
      print_board(game_status)
      print("waiting for the other player")
      waiting_for_other_played_logged = True

    if game_status['next'] == player_idx:
      print_board(game_status)
      move_input = parse_make_move_input(player_mark)
      move_result = make_move(server_address, game_joined['id'], player_idx, move_input)

      if move_result is not None:
        if move_result['status'] == "bad":
          print("invalid input")
      waiting_for_other_played_logged = False


    sleep(1)
    game_status = get_game_status(server_address, game_joined['id'])


  winner = game_status['winner']
  if winner == player_idx:
    print("you win")
  elif winner != 0:
    print("you lose")
  else:
    print("draw")

def main(args):
  host, port = args
  server_address = "http://" + host + ":" + str(port)

  run_game_loop(server_address)


if __name__ == "__main__":
  main(sys.argv[1:])
