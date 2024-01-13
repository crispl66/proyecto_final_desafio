from flask import Flask, jsonify, render_template, request
from transformers import pipeline
from gtts import gTTS
import requests
import os 
from pymongo import MongoClient 
from pdfminer.high_level import extract_text 

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
        return render_template ('endpoints.html')

@app.route('/subir_pdf', methods=['POST'])
    def subir_pdf():
        file = request.files['file']
        return file

@app.route('/resumen', methods=['GET'])
    def resumen(file):
        text = extract_text (file)
        API_TOKEN = "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"

        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {API_TOKEN}"}

        def query(payload):
	        response = requests.post(API_URL, headers=headers, json=payload)
	        return response.json()

        resumen = query({"inputs":text})
        contenido_resumen = resumen[0][next(iter(resumen[0]))]
        resumen_collection.insert_one({'resumen': contenido_resumen})
        return jsonify(contenido_resumen)

@app.route('/audio', methods=['GET'])
    def audio(contenido_resumen)
        tts = gTTS(text=contenido_resumen, lang='es')
        audio = tts.save("audio.mp3")
        audios_collection.insert_one({'audio': audio})
        return audio

if __name__ == '__main__':
    app.run(debug=True,port=8080)
