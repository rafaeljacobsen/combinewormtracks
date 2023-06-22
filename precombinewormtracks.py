import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import pickle
import sys

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

def precombinewormtracks(path):
    tracks=np.load(path)
    tracksdf=pd.DataFrame(tracks, columns = ['ID','time','x','y'])

    #removes womrs with a mean angle between points less than 120
    meanangles=pd.DataFrame(columns=["meanangle"],index=np.unique(tracksdf.ID).astype(int))
    print("Removes slow and erratic worms:")
    for ID in tqdm(np.unique(tracksdf.ID).astype(int)):
        if len(tracksdf.loc[tracksdf.ID==ID])<6:
            meanangles.loc[ID]=120
            continue
        start=int(min(tracksdf.loc[tracksdf.ID==ID].time))
        end=int(max(tracksdf.loc[tracksdf.ID==ID].time))
        #takes three consecutive points in time and calculates the engle between them
        a=tracksdf.loc[(tracksdf.ID==ID)
                       &(start<tracksdf.time)
                       &(tracksdf.time<end-2)]
        b=tracksdf.loc[(tracksdf.ID==ID)
                       &(start+1<tracksdf.time)
                       &(tracksdf.time<end-1)]
        c=tracksdf.loc[(tracksdf.ID==ID)
                       &(start+2<tracksdf.time)
                       &(tracksdf.time<end)]
        meanangles.loc[ID]=np.mean(np.abs(np.degrees(np.arctan2(np.asarray(c.y)-np.asarray(b.y),
                                                                          np.asarray(c.x)-np.asarray(b.x))
                                                               - np.arctan2(np.asarray(a.y)-np.asarray(b.y),
                                                                            np.asarray(a.x)-np.asarray(b.x)))))
    tracksdf=tracksdf[np.isin(np.asarray(tracksdf.ID),meanangles[meanangles.meanangle>=120].index)]

    #creates dataframe with start and end times for each ID
    startend=pd.DataFrame(columns=["start","end"])
    for ID in np.unique(tracksdf.ID).astype(int):
        startend.loc[ID,:]=int(np.min(tracksdf.loc[tracksdf.ID==ID].time)),int(np.max(tracksdf.loc[tracksdf.ID==ID].time))
    startend=startend.astype(int)

    #gets all possible combinations of two indexes within 10 frames and 20 distance
    possiblecombos=pd.DataFrame(columns=["ID1","ID2","end","start"])#,"dist"])
    print("Finds all possible track combinations")
    for ID in tqdm(np.unique(tracksdf.ID)):
        endindex=startend.loc[ID].end
        endlocation=tracksdf.loc[(tracksdf.ID==ID) & (tracksdf.time==endindex),["x","y"]].values
        for end in range(endindex,endindex+10):
            if end+1 in list(startend.start):
                for startID in startend.index[startend.start==end+1]:
                    startlocation=tracksdf.loc[(tracksdf.ID==startID) & (tracksdf.time==end+1),["x","y"]].values
                    if np.linalg.norm(startlocation-endlocation) < 20:
                        possiblecombos.loc[len(possiblecombos.index)] = [int(ID),startID,endindex,end+1]#,np.linalg.norm(startlocation-endlocation)]

    #finds all certain combinations
    dists=[]
    angles=[]
    lengths=np.zeros([len(possiblecombos.index),2])
    print("Finds worm combinations that are very likely to be correct:")
    for i in tqdm(range(len(possiblecombos.index))):
        ID1=int(possiblecombos[possiblecombos.index==i].ID1.iloc[0])#stores IDs for the start and end track
        ID2=int(possiblecombos[possiblecombos.index==i].ID2.iloc[0])#stores IDs for the start and end track
        lengths[i,:]=[len(tracksdf[tracksdf.ID==ID1]),len(tracksdf[tracksdf.ID==ID2])] #stores the lengths of each track

        #finds the difference between the last points of ID1
        diff1=(tracksdf[(tracksdf.ID==ID1) & (tracksdf.time==startend.loc[ID1].end)][["x","y"]].values[0]
               -tracksdf[(tracksdf.ID==ID1) & (tracksdf.time==startend.loc[ID1].end-1)][["x","y"]].values[0])
        #finds the difference between the first points of ID2
        diff2=(tracksdf[(tracksdf.ID==ID2) & (tracksdf.time==startend.loc[ID2].start+1)][["x","y"]].values[0]
               -tracksdf[(tracksdf.ID==ID2) & (tracksdf.time==startend.loc[ID2].start)][["x","y"]].values[0])
        #finds the location of the end of ID1
        ID1end=tracksdf[(tracksdf.ID==ID1)&(tracksdf.time==max(tracksdf[tracksdf.ID==ID1].time))][["x","y"]].values[0]

        #finds the location of the start of ID2
        ID2start=tracksdf[(tracksdf.ID==ID2)&(tracksdf.time==min(tracksdf[tracksdf.ID==ID2].time))][["x","y"]].values[0]

        #finds the distance between the predicted points
        dist = np.sqrt(np.sum(np.square(ID1end+diff1*(int(possiblecombos[possiblecombos.index==i].start.iloc[0])
                                                  -int(possiblecombos[possiblecombos.index==i].end.iloc[0]))/2
                                        -(ID2start-diff2*(int(possiblecombos[possiblecombos.index==i].start.iloc[0])
                                                      -int(possiblecombos[possiblecombos.index==i].end.iloc[0]))/2))))
        #finds the angle between the predicted lines
        angle = np.min([np.abs(np.arctan2(diff1[1],diff1[0])
                           -np.arctan2(diff2[1],diff2[0]))*(180/np.pi),
                    360-np.abs(np.arctan2(diff1[1],diff1[0])
                               -np.arctan2(diff2[1],diff2[0]))*(180/np.pi)])
        dists.append(dist)
        angles.append(angle)

    #combines IDs found with the above method
    confirmeds=np.nonzero((np.asarray(dists)<10)
                      & (np.sum(lengths,axis=1)>=15)
                      & (lengths[:,0]>=4)
                      & (lengths[:,1]>4)
                      & (np.asarray(angles)<60))[0]
    if np.any(np.unique(possiblecombos.loc[confirmeds].ID1,return_counts=True)[1]!=1) or np.any(np.unique(possiblecombos.loc[confirmeds].ID2,return_counts=True)[1]!=1):
        print("ERROR: PRELIMINARY CLASSIFICATION FAILED: DUPLICATE MADE")

    idstodrop=[]
    for i in confirmeds: #i represents the index of correct combo
        ID1,ID2=possiblecombos.loc[i][["ID1","ID2"]].values
        tracksdf.loc[tracksdf.ID==ID2,["ID"]]=ID1
        idstodrop.append(np.asarray(possiblecombos[possiblecombos.ID2==ID2].index))

    #creates dataframe with start and end times for each ID
    startend=pd.DataFrame(columns=["start","end"])
    for ID in np.unique(tracksdf.ID).astype(int):
        startend.loc[ID,:]=int(np.min(tracksdf.loc[tracksdf.ID==ID].time)),int(np.max(tracksdf.loc[tracksdf.ID==ID].time))
    startend.astype(int)

    possiblecombos=pd.DataFrame(columns=["ID1","ID2","end","start"])#,"dist"])
    print("Finds all possible track combinations again:")
    for ID in tqdm(np.unique(tracksdf.ID)):
        endindex=startend.loc[ID].end
        endlocation=tracksdf.loc[(tracksdf.ID==ID) & (tracksdf.time==endindex),["x","y"]].values
        for end in range(endindex,endindex+10):
            if end+1 in list(startend.start):
                for startID in startend.index[startend.start==end+1]:
                    startlocation=tracksdf.loc[(tracksdf.ID==startID) & (tracksdf.time==end+1),["x","y"]].values
                    if np.linalg.norm(startlocation-endlocation) < 20:
                        possiblecombos.loc[len(possiblecombos.index)] = [int(ID),startID,endindex,end+1]#,np.linalg.norm(startlocation-endlocation)]

    combos=[]
    for ID in np.unique(tracksdf.ID).astype(int):
        combo=list(np.flip(findpairreverse(ID,[],possiblecombos))[:-1])+findpair(ID,[],possiblecombos)
        len(combo)>1 and combos.append(sorted(combo))

    uniquecombos=[]
    for combo in combos:
        if combo not in uniquecombos:
            uniquecombos.append(combo)
    combos=uniquecombos
    print("Number of combinations: "+str(len(combos)))

    outputs={}
    outputs["combos"]=combos
    outputs["tracksdf"]=tracksdf
    outputs["startend"]=startend

    with open('precombinewormtracks.pickle', 'wb') as handle:
        pickle.dump(outputs, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    path = sys.argv[1]
    precombinewormtracks(path)
