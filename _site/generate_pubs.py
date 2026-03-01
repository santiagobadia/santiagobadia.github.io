import os
import re

def clean_latex(text):
    if not text:
        return ""
    # Remove LaTeX commands like {\'{u}} or {\textendash}
    # First, handle common ones
    text = text.replace('\\textendash', '-')
    text = text.replace('\\textemdash', '--')
    # Remove any remaining backslashes and the following character (if it's a quote/accent) or just the backslash
    text = re.sub(r'\\(["\'^`~=])', r'\1', text)
    # Remove any remaining backslashes
    text = text.replace('\\', '')
    # Remove extra braces
    text = text.replace('{', '').replace('}', '')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def to_yaml(data):
    lines = []
    for item in data:
        # Use single quotes for YAML values and escape internal single quotes
        # OR double quotes and escape backslashes and double quotes.
        # Let's use double quotes and be very careful.
        def escape(s):
            if not s: return ""
            return str(s).replace('\\', '\\\\').replace('"', '\"')

        lines.append("- title: \"" + escape(item.get('title', '')) + "\"")
        lines.append("  authors: \"" + escape(item.get('authors', '')) + "\"")
        lines.append("  year: " + str(item.get('year', '')))
        lines.append("  journal: \"" + escape(item.get('journal', '')) + "\"")
        lines.append("  doi: \"" + escape(item.get('doi', '')) + "\"")
        lines.append("  url: \"" + escape(item.get('url', '')) + "\"")
        lines.append("  arxiv: \"" + escape(item.get('arxiv', '')) + "\"")
    return "\n".join(lines)

def main():
    home = os.path.expanduser('~')
    doi_bib = os.path.join(home, 'gh/santiagobadia/resume/bib/doi-works.bib')
    arxiv_bib = os.path.join(home, 'gh/santiagobadia/resume/bib/arxiv-works.bib')
    
    pubs = []
    
    def parse_file(path):
        if not os.path.exists(path): return []
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # More robust entry splitting: @TYPE{ID, ... }
        entries = re.findall(r'@(article|misc)\{(.*?),\s*(.*?)\n\}', content, re.DOTALL)
        results = []
        for etype, eid, ebody in entries:
            # Simple field extraction using regex that handles { } pairs better
            def get_field(field_name, body):
                # Look for field = { ... } or field = " ... " or field = 2020
                pattern = rf'{field_name}\s*=\s*([\{{"])(.*?)([\}}"])'
                m = re.search(pattern, body, re.DOTALL)
                if m:
                    return m.group(2)
                # Fallback for unquoted numbers
                m = re.search(rf'{field_name}\s*=\s*(\d+)', body)
                if m:
                    return m.group(1)
                return ""

            title = get_field('title', ebody)
            authors = get_field('author', ebody)
            year = get_field('year', ebody)
            journal = get_field('journal', ebody)
            doi = get_field('doi', ebody)
            url = get_field('url', ebody)
            arxiv = get_field('eprint', ebody)
            
            if not journal and etype == 'misc':
                journal = "arXiv"

            results.append({
                'id': eid,
                'title': clean_latex(title),
                'authors': clean_latex(authors).replace(' and ', ', '),
                'year': year,
                'journal': clean_latex(journal),
                'doi': doi,
                'url': url,
                'arxiv': arxiv
            })
        return results

    pubs.extend(parse_file(doi_bib))
    pubs.extend(parse_file(arxiv_bib))
    
    seen_ids = set()
    unique_pubs = []
    for p in pubs:
        if p['id'] not in seen_ids:
            unique_pubs.append(p)
            seen_ids.add(p['id'])
    
    arxiv_from_pdf = [
        "2506.11956", "2508.15320", "2508.17705", "2508.17687", 
        "2409.15863", "2411.08064", "2411.04591", "2403.14054",
        "2410.13023", "2405.10478", "2401.12649", "2311.14363",
        "2303.13672", "2303.11617", "2307.10605", "2306.06304",
        "2306.11213", "2206.03626", "2208.08538", "2201.06632",
        "2207.10975", "2109.09983", "2110.01378"
    ]
    
    for aid in arxiv_from_pdf:
        found = False
        for p in unique_pubs:
            if p.get('arxiv') == aid or aid in p['id']:
                found = True
                break
        if not found:
            unique_pubs.append({
                'id': aid,
                'title': f"Recent work on arXiv: {aid}",
                'authors': "Santiago Badia et al.",
                'year': "20" + aid[:2],
                'journal': "arXiv",
                'arxiv': aid,
                'url': f"https://arxiv.org/abs/{aid}"
            })
    
    unique_pubs.sort(key=lambda x: str(x.get('year', '0')), reverse=True)
    
    with open('_data/publications.yml', 'w', encoding='utf-8') as f:
        f.write(to_yaml(unique_pubs))

if __name__ == "__main__":
    main()