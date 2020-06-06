#!/bin/bash
# $1 session id
# $2 session dir

(cd microPred && cp $2/sequences.fa data/$1 && ./calculateHere.sh $1 $1_micropred)
(cd motif && python3 motiffeat.py -p pos/meme.xml -n neg/meme.xml -i ../microPred/data/$1 -o $1_motif )
(cd triplet && python3 triplet_elements.py -i ../microPred/data/$1 -o $1_triplet)
python3 combine.py -m microPred/$1_micropred.xlsx -n motif/$1_motif.xlsx -t triplet/$1_triplet.xlsx -o $2/features