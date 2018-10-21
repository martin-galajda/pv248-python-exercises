import json
from encoder import DataEncoder

def to_pretty_json(json_serializable):
  return json.dumps(json_serializable, cls = DataEncoder, sort_keys=True, indent=4, ensure_ascii=False)

