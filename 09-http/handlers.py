from aiohttp import web
import urllib.request
import json
import re
import copy
import ssl, socket


DEFAULT_TIMEOUT = 1
DEFAULT_POST_HEADERS = {
  'Content-Type': 'application/json; charset=utf-8'
}

OVERRIDE_POST_HEADERS = {
  'Accept-Encoding': 'identity'
}

OVERRIDE_GET_HEADERS = {
  'Accept-Encoding': 'identity'
}

DEFAULT_JSON_POST_HANDLER = {
  'timeout': DEFAULT_TIMEOUT,
  'type': 'GET',
  'content': None,
  'url': None,
  'headers': DEFAULT_POST_HEADERS,
}

def validate_ssl(response):
  host = urllib.parse.urlparse(response.geturl()).netloc
  port = 443
  ctx = ssl.create_default_context()
  s = ctx.wrap_socket(socket.socket(), server_hostname=host)

  try:
    s.connect((host, port))
  except:
    return False, None

  certificate = s.getpeercert()
  names_list = [subjectAltName[1] for subjectAltName in certificate['subjectAltName']]
  return True, names_list


def parse_response_headers(response):
  parsed_headers = {}
  for header in response.getheaders():
    header_key, header_value = header

    parsed_headers[header_key] = header_value

  return parsed_headers

def merge_dicts(dict_one,  dict_two):
  merged = copy.deepcopy(dict_one)
  merged.update(dict_two)
  return merged

def send_response(body_content_dict):
  headers = []
  if 'code' not in body_content_dict:
    body_content_dict['code'] = 200
  response_body_bytes = bytes(json.dumps(body_content_dict, indent=2), encoding='utf8')

  headers += [('Content-Type', 'application/json; charset=utf-8')]

  return web.Response(body=response_body_bytes, headers=headers)

def forward_request(url, headers, timeout, body, method):
  if not re.match('http://.*|https://.*', url):
    url = 'http://' + url

  # disable SSL validation (for invalid SSL certificates)
  request_ctx = ssl.create_default_context()
  request_ctx.check_hostname = False
  request_ctx.verify_mode = ssl.CERT_NONE
  urlopen_kargs = {
    'context': request_ctx,
    'timeout': timeout
  }

  if method == "POST":
    headers = merge_dicts(DEFAULT_POST_HEADERS, headers)
    headers = merge_dicts(headers, OVERRIDE_POST_HEADERS)
    req = urllib.request.Request(url, headers=headers)

    json_data = json.dumps(body)
    json_data_bytes = json_data.encode('utf-8')  # needs to be bytes
    req.add_header('Content-Length', len(json_data_bytes))

    urlopen_args = [req, json_data_bytes]
  elif method == "GET":
    headers = merge_dicts(headers, OVERRIDE_GET_HEADERS)
    req = urllib.request.Request(url, headers=headers)
    urlopen_args = [req]

  else:
    return send_response({
      'code': 'invalid json'
    })

  try:
    response = urllib.request.urlopen(*urlopen_args, **urlopen_kargs)
  except Exception as e:
    print(str(e))
    return send_response({
      'code': 'timeout'
    })

  response_content = response.read()
  response_content = response_content.decode('utf-8')
  try:
    response_body = {
      'json': json.loads(response_content), 
      'code': response.getcode(),
      'headers': parse_response_headers(response)
    }
  except Exception:
    response_body = {
      'content': str(response_content),
      'code': response.getcode(),
      'headers': parse_response_headers(response)
    }

  if url.startswith('https'):
    certificate_valid, names = validate_ssl(response)
    response_body['certificate valid'] = certificate_valid
    if names:
      response_body['certificate for'] = names

  return send_response(body_content_dict=response_body)


def make_get_handler(forward_site):
  forward_site = forward_site.strip('/')
  async def get_handler(request):
    forwarded_headers = copy.deepcopy(dict(request.headers.copy()))
    if forwarded_headers['Host'] and re.match('.*localhost.*|.*127.0.0.1.*|.*0.0.0.0.*', forwarded_headers['Host']):
      del forwarded_headers['Host']

    return forward_request(forward_site + request.path_qs, forwarded_headers, DEFAULT_TIMEOUT, None, 'GET')

  return get_handler

def make_post_handler():
  async def post_handler(request):
    try:
      json = await request.json()
    except Exception:
      return send_response({
        'code': 'invalid json'
      })
    json = merge_dicts(DEFAULT_JSON_POST_HANDLER, json)

    type = json['type']
    url = json['url']
    headers = json['headers']
    content = json['content']
    timeout = json['timeout']

    if not url or (type == "POST" and not content):
      # code: invalid json
      return send_response({
        'code': 'invalid json'
      })

    return forward_request(url, headers, timeout, content, type)


  return post_handler



