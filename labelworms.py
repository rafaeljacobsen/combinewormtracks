import h5py
import numpy as np
import matplotlib.pyplot as plt
import cv2
import pandas as pd
np.set_printoptions(suppress=True)
from tqdm import tqdm
import argparse

def labelworms(imgpath,sumarraypath,frames,output,thresh):
    images = h5py.File(imgpath,'r+')
    sumarray=np.load(sumarraypath)
    keyids=[]
    for i in images.keys():
        if i.isdigit():
            keyids.append(int(i))
    thresh=20
    img=images["0"]['frame'][0].max(2)-sumarray/np.max(keyids)
    img=np.vectorize(lambda x: 0 if x <thresh else 1)(img)
    img=np.array(img*255, np.uint8)
    #plt.imshow(img,cmap='Greys')
    ID=1
    frame0=np.zeros((1,4),dtype=float)

    _, threshold = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, 1)

    for cnt in contours:
        if len(cnt)>25:
            x,y=np.average(cnt[:,0],axis=0)
            frame0=np.vstack([frame0,[ID,0,x,y]])
            ID+=1
    frame0=frame0[1:]
    tracks=frame0

    maxID=np.max(frame0[:,0])
    if frames=="auto":
        frames=np.max([int(num) for num in images.keys() if num.isdigit()])
    else:
        frames=int(frames)
    for frame in tqdm(range(1,frames)):
        thresh=20
        img=images[str(frame)]['frame'][0].max(2)-sumarray/np.max(keyids)
        img=np.vectorize(lambda x: 0 if x <20 else 1)(img)
        img=np.array(img*255, np.uint8)
        #plt.imshow(img,cmap='Greys')
        ID=1
        frame1=np.zeros((1,4),dtype=float)

        _, threshold = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, 1)

        for cnt in contours:
            if len(cnt)>15:
                x,y=np.average(cnt[:,0],axis=0)
                frame1=np.vstack([frame1,[ID,frame,x,y]])
                ID+=1
        frame1=frame1[1:]

        threshold = 20

        claimed = []
        for i in range(len(frame0)):
            candidates = []
            distances = []
            for j in range(len(frame1)):
                if j in claimed:
                    continue
                distance = (frame1[j][2]-frame0[i][2])**2 + (frame1[j][3]-frame0[i][3])**2
                if distance < threshold**2:
                    candidates.append(j)
                    distances.append(distance)
            if len(candidates) > 0:
                closest = np.argmin(distances)
                frame1[candidates[closest]][0] = frame0[i][0]
                claimed.append(candidates[closest])

        newidindex=1
        for i in range(len(frame1)):
            if i not in claimed:
                maxID+=1
                frame1[i][0] = maxID
        tracks=np.concatenate([tracks,frame1])

        frame0=frame1
    np.savetxt(output,tracks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find worms')
    parser.add_argument('imgpath', help='image path')
    parser.add_argument('-sumarraypath', type=str, default="sumarray.npy", help='path to sumarray')
    parser.add_argument('-frames', type=str, default="auto", help='number of frames to go through')
    parser.add_argument('-output', type=str, default="tracks.csv", help='outputpath')
    parser.add_argument('-thresh', type=str, default="20", help='threshold')

    args=parser.parse_args()
    imgpath=args.imgpath
    sumarraypath=args.sumarraypath
    frames=args.frames
    output=args.output
    thresh=args.thresh

    labelworms(imgpath,sumarraypath,frames,output,thresh)
