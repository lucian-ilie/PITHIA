#!/bin/bash
# Usage: bash run_PITIHA.sh [DATASET_FILE_ADDRESS]


export DATASET_FILE=$1
mkdir testFeatures
mkdir testFeatures/fasta/
mkdir testFeatures/a3m/
mkdir testFeatures/embd/
mkdir outputMSA

fastaDir=testFeatures/fasta/
a3mDir=testFeatures/a3m/
embd=testFeatures/embd/
output=outputMSA/

python fastaToFile.py $DATASET_FILE $fastaDir

bash gra3m.sh $fastaDir $a3mDir
source /home/ubuntu/deepENV/bin/activate
python msaEmbd.py $DATASET_FILE $a3mDir $embd
python predict.py $DATASET_FILE $embd $output
