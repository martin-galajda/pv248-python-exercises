from aiohttp import web
from handlers import make_get_handler, make_post_handler
import sys

def main(args):
  port, directory = args
  print("port: %d " % int(port))
  app = web.Application()

  get_handler_cgi = make_get_handler(directory, port)
  post_handler_cgi = make_post_handler(directory, port)

  app.add_routes([web.get('/{tail:.*}', get_handler_cgi)])
  app.add_routes([web.post('/{tail:.*}', post_handler_cgi)])

  web.run_app(app, port = int(port))

if __name__ == "__main__":
  main(sys.argv[1:])
