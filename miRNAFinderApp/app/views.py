from app import app, mlModel
from flask import render_template, send_from_directory
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
    sessionID = mlModel.getSessID()
    return render_template('results.html',tables=[pred['pred'].to_html(classes='table', border=0, index=False, justify='inherit')],sID=sessionID)

@app.route('/feat/<path:filename>', methods=['GET'])
def download_feat(filename):
    direc = mlModel.getDataDir() + '/' + filename
    return send_from_directory(directory=direc, filename='features.xlsx',as_attachment=True)

@app.route('/pred/<path:filename>', methods=['GET'])
def download_pred(filename):
    direc = mlModel.getDataDir() + '/' + filename
    return send_from_directory(directory=direc, filename='predications.xlsx',as_attachment=True)

@app.route('/resourcesdw/<path:filename>', methods=['GET'])
def resourcesdw(filename):
    return send_from_directory(directory='static/resources', filename=filename,as_attachment=True)
