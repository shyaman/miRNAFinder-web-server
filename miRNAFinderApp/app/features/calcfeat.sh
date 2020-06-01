#!/bin/bash
(cd microPred && ./calculateHere.sh $1 $2_micropred)
(cd motif && python3 motiffeat.py -p pos/meme.xml -n neg/meme.xml -i ../microPred/data/$1 -o $2_motif )
(cd triplet && python3 triplet_elements.py -i ../microPred/data/$1 -o $2_triplet)
python3 combine.py -m microPred/$2_micropred.xlsx -n motif/$2_motif.xlsx -t triplet/$2_triplet.xlsx -o $2_feat