import json
import inspect

class DataEncoder(json.JSONEncoder):
  def default(self, obj):
    if obj.__class__.__name__:
      return obj.to_dict()
    # Let the base class default method raise the TypeError
    print("not class")
    return json.JSONEncoder.default(self, obj)
