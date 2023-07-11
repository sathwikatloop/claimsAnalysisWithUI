import json
from pathlib import Path

mapping_file_path = Path(__file__).parent.parent / 'data' / 'mapping.json'

with open(mapping_file_path, 'r') as fp:
    mapping = json.load(fp)
