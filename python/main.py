import os
import sys
from pdf_reader import process_pdf
from ocr_module import perform_ocr
from translation_module import translate_detections
from image_processor_module import process_image
from dotenv import load_dotenv
import torch

load_dotenv()
# Get git_folder from environment variable, with a fallback value
git_folder = os.environ.get('ITT_ROOT', 'C:\dev\ocr\python')

# Check CUDA availability
print(f"CUDA is{'nt' if not torch.cuda.is_available() else ''} available")
if torch.cuda.is_available():
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Using CPU")


def get_next_run_number(output_dir):
    existing_runs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d)) and d.isdigit()]
    return max([int(d) for d in existing_runs], default=0) + 1

def main(working_dir, pdf_file_path=None):
    output_dir = os.path.join(working_dir, 'output')
    run_number = get_next_run_number(output_dir)
    run_dir = os.path.join(output_dir, f"{run_number:03d}")
    os.makedirs(os.path.join(run_dir, 'input_images'), exist_ok=True)
    os.makedirs(os.path.join(run_dir, 'output_images'), exist_ok=True)

    # Step 1: PDF to Images
    if pdf_file_path:
        image_paths = process_pdf(pdf_file_path, os.path.join(run_dir, 'input_images'))
    else:
        image_paths = [os.path.join(run_dir, 'input_images', f) for f in os.listdir(os.path.join(run_dir, 'input_images'))]

    # Step 2: OCR
    detections_per_image = perform_ocr(image_paths)
    
    # Step 3: Translation (character substitution)
    for i, detections in enumerate(detections_per_image):
        detections_per_image[i] = translate_detections(detections, ["41","шщ","Св", "Ю!", "СТ", "ЦЕНТР", "0А", "ОА", ",АН", "РВС", "БІК", "04"])

    # Step 4: Image Processing
    for image_path, detections in zip(image_paths, detections_per_image):
        process_image(image_path, detections, os.path.join(run_dir, 'output_images'))

    print("Processing complete.")

if __name__ == "__main__":
    
    working_dir = git_folder
    pdf_file_path = git_folder + '\\resources\sample.pdf'
    main(working_dir, pdf_file_path)