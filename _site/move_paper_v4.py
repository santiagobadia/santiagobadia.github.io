import re

def main():
    with open('_site/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Identifying markers
    doi = "10.1007/s10208-025-09734-6"
    target_year_marker = "<h2>2025</h2>"
    grid_marker = '<div class="publications-grid">'

    # Find the row containing the DOI
    # We'll look for the start of the row before the DOI and the end of the row after the DOI
    # Typical structure: <div class="pub-row"> ... DOI ... </div>\s*</div>\s*</div>
    
    # Let's find all pub-rows and identify the one with our DOI
    parts = content.split('<div class="pub-row">')
    row_to_move = None
    new_parts = [parts[0]]
    
    for part in parts[1:]:
        if doi in part:
            # Found it. We need to find the end of this row block.
            # Usually it ends with two or three </div> depending on thumbnail.
            # But let's just use the split boundary.
            # The next part starts with <div class="pub-row"> or the grid ends.
            row_to_move = '<div class="pub-row">' + part
            # We need to be careful about trailing content if it's the last row
            if '</div>
  
' in row_to_move:
                 # Split at the end of the publications grid if it's the last one
                 grid_end = '</div>
  
'
                 sub_parts = row_to_move.split(grid_end)
                 row_to_move = sub_parts[0] + '</div>'
                 new_parts.append(grid_end.join(sub_parts[1:]))
            continue
        new_parts.append(part)

    if row_to_move:
        print("Found row to move")
        content = '<div class="pub-row">'.join(new_parts)
        # Update year in the block
        row_to_move = row_to_move.replace("2024", "2025")
        
        # Find where to insert
        pos = content.find(target_year_marker)
        if pos != -1:
            grid_pos = content.find(grid_marker, pos)
            if grid_pos != -1:
                insert_at = grid_pos + len(grid_marker)
                content = content[:insert_at] + "
      " + row_to_move + content[insert_at:]
                with open('_site/index.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("Successfully moved row")
            else:
                print("Grid marker not found")
        else:
            print("Year marker not found")
    else:
        print("Row not found")

if __name__ == "__main__":
    main()
