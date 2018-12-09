from aiohttp import web
import json

def send_ok_response(json_data):
  response_body_bytes = bytes(json.dumps(json_data, indent=2), encoding='utf8')

  headers = {
    'Content-Type': 'application/json; charset=utf-8'
  }
  return web.Response(status=200, body=response_body_bytes, headers=headers)

def send_client_error_response(json_data):
  response_body_bytes = bytes(json.dumps(json_data, indent=2), encoding='utf8')

  headers = {
    'Content-Type': 'application/json; charset=utf-8'
  }

  return web.Response(status=400, body=response_body_bytes, headers=headers)


def make_start_handler(storage):
  async def get_start_handler(request):

    player_name = request.query['name'] if 'name' in request.query else ''

    game = storage.assign_game_to_player(player_name)

    return send_ok_response({
      'game': game['id']
    })

  
  return get_start_handler

def make_status_handler(storage):
  async def get_status_handler(request):
    params = request.query

    if not 'game' in params:
      return send_client_error_response({
        'reason': 'Missing game query parameter!'
      })

    try:
      game_id = int(params['game'])
    except Exception:
      return send_client_error_response({
        'reason': 'Invalid game query parameter! Expected positive integer.'
      })


    if not storage.game_exists(game_id):
      return send_client_error_response({
        'error': 'Game with id %d does not exist.' % game_id
      })

    status = storage.get_game_status(game_id)

    return send_ok_response(status)
  
  return get_status_handler

def make_play_handler(storage):
  async def get_play_handler(request):
    params = request.query

    if not 'game' in params:
      return send_client_error_response({
        'reason': 'Missing game query parameter!'
      })

    if not 'x' in params:
      return send_client_error_response({
        'reason': 'Missing x query parameter!'
      })

    if not 'y' in params:
      return send_client_error_response({
        'reason': 'Missing y query parameter!'
      })

    if not 'player' in params:
      return send_client_error_response({
        'reason': 'Missing player query parameter!'
      })

    try:
      game_id = int(params['game'])
      x = int(params['x'])
      y = int(params['y'])
      player_id = int(params['player'])
    except ValueError:
      return send_client_error_response({
        'reason': 'game, x, y, player must be integers!'
      })


    if not storage.game_exists(game_id):
      return send_client_error_response({
        'error': 'Game with id %d does not exist.' % game_id
      })

    return send_ok_response(storage.make_move(game_id, x, y, player_id))



  return get_play_handler
