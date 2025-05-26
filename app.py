from flask import Flask, request, send_file
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import mimetypes

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'txt'}
MIME_TO_EXTENSION = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'image/jpg': 'jpg',
    'image/gif': 'gif',
    'image/bmp': 'bmp',
    'image/tiff': 'tiff',
    'text/plain': 'txt',
}

def get_extension_from_mime(mime_type):
    return MIME_TO_EXTENSION.get(mime_type)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image_to_pdf(image_data):
    try:
        img = Image.open(BytesIO(image_data))
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        img_width, img_height = img.size

        aspect = img_width / float(img_height)
        if aspect > width / height:
            new_width = width - 50
            new_height = new_width / aspect
        else:
            new_height = height - 50
            new_width = new_height * aspect

        x = (width - new_width) / 2
        y = (height - new_height) / 2

        c.drawImage(ImageReader(BytesIO(image_data)), x, y, width=new_width, height=new_height)
        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error converting image: {e}")
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
        print(f"Error converting text: {e}")
        return None

@app.route('/convert_to_pdf', methods=['POST'])
def convert_to_pdf():
    if 'file' not in request.files:
        return "No file part in the request", 400
    file = request.files['file']
    if file.filename == '':
        # Try to get extension from Content-Type
        mime_type = request.headers.get('Content-Type')
        if mime_type:
            possible_extension = get_extension_from_mime(mime_type.split(';')[0].lower())
            if possible_extension and possible_extension in ALLOWED_EXTENSIONS:
                file_extension = possible_extension
            else:
                return "Could not determine file type from Content-Type", 400
        else:
            return "No filename and no Content-Type provided", 400
    else:
        file_extension = file.filename.rsplit('.', 1)[1].lower()

    if file:
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
