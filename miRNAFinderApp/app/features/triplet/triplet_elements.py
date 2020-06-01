import RNA
import re
import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize
import random
import sys, getopt

#import biopython library
from Bio import SeqIO

import os
from collections import OrderedDict

inputfile = ''
outputfile = ''
try:
    opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile="])
except getopt.GetoptError:
    print ('test.py -i <inputfile> -o <outputfile>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print ('test.py -i <inputfile> -o <outputfile>')
        sys.exit()
    elif opt in ("-i", "--ifile"):
        inputfile = arg
    elif opt in ("-o", "--ofile"):
        outputfile = arg

if inputfile == '' or outputfile == '':
    print ('test.py -i <inputfile> -o <outputfile>')
    sys.exit(1)

#Calculate triplet element for given sequrnce and structure
def calculateTripletElement(seq, struct):
    #preprocess sequence and structure
    seq = re.sub(r'[R]', random.choice(["A", "G"]), seq)
    seq = re.sub(r'[Y]', "C", seq)
    seq = re.sub(r'[W]', "A", seq)
    seq = re.sub(r'[S]', random.choice(["C", "G"]), seq)
    seq = re.sub(r'[M]', random.choice(["C", "A"]), seq)
    seq = re.sub(r'[K]', "G", seq)
    seq = re.sub(r'[B]', random.choice(["C", "G"]), seq)
    seq = re.sub(r'[D]', random.choice(["A", "G"]), seq)
    seq = re.sub(r'[V]', random.choice(["C", "A", "G"]), seq)
    seq = re.sub(r'[H]', random.choice(["C", "A"]), seq)
    seq = re.sub(r'[N]', random.choice(["C", "A", "G", "U"]), seq)
    seq = re.sub(r'[^ACGUacgu]', "U", seq)
    struct = re.sub(r'[)]', "(", struct)
    
    #create triplet dict
    nucleotide = ['A', 'C', 'G', 'U']
    dotBrackets = ["(((", "((.", "(..", "(.(", ".((", ".(.", "..(", "..."]
    tripletEl = OrderedDict()
    for char in nucleotide:
        for dotB in dotBrackets:
            tripletEl[str(char+dotB)] = 0
            
    #counting triplet elements
    triplet = []

    i=0
    kmer=3
    while i < len(seq):
        subStr = seq[i : i+kmer]
        subStruct = struct[i : i+kmer]
        i=i+1

        if len(subStr) == 3:
            tripStr = subStr[1] + subStruct
            tripletEl[str(tripStr)] = tripletEl.get(str(tripStr)) + 1 
            
    #normalized the vector
    tripletArr = np.zeros([1, 32], dtype = float)
    count = 0
    for elemt in tripletEl.values():
        tripletArr[0, count] = elemt
        count = count + 1
    tripletArr = normalize(tripletArr)
    
    #update dict with normalized values
    count = 0
    for key, value in tripletEl.items():
        tripletEl[str(key)] = tripletArr[0, count]
        count = count + 1
    
    #Create dataframe and return
    return pd.DataFrame([tripletEl])

# Turn-off dangles globally
RNA.cvar.dangles = 0

# Nearest Neighbor Parameter reversal functions
revert_NN = { 
    RNA.DECOMP_PAIR_HP:       lambda i, j, k, l, f, p: - f.eval_hp_loop(i, j) - 100,
    RNA.DECOMP_PAIR_IL:       lambda i, j, k, l, f, p: - f.eval_int_loop(i, j, k, l) - 100,
    RNA.DECOMP_PAIR_ML:       lambda i, j, k, l, f, p: - p.MLclosing - p.MLintern[0] - (j - i - k + l - 2) * p.MLbase - 100,
    RNA.DECOMP_ML_ML_STEM:    lambda i, j, k, l, f, p: - p.MLintern[0] - (l - k - 1) * p.MLbase,
    RNA.DECOMP_ML_STEM:       lambda i, j, k, l, f, p: - p.MLintern[0] - (j - i - k + l) * p.MLbase,
    RNA.DECOMP_ML_ML:         lambda i, j, k, l, f, p: - (j - i - k + l) * p.MLbase,
    RNA.DECOMP_ML_ML_ML:      lambda i, j, k, l, f, p: 0,
    RNA.DECOMP_ML_UP:         lambda i, j, k, l, f, p: - (j - i + 1) * p.MLbase,
    RNA.DECOMP_EXT_STEM:      lambda i, j, k, l, f, p: - f.E_ext_loop(k, l),
    RNA.DECOMP_EXT_EXT:       lambda i, j, k, l, f, p: 0,
    RNA.DECOMP_EXT_STEM_EXT:  lambda i, j, k, l, f, p: - f.E_ext_loop(i, k),
    RNA.DECOMP_EXT_EXT_STEM:  lambda i, j, k, l, f, p: - f.E_ext_loop(l, j),
    RNA.DECOMP_EXT_EXT_STEM1: lambda i, j, k, l, f, p: - f.E_ext_loop(l, j-1),
            }

fasta_sequences = SeqIO.parse(inputfile,'fasta')
sequence = []
id = []
secondary_structure_dot_bracket = []
secondary_structure_mfe = []
for fasta in fasta_sequences:
    seq1 = str(fasta.seq)
    sequence.append(seq1)
    id.append(fasta.id)
    # Data structure that will be passed to our MaximumMatching() callback with two components:
    # 1. a 'dummy' fold_compound to evaluate loop energies w/o constraints, 2. a fresh set of energy parameters
    mm_data = { 'dummy': RNA.fold_compound(seq1), 'params': RNA.param() }

    # Maximum Matching callback function (will be called by RNAlib in each decomposition step)
    def MaximumMatching(i, j, k, l, d, data):
        return revert_NN[d](i, j, k, l, data['dummy'], data['params'])

    # Create a 'fold_compound' for our sequence
    fc = RNA.fold_compound(seq1)

    # Add maximum matching soft-constraints
    fc.sc_add_f(MaximumMatching)
    fc.sc_add_data(mm_data, None)

    # Call MFE algorithm
    (s, mm) = fc.mfe()

    secondary_structure_dot_bracket.append(s)
    secondary_structure_mfe.append(-mm)
    # print result
    # print ("%s\n%s (MM: %d)\n" %  (seq1, s, mm))
dict = {'id': id, 'seq': sequence, 'secondary_structure_dot_bracket': secondary_structure_dot_bracket}  
dataframe = pd.DataFrame(dict)
         
#create empty dataframe
nucleotide = ['A', 'C', 'G', 'U']
dotBrackets = ["(((", "((.", "(..", "(.(", ".((", ".(.", "..(", "..."]
columns = []
for char in nucleotide:
    for dotB in dotBrackets:
        columns.append(str(char+dotB))


tripletDf = pd.DataFrame(columns = columns)

for index, row in dataframe.iterrows():
    seq = str(row['seq'])
    struct = str(row['secondary_structure_dot_bracket'])
    currDf = calculateTripletElement(seq, struct)
    tripletDf = tripletDf.append(currDf, ignore_index=True, sort=False)
newDf = pd.concat([dataframe,tripletDf], axis=1, sort=False)
newDf.to_excel(outputfile+'.xlsx', index=False)

