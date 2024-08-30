import fitz  # PyMuPDF
import os

def process_pdf(pdf_path, output_dir):
    pdf_document = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            
            image_filename = f"page{page_num+1}_img{img_index+1}.png"
            image_path = os.path.join(output_dir, image_filename)
            
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            
            image_paths.append(image_path)

    pdf_document.close()
    return image_paths