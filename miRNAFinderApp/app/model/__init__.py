import pickle
import sklearn
import os

scalerFile = "scaler.pk"
class Model:
    def __init__(self):
        self.scaler = pickle.load(open(os.path.join(os.path.dirname(__file__), scalerFile), 'rb'))
        print('ml init')

    def predict(self):
        return "nice you're goooood"