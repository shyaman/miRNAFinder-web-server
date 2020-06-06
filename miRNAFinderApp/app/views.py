from app import app, mlModel
from flask import render_template
from flask import request, jsonify
import time

@app.route("/",methods = ['GET'])
def index():
    return render_template('index.html')

@app.route("/resources",methods = ['GET'])
def resources():
    return render_template('resources.html')

@app.route("/about-us",methods = ['GET'])
def about_us():
    return render_template('about-us.html')

@app.route("/validate",methods = ['POST'])
def validate():
    validation = mlModel.fastaValidator(request.json['seq'])
    return jsonify({'msg': 'success', 'valid': validation})

@app.route("/results",methods = ['POST','GET'])
def results():
    time.sleep(5)
    return render_template('results.html')