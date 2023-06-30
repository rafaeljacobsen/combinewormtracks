import sys
import numpy as np
import h5py
from tqdm import tqdm
def createsumarray(path):
    images = h5py.File(path,'r+')
    sumarray=np.zeros(np.shape(images["1"]['frame'][0].max(2)))
    for i in tqdm(np.asarray(list(images.keys()))):
        if i.isdigit():
            sumarray+=images[i]['frame'][0].max(2)
    np.save("sumarray.npy",sumarray)


if __name__ == "__main__":
    path = sys.argv[1]
    createsumarray(path)
