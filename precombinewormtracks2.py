import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle
import sys
import h5py
import argparse

def findpair(ID2,history,possiblecombos):
    if ID2 in list(possiblecombos.ID1):
        #need to consider that there may be more than one possibility for an end point
        #ended up taking the first value because it's the closest in time
        return(findpair(list(possiblecombos.loc[possiblecombos.ID1==ID2].ID2)[0],history+[ID2],possiblecombos))
    else:
        return(history+[ID2])

def findpairreverse(ID1,history,possiblecombos):
    if ID1 in list(possiblecombos.ID2):
        #need to consider that there may be more than one possibility for an end point
        #ended up taking the first value because it's the closest in time
        return(findpairreverse(list(possiblecombos.loc[possiblecombos.ID2==ID1].ID1)[0],history+[ID1],possiblecombos))
    else:
        return(history+[ID1])

def precombinewormtracks(path,type):
    if path[-3:]=="npy":
        tracks=np.load(path)
        tracksdf=pd.DataFrame(tracks, columns = ['ID','time','x','y'])
        print("File type: npy")
    elif path[-3:]=="csv":
        print("File type: csv")
        if type == "numpy":
            tracksdf=pd.DataFrame(np.genfromtxt(path), columns = ['ID','time','x','y'])
        else:
            tracksdf=pd.read_csv(path)
            if 'Unnamed: 0' in tracksdf.columns:
                tracksdf=tracksdf.drop(columns=['Unnamed: 0'])
    elif path[-2:]=="h5":
        print("File type: h5")
        img=h5py.File(path,"r+")
        tracks=img["points"]
        tracksdf=pd.DataFrame(tracks, columns = ['ID','time','x','y'])

    outputs={}
    outputs["tracksdf"]=tracksdf

    with open('precombinewormtracks.pickle', 'wb') as handle:
        pickle.dump(outputs, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Precombine worm tracks')
    parser.add_argument('pointpath', help='points path')
    parser.add_argument('-type', type=str, default="numpy", help='type of dataset, either numpy or pandas')

    args=parser.parse_args()

    pointpath=args.pointpath
    type=args.type
    precombinewormtracks(pointpath,type)
