from aiohttp import web
from handlers import make_get_handler, make_post_handler
import sys

def main(args):
  port, forward_site = args
  print("port: %d " % int(port))
  app = web.Application()

  get_handler = make_get_handler(forward_site)

  app.add_routes([web.get('/{whatever}', get_handler)])
  app.add_routes([web.get('/', get_handler)])
  app.add_routes([web.post('/', make_post_handler())])

  web.run_app(app, port = int(port))

if __name__ == "__main__":
  main(sys.argv[1:])
