#!/bin/bash
# ./calculateHere.sh input_file output_file
(cd progs && perl microPred.pl $1)
python3 micropredid.py -i $1 -o $2 