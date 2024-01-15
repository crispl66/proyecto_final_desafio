import os
import shutil
import cv2
import json
import pandas as pd
import logging
from flask import Flask, jsonify, request, flash, redirect, Response
from pathlib import Path



app = Flask(__name__)

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
@app.route('/pass', methods=['POST'])
def post():
try:
    pdf_file = request.files['file']
    pdf_name = pdf_file.filename
    save_path = os.path.join(
    app.config.get('upload_folder'),pdf_name)
    pdf_file.save(save_path)
    # getting file size
    file=Path(save_path).stat().st_size
    shutil.rmtree(upload_folder)
    final_data = pd.DataFrame(
    {'pdf':pdf_name,'size':"{} bytes".format(file)})
    return final_data.to_json(orient="records")
except Exception as e:
    app.logger.info("error occurred")