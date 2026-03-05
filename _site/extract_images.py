import os
import json
import shutil
import glob

def find_best_image(folder_path):
    # Find all images in the folder and subfolders
    extensions = ['*.png', '*.jpg', '*.jpeg']
    images = []
    for ext in extensions:
        # Check standard depths
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    filepath = os.path.join(root, file)
                    # Ignore some common non-paper images if possible
                    name = file.lower()
                    if 'logo' not in name and 'orcid' not in name and 'elsevier' not in name:
                        images.append(filepath)
    
    if not images:
        return None
        
    # Heuristic: try to find an image in a folder named 'figures' or 'figs'
    for img in images:
        if 'fig' in img.lower() or 'image' in img.lower():
            return img
            
    # Fallback: largest image is often a good figure
    images.sort(key=lambda x: os.path.getsize(x), reverse=True)
    return images[0]

def main():
    pub_dir = os.path.expanduser('~/gh/articles/02_published/')
    
    with open('_data/publications.json', 'r', encoding='utf-8') as f:
        pubs = json.load(f)
        
    # Map DOIs to folders
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
            
        if year >= 2020:
            doi = p.get('doi', '')
            if doi in doi_to_folder:
                best_img = find_best_image(doi_to_folder[doi])
                if best_img:
                    ext = os.path.splitext(best_img)[1].lower()
                    new_filename = f"{p['id']}{ext}"
                    new_path = os.path.join('assets/images/publications', new_filename)
                    shutil.copy2(best_img, new_path)
                    p['image'] = f"/assets/images/publications/{new_filename}"
                    print(f"Added image for {p['id']} -> {new_filename}")

    with open('_data/publications.json', 'w', encoding='utf-8') as f:
        json.dump(pubs, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
