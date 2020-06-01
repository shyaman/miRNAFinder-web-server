# AUTHOR:  Shyaman Jayasundara, jmshyaman@eng.pdn.ac.lk
# DATE:15/03/2020

import sys, getopt
import pandas as pd
from Bio import SeqIO

inputfile = ''
outputfile = ''
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
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
print ('Input file is :', inputfile)
print ('Output file is :', outputfile)

if inputfile == '' or outputfile == '':
  print ('test.py -i <inputfile> -o <outputfile>')
  sys.exit(1)

cols = ['id', 'cg', '%AA', '%AC', '%AG', '%AU', '%CA', '%CC', '%CG', '%CU', '%GA', '%GC', '%GG', '%GU', '%UA', '%UC', '%UG', '%UU', 'mfe1', 'mfe2', 'dG', 'dP', 'dQ', 'dD', 'dF', 'zG', 'zP', 'zQ', 'zD', 'zF', 'mfe3', 'mfe4', 'nefe', 'freq', 'div', 'diff', 'dH', 'dHL', 'dS', 'dSL', 'Tm', 'TmL', 'auL', 'gcL', 'guL', 'bpStems', 'auStems', 'gcStems', 'guStems']
fasta_sequences = SeqIO.parse(open("./data/"+inputfile),'fasta')
id = []
for fasta in fasta_sequences:
    id.append(fasta.id)
ft = pd.read_csv("./data/all."+inputfile+"-48.features",sep='\s+',header=None)
ft.insert(loc=0,column ='id', value=id)
ft.columns = cols
ft.to_excel(outputfile+".xlsx",index=False)
