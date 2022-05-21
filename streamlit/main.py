import streamlit as st
import pandas as pd
import numpy as np
from Bio import SeqIO
from io import StringIO
import time
import uuid 
import pickle
import os
import subprocess

if 'id' not in st.session_state:
    st.session_state.id = str(uuid.uuid1())

if 'fasta' not in st.session_state:
    st.session_state.fasta = ''

scalerFile = "files/min_max_scaler.pkl"
pcaFile = "files/pca.pkl"
modelFile = "files/ml_nn_model.pkl"

min_max_scaler = pickle.load(open(os.path.join(os.path.dirname(__file__), scalerFile), 'rb'))
pca = pickle.load(open(os.path.join(os.path.dirname(__file__), pcaFile), 'rb'))
ml_model = pickle.load(open(os.path.join(os.path.dirname(__file__), modelFile), 'rb'))


# this fn validate the fasta file and returns the num of seqs
def fastaValidator(seq):
    faString = StringIO(seq.strip())
    fasta = SeqIO.parse(faString, "fasta")
    seqCount = sum(1 for _ in fasta)
    return seqCount

def predict(seq):
    sessionID = st.session_state.id
    curSessionDir = os.path.join(os.path.dirname(__file__),'static/outputs',sessionID)
    assert curSessionDir != ''
    if not os.path.exists(curSessionDir):
            os.makedirs(curSessionDir)

    faString = StringIO(seq.strip())
    fasta = SeqIO.parse(faString, "fasta")
    fasPath = os.path.join(curSessionDir, "sequences.fa")
    SeqIO.write(fasta,fasPath, "fasta-2line")


    subprocess.run(["./calcfeat.sh",sessionID, curSessionDir],
                cwd=os.path.join(os.path.dirname(__file__),'features'))

    if(not os.path.isfile(curSessionDir+"/features.xlsx")):
        st.error("Error occured!")
        exit()

    
    os.remove(os.path.join(os.path.dirname(__file__),'features/microPred',sessionID+'_micropred.xlsx'))
    os.remove(os.path.join(os.path.dirname(__file__),'features/microPred/data',sessionID))
    os.remove(os.path.join(os.path.dirname(__file__),'features/microPred/data','all.'+sessionID+'-48.features'))
    os.remove(os.path.join(os.path.dirname(__file__),'features/microPred/data','selected.'+sessionID+'.-21.features'))
    os.remove(os.path.join(os.path.dirname(__file__),'features/motif',sessionID+'_motif.xlsx'))
    os.remove(os.path.join(os.path.dirname(__file__),'features/triplet',sessionID+'_triplet.xlsx'))

    feat = pd.read_excel(curSessionDir+"/features.xlsx")
    fFeat = feat.iloc[:,3:]
    fFeat = min_max_scaler.transform(fFeat)
    fFeat = pca.transform(fFeat)

    classBinary = ml_model.predict(fFeat)
    class_probabilities = ml_model.predict_proba(fFeat)
    confidence_score = class_probabilities[np.arange(len(classBinary)), classBinary]
    finalPred = pd.DataFrame({'Seq-ID':feat.id,'Prediction':classBinary,'Confidence-Score':confidence_score})
    finalPred.replace({'Prediction': {0: "Not a pre-miRNA", 1: "A pre-miRNA"}},inplace=True)
    finalPred.to_excel(curSessionDir+"/predictions.xlsx", index=False)

    return finalPred

st.title("miRNAFinder")

seq = st.text_area("Enter sequences in FASTA format",key="fasta")

seq_file = st.file_uploader("Or, Upload a FASTA file", type=["fa", "fasta"])

if seq_file is not None:

    # To convert to a string based IO:
    stringio = StringIO(seq_file.getvalue().decode("utf-8"))

    # To read file as string:
    seq = stringio.read()

if seq != "" and not fastaValidator(seq):
    st.error("Invalid input sequence(s)!")

predict_clicked = st.button("Predict",disabled= not fastaValidator(seq))

if  predict_clicked:
    # Add a placeholder
    latest_iteration = st.empty()
    start_time = time.time()
    pred_out = predict(seq)
    duration = time.time() - start_time
    st.write(pred_out)
    