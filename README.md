# The source code of PITHIA web server
The PITHIA source code is designed for high-throughput prediction. It does not have the limitation of 10 sequences per run.
# Citation
SeyedMohsen Hosseini and Lucian Ilie, PITHIA: Protein interaction site prediction using
multiple sequence alignments and attention. 

Contact: 

SeyedMohsen Hosseini (shosse59@uwo.ca)

Lucian Ilie (ilie@uwo.ca)
# System requirement
PITHIA is developed under Linux environment with python 3.7.
Recommended RAM: > 24GB. The RAM requirement mainly depends on the length of the input sequence. 

# Installation
1. clone the source code of PITHIA
```
mkdir -p Src && cd Src
git clone [PITHIA git link]
```
2. install python packages. Python virtual environment is recommended for package management.

```
pip3 install -r requirement.txt
```

3. install dependencies

 
 - install [hh-suite](https://github.com/soedinglab/hh-suite). The [database](http://gwdu111.gwdg.de/~compbiol/uniclust/2020_06/) used in PITHIA is uniref30_2020_06.
 
# Running PITIHA
```
bash run_PITIHA.sh [Fasta file]
```

# PITIHA model architecture 
![](img/Model_architecture.png)
