import pdfplumber


def extract_text_from_pdf(pdf_path):

    text = ""   

    
    with pdfplumber.open(pdf_path) as pdf:

        
        for page in pdf.pages:

            
            page_text = page.extract_text()

            
            if page_text:
                text = text + page_text + "\n"

    
    return text



def get_pdf_info(pdf_path):

    
    with pdfplumber.open(pdf_path) as pdf:

    
        total_pages = len(pdf.pages)

        
        file_name = pdf_path.split("\\")[-1]

    return {
        "total_pages": total_pages,
        "file_name": file_name
    }
