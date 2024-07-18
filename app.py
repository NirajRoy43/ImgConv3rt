from flask import Flask, request, render_template, send_file
from PIL import Image
from fpdf import FPDF
from pdf2image import convert_from_path
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/uploads/'
CONVERTED_FOLDER = '/tmp/converted/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CONVERTED_FOLDER):
    os.makedirs(CONVERTED_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        conversion_type = request.form['conversion_type']
        if conversion_type == 'jpg_to_png':
            converted_path = convert_jpg_to_png(file_path)
        elif conversion_type == 'png_to_jpg':
            converted_path = convert_png_to_jpg(file_path)
        elif conversion_type == 'jpg_to_pdf':
            converted_path = convert_jpg_to_pdf(file_path)
        elif conversion_type == 'png_to_pdf':
            converted_path = convert_png_to_pdf(file_path)
        elif conversion_type == 'pdf_to_image':
            converted_path = convert_pdf_to_image(file_path)

        return send_file(converted_path, as_attachment=True)

def convert_jpg_to_png(file_path):
    image = Image.open(file_path)
    converted_path = os.path.join(app.config['CONVERTED_FOLDER'], os.path.splitext(os.path.basename(file_path))[0] + '.png')
    image.save(converted_path)
    return converted_path

def convert_png_to_jpg(file_path):
    image = Image.open(file_path)
    converted_path = os.path.join(app.config['CONVERTED_FOLDER'], os.path.splitext(os.path.basename(file_path))[0] + '.jpg')
    image = image.convert('RGB')
    image.save(converted_path)
    return converted_path

def convert_jpg_to_pdf(file_path):
    image = Image.open(file_path)
    converted_path = os.path.join(app.config['CONVERTED_FOLDER'], os.path.splitext(os.path.basename(file_path))[0] + '.pdf')
    pdf = FPDF()
    pdf.add_page()
    pdf.image(file_path, x = 10, y = 8, w = 190)
    pdf.output(converted_path)
    return converted_path

def convert_png_to_pdf(file_path):
    return convert_jpg_to_pdf(file_path)

def convert_pdf_to_image(file_path):
    images = convert_from_path(file_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(app.config['CONVERTED_FOLDER'], f"{os.path.splitext(os.path.basename(file_path))[0]}_page_{i+1}.png")
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    return image_paths[0]  # Return the first image for download

if __name__ == '__main__':
    app.run(debug=True)
