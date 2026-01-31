from flask import Flask, render_template, request, send_file
import PyPDF2
import os
import io

# We use template_folder='../templates' because the python file is inside the 'api' folder
app = Flask(__name__, template_folder='../templates')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return render_template('index.html', error="No file selected")

        file = request.files['pdf_file']

        if file.filename == '':
            return render_template('index.html', error="No file selected")

        if file and file.filename.endswith('.pdf'):
            try:
                # Read PDF directly from memory
                pdf_reader = PyPDF2.PdfReader(file)
                
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"

                # Prepare file for download in memory
                txt_filename = os.path.splitext(file.filename)[0] + '.txt'
                mem_file = io.BytesIO()
                mem_file.write(text_content.encode('utf-8'))
                mem_file.seek(0)

                return send_file(
                    mem_file,
                    as_attachment=True,
                    download_name=txt_filename,
                    mimetype='text/plain'
                )

            except Exception as e:
                # Print error to Vercel logs for debugging
                print(f"Error: {e}")
                return render_template('index.html', error=f"Error processing PDF: {str(e)}")
        else:
            return render_template('index.html', error="Invalid file type. Please upload a PDF.")

    return render_template('index.html')

# NOTE: We removed app.run(debug=True) because Vercel handles the server startup.
