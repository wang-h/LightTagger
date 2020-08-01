import json


def get_json(path_json: str):
    with open(path_json, encoding='utf-8') as f:
        return json.load(f)
