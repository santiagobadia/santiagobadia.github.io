import json
import re

def comprehensive_latex_decode(text):
    if not text:
        return ""
    
    # Mapping of common LaTeX accents to Unicode
    # Note: the input might already have been mangled into things like Mart'i
    # so we should handle both the "half-mangled" state and raw LaTeX if any remains.
    
    replacements = {
        # Mangled versions seen in the image/grep
        "Mart'i": "Martín",
        "Mart'in": "Martín",
        "Jes'u": "Jesús",
        "Guti'errez": "Gutiérrez",
        "Gutierr'ez": "Gutiérrez",
        "Guti'e": "Gutiérrez",
        "Guill'e": "Guillén",
        "Colom'e": "Colomés",
        "J'e": "Jérémie",
        "Bonill'a": "Bonilla", # checking for others
        "Codin'a": "Codina",
        "Verdug'o": "Verdugo",
        "Planas'a": "Planas",
        "Caiced'o": "Caicedo",
        "Piscop'o": "Piscopo",
        "Martorell'a": "Martorell",
        "Andr'e": "André",
        "Kj'o": "kjø", # Martin Hornkjøl
        
        # Standard LaTeX patterns (just in case)
        r"\\\'i": "í",
        r"\\\'u": "ú",
        r"\\\'e": "é",
        r"\\\'a": "á",
        r"\\\'o": "ó",
        r"\\\"u": "ü",
        r"\\~n": "ñ",
        r"\\v{s}": "š",
        r"\\v{c}": "č",
        r"\\v{z}": "ž",
        r"\\\'{\\i}": "í",
        r"\\\'\\i": "í",
    }
    
    # Also handle the pattern where it left a single quote before the letter
    # like Guti'errez -> Gutiérrez
    # This is tricky as single quotes are valid in English. 
    # Let's focus on known co-author names.
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
        
    # Generic regex for remaining accents if any: \'a -> á
    # (Only if it looks like a name mangling)
    # We'll skip generic regex to avoid false positives with apostrophes.
    
    return text

def main():
    with open('_data/publications.json', 'r', encoding='utf-8') as f:
        pubs = json.load(f)
        
    for p in pubs:
        p['authors'] = comprehensive_latex_decode(p.get('authors', ''))
        p['title'] = comprehensive_latex_decode(p.get('title', ''))
        
    with open('_data/publications.json', 'w', encoding='utf-8') as f:
        json.dump(pubs, f, indent=4, ensure_ascii=False)
    print("Comprehensive accent fix completed.")

if __name__ == "__main__":
    main()
