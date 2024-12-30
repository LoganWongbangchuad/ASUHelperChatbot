from pathlib import Path
from bs4 import BeautifulSoup
import json
import chardet

folder_path = Path("scraped_pages")

output_file = "general_extracted_data.json"
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
        headings = [heading.get_text(strip = True) for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]  # Extract all <p> tags
        links = [link.get("href") for link in soup.find_all("a", href=True)]
        tables = [
            [[cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
             for row in table.find_all("tr")]
            for table in soup.find_all("table")
        ]

        # Append extracted data
        data.append({
            "file_name": file_path.name,
            "title": title,
            "description": description,
            "headings": headings,
            "paragradphs": paragraphs,
            "links": links,
            "tables": tables
        })

    except Exception as e:
        print(f"Skipping file {file_path.name} due to error: {e}")
    
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)

print(f"Extracted data saved to {output_file}")