import os
import re
import pathlib

folder = pathlib.Path('app/', 'templates')

translation_keys = set()

for file in os.listdir(folder):
    if file.endswith('.html'):
        text = pathlib.Path(folder , file).read_text()
        # find all the strings that are in the format of {{ txt_key }} starting with txt_
        matches = re.findall(r'{{\s*txt_[^}]*\s*}}', text)
        for match in matches:
            translation_keys.add(match.strip('{}').strip())

for key in translation_keys:
    print(f'"{key}": "{key[4:]}",')