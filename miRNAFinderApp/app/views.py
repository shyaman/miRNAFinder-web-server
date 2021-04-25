from app import app
from flask import render_template, send_from_directory
from flask import request, jsonify, url_for
import time
from app.model import predict_class, fastaValidator, resultsToHTML

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
    count = fastaValidator(request.json['seq'])
    if count>10:
        validation = False
        message = "Maximum number of sequences is 10!"
    elif count>0:
        validation = True
        message = "Success!"
    else :
        validation = False
        message = "Invalid input sequence(s)!"
    return jsonify({'msg': message, 'valid': validation})


@app.route("/results",methods = ['POST'])
def results():
    task_id = request.form.get('task_id')
    duration = request.form.get('duration')
    predtab = resultsToHTML(task_id)
    return render_template('results.html',tables=[predtab],tID=task_id, dur= duration)

@app.route('/predict', methods=['POST'])
def predict():
    seq = request.json['seq']
    task = predict_class.apply_async(args=[seq])
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}

@app.route('/feat/<path:task_id>', methods=['GET'])
def download_feat(task_id):
    path = 'static/outputs/'+task_id
    return send_from_directory(directory=path, filename='features.xlsx',as_attachment=True)

@app.route('/pred/<path:task_id>', methods=['GET'])
def download_pred(task_id):
    path = 'static/outputs/'+task_id
    return send_from_directory(directory=path, filename='predictions.xlsx',as_attachment=True)

@app.route('/resourcesdw/<path:filename>', methods=['GET'])
def resourcesdw(filename):
    return send_from_directory(directory='static/resources', filename=filename,as_attachment=True)


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = predict_class.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'duration' in task.info:
            response['task_id'] = task.info['task_id']
            response['duration'] = task.info['duration']

    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(directory='static/assets/img', filename='favicon.ico', mimetype='image/vnd.microsoft.icon')
