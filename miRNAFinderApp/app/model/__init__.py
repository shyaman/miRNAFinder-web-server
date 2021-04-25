import pickle
import sklearn
import os
from Bio import SeqIO
from io import StringIO
import datetime
import random, string
import subprocess
import pandas as pd
import numpy as np
from .. import celery_app 
from .. import app


import time

scalerFile = "files/min_max_scaler.pkl"
pcaFile = "files/pca.pkl"
modelFile = "files/ml_nn_model.pkl"


print('Initializing models....')
min_max_scaler = pickle.load(open(os.path.join(os.path.dirname(__file__), scalerFile), 'rb'))
pca = pickle.load(open(os.path.join(os.path.dirname(__file__), pcaFile), 'rb'))
ml_model = pickle.load(open(os.path.join(os.path.dirname(__file__), modelFile), 'rb'))



@celery_app.task(bind=True)
def predict_class(self, seq):
    start_time = time.time()

    sessionID = self.request.id
    curSessionDir = os.path.join(app.root_path,'static/outputs',sessionID)
    print(curSessionDir)
    assert curSessionDir != ''
    if not os.path.exists(curSessionDir):
            os.makedirs(curSessionDir)

    faString = StringIO(seq.strip())
    fasta = SeqIO.parse(faString, "fasta")
    fasPath = os.path.join(curSessionDir, "sequences.fa")
    SeqIO.write(fasta,fasPath, "fasta-2line")
    print("Success writing seq to path")

    self.update_state(state='PROGRESS',
                          meta={'current': 25, 'total': 100,
                                'status': "Extracting features..."})

    subprocess.run(["./calcfeat.sh",sessionID, curSessionDir],
    cwd=os.path.join(app.root_path,'features'))
    print("Feature claculation success!")
    if(not os.path.isfile(curSessionDir+"/features.xlsx")):
        self.update_state(state='FAILURE')
        return {'status': 'Failed!'}
    
    os.remove(os.path.join(app.root_path,'features/microPred',sessionID+'_micropred.xlsx'))
    os.remove(os.path.join(app.root_path,'features/microPred/data',sessionID))
    os.remove(os.path.join(app.root_path,'features/microPred/data','all.'+sessionID+'-48.features'))
    os.remove(os.path.join(app.root_path,'features/microPred/data','selected.'+sessionID+'.-21.features'))
    os.remove(os.path.join(app.root_path,'features/motif',sessionID+'_motif.xlsx'))
    os.remove(os.path.join(app.root_path,'features/triplet',sessionID+'_triplet.xlsx'))

    feat = pd.read_excel(curSessionDir+"/features.xlsx")
    fFeat = feat.iloc[:,3:]
    fFeat = min_max_scaler.transform(fFeat)
    fFeat = pca.transform(fFeat)

    self.update_state(state='PROGRESS',
                          meta={'current': 50, 'total': 100,
                                'status': "Making predictioins..."})

    classBinary = ml_model.predict(fFeat)
    class_probabilities = ml_model.predict_proba(fFeat)
    confidence_score = class_probabilities[np.arange(len(classBinary)), classBinary]
    finalPred = pd.DataFrame({'Seq-ID':feat.id,'Prediction':classBinary,'Confidence-Score':confidence_score})
    finalPred.replace({'Prediction': {0: "Not a pre-miRNA", 1: "A pre-miRNA"}},inplace=True)
    finalPred.to_excel(curSessionDir+"/predictions.xlsx", index=False)

    duration = time.time() - start_time

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
             'duration': round(duration), 'task_id': sessionID }
       

def fastaValidator(seq):
    faString = StringIO(seq.strip())
    fasta = SeqIO.parse(faString, "fasta")
    seqCount = sum(1 for _ in fasta)
    return seqCount  # False when `fasta` is empty, i.e. wasn't a FASTA file

def resultsToHTML(task_id):
    results = pd.read_excel(os.path.join(app.root_path,'static/outputs',task_id,
        'predictions.xlsx'),index_col=None).to_html(classes='table', border=0, index=False, justify='inherit')
    return results