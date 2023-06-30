import argparse
from src.gui import GUI

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch Annotation GUI')
    parser.add_argument('imgpath', help='image path')
    parser.add_argument('precombinedwormtracks', help='track for data from pre-ran algorithm')

    args=parser.parse_args()

    imgpath=args.imgpath
    precombinedwormtracks=args.precombinedwormtracks
    gui=GUI(imgpath,precombinedwormtracks)
    gui.start()
    print("GUI closed succesfully")
