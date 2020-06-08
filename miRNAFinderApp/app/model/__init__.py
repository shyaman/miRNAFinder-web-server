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

scalerFile = "files/min_max_scaler.pkl"
pcaFile = "files/pca.pkl"
modelFile = "files/ml_nn_model.pkl"

sessionDir = 'tmp/'

class Model:
    def __init__(self):
        print('Initializing models....')
        self.__min_max_scaler = pickle.load(open(os.path.join(os.path.dirname(__file__), scalerFile), 'rb'))
        self.__pca = pickle.load(open(os.path.join(os.path.dirname(__file__), pcaFile), 'rb'))
        self.__ml_model = pickle.load(open(os.path.join(os.path.dirname(__file__), modelFile), 'rb'))

        self.__sessionID = ''
        self.__curSessionDir = ''

    def predict(self,seq):
        self.__createSession()
        assert self.__curSessionDir != ''
        self.fastaS2F(seq)
        self.__calcfeat()
        print("Feature claculation success!")
        if(not os.path.isfile(self.__curSessionDir+"/features.xlsx")):
            return {'success':False}

        feat = pd.read_excel(self.__curSessionDir+"/features.xlsx")
        fFeat = feat.iloc[:,3:]
        fFeat = self.__min_max_scaler.transform(fFeat)
        fFeat = self.__pca.transform(fFeat)

        classBinary = class_probabilities = self.__ml_model.predict(fFeat)
        class_probabilities = self.__ml_model.predict_proba(fFeat)
        confidence_score = class_probabilities[np.arange(len(classBinary)), classBinary]
        finalPred = pd.DataFrame({'Seq-ID':feat.id,'Class':classBinary,'Confidence-Score':confidence_score})
        finalPred.to_excel(self.__curSessionDir+"/predications.xlsx")

        self.__sessionID = ''
        self.__curSessionDir = ''
        
        return {'success':False, 'pred':finalPred}
    
    def __calcfeat(self):
        subprocess.run(["./calcfeat.sh",self.__sessionID, self.__curSessionDir],
        cwd=os.path.join(os.path.dirname(__file__), "../features"))
        return 

    def __createSession(self):
        # create session name
        x = datetime.datetime.now()
        randS = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        sessionName = x.strftime("%y-%m-%d_%H-%M_")+randS
        # make directory for session
        dirName = os.path.join(os.path.dirname(__file__), sessionDir , sessionName)
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        self.__sessionID = sessionName
        self.__curSessionDir = os.path.join(os.path.abspath(os.path.dirname(__file__)), sessionDir , sessionName)
        return 
    
    def fastaS2F(self,seqStr):
        assert self.fastaValidator(seqStr) == True
        faString = StringIO(seqStr.strip())
        fasta = SeqIO.parse(faString, "fasta")
        fasPath = os.path.join(self.__curSessionDir, "sequences.fa")
        SeqIO.write(fasta,fasPath, "fasta-2line")
        print("Success writing seq to path")
        return

    def fastaValidator(self,seq):
        faString = StringIO(seq.strip())
        fasta = SeqIO.parse(faString, "fasta")
        return any(fasta)  # False when `fasta` is empty, i.e. wasn't a FASTA file

# model = Model()
# model.predict(""">hsa-let-7a-1 MI0000060
# UGGGAUGAGGUAGUAGGUUGUAUAGUUUUAGGGUCACACCCACCACUGGGAGAUAACUAUACAAUCUACUGUCUUUCCUA""")