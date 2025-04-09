import requests
import re
import json
from collections import defaultdict

URL = "https://it.wikisource.org/w/api.php?action=query&prop=revisions&titles=Italia,%20Repubblica%20-%20Costituzione&rvslots=main&rvprop=content&formatversion=2&format=json"


def fetch_constitution_text():
    def find_key_value(json_data, target_key):
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if key == target_key:
                    return value  # Found the key!
                if isinstance(value, (dict, list)):
                    result = find_key_value(value, target_key)
                    if result is not None:
                        return result
        elif isinstance(json_data, list):
            for item in json_data:
                result = find_key_value(item, target_key)
                if result is not None:
                    return result
        return None  # Key not found

    r = requests.get(URL)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to download constitution: {r.status_code}")

    c: str = find_key_value(r.json(), 'content')
    if c is None:
        raise RuntimeError(f"Failed to parse page")
    i = c.index('Costituzione della Repubblica Italiana nel seguente testo: \n\n')
    if i < 0:
        raise RuntimeError(f"Failed to parse page (preamble)")
    c = c[i:]
    i = c.index('\n\n{{Centrato}}Data a Roma, addì 27 dicembre 1947')
    if i < 0:
        raise RuntimeError(f"Failed to parse page (post)")
    c = c[:i]

    return c


def parse_constitution(raw_text):
    # We'll use a simple line-based parse since structure is regular
    lines = raw_text.splitlines()
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    current_parte = 'Prefazione'
    current_titolo = 'Principi Fondamentali'
    current_sezione = None
    current_articolo = None
    articolo_text = []

    articolo_re = re.compile(r"^===== (.+?) =====")
    sezione_re = re.compile(r"^==== (.+?) ====")
    titolo_re = re.compile(r"^=== (.+?) ===")
    parte_re = re.compile(r"^== (.+?) ==")

    def save_in_result_maybe():
        nonlocal articolo_text
        if current_articolo and articolo_text:
            # Save previous articolo
            result[current_parte][current_titolo][current_sezione][current_articolo] = articolo_text
            articolo_text = []

    for line in lines:
        line = line.strip().replace('<br />', '')
        if not line:
            continue

        if m := parte_re.match(line):
            current_parte = m[1].strip(" '")
            current_titolo = None
            continue

        if m := titolo_re.match(line):
            current_titolo = m[1]
            continue

        if m := sezione_re.match(line):
            current_sezione = m[1]
            continue

        if m := articolo_re.match(line):
            save_in_result_maybe()
            current_articolo = m[1]
            continue

        if current_articolo:
            # Split paragraphs and append
            articolo_text.append(line)

    # Save last articolo
    save_in_result_maybe()

    return result


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_json():
    fn = '/tmp/costituzioneItaliana.json'
    try:
        with open(fn) as fi:
            jtext = json.load(fi)
    except (OSError, FileNotFoundError, json.JSONDecodeError):
        jtext = parse_constitution(fetch_constitution_text())
        with open(fn, 'w') as fo:
            json.dump(jtext, fo)
    return jtext


if __name__ == "__main__":
    print("Downloading...")
    text = fetch_constitution_text()
    print("Parsing...")
    parsed = parse_constitution(text)
    print("Saving...")
    save_json(parsed, "/tmp/italian_constitution.json")
    print("Done.")
