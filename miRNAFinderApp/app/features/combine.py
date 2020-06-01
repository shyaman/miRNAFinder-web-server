import pandas as pd
from pandas import DataFrame
from Bio import SeqIO
import sys, getopt


argv = sys.argv[1:]
meme_files=[]
outfile = '' 
motif = ''
triplet = ''
micropred = ''

try:
    opts, args = getopt.getopt(argv,"hm:n:t:o:")
except getopt.GetoptError:
    print ('combine.py -m <micropred> -n <motif> -t <triplet> -o <outfile>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print ('combine.py -m <micropred> -n <motif> -t <triplet> -o <outfile>')
        sys.exit()
    elif opt in ("-m"):
        micropred = arg
    elif opt in ("-n"):
        motif = arg
    elif opt in ("-t"):
        triplet = arg
    elif opt in ("-o"):
        outfile = arg

if micropred == '' or motif == '' or outfile == '' or triplet == '' :
  print ('combine.py -m <micropred> -n <motif> -t <triplet> -o <outfile>')
  sys.exit(1)

dataFiles = [micropred, motif, triplet]

excels = [pd.read_excel(name) for name in dataFiles]

combined_data={}
combined_data['id']=excels[0]['id']
combined_data['seq']=excels[2]['seq']
combined_data['secondary_structure_dot_bracket']=excels[2]['secondary_structure_dot_bracket']

for data in excels:
    for col in data:
        if(col!='id' and col!="seq" and col!='secondary_structure_dot_bracket'):
            combined_data[col]=data[col]

combined_data = pd.DataFrame(combined_data)
combined_data.to_excel(outfile+'.xlsx',index=False)