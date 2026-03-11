import argparse
from src.gui import GUI

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch Annotation GUI')
    parser.add_argument('imgpath', help='image path')
    parser.add_argument('precombinedwormtracks', help='track for data from pre-ran algorithm')

    parser.add_argument('-rotate', action='store_true', default=False, help='whether the image should be rotated by 90 degrees')
    parser.add_argument('-invert', action='store_true', default=False, help='whether the image should be inverted')
    parser.add_argument('-minlevel', type=int, default=80, help='image cutoff number')
    args=parser.parse_args()

    imgpath=args.imgpath
    precombinedwormtracks=args.precombinedwormtracks
    rotate=args.rotate
    invert=args.invert
    minlevel=args.minlevel
    gui=GUI(imgpath,precombinedwormtracks,rotate,invert,minlevel)
    gui.start()
    print("GUI closed succesfully")
