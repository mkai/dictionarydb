from iso639 import languages


def get_language(code):
    try:
        return languages.get(part3=code)
    except Exception:
        return None
