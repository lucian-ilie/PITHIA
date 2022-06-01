import sys
from tensorflow import keras
from keras.models import *
from keras.layers import *
import tensorflow as tf
import keras.backend as K

from keras.layers import LSTM, Dense, Flatten, Reshape, TimeDistributed, Bidirectional, CuDNNLSTM, CuDNNGRU, GRU, \
    Dropout, Input, Conv2D, MaxPool2D, ConvLSTM2D, SpatialDropout2D, Conv1D, MaxPool1D, Concatenate, BatchNormalization, \
    Activation, AveragePooling2D, Embedding, MultiHeadAttention, Lambda, GlobalMaxPooling1D


import numpy as np
from keras.models import load_model
from collections import defaultdict


LOCAL_NEGHBOR_SIZE = 4 
GLOBAL_NEIGHBOR_SIZE = 0 # Even (WILL INCREASE IF NOT ENOUGH LOCAL NEGHBOR)
WINDOW_SIZE = 1 + 2*LOCAL_NEGHBOR_SIZE + GLOBAL_NEIGHBOR_SIZE
KEY_SIZE = WINDOW_SIZE
HEAD_NUM = 1

def protToDict(datasetAddress, embd_files):
    protDict =  defaultdict(dict)
    dataset_file = open(datasetAddress)
    while True:
        line_PID = dataset_file.readline().strip()[1:]
        line_Pseq = dataset_file.readline().strip()
        #line_feature = dataset_file.readline().strip()
        if not line_Pseq:
            break
        if len(line_Pseq) < 1024:
            prot_file = open('{}/{}.txt'.format(embd_files, line_PID))
            for index, prot_line in enumerate(prot_file):
                prot_line = prot_line.strip().split(':')[1]
                embd_value = [float(x) for x in prot_line.split()]
                protDict[line_PID][index] = embd_value
    return protDict




def readFeatures2D(neighborList,proteinName, protDict):
    selectedFeature = []
    for neighbor in neighborList:
        if neighbor != 'Zpad':
            try:
                selectedFeature.append(np.array(protDict[proteinName][neighbor]))
            except:
                print(proteinName, neighbor)
                print(protDict[proteinName])
                exit(1)
        else:
                selectedFeature.append(np.zeros(768).astype('float32'))

    return np.array(selectedFeature)
    

def build2DWindows(aaIndex, proteinLenght, proteinName, protDict, windowSize=WINDOW_SIZE):
    addToLeft = 0
    addToRight = 0
    if aaIndex <= LOCAL_NEGHBOR_SIZE:
        addToLeft = LOCAL_NEGHBOR_SIZE - aaIndex
    if aaIndex+LOCAL_NEGHBOR_SIZE + 1 > proteinLenght:
        addToRight = aaIndex+LOCAL_NEGHBOR_SIZE + 1 - proteinLenght

    neighborList = [i for i in range(aaIndex-LOCAL_NEGHBOR_SIZE + addToLeft, aaIndex+LOCAL_NEGHBOR_SIZE+1 - addToRight)]
    #print(neighborList)
    cnt = 0
    lrFlag = 0 + addToRight - addToLeft
    for i in range(100):
        if cnt < GLOBAL_NEIGHBOR_SIZE + addToRight + addToLeft:
            if lrFlag <= 0:
                neighborList = ['Zpad'] + neighborList
                lrFlag +=1
                cnt +=1
            else:
                neighborList = neighborList + ['Zpad']
                lrFlag -= 1
                cnt +=1
        else:
            break
    
    Features2D = readFeatures2D(neighborList, proteinName,protDict)
    #print(Features2D.shape)
    return Features2D
    


def readSort(datasetAddress, embd_files):
    features3D = []
    labels = []
    protDict = protToDict(datasetAddress, embd_files)
    dataset_file = open(datasetAddress, 'r')
    while True:
        line_PID = dataset_file.readline().strip()
        line_Pseq = dataset_file.readline().strip()
        #line_feature = dataset_file.readline().strip()
        if not line_Pseq:
            break
        len_line_Pseq = len(line_Pseq)
        if len_line_Pseq < 1024:
            protName = line_PID[1:]
            for aaIndex in range(len_line_Pseq):
                features3D.append(build2DWindows(aaIndex, len_line_Pseq, protName, protDict))
    print(np.array(features3D).shape)
    return np.array(features3D)



def Predict(test_all_features_np3D, input_file, output_dir, selectedModel):
    if selectedModel=='TF':
        input_features = Input(shape=((int)(WINDOW_SIZE), 768), name="input_ens_1")
        att_layer = MultiHeadAttention(num_heads=HEAD_NUM, key_dim=KEY_SIZE)(input_features, input_features)
        out3 = Flatten()(att_layer) 
        out3 = Dropout(rate=0)(out3)
        out3 = Dense(128, activation='relu', name="dense_att_1")(out3)
        out3 = Dropout(rate=0)(out3)
        out3 = Dense(16, activation='relu', name="dense_att_2")(out3)
        out3 = Dropout(rate=0)(out3)
        out3 = Dense(1, activation='sigmoid', name="dense_att_4")(out3)
        model = keras.models.Model(inputs=input_features, outputs=out3)
        model.load_weights("models/PITHIA.h5")


    
    y_pred_testing = model.predict(test_all_features_np3D, batch_size=1024).ravel()

    # load input proteins again and output the predict values 
    start_index = 0
    fin = open(input_file, "r")
    while True:
        line_PID = fin.readline()[1:].rstrip('\n').rstrip(' ')
        line_Pseq = fin.readline().rstrip('\n').rstrip(' ')
        #line_feature = fin.readline().rstrip('\n').rstrip(' ')
        if not line_Pseq:
            break
        fout = open("{}/{}.txt".format(output_dir, line_PID.upper()), "w")
        #fout = open("outDset500/"+line_PID.upper()+".txt", "w")

        for i in range(len(line_Pseq)):
            fout.write("{}\t{}\t{}\n".format(i,line_Pseq[i], str(y_pred_testing[start_index + i])))
        fout.close()
        start_index += len(line_Pseq)
    fin.close()







def main():
    input_file = sys.argv[1]
    embd_files = sys.argv[2]
    output = sys.argv[3]

    protDict = protToDict(input_file, embd_files)
    test_all_features_np3D = readSort(input_file, embd_files)
    Predict(test_all_features_np3D, input_file, output, 'TF')
    print('Done!')
    

if __name__ == '__main__':
    main()
