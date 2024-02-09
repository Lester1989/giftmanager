from fastapi import Request
from fastapi.templating import Jinja2Templates
import pathlib
import json

locales: dict[str, dict[str, str]] = {
    file_name.stem.lower(): json.loads(file_name.read_text(encoding='utf-8'))
    for file_name in pathlib.Path('app/', 'locale').iterdir()
}
templates = Jinja2Templates(directory="app/templates")
templates.env.globals['app_version'] = pathlib.Path('version.txt').read_text(encoding='utf-8').strip()

def get_translations(request:Request)->dict[str,str]:
    requested_languages:list[str] = request.headers.get('Accept-Language','en').split(',')
    for language in requested_languages:
        clean_language = language.split('-')[0].lower()
        if clean_language in locales:
            return locales[clean_language]
    return locales['en']