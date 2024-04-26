import os
import re
import pathlib
import json

folder_templates = pathlib.Path('app', 'templates')

folder_languages = pathlib.Path('app', 'locale')

translation_keys:set[str] = set()
localized_keys:dict[str,dict[str,str]] = {}

for file in os.listdir(folder_templates):
    if file.endswith('.html'):
        text = pathlib.Path(folder_templates , file).read_text()
        # find all the strings that are in the format of {{ txt_key }} starting with txt_
        matches = re.findall(r'{{\s*txt_[^}]*\s*}}', text)
        for match in matches:
            translation_keys.add(match.strip('{}').replace('|safe','').strip())



for file in os.listdir(folder_languages):
    if file.endswith('.json'):
        localized_keys[file] = json.loads(pathlib.Path(folder_languages, file).read_text(encoding='utf-8'))

# check if all translation keys are present in all languages
for key in translation_keys:
    for translations in localized_keys.values():
        if key not in translations:
            translations[key] = f'{key.upper()}__MISSING__'
            print(f'Key {key} is missing in one of the languages')

# write the translations back to the files
for lang, translations in localized_keys.items():
    with open(pathlib.Path(folder_languages, lang), 'w', encoding='utf-8') as file:
        file.write(json.dumps(translations, indent=4, ensure_ascii=False, sort_keys=True))