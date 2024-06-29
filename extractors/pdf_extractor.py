import PyPDF2

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text if text else None
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except PermissionError:
        print(f"Error: Permission denied when trying to open {file_path}.")
    except PyPDF2.errors.PdfReadError:
        print(f"Error: The file {file_path} could not be read as a PDF.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    return None