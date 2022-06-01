#!/bin/bash
#SBATCH --time=24:30:00
#SBATCH --cpus-per-task=6
#SBATCH --mem=56G
#SBATCH --output=New-%j.out  #%j for jobID

source /home/mohsenh/grMSATransformer/bin/activate

python msaEmbdTrain.py
