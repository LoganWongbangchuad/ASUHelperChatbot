from pathlib import Path
from bs4 import BeautifulSoup
import json
import chardet
import os

# Folder paths
folder_path = Path("scraped_pages")
output_folder = Path("extracted_pages")
output_folder.mkdir(exist_ok=True)  # Create the folder if it doesn't exist

data = []

for file_path in folder_path.glob("*.html"):
    print(f"Processing: {file_path.name}")  # Debug: Current file

    try:
        # Detect the file's encoding
        with open(file_path, "rb") as file:
            raw_data = file.read()
            detected = chardet.detect(raw_data)
            detected_encoding = detected['encoding']

            # Log detected encoding
            print(f"Detected encoding for {file_path.name}: {detected_encoding}")

            # If no encoding detected or detection fails, try utf-8 as fallback
            if not detected_encoding:
                detected_encoding = "utf-8"

        # Read the file using the detected or fallback encoding
        try:
            with open(file_path, "r", encoding=detected_encoding) as file:
                content = file.read()
        except Exception as e:
            print(f"Failed to read {file_path.name} with encoding {detected_encoding}: {e}")
            continue  # Skip this file if it still fails

        soup = BeautifulSoup(content, "html.parser")

                # Extract data
        title = soup.title.string if soup.title else "No Title"
        text = soup.get_text(strip=True) if soup.get_text() else "No Text"
        meta_description = soup.find("meta", attrs={"name": "description"})
        description = meta_description.get("content") if meta_description else "No Description"

        # Extract meta tags (key-value pairs)
        meta_tags = {
            meta.get("name", meta.get("property", "unknown")): meta.get("content", "")
            for meta in soup.find_all("meta") if meta.get("content")
        }

        headings = [heading.get_text(strip=True) for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]  # Extract all <p> tags
        list_items = [li.get_text(strip=True) for li in soup.find_all("li")]  # Extract all <li> tags
        table_headers = [th.get_text(strip=True) for th in soup.find_all("th")]  # Extract all <th> tags
        td_data = [td.get_text(strip=True) for td in soup.find_all("td")]  # Extract all <td> tags (renamed to `td_data`)
        captions = [caption.get_text(strip=True) for caption in soup.find_all("caption")]  # Extract all <caption> tags
        links = [a.get("href") for a in soup.find_all("a", href=True)]  # Extract all <a> tags with href attributes
        tables = []

        # Process tables
        for table in soup.find_all("table"):
            current_table = []  # Rename to `current_table` to avoid overwriting global `table_data`
            
            # Extract header rows from <thead>
            thead = table.find("thead")
            if thead:
                for row in thead.find_all("tr"):
                    header_cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
                    if header_cells:  # Only append non-empty rows
                        current_table.append(header_cells)
            
            # Extract body rows from <tbody>
            tbody = table.find("tbody")
            if tbody:
                for row in tbody.find_all("tr"):
                    body_cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
                    if body_cells:  # Only append non-empty rows
                        current_table.append(body_cells)
            
            # If no <thead> or <tbody>, process rows directly under <table>
            if not thead and not tbody:
                for row in table.find_all("tr"):
                    cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
                    if cells:  # Only append non-empty rows
                        current_table.append(cells)
            
            if current_table:  # Only append non-empty tables
                tables.append(current_table)

        # Combine extracted data
        extracted_data = {
            "file_name": file_path.name,
            "title": title,
            "description": description,
            "meta_tags": meta_tags,  # Includes all meta tags
            "headings": headings,
            "paragraphs": paragraphs,
            "list_items": list_items,
            "table_headers": table_headers,
            "table_data": td_data,  # Use the renamed `td_data` for global <td> extraction
            "captions": captions,
            "links": links,  # Includes extracted links
            "tables": tables
        }
        data.append(extracted_data)


        # Save each section to a separate file
        output_path = output_folder / f"{file_path.stem}_extracted.json"
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(extracted_data, output_file, indent=4)
        print(f"Data saved to {output_path}")

    except Exception as e:
        print(f"Skipping file {file_path.name} due to error: {e}")

# Optionally save all combined data in a single file (if needed)
combined_output_file = output_folder / "combined_extracted_data.json"
with open(combined_output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)

print(f"Combined data saved to {combined_output_file}")
