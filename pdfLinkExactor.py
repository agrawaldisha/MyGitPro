import fitz  # PyMuPDF

# Correct file path (no file:///)
pdf_path = "C:/Users/disha.agrawal/Desktop/DataEngineeringFiles/GCP/GCP-Data-Engineer-Master-Cheat-Sheet.pdf"
doc = fitz.open(pdf_path)

# Extract links
for page_num in range(len(doc)):
    for link in doc[page_num].get_links():
        if 'uri' in link:
            print(f"Page {page_num + 1}: {link['uri']}")
