# scraper/utils.py

def clean_text(text):
    import re
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
