from flask import Flask, render_template, request, send_file
import PyPDF2
import os
import io

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

# Ensure upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file is part of the request
        if 'pdf_file' not in request.files:
            return render_template('index.html', error="No file selected")

        file = request.files['pdf_file']

        # Check if filename is empty
        if file.filename == '':
            return render_template('index.html', error="No file selected")

        if file and file.filename.endswith('.pdf'):
            try:
                # Read the PDF file directly from memory (no need to save to disk first)
                pdf_reader = PyPDF2.PdfReader(file)
                
                text_content = ""
                # Extract text from all pages
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"

                # Create a text file in memory
                txt_filename = os.path.splitext(file.filename)[0] + '.txt'
                mem_file = io.BytesIO()
                mem_file.write(text_content.encode('utf-8'))
                mem_file.seek(0)

                # Send the file to the user to download
                return send_file(
                    mem_file,
                    as_attachment=True,
                    download_name=txt_filename,
                    mimetype='text/plain'
                )

            except Exception as e:
                return render_template('index.html', error=f"Error processing PDF: {str(e)}")
        else:
            return render_template('index.html', error="Invalid file type. Please upload a PDF.")

    return render_template('index.html')

if __name__ == '__main__':
    # For local testing
    app.run(debug=True, port=5000)