import os
import requests

def download_pdf(url, save_path):
    """Downloads a PDF from a URL to a local path."""
    if os.path.exists(save_path):
        print(f"File already exists at {save_path}")
        return

    print(f"Downloading from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded successfully to {save_path}")
    except Exception as e:
        print(f"Failed to download: {e}")

if __name__ == "__main__":
    # URL for Tamil Nadu Class 6 English Term 1 Textbook
    # Using a direct link found from search results or a placeholder if direct link is dynamic.
    # Based on search, text books are available at tntextbooks.in. 
    # I will use a known stable link structure or a direct link if available.
    # For this example, I will use a placeholder URL that the user might need to update if it breaks, 
    # but I will try to find a valid one. 
    # A common pattern for these is often hosted on specific government servers.
    # Let's try a likely valid URL based on common patterns, or ask user to provide if it fails.
    # Actually, I'll use a specific link from a reliable source if I can, otherwise I'll put a placeholder.
    
    # Found from search: https://www.tntextbooks.in/p/6th-books.html -> leads to PDF links.
    # Direct PDF links often change. I will use a generic function and a likely URL.
    # If this fails, the user can manually place the file.
    
    # Example link (this is a sample, might need update):
    # http://www.tnschools.gov.in/media/textbooks/6_English_Term_1.pdf (Hypothetical)
    # Better to use a specific one if possible. 
    # Let's use a placeholder that instructs the user if it fails, or tries a few knowns.
    
    # For the purpose of this task, I will try to download from a source found in search or 
    # just create the folder and ask the user to put the file there if download fails.
    
    # Let's try to download a sample chapter or the full book if possible.
    # Since I cannot browse to find the exact dynamic link, I will create the script 
    # to accept a URL, and default to a likely one, but with clear instructions.
    
    TARGET_URL = "https://www.tntextbooks.in/2020/12/std-6-english-term-1-text-book-download.html" # This is an HTML page, not PDF.
    # Real PDF link is usually hidden. 
    # I will write the script to *simulate* the download or just create the directory structure 
    # and instruct the user to place the file 'textbook.pdf' in 'data/'.
    
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    PDF_PATH = os.path.join(DATA_DIR, "textbook.pdf")
    
    # Since I can't guarantee a direct deep link without browsing, 
    # I will create a dummy file for testing if download fails, 
    # BUT I will ask the user to replace it.
    
    print(f"Please ensure the Class 6 English Textbook PDF is at: {PDF_PATH}")
    print("If you have the direct link, you can modify this script.")
    
    # For now, we will just ensure the directory exists.
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(PDF_PATH):
        print("PDF not found. Please manually download the 'Class 6 English Term 1' PDF")
        print("and save it as 'data/textbook.pdf' in this project directory.")
        # Create a dummy file so other scripts don't crash immediately during initial checks
        # with open(PDF_PATH, 'w') as f:
        #     f.write("This is a placeholder for the textbook PDF.")
    else:
        print("PDF found.")

