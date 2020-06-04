from app import app, mlModel
from flask import render_template
from flask import request,redirect, url_for
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

@app.route("/predict", methods=['POST','GET'])
def predict():
    # Get the file from post request
    f = request.get_json()
    print(f)
    # # Save the file to ./uploads
    # basepath = os.path.dirname(__file__)
    # file_path = os.path.join(
    #     basepath, 'uploads', secure_filename(f.filename))
    # f.save(file_path)

    # # Make prediction
    # preds = model_predict(file_path, model)

    # # Process your result for human
    # # pred_class = preds.argmax(axis=-1)            # Simple argmax
    # pred_class = decode_predictions(preds, top=1)   # ImageNet Decode
    # result = str(pred_class[0][0][1])               # Convert to string
    return "Send"


@app.route("/results",methods = ['POST','GET'])
def results():
    time.sleep(5)
    return render_template('results.html')