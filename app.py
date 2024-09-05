from flask import Flask, request, render_template, url_for
import fitz  # PyMuPDF
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
import os

nltk.download('punkt')

app = Flask(__name__)

# Ensure output directory exists
output_folder = "static/output"
os.makedirs(output_folder, exist_ok=True)

# Function to extract text and images from PDF
def extract_pdf_content(pdf_path):
    pdf_data = {}
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        images = page.get_images(full=True)
        
        # Store text and images for each page
        pdf_data[f"page_{page_num}"] = {"text": text, "images": []}
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_filename = f"image_page_{page_num}_{img_index}.png"
            image_path = os.path.join(output_folder, image_filename)
            pdf_data[f"page_{page_num}"]["images"].append(image_path)
            
            # Save the image in the output folder
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
    
    return pdf_data

# Extract PDF data once (or implement file upload)
pdf_data = extract_pdf_content('output.pdf')

# Route for handling the query
@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""
    response_images = []
    
    if request.method == "POST":
        query = request.form["query"]
        tokens = word_tokenize(query.lower())
        
        for page, content in pdf_data.items():
            sentences = sent_tokenize(content["text"])
            matched_sentences = [sent for sent in sentences if any(token in sent.lower() for token in tokens)]
            if matched_sentences:
                response_text = " ".join(matched_sentences)
                response_images = [url_for('static', filename=img.replace("static/", "")) for img in content["images"]]
                break

    return render_template("index.html", response_text=response_text, response_images=response_images)

if __name__ == "__main__":
    app.run(debug=True)
