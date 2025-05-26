from flask import Flask, request, send_file
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image_to_pdf(image_data):
    try:
        img = Image.open(BytesIO(image_data))
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        img_width, img_height = img.size

        # Calculate aspect ratio to fit within the PDF page
        aspect = img_width / float(img_height)
        if aspect > width / height:
            new_width = width - 50  # Add some margin
            new_height = new_width / aspect
        else:
            new_height = height - 50 # Add some margin
            new_width = new_height * aspect

        x = (width - new_width) / 2
        y = (height - new_height) / 2

        c.drawImage(ImageReader(BytesIO(image_data)), x, y, width=new_width, height=new_height)
        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        return None

def convert_text_to_pdf(text_data):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        textobject = c.beginText(x=50, y=750)
        for line in text_data.decode('utf-8').splitlines():
            textobject.textLine(line)
        c.drawText(textobject)
        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        return None

@app.route('/convert_to_pdf', methods=['POST'])
def convert_to_pdf():
    if 'file' not in request.files:
        return "No file part in the request", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        file_data = file.read()

        if file_extension in {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}:
            pdf_buffer = convert_image_to_pdf(file_data)
            if pdf_buffer:
                return send_file(pdf_buffer, download_name='converted.pdf', as_attachment=True, mimetype='application/pdf')
            else:
                return "Error converting image to PDF", 500
        elif file_extension == 'txt':
            pdf_buffer = convert_text_to_pdf(file_data)
            if pdf_buffer:
                return send_file(pdf_buffer, download_name='converted.pdf', as_attachment=True, mimetype='application/pdf')
            else:
                return "Error converting text to PDF", 500
        else:
            return "Unsupported file type", 400

    return "Something went wrong", 500

if __name__ == '__main__':
    app.run(debug=True)