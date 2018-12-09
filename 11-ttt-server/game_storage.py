import numpy as np

def check_if_player_won(game, player_idx):
  player_key = 'player_%d' % player_idx
  player_1_info = game[player_key]

  if len(np.where(player_1_info[PRECOMPUTED_ROWS_SCORE_KEY] == 3)[0]) > 0:
    return True
  if len(np.where(player_1_info[PRECOMPUTED_COLS_SCORE_KEY] == 3)[0]) > 0:
    return True
  if len(np.where(player_1_info[PRECOMPUTED_DIAGONALS_SCORE_KEY] == 3)[0]) > 0:
    return True

  return False


def get_game_result(game):
  board = game['board']

  if check_if_player_won(game, 1) == True:
    return {
      'winner': 1
    }

  if check_if_player_won(game, 2) == True:
    return {
      'winner': 2
    }

  is_board_full = len(np.where(board == 0)[0]) == 0

  if is_board_full:
    return {
      'winner': 0
    }

  return {
    'board': board.tolist(),
    'next': game[NEXT_PLAYER_KEY]
  }

PRECOMPUTED_ROWS_SCORE_KEY = 'precomputed_rows_score'
PRECOMPUTED_COLS_SCORE_KEY = 'precomputed_cols_score'
PRECOMPUTED_DIAGONALS_SCORE_KEY = 'precomputed_diagonals_score'
NEXT_PLAYER_KEY = 'next_player'

class GameStorage():
  def __init__(self):
    self.games = {}
    self.next_game_id = 0

  def create_new_game(self, game_name):
    new_game = {
      'id': self.next_game_id,
      'board': np.zeros(9, dtype=np.int32).reshape(3, 3),
      'name': game_name,
      'player_1': {
        PRECOMPUTED_ROWS_SCORE_KEY: np.zeros(3, dtype=np.int32),
        PRECOMPUTED_COLS_SCORE_KEY: np.zeros(3, dtype=np.int32),
        PRECOMPUTED_DIAGONALS_SCORE_KEY: np.zeros(2, dtype=np.int32),
      },
      'player_2': {
        PRECOMPUTED_ROWS_SCORE_KEY: np.zeros(3, dtype=np.int32),
        PRECOMPUTED_COLS_SCORE_KEY: np.zeros(3, dtype=np.int32),
        PRECOMPUTED_DIAGONALS_SCORE_KEY: np.zeros(2, dtype=np.int32),
      },
      NEXT_PLAYER_KEY: 1,
    }
    self.games[self.next_game_id] = new_game
    self.next_game_id += 1

    return new_game

  def get_game_by_id(self, game_id):
    if game_id in self.games:
      return self.games[game_id]

    return None

  def _update_game(self, game, x, y, player_id):
    player_key = 'player_%d' % player_id
    board = game['board']

    board[x, y] = player_id

    game[player_key][PRECOMPUTED_ROWS_SCORE_KEY][x] += 1
    game[player_key][PRECOMPUTED_COLS_SCORE_KEY][y] += 1

    if x == y:
      game[player_key][PRECOMPUTED_DIAGONALS_SCORE_KEY][0] += 1

    if (x == 0 and y == 2) or (x == 1 and y == 1) or (x == 2 and y == 0):
      game[player_key][PRECOMPUTED_DIAGONALS_SCORE_KEY][1] += 1

    game[NEXT_PLAYER_KEY] = 2 if player_id == 1 else 1

  def make_move(self, game_id, x, y, player_id):
    if x < 0 or x >= 3:
      return {
        'message': "Invalid x. Must be from interval [0,2].",
        'status': "bad"
      }

    if y < 0 or y >= 3:
      return {
        'message': "Invalid y. Must be from interval [0,2].",
        'status': "bad"
      }

    game = self.games[game_id]

    next_player = game[NEXT_PLAYER_KEY]

    if next_player != player_id:
      return {
        'message': "Not your move.",
        'status': "bad"
      }

    game_result = get_game_result(game)
    if not 'board' in game_result:
      return {
        'message': "Game already ended.",
        'status': "bad"
      }

    if game['board'][x, y] != 0:
      return {
        'message': "The field is already occupied.",
        'status': "bad"
      }
    
    self._update_game(game, x, y, player_id)
    return {
      'status': "ok"
    }

  def game_exists(self, game_id):
    return game_id in self.games

  def get_game_status(self, game_id):
    game = self.get_game_by_id(game_id)

    return get_game_result(game)
