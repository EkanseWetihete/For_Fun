import os
import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # Only consider non-empty pages
                text.append(page_text)
    return "\n".join(text)

def process_pdfs_in_folder(folder_1, folder_2):
    if not os.path.exists(folder_2):
        os.makedirs(folder_2)
    
    # Get list of all .pdf files in folder_1
    pdf_files = [f for f in os.listdir(folder_1) if f.lower().endswith('.pdf')]
    
    for pdf_file in pdf_files:
        # Corresponding .txt file name
        txt_file_name = os.path.splitext(pdf_file)[0] + '.txt'
        txt_file_path = os.path.join(folder_2, txt_file_name)
        
        # Check if the .txt file already exists
        if not os.path.isfile(txt_file_path):
            pdf_file_path = os.path.join(folder_1, pdf_file)
            print(f"Processing {pdf_file_path}...")
            
            # Extract text from the PDF
            text = extract_text_from_pdf(pdf_file_path)
            
            # Save the extracted text to a .txt file
            with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
            print(f"Saved text to {txt_file_path}")
        else:
            print(f"Text file {txt_file_path} already exists. Skipping...")

def combine_text_files(source_folder, destination_file):
    with open(destination_file, 'w', encoding='utf-8') as outfile:
        # Iterate through all .txt files in the source folder
        for txt_file in os.listdir(source_folder):
            if txt_file.lower().endswith('.txt'):
                txt_file_path = os.path.join(source_folder, txt_file)
                with open(txt_file_path, 'r', encoding='utf-8') as infile:
                    # Write the content of each .txt file to the combined file
                    outfile.write(infile.read())
                    outfile.write("\n")  # Optionally add a newline between files
    print(f"All text files have been combined into {destination_file}")

if __name__ == "__main__":
    folder_1 = "PDF_files"  # Replace with your folder_1 path
    folder_2 = "TXT_files"  # Replace with your folder_2 path
    combined_file = "Combined_data/Combined_data.txt"  # Path for the combined file

    # Process PDF files to text
    process_pdfs_in_folder(folder_1, folder_2)
    
    # Create the combined data folder if it doesn't exist
    combined_folder = os.path.dirname(combined_file)
    if not os.path.exists(combined_folder):
        os.makedirs(combined_folder)
    
    # Combine all .txt files into a single file
    combine_text_files(folder_2, combined_file)