import pickle
import sklearn
import os
from Bio import SeqIO
from io import StringIO
import datetime
import random, string

scalerFile = "files/min_max_scaler.pkl"
pcaFile = "files/pca.pkl"
modelFile = "files/ml_nn_model.pkl"

sessionDir = 'tmp/'

class Model:
    def __init__(self):
        print('Initializing models....')
        self.min_max_scaler = pickle.load(open(os.path.join(os.path.dirname(__file__), scalerFile), 'rb'))
        self.pca = pickle.load(open(os.path.join(os.path.dirname(__file__), pcaFile), 'rb'))
        self.ml_model = pickle.load(open(os.path.join(os.path.dirname(__file__), modelFile), 'rb'))

        self.__curSessionDir = ''
        self.__faPath = ''
        self.__featPath = ''

    def predict(self,seq):
        self.__createSession()
        assert self.__curSessionDir != ''
        self.fastaS2F(seqStr)

        return 
    
    def __calcfeat(self,):
        # to implement 
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
        self.__curSessionDir = dirName
        return 
    
    def fastaS2F(self,seqStr):
        assert type(seqStr) is str
        faString = StringIO(seqStr)
        fasta = SeqIO.parse(faString, "fasta")
        fasPath = os.path.join(self.__curSessionDir, "sequences.fa")
        SeqIO.write(fasta,fasPath, "fasta-2line")
        print("Success writing seq to path")
        return

    def fastaValidator(self,seq):
        faString = StringIO(seq)
        fasta = SeqIO.parse(faString, "fasta")
        return any(fasta)  # False when `fasta` is empty, i.e. wasn't a FASTA file

model = Model()
s = """>gi|321257144|ref|XP_003193485.1| flap endonuclease [Cryptococcus gattii WM276]
MGIKGLTGLLSENAPKCMKDHEMKTLFGRKVAIDASMSIYQFLIAVRQQDGQMLMNESGDVTSHLMGFFYRTIRMVDHGIKPCYIFDGKPPELKGSVLAKRFARREEAKEGEEEAKETGTAEDVDKLARRQVRVTREHNEECKKLLSLMGIPVVTAPGEAEAQCAELARAGKVYAAGSEDMDTLTFHSPILLRHLTFSEAKKMPISEIHLDVALRDLEMSMDQFIELCILLGCDYLEPCKGIGPKTALKLMREHGTLGKVVEHIRGKMAEKAEEIKAAADQLFLKPDVVNGDDLVLEWKQPDTEGLVEFLCRDKGFNEDRVRAGAAKLSKMLAAKQQGRLDGFFTVKPKEPAAKDAGKGKGKDTKGEKRKAEEKGAAKKKTKK"""
model.predict()
print(model.fastaS2F(s))