from flask import Flask, jsonify, render_template, request, send_file
from gtts import gTTS
import requests
import os 
from pymongo import MongoClient 
from pdfminer.high_level import extract_text 
from gridfs import GridFS
from PyPDF2 import PdfReader

app = Flask(__name__)

#conexiones con BBDD
mongo_url ='mongodb+srv://falberola:5zZi7xSEYPPIdGgc@cluster0.hd9lmf3.mongodb.net/datadmin_fincas'
client = MongoClient(mongo_url)
db = client.get_database('datadmin_fincas')
resumen_collection = db['resumen'] 
audios_collection = db['audios'] 

@app.route('/', methods=['GET'])
def plantilla():
    return render_template('endpoints.html')

@app.route('/subir_pdf', methods=['POST'])
def prueba():
    if 'file' not in request.files:
        return "No se proporcionó ningún archivo"
    file = request.files['file']

    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    API_TOKEN = "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"
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    resumen = query({"inputs": text})
    contenido_resumen = resumen[0][next(iter(resumen[0]))]      

    resumen_collection.insert_one({'resumen': contenido_resumen})
    
    return jsonify({'resumen': contenido_resumen}) 

@app.route('/resumen', methods=['GET','POST'])
def resumen():
    text = extract_text('./Acta comunidad.pdf')
    local_pdf_file = './Acta comunidad.pdf'

    API_TOKEN = "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"

    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
        
    resumen = query({"inputs":text})

    contenido_resumen = resumen[0][next(iter(resumen[0]))]

    texto = contenido_resumen

    tts = gTTS(text=texto, lang='es')

    tts.save("audio.mp3")


    resumen_collection.insert_one({'resumen': texto})

    local_audio_file = './audio.mp3'

    # Connect to the GridFS collection
    fs_pdf = GridFS(db, collection='pdfs')
    fs_audio = GridFS(db, collection='audios')

    # Open the local audio file in binary mode ('rb')
    with open(local_audio_file, 'rb') as audio_file:
        # Save the binary content to GridFS
        audio_file_id = fs_audio.put(audio_file, filename='audio.mp3', metadata={'folder': 'audios'})

    with open(local_pdf_file, 'rb') as pdf_file:
        # Save the binary content to GridFS
        pdf_file_id = fs_pdf.put(pdf_file, filename='acta.pdf', metadata={'folder': 'pdfs'})
    #audios_collection.insert_one({'audio': audio_binario})

    return jsonify({'resumen': texto})

@app.route('/audio', methods=['GET','POST'])
def audio():
    text = extract_text('./Acta comunidad.pdf')
    local_pdf_file = './Acta comunidad.pdf'
    #raw = parser.from_file('./texto1.pdf')

    API_TOKEN = "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"

    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
        
    resumen = query({"inputs":text})

    contenido_resumen = resumen[0][next(iter(resumen[0]))]

    texto = contenido_resumen

    tts = gTTS(text=texto, lang='es')

    tts.save("audio.mp3")


    resumen_collection.insert_one({'resumen': texto})

    local_audio_file = './audio.mp3'

    # Connect to the GridFS collection
    fs_pdf = GridFS(db, collection='pdfs')
    fs_audio = GridFS(db, collection='audios')

    # Open the local audio file in binary mode ('rb')
    with open(local_audio_file, 'rb') as audio_file:
        # Save the binary content to GridFS
        audio_file_id = fs_audio.put(audio_file, filename='audio.mp3', metadata={'folder': 'audios'})

    with open(local_pdf_file, 'rb') as pdf_file:
        # Save the binary content to GridFS
        pdf_file_id = fs_pdf.put(pdf_file, filename='acta.pdf', metadata={'folder': 'pdfs'})
    #audios_collection.insert_one({'audio': audio_binario})

    return send_file(local_audio_file, mimetype='audio/mp3', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True,port=8000)