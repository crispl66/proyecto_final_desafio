from flask import Flask, jsonify, render_template, request, send_file
from gtts import gTTS
import requests
import os 
from pymongo import MongoClient 
from pdfminer.high_level import extract_text 
from gridfs import GridFS
from bson import ObjectId

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
def subir_pdf():
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

    return jsonify({
        'pdf_id': str(pdf_file_id),
        'audio_id': str(audio_file_id),
        'resumen': texto,
    })

@app.route('/get_pdf/<pdf_id>', methods=['GET'])
def get_pdf(pdf_id):
    fs_pdf = GridFS(db, collection='pdfs')
    pdf_file = fs_pdf.get(ObjectId(pdf_id))
    return send_file(pdf_file, as_attachment=True)


@app.route('/get_audio/<audio_id>', methods=['GET'])
def get_audio(audio_id):
    fs_audio = GridFS(db, collection='audios')
    audio_file = fs_audio.get(ObjectId(audio_id))
    return send_file(audio_file, mimetype='audio/mpeg', as_attachment=True)



@app.route('/resumen', methods=['GET','POST'])
def resumen():
    #if 'file' not in request.files:
    #    return "No se proporcionó ningún archivo"
    #file = request.files['file']
    #file_content = request.args.get('file_content')

    file_path = os.path.join("temp", "uploaded_file.pdf")

    file = request.files['file']

    if not os.path.exists(file_path):
        return "No se encontró el archivo", 400
    if not file:
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

if __name__ == '__main__':
    app.run(debug=True,port=8000)