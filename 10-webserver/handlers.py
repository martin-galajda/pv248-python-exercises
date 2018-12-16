from aiohttp import web
import re
import copy
import os
import asyncio

def append_http_headers(env, headers):
  for header_key in headers:
    env["HTTP_" + re.sub('-', '_', header_key.upper())] = headers[header_key]

  return env

def normalize_http_headers(headers):
  normalized = {}
  for header_key in headers:
    normalized[header_key.lower()] = headers[header_key]

  return normalized

def merge_dicts(dict_one,  dict_two):
  merged = copy.deepcopy(dict_one)
  merged.update(dict_two)
  return merged


def process_cgi_env(request, server_name, port, req_method, path_to_script, query, req_path):
  headers = normalize_http_headers(request.headers)

  env = copy.deepcopy(os.environ)
  env['SERVER_SOFTWARE'] = 'aiohttp Python/3.6.4'
  env['SERVER_NAME'] = server_name
  env['GATEWAY_INTERFACE'] = 'CGI/1.1'
  env['SERVER_PROTOCOL'] = 'HTTP/1.0'
  env['SERVER_PORT'] = port
  env['REQUEST_METHOD'] = req_method
  env['PATH_INFO'] = ''
  env['PATH_TRANSLATED'] = req_path
  env['SCRIPT_NAME'] = path_to_script
  if query:
    env['QUERY_STRING'] = query

  # TODO: ?
  env['REMOTE_ADDR'] = request.remote if 'remote' in request else ''
  authorization = headers['authorization'] if 'authorization' in headers else ''
  if authorization:
    authorization = authorization.split()
    if len(authorization) == 2:
      import base64, binascii
      env['AUTH_TYPE'] = authorization[0]
      if authorization[0].lower() == "basic":
        try:
          authorization = authorization[1].encode('ascii')
          authorization = base64.decodebytes(authorization). \
            decode('ascii')
        except (binascii.Error, UnicodeError):
          pass
        else:
          authorization = authorization.split(':')
          if len(authorization) == 2:
            env['REMOTE_USER'] = authorization[0]

  env['CONTENT_TYPE'] = str(request.content_type if request.content_type else '')
  env['CONTENT_LENGTH'] = str(request.content_length if request.content_length else '')
  env['HTTP_REFERER'] = headers['referer'] if 'referer' in headers else ''

  if not env['CONTENT_TYPE']:
    env['CONTENT_TYPE'] = headers['content-type'] if 'content-type' in headers else ''
  if not env['CONTENT_LENGTH']:
    env['CONTENT_LENGTH'] = headers['content-length'] if 'content-length' in headers else ''

  env = append_http_headers(env, request.headers)

  print(env['CONTENT_TYPE'])
  print(env['CONTENT_LENGTH'])

  return env

def is_stop_header_line(line):
  if line.strip() == "" or line.strip() == "\n":
    return True
  return False

def safely_parse_header(line):
  REGEX = '(.+?):(.+)'
  match = re.match(REGEX, line)

  if match is None:
    return {}

  key, value = match.groups()
  new_header = {
    key: value
  }

  return new_header

async def handle_cgi_req(dir_path, request, port, method):
  filepath = '"' + dir_path + request.path + '"'

  process = await asyncio.create_subprocess_shell(
    filepath,
    # stdout must a pipe to be accessible as process.stdout
    stdout=asyncio.subprocess.PIPE,
    stdin=asyncio.subprocess.PIPE,
    # stdout=resp,
    env=process_cgi_env(request, 'localhost', port, method, filepath, request.query_string, request.path)
  )

  CHUNK_SIZE = 256


  if method == 'POST':
    if request.can_read_body:
      reader = request.content
      data = await reader.read()

      await process._feed_stdin(data)
      process.stdin.drain()
      process.stdin.close()

  headers_prepared = {}
  resp = None

  while resp is None:
    line = await process.stdout.readline()
    line = line.decode('utf-8')
    if is_stop_header_line(line):
      resp = web.StreamResponse(status=200, reason='OK', headers=headers_prepared)

    parsed_header = safely_parse_header(line)
    headers_prepared = merge_dicts(headers_prepared, parsed_header)

  # The StreamResponse is a FSM. Enter it with a call to prepare.
  await resp.prepare(request)

  while True:
    chunk = await process.stdout.read(CHUNK_SIZE)

    if not chunk:
      if process.returncode is None:
        # wait for one sec, maybe process is computing sth
        await asyncio.sleep(1)
        continue
      else:
        break
    await resp.write(bytes(chunk))


  return resp

def handle_static_req(dir_path, request):
  filepath = dir_path + request.path
  return web.FileResponse(filepath)

def make_get_handler(directory, port):
  dir_path = os.path.join(os.path.dirname(__file__), directory)
  async def get_handler(request):
    if not request.path.endswith('.cgi'):
      return handle_static_req(dir_path, request)
    else:
      return await handle_cgi_req(dir_path, request, port, 'GET')
  
  return get_handler

def make_post_handler(directory, port):
  dir_path = os.path.join(os.path.dirname(__file__), directory)
  async def post_handler(request):
    if request.path.endswith('.cgi'):
      return await handle_cgi_req(dir_path, request, port, 'POST')

    return web.Response(text="Not found.", status=404)
  
  return post_handler



