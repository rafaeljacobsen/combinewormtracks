Instructions:
First, run createsumarray.py on the h5 file to get the background.
python3 createsumarray.py FILEPATH -output=OUTPUTPATH (default=sumarray.npy)


Then, run labelworms.py on the h5 file you want labeled.
python3 labelworms.py FILEPATH -sumarraypath=SUMARRAYPATH (default=sumarray.npy) -frames=NUMFRAMES (default=all frames) -output=OUTPUTFILE (default=tracks.csv)

This file will have the worm tracks, but it will likely have many mistakes. In order to rectify some of these mistakes and prepare the tracks for manual checking, run
python3 precombinewormtracks.py TRACKSPATH -type=TYPEOFDATASET (either numpy or pandas)

Now you can launch the actual gui:
python3 launchgui.py FILEPATH PRECOMBINEDWORMTRACKSPATH -rotate=False (some images need to be rotated) -sumarraypath=SUMARRAYPATH (default=sumarray.npy)

A gui will launch. Cycle through all the ends of the tracks with the next combination button, fixing any errors with the buttons on the right hand size of the screen. Increase/decrease the time and distance that other tracks are shown with the inputs on the top of the screen. Clicking save or exiting the file will save the tracks, which can then be inspected with inspectwormtracks/inspecttracks.py.
