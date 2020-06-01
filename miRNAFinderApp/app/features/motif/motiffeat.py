import pandas as pd
from Bio import SeqIO
import sys, getopt
import xml.etree.ElementTree as ET


argv = sys.argv[1:]
meme_files=[]
infile = '' 
pos = ''
neg = ''
out = ''

try:
    opts, args = getopt.getopt(argv,"hp:n:i:o:")
except getopt.GetoptError:
    print ('motiffeat.py -p <file1> -n <file2> -i <infile> -o <outfile>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print ('motiffeat.py -p <file1> -n <file2> -i <infile> -o <outfile>')
        sys.exit()
    elif opt in ("-p"):
        pos = arg
    elif opt in ("-n"):
        neg = arg
    elif opt in ("-i"):
        infile = arg
    elif opt in ("-o"):
        out = arg

if pos == '' or neg == '' or infile == '' or out == '':
  print ('motiffeat.py -p <file1> -n <file2> -i <infile> -o <outfile>')
  sys.exit(1)

def getSeqFromFasta(file):
  data={'id':[],'seq':[]}
  with open(file, "r") as handle:
    for record in SeqIO.parse(handle, "fasta"):
        data['id'].append(record.id)
        data['seq'].append(record.seq)
  return data
def getMotifLetters(regexpattern):
  reg=[]
  b=False
  r=''
  flag=False
  for i in regexpattern:

    if (b==False and i=='['):
      b=True

    elif (b==False and i.isalpha() and flag==False):
      reg.append(i)

    elif (b==True and i.isalpha() and flag==False):
      r=r+i
      flag=True
      b=False

    elif (flag==True and i.isalpha() and b==False):
      r=r+i

    elif (i==']' and flag==True):
      reg.append(r)
      r=''
      flag=False
      b=False
    
  return reg

def getMotifList():
  motif_list=[]
  motif_regex={}
  tree = ET.parse(pos)
  root = tree.getroot()
  for motif in root.iter('motif'):
    name = str(motif.attrib['name'])
    if not name in motif_regex.keys(): 
      motif_list.append(name)
      motif_regex[name]=str(motif.find('regular_expression').text).strip()
  tree = ET.parse(neg)
  root = tree.getroot()
  for motif in root.iter('motif'):
    name = str(motif.attrib['name'])
    if not name in motif_regex.keys(): 
      motif_list.append(name)
      motif_regex[name]=str(motif.find('regular_expression').text).strip()
  return motif_list,motif_regex



motif_features={}
data_motifs={}

motif_list,motif_regex=getMotifList()

motif_features={key: [] for key in motif_list}

data=getSeqFromFasta(infile)

data_motifs['id']=data['id']
data_motifs['seq']=data['seq']

for motif in motif_list:
    motif_patternLetters=getMotifLetters(motif_regex[motif])
    w=len(motif_patternLetters)

    for sequence in data['seq']:
        maxMatchScore=0

        for i in range (0,len(sequence)-w + 1):
            count=0
            sub_seq=sequence[i:i+w]
            for j in range(0,w):
                if sub_seq[j] in motif_patternLetters[j]:
                    count=count+1
            match_score=round(count/w,4)
            if(maxMatchScore<match_score):
                maxMatchScore=match_score
        motif_features[motif].append(maxMatchScore)

for i, motif in enumerate(motif_list):
    data_motifs["motif"+str(i)]=motif_features[motif]

pd_motifs = pd.DataFrame(data_motifs)
pd_motifs.to_excel(out+'.xlsx',index=False)


