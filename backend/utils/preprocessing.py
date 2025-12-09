import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\sàâäéèêëîïôöùûüç]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text