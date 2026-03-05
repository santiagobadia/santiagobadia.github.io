import os
import json
import subprocess

def main():
    with open('_data/publications.json', 'r') as f:
        pubs = json.load(f)

    pub_dir = os.path.expanduser('~/gh/articles/02_published/')
    doi_to_folder = {}
    if os.path.exists(pub_dir):
        for folder in os.listdir(pub_dir):
            if '-' in folder and '10.' in folder:
                doi_part = folder.split('-', 1)[1].replace(':', '/')
                doi_to_folder[doi_part] = os.path.join(pub_dir, folder)
            elif folder.startswith('10.'):
                doi_part = folder.replace(':', '/')
                doi_to_folder[doi_part] = os.path.join(pub_dir, folder)

    for p in pubs:
        try:
            year = int(p.get('year', 0))
        except ValueError:
            year = 0
            
        if year >= 2020 and not p.get('image'):
            doi = p.get('doi', '')
            if doi in doi_to_folder:
                folder = doi_to_folder[doi]
                # Find a PDF
                pdfs = []
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith('.pdf') and 'review' not in file.lower() and 'rebuttal' not in file.lower():
                            pdfs.append(os.path.join(root, file))
                
                if pdfs:
                    pdf_path = pdfs[0]
                    # Create thumbnail using sips (macOS built-in)
                    filename = f"{p['id']}.png"
                    out_path = os.path.join('assets/images/publications', filename)
                    
                    try:
                        # sips converts the first page by default
                        # we can constrain the size to save bandwidth, e.g., max width 600px
                        subprocess.run(['sips', '-s', 'format', 'png', '--resampleWidth', '600', pdf_path, '--out', out_path], check=True, capture_output=True)
                        p['image'] = f"/assets/images/publications/{filename}"
                        print(f"Extracted PDF thumbnail for {p['id']}")
                    except Exception as e:
                        print(f"Failed to extract image for {p['id']}: {e}")

    with open('_data/publications.json', 'w', encoding='utf-8') as f:
        json.dump(pubs, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
