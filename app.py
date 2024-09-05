import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Ensure you have the NLTK punkt tokenizer downloaded
nltk.download('punkt')

# Function to extract text and images from PDF
def extract_pdf_content(pdf_path):
    pdf_data = {}
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        images = page.get_images(full=True)

        # Store text and images for each page
        pdf_data[f"page_{page_num}"] = {
            "text": text,
            "images": []
        }

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_filename = f"image_page_{page_num}_{img_index}.png"
            pdf_data[f"page_{page_num}"]["images"].append(image_filename)

            # Save the image
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)

    return pdf_data

# Function to handle user queries
def handle_query(query, pdf_data):
    tokens = word_tokenize(query.lower())
    response_text = ""
    response_images = []

    # Search through the extracted PDF data for relevant content
    for page, content in pdf_data.items():
        sentences = sent_tokenize(content["text"])
        matched_sentences = [sent for sent in sentences if all(token in sent.lower() for token in tokens)]
        
        if matched_sentences:
            response_text += " ".join(matched_sentences) + "\n"
            response_images.extend(content["images"])  # Collect images from all relevant content

    return response_text.strip(), response_images

# Function to run the chatbot and update the UI
def run_chatbot():
    user_query = entry.get()
    entry.delete(0, tk.END)

    response_text, response_images = handle_query(user_query, pdf_data)

    # Clear the text area and previous images
    text_area.delete(1.0, tk.END)
    for widget in window.pack_slaves():
        if isinstance(widget, tk.Label):
            widget.destroy()

    if response_text:
        text_area.insert(tk.END, response_text + "\n")
        for img_path in response_images:
            # Display the image in the UI
            img = Image.open(img_path)
            img = img.resize((200, 200), Image.LANCZOS)  # Resize for display
            img = ImageTk.PhotoImage(img)
            panel = tk.Label(window, image=img)
            panel.image = img  # Keep a reference to avoid garbage collection
            panel.pack()
    else:
        text_area.insert(tk.END, "I'm sorry, I couldn't find any relevant information.\n")

# Path to your PDF file
pdf_path = "output.pdf"
pdf_data = extract_pdf_content(pdf_path)

# Create the main window
window = tk.Tk()
window.title("PDF Chatbot")

# Create a text area for displaying responses
text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=50, height=10)
text_area.pack(pady=10)

# Create an entry box for user input
entry = tk.Entry(window, width=50)
entry.pack(pady=10)

# Create a button to submit the query
submit_button = tk.Button(window, text="Ask", command=run_chatbot)
submit_button.pack(pady=10)

# Run the Tkinter event loop
window.mainloop()
