from flask import Blueprint, render_template, request, jsonify
from .promt import question_answer_bot
import os
from .dataProcessing import data_preparation_and_upload
from .retrieval import existing_namespaces

main = Blueprint('main', __name__)

messages = []
namespace = None

@main.route('/')
def index():
    return render_template('index.html', messages=messages)

@main.route('/send_message', methods=['POST'])
def send_message():
    try:
        user_message = request.json['message']
        messages.append({'sender': 'user', 'content': user_message})
        print(user_message)

        bot_reply = question_answer_bot(user_message, namespace)
        print(bot_reply)
        messages.append({'sender': 'bot', 'content': bot_reply})

        return jsonify({'reply': bot_reply})
    
    except Exception as e:
        return jsonify({'reply': "Something went wrong."})

@main.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename, _= os.path.splitext(file.filename)
    print(filename)

    all_uploaded_files = existing_namespaces()
    print(all_uploaded_files)
    if filename in all_uploaded_files:
        return jsonify({'error': 'File already exists'}), 400
    
    # Process for data chunking and uploading Vector to Pinecone
    result = data_preparation_and_upload(file, filename)

    if result:
        return jsonify({'filename': filename, 'files': all_uploaded_files}), 200
    else:
        return jsonify({'error': 'Data preparation and upload failed'}), 500


@main.route('/initial_files')
def initial_files():
    files = existing_namespaces()
    return jsonify({'files': files})

@main.route('/select_pdf', methods=['POST'])
def select_pdf():
    data = request.json
    filename = data.get('filename')
    filename_without_ext = os.path.splitext(filename)[0]  # Extract filename without extension
    global namespace
    namespace = filename_without_ext
    return jsonify({'filename': filename_without_ext}), 200
