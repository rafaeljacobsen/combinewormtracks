import sys
import numpy as np
import h5py
from tqdm import tqdm
import argparse
def createsumarray(path,output):
    images = h5py.File(path,'r+')
    sumarray=np.zeros(np.shape(images["1"]['frame'][0].max(2)))
    for i in tqdm(np.asarray(list(images.keys()))):
        if i.isdigit():
            sumarray+=images[i]['frame'][0].max(2)
    np.save(output,sumarray)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find worms')
    parser.add_argument('imgpath', help='image path')
    parser.add_argument('-output', type=str, default="sumarray.npy", help='outputpath')

    args=parser.parse_args()
    imgpath=args.imgpath
    output=args.output
    createsumarray(imgpath,output)
