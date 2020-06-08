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
    seq = request.files['fafile'].read().decode("utf-8").strip()
    seq = seq or request.form.get('sequence').strip()
    pred = mlModel.predict(seq)
    return render_template('results.html',tables=[pred['pred'].to_html(classes='table', border=0, index=False, justify='inherit')])