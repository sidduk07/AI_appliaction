from flask import Flask, request, render_template, flash, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from extractors.pdf_extractor import extract_text_from_pdf
from extractors.ppt_extractor import extract_text_from_ppt
from models.answer_generator import init_model, generate_answer
import logging
import torch

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.secret_key = 'supersecretkey'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Ensure the uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_model():
    try:
        init_model()
        app.logger.info("Model initialized successfully")
    except Exception as e:
        app.logger.error(f"Error initializing model: {str(e)}")
        raise
@app.route('/check_session')
def check_session():
    return {
        'document_text': session.get('document_text', 'Not set'),
        'document_name': session.get('document_name', 'Not set')
    }

@app.route('/debug_file')
def debug_file():
    if 'document_path' not in session:
        return "No document path in session"
    
    try:
        with open(session['document_path'], 'r') as file:
            content = file.read()
        return f"File contents (first 500 chars): {content[:500]}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html', file_uploaded='document_text' in session)

@app.route('/upload', methods=['POST'])
def upload():
    app.logger.info("Upload route accessed")
    if 'file' not in request.files:
        app.logger.warning("No file part in request")
        flash('No file part', 'error')
        return redirect(url_for('index'))
   
    file = request.files['file']
    if file.filename == '':
        app.logger.warning("No selected file")
        flash('No selected file', 'error')
        return redirect(url_for('index'))
   
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
           
            app.logger.info(f"File saved: {filepath}")
           
            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(filepath)
            elif filename.lower().endswith(('.ppt', '.pptx')):
                text = extract_text_from_ppt(filepath)
            else:
                raise ValueError('Unsupported file type')
            
            if text is None or text == "":
                raise ValueError('Failed to extract text from file')

            app.logger.info(f"Extracted text length: {len(text)}")
            
            session['document_text'] = text
            session['document_name'] = filename
            app.logger.info(f"Document text stored in session. Length: {len(session['document_text'])}")
            flash('File successfully uploaded and processed', 'success')
            return render_template('index.html', file_uploaded=True)
        except Exception as e:
            app.logger.error(f"Error processing file: {str(e)}")
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(url_for('index'))
    else:
        app.logger.warning(f"Invalid file type: {file.filename}")
        flash('Allowed file types are pdf, ppt, pptx', 'error')
        return redirect(url_for('index'))
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
   
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
   
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
           
            app.logger.info(f"File saved: {filepath}")
           
            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(filepath)
            elif filename.lower().endswith(('.ppt', '.pptx')):
                text = extract_text_from_ppt(filepath)
            else:
                raise ValueError('Unsupported file type')
            
            session['document_text'] = text
            session['document_name'] = filename
            app.logger.info(f"Document text stored in session. Length: {len(text)}")
            flash('File successfully uploaded and processed', 'success')
            return render_template('index.html', file_uploaded=True)
        except Exception as e:
            app.logger.error(f"Error processing file: {str(e)}")
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(url_for('index'))
    else:
        flash('Allowed file types are pdf, ppt, pptx', 'error')
        return redirect(url_for('index'))

@app.route('/answer', methods=['POST'])
def answer():
    question = request.form.get('question')
    app.logger.info(f"Received question: {question}")
    
    if not question:
        app.logger.warning("No question provided")
        flash('No question provided', 'error')
        return redirect(url_for('index'))

    if 'document_path' not in session:
        app.logger.warning("No document path in session")
        flash('No document has been uploaded yet', 'error')
        return redirect(url_for('index'))

    document_path = session.get('document_path')
    app.logger.info(f"Document path from session: {document_path}")
    
    try:
        with open(document_path, 'r') as file:
            context = file.read()
        app.logger.info(f"Successfully read context from file. Length: {len(context)}")

        app.logger.info(f"Generating answer for question: {question}")
        answer = generate_answer(question, context)
        app.logger.info(f"Generated answer: {answer}")
        return render_template('answer.html', question=question, answer=answer)
    except Exception as e:
        app.logger.error(f"Error generating answer: {str(e)}", exc_info=True)
        flash(f'Error generating answer: {str(e)}', 'error')
        return redirect(url_for('index'))
    question = request.form.get('question')
    if not question:
        flash('No question provided', 'error')
        return redirect(url_for('index'))

    if 'document_text' not in session:
        flash('No document has been uploaded yet', 'error')
        return redirect(url_for('index'))

    context = session.get('document_text')
    if not context:
        app.logger.error("Document text is empty in session")
        flash('Error retrieving document text', 'error')
        return redirect(url_for('index'))

    try:
        app.logger.info(f"Generating answer for question: {question}")
        answer = generate_answer(question, context)
        return render_template('answer.html', question=question, answer=answer)
    except Exception as e:
        app.logger.error(f"Error generating answer: {str(e)}")
        flash(f'Error generating answer: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset():
    session.pop('document_text', None)
    session.pop('document_name', None)
    flash('Document has been reset', 'info')
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

def initialize_model():
    try:
        init_model()
        app.logger.info("Llama 3 model initialized successfully")
    except Exception as e:
        app.logger.error(f"Error initializing Llama 3 model: {str(e)}")
        raise

if __name__ == '__main__':
    # Initialize the Llama 3 model before starting the Flask app
    initialize_model()
    app.run(debug=True)