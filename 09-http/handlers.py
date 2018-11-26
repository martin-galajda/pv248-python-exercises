from aiohttp import web
import urllib.request
import json
import zlib
import re

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
  'timeout': 1,
  'type': 'GET',
  'content': None,
  'url': None,
  'headers': DEFAULT_POST_HEADERS,
}

STRIP_UPSTREAM_HEADERS = ['content-length', 'transfer-encoding', 'content-encoding', 'content-type']

def merge_dicts(dict_one,  dict_two):
  merged = dict_one.copy()
  merged.update(dict_two)
  return merged

def send_response(body_content_dict, headers):
  if 'code' not in body_content_dict:
    body_content_dict['code'] = 200
  response_body_bytes = bytes(json.dumps(body_content_dict, indent=2), encoding='utf8')

  headers += [('Content-Type', 'application/json; charset=utf-8')]

  return web.Response(body=response_body_bytes, headers=headers)

def perform_req(url, headers, timeout, body, method):
  if method == "POST":
    headers = merge_dicts(headers, OVERRIDE_POST_HEADERS)
    req = urllib.request.Request(url, headers=headers)

    json_data = json.dumps(body)
    json_data_bytes = json_data.encode('utf-8')  # needs to be bytes
    req.add_header('Content-Length', len(json_data_bytes))

    response = urllib.request.urlopen(req, json_data_bytes, timeout=timeout)
    urlopen_kargs = {
      'timeout': timeout
    }
    urlopen_args = [req, json_data_bytes]

  elif method == "GET":
    headers = merge_dicts(headers, OVERRIDE_GET_HEADERS)
    req = urllib.request.Request(url, headers=headers)
    urlopen_kargs = {
      'timeout': timeout
    }
    urlopen_args = [req]

  else:
    return send_response({
      'code': 'invalid json'
    }, [])

  try:
    response = urllib.request.urlopen(*urlopen_args, **urlopen_kargs)
  except Exception as e:
    return send_response({
      'code': 'timeout'
    }, [])

  response_content = response.read()

  return_headers = []
  orig_resp_content_type = ''

  for header in response.getheaders():
    header_key, header_value = header
    if header_key.lower() == 'content-type':
      orig_resp_content_type = header[1]

    if header_key.lower() not in STRIP_UPSTREAM_HEADERS:
      return_headers += [(header_key, header_value)]

  response_content = response_content.decode('utf-8')
  if re.match('.*json.*', orig_resp_content_type) is not None:
    try:
      response_body = {
        'json': json.loads(response_content), 
        'code': response.getcode()
      }
    except Exception:
      response_body = {
        'content': str(response_content),
        'code': response.getcode()
      }
  else:
    response_body = {
      'content': str(response_content),
      'code': response.getcode()
    }

  return send_response(body_content_dict=response_body, headers=return_headers)


def make_get_handler(forward_site):
  forward_site = forward_site.strip('/')
  async def get_handler(request):
    forwarded_headers = dict(request.headers.copy())
    if forwarded_headers['Host'] and re.match('.*localhost.*|.*127.0.0.1.*|.*0.0.0.0.*', forwarded_headers['Host']):
      del forwarded_headers['Host']

    return perform_req(forward_site + request.path_qs, forwarded_headers, 1, None, 'GET')

  return get_handler

def make_post_handler(forward_site):
  async def post_handler(request):

    try:
      json = await request.json()
    except Exception:
      return send_response({
        'code': 'invalid json'
      }, [])
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
      }, [])

    return perform_req(url, headers, timeout, content, type)


  return post_handler



