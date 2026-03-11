# Santiago Badia Webpage - Engineering Mandates

## Workspace Paths
- **Webpage Source**: `/Users/jbad0002/gd-monash/gh/santiagobadia/webpage`
- **Article Source**: `/Users/jbad0002/gd-monash/gh/articles/` (Contains subfolders `01_submitted/` and `02_published/`)
- **Note**: NEVER use the old `Insync` paths.

## Publication Framework
Always follow the "Data First" approach:
1. **Modify Data**: Update `_data/publications.json` (and keep `publications.json` in root synced).
2. **Handle Status**: 
   - `submitted`: Journal is "arXiv" or empty.
   - `accepted`: Journal is set, but `status` field is manually set to `accepted`.
   - `published`: Default for entries with a journal and DOI.
3. **Build Site**: Run the local Jekyll build to generate HTML from JSON.
4. **Push Changes**: Commit source data, images, and the rebuilt `_site` folder.

## Thumbnail Extraction
- **Priority**: Use high-quality figures (`.png` or `.jpg`) from the **Article Source** folders.
- **Extraction**: If no original image exists, extract a colorful figure from the paper PDF using `gs` (Ghostscript) at 300dpi.
- **Optimization**: Resize all thumbnails to a maximum dimension of 600px using `sips -Z 600`.
- **Location**: Store in `assets/images/publications/` using the DOI or arXiv ID as the filename.

## Build Environment
Due to system restrictions, use the local Bundler/Jekyll installation:
```bash
export PATH=$PATH:$(ruby -e 'print Gem.user_dir')/bin
export GEM_PATH=$(ruby -e 'print Gem.user_dir'):$(gem env gempath)
bundle _2.4.22_ config set --local path 'vendor/bundle'
bundle _2.4.22_ install
bundle _2.4.22_ exec jekyll build
```

## Styling
- Default: **Dark Mode**.
- Toggle: Controlled by `body.light-mode` class and persistent via `localStorage`.
- Profile: Styled as a circle with a white border.
