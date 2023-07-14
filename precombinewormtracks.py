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
    elif path[-3:]=="csv":
        if type == "numpy":
            tracksdf=pd.DataFrame(np.genfromtxt(path), columns = ['ID','time','x','y'])
        else:
            tracksdf=pd.read_csv(path)
            tracksdf=tracksdf.drop(columns=['Unnamed: 0'])
    elif path[-2:]=="h5":
        img=h5py.File(path,"r+")
        tracks=img["points"]
        tracksdf=pd.DataFrame(tracks, columns = ['ID','time','x','y'])
    #removes womrs with a mean angle between points less than 120
    #meanangles=pd.DataFrame(columns=["meanangle"],index=np.unique(tracksdf.ID).astype(int))
    #print("Removes slow and erratic worms:")
    #for ID in tqdm(np.unique(tracksdf.ID).astype(int)):
    #    if len(tracksdf.loc[tracksdf.ID==ID])<6:
    #        meanangles.loc[ID]=120
    #        continue
    #    start=int(min(tracksdf.loc[tracksdf.ID==ID].time))
    #    end=int(max(tracksdf.loc[tracksdf.ID==ID].time))
    #    #takes three consecutive points in time and calculates the engle between them
    #    a=tracksdf.loc[(tracksdf.ID==ID)
    #                   &(start<tracksdf.time)
    #                   &(tracksdf.time<end-2)]
    #    b=tracksdf.loc[(tracksdf.ID==ID)
    #                   &(start+1<tracksdf.time)
    #                   &(tracksdf.time<end-1)]
    #    c=tracksdf.loc[(tracksdf.ID==ID)
    #                   &(start+2<tracksdf.time)
    #                   &(tracksdf.time<end)]
    #    meanangles.loc[ID]=np.mean(np.abs(np.degrees(np.arctan2(np.asarray(c.y)-np.asarray(b.y),
    #                                                                      np.asarray(c.x)-np.asarray(b.x))
    #                                                           - np.arctan2(np.asarray(a.y)-np.asarray(b.y),
    #                                                                        np.asarray(a.x)-np.asarray(b.x)))))
    #tracksdf=tracksdf[np.isin(np.asarray(tracksdf.ID),meanangles[meanangles.meanangle>=120].index)]

    #creates dataframe with start and end times for each ID
    startend=pd.DataFrame(columns=["start","end"])
    tracksdf=tracksdf.dropna()
    for ID in np.unique(tracksdf.ID).astype(int):
        if ID < 0:
            print(ID)
            tracksdf=tracksdf[tracksdf.ID!=ID]
        else:
            startend.loc[ID,:]=int(np.nanmin(tracksdf.loc[tracksdf.ID==ID].time)),int(np.nanmax(tracksdf.loc[tracksdf.ID==ID].time))
    startend=startend.astype(int)

    #gets all possible combinations of two indexes within 10 frames and 20 distance
    possiblecombos=pd.DataFrame(columns=["ID1","ID2","end","start"])#,"dist"])
    idstodrop=[]
    print("Finds all possible track combinations and drops short tracks")
    for ID in tqdm(np.unique(tracksdf.ID)):
        length=len(tracksdf[tracksdf.ID==ID])
        if length<4:
            idstodrop.append(ID)
            continue
        #print(ID)
        endindex=startend.loc[ID].end
        endlocation=tracksdf.loc[(tracksdf.ID==ID) & (tracksdf.time==endindex),["x","y"]].values
        for end in range(endindex,endindex+10):
            if end+1 in list(startend.start):
                for startID in startend.index[startend.start==end+1]:
                    startlocation=tracksdf.loc[(tracksdf.ID==startID) & (tracksdf.time==end+1),["x","y"]].values
                    if np.linalg.norm(startlocation-endlocation) < 20:
                        possiblecombos.loc[len(possiblecombos.index)] = [int(ID),startID,endindex,end+1]#,np.linalg.norm(startlocation-endlocation)]


    with open('combinedids.txt', 'w') as f:
        f.write('Dropping: '+str(idstodrop))
        print('Dropping: '+str(len(idstodrop)))
        tracksdf=tracksdf[np.isin(tracksdf.ID,idstodrop,invert=True)]
        possiblecombos=possiblecombos[np.isin(possiblecombos.ID1,idstodrop,invert=True)]
        possiblecombos=possiblecombos[np.isin(possiblecombos.ID2,idstodrop,invert=True)]
        possiblecombos=possiblecombos.reset_index()


    idstodrop = []
    #finds all certain combinations
    dists=[]
    angles=[]
    lengths=np.zeros([len(possiblecombos.index),2])
    print("Finds worm combinations that are very likely to be correct:")
    for i in tqdm(range(len(possiblecombos.index))):
        ID1=int(possiblecombos[possiblecombos.index==i].ID1.iloc[0])#stores IDs for the start and end track
        ID2=int(possiblecombos[possiblecombos.index==i].ID2.iloc[0])#stores IDs for the start and end track
        lengths[i,:]=[len(tracksdf[tracksdf.ID==ID1]),len(tracksdf[tracksdf.ID==ID2])] #stores the lengths of each track

        if len(tracksdf[(tracksdf.ID==ID1)].values) == 1 or len(tracksdf[(tracksdf.ID==ID2)].values) == 1:
            continue
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

    print("number of tracks combined: "+str(len(confirmeds)))

    if np.any(np.unique(possiblecombos.loc[confirmeds].ID1,return_counts=True)[1]!=1) or np.any(np.unique(possiblecombos.loc[confirmeds].ID2,return_counts=True)[1]!=1):
        print("ERROR: PRELIMINARY CLASSIFICATION FAILED: DUPLICATE MADE")

    with open('combinedids.txt', 'w') as f:
        f.write('Dropping: '+str(idstodrop))
        for i in confirmeds: #i represents the index of correct combo
            ID1,ID2=possiblecombos.loc[i][["ID1","ID2"]].values
            tracksdf.loc[tracksdf.ID==ID2,["ID"]]=ID1
            idstodrop.append(ID2)
            f.write('ID1: '+str(ID1)+', ID2: '+str(ID2))
            f.write('\n')
        tracksdf=tracksdf[np.isin(tracksdf.ID,idstodrop,invert=True)]


    #creates dataframe with start and end times for each ID
    startend=pd.DataFrame(columns=["start","end"])
    for ID in np.unique(tracksdf.ID).astype(int):
        startend.loc[ID,:]=int(np.min(tracksdf.loc[tracksdf.ID==ID].time)),int(np.max(tracksdf.loc[tracksdf.ID==ID].time))
    startend.astype(int)

    #creates density map of where tracks end
    xs=[]
    ys=[]
    offscreens=[]
    for ID in np.unique(tracksdf.ID.values):
        x=np.round(tracksdf[(tracksdf.ID==ID)&(tracksdf.time==startend.loc[ID].end)].x.values[0],1)
        y=np.round(tracksdf[(tracksdf.ID==ID)&(tracksdf.time==startend.loc[ID].end)].y.values[0],1)
        if (x<10) or (x>np.max(tracksdf.x)-10) or (y<10) or (y>np.max(tracksdf.y)-10):
            offscreens.append(int(ID))
        xs.append(x)
        ys.append(y)

    nbins=400
    densityhist=np.histogram2d(xs,ys,bins=nbins)
    densityindexes=np.unravel_index(np.argsort(densityhist[0].flatten())[-30:-1], np.shape(np.histogram2d(xs,ys,bins=nbins)[0]))

    statpixels=[]
    print("Finding stationary pixels:")
    for index1,index2 in tqdm(zip(densityindexes[0],densityindexes[1])):
        tx=densityhist[1][index1]
        ty=densityhist[1][index2]
        for ID in np.unique(tracksdf.ID.values):
            x=np.round(tracksdf[(tracksdf.ID==ID)&(tracksdf.time==startend.loc[ID].end)].x.values[0],1)
            y=np.round(tracksdf[(tracksdf.ID==ID)&(tracksdf.time==startend.loc[ID].end)].y.values[0],1)
            if (tx-5<x and x<tx+5) and (ty-5 < y and y < ty+5):
                if len(tracksdf[tracksdf.ID==ID])<5 or (np.max(tracksdf[tracksdf.ID==ID].x.values)-np.min(tracksdf[tracksdf.ID==ID].x.values)<10 and np.max(tracksdf[tracksdf.ID==ID].y.values)-np.min(tracksdf[tracksdf.ID==ID].y.values)<10):
                    statpixels.append(ID)
                    #print(str(int(ID)) + ": " + str(x) + " " + str(y) + ", time = " + str(int(startend.loc[ID].end)) + ", number = " + str(len(tracksdf[tracksdf.ID==ID])))

    print("number of tracks that are stationary: "+str(len(statpixels)))
    #drops IDs that are probably still frames on screen
    tracksdf=tracksdf[np.isin(tracksdf.ID,statpixels,invert=True)]

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

    #will remove combos, shouldn't be how this is organized anymore
    #combos=[]
    #for ID in np.unique(tracksdf.ID).astype(int):
    #    combo=list(np.flip(findpairreverse(ID,[],possiblecombos))[:-1])+findpair(ID,[],possiblecombos)
    #    len(combo)>1 and combos.append(sorted(combo))

    #uniquecombos=[]
    #for combo in combos:
    #    if combo not in uniquecombos:
    #        uniquecombos.append(combo)
    #combos=uniquecombos
    #print("Number of combinations: "+str(len(combos)))

    outputs={}
    ends=[i for i in np.unique(tracksdf.ID.values) if i not in np.asarray(offscreens)]
    ends=[i for i in ends if np.max(tracksdf[tracksdf.ID==i].time.values)<np.max(tracksdf.time.values)-15]
    outputs["ends"]=[x for _, x in sorted(zip(startend.loc[ends].end.values, ends))]
    print("Number of ends: "+str(len(outputs["ends"])))
    outputs["tracksdf"]=tracksdf
    outputs["startend"]=startend

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
