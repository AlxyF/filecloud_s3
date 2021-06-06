from pathlib import Path
from typing import Dict
import json

def get_scheme(schema:str) -> Dict:
    try:
        file_name = '{}.json'.format(schema)
        schema_path = Path(__file__).with_name(file_name)
        with open(schema_path, 'r') as f:
            schema = json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        raise RuntimeError('{} schema is missing or invalid'.format(file_name))
    return schema