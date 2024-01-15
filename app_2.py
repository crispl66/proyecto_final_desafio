from flask import Flask, jsonify, render_template, request, Response
from gtts import gTTS
import requests
import os 
from pymongo import MongoClient 
from pdfminer.high_level import extract_text
import json

app = Flask(__name__)

#conexiones con BBDD
mongo_url ='mongodb+srv://falberola:5zZi7xSEYPPIdGgc@cluster0.hd9lmf3.mongodb.net/datadmin_fincas'
client = MongoClient(mongo_url)
db = client.get_database('datadmin_fincas')
resumen_collection = db['resumen'] 
audios_collection = db['audios'] 

#API
# API_TOKEN = "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"

# API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
# headers = {"Authorization": f"Bearer {API_TOKEN}"}

@app.route('/', methods=['GET'])
def plantilla():
    return render_template('endpoints.html')

@app.route('/subir_pdf', methods=['POST'])
def subir_pdf():
    if 'file' not in request.files:
        return "No se proporcionó ningún archivo", 400

    file = request.files['file']

    if not file:
        return "El archivo está vacío", 400

    # Ubicación temporal
    file_path = os.path.join("temp", "uploaded_file.pdf")
    file.save(file_path)

    return "Archivo recibido correctamente", 200

@app.route('/resumen', methods=['GET','POST'])
def resumen():
    #if 'file' not in request.files:
    #    return "No se proporcionó ningún archivo"
    #file = request.files['file']
    #file_content = request.args.get('file_content')

    try:
        path = os.path.dirname(os.path.abspath(__file__))
        upload_folder=os.path.join(
        path.replace("/file_folder",""),"tmp")
        os.makedirs(upload_folder, exist_ok=True)
        app.config['upload_folder'] = upload_folder
    except Exception as e:
        app.logger.info('An error occurred while creating temp folder')
        app.logger.error('Exception occurred : {}'.format(e))

@app.route('/')
def index():
    return Response(json.dumps({
    'status': True,
    'code': 200,
    'message': 'Its Working!'}), mimetype='application/json')

    file_path = os.path.join("temp", "uploaded_file.pdf")

    if not os.path.exists(file_path):
        return "No se encontró el archivo", 400
    if not 'file':
        return "No se proporcionó ningún archivo en el parámetro 'file'", 400

    text = extract_text(file_path)
    
    API_TOKEN = "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"
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    resumen = query({"inputs": text})
    contenido_resumen = resumen[0][next(iter(resumen[0]))]
    resumen_collection.insert_one({'resumen': contenido_resumen})
    tts = gTTS(text=contenido_resumen, lang='es')
    audio = tts.save("audio.mp3")
    audios_collection.insert_one({'audio': audio})
    
    return jsonify({'resumen': contenido_resumen, 'audio': audio})

'''@app.route('/subir_pdf', methods=['GET','POST'])
def subir_pdf():
    if 'file' not in request.files:
        return "No se proporcionó ningún archivo"
    file = request.files['file']
    return file

@app.route('/resumen', methods=['GET','POST'])
def resumen():
    #if 'file' not in request.files:
    #    return "No se proporcionó ningún archivo"
    #file = request.files['file']
    file_content = request.args.get('file_content')

    if not file_content:
        return "No se proporcionó ningún archivo en el parámetro 'file_content'", 400

    text = extract_text(file_content)
    
    API_TOKEN = "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"
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    resumen = query({"inputs": text})
    contenido_resumen = resumen[0][next(iter(resumen[0]))]
    resumen_collection.insert_one({'resumen': contenido_resumen})
    
    return jsonify({'resumen': contenido_resumen})'''

@app.route('/audio', methods=['GET'])
def audio(contenido_resumen):
    tts = gTTS(text=contenido_resumen, lang='es')
    audio = tts.save("audio.mp3")
    audios_collection.insert_one({'audio': audio})
    return audio

if __name__ == '__main__':
    app.run(debug=True,port=8000)
