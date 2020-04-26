from app import app, mlModel
from flask import render_template
from flask import request

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/predict", methods=['POST'])
def predict():
    data = request.form.get('sequence')
    return render_template('index.html', prediction="It's a mirna")