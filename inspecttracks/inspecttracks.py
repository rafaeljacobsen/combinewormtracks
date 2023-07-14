import argparse
from gui import GUI

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch Annotation GUI')
    parser.add_argument('imgpath', help='image path')
    parser.add_argument('trackspath', help='path to tracks')

    parser.add_argument('-rotate', type=str, default=False, help='whether the image should be rotated by 90 degrees')
    parser.add_argument('-sumarraypath', type=str, default="../sumarray.npy", help='path to sumarray')
    args=parser.parse_args()

    imgpath=args.imgpath
    trackspath=args.trackspath
    rotate=args.rotate
    sumarraypath=args.sumarraypath
    gui=GUI(imgpath,trackspath,rotate,sumarraypath)
    gui.start()
    print("GUI closed succesfully")
