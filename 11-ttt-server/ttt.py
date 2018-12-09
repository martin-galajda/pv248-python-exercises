from aiohttp import web
from handlers import make_play_handler, make_start_handler, make_status_handler
import sys
from game_storage import GameStorage

def main(args):
  port = args[0]
  print("port: %d " % int(port))
  app = web.Application()
  storage = GameStorage()

  app.add_routes([web.get('/start', make_start_handler(storage))])
  app.add_routes([web.get('/status', make_status_handler(storage))])
  app.add_routes([web.get('/play', make_play_handler(storage))])

  web.run_app(app, port = int(port))

if __name__ == "__main__":
  main(sys.argv[1:])
