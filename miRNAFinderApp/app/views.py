from app import app, mlModel
from flask import render_template
from flask import request

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/resources")
def resources():
    return render_template('resources.html')

@app.route("/about-us")
def about_us():
    return render_template('about-us.html')

@app.route("/predict", methods=['POST'])
def predict():
    data = request.form.get('sequence')
    return render_template('index.html', prediction="It's a mirna")