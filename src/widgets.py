import random
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from PyQt5.Qt import Qt
import time as TIME
from PyQt5.QtWidgets import QGraphicsEllipseItem

class CombineDialogErr(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ERROR")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Cannot combine overlapping tracks")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class RemovingTracks(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ERROR")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Removing very long track")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class TrackFig(pg.PlotWidget):
    def __init__(self,gui):
        self.gui=gui

        self.plots={}
        self.circles = []  # Track all the circles
        self.circle_centers = []  # Centers of all circles
        self.is_dragging = False  # Track whether we are dragging to adjust radius
        self.is_s_pressed = False  # Flag to determine if 's' is pressed
        super().__init__()

        #creates the image item
        self.image=pg.ImageItem()
        self.addItem(self.image)

        # build lookup table
        self.lut = np.zeros((256,3), dtype=np.ubyte)
        self.lut[0:10,:] =255
        self.lut[10:74,:] = np.stack([np.flip(np.arange(0,255,4)),
                                np.flip(np.arange(0,255,4)),
                                np.flip(np.arange(0,255,4))],axis=1)
        self.lut[74:,:] = 0

        # Apply the colormap
        self.image.setLookupTable(self.lut)
        # creates a legend (and keep it readable on white backgrounds)
        self._recreate_legend()

        self.setAspectLocked()

    def _recreate_legend(self):
        """
        PyQtGraph's PlotWidget.clear() can remove legend graphics items, and the
        default legend label color may be hard to see depending on theme/config.
        Recreate + restyle the legend so track IDs remain visible.
        """
        # best-effort remove any previous legend instance
        if hasattr(self, "legend") and self.legend is not None:
            try:
                self.removeItem(self.legend)
            except Exception:
                pass

        self.legend = self.addLegend()

        # best-effort styling across pyqtgraph versions
        try:
            self.legend.setBrush(pg.mkBrush(255, 255, 255, 200))
        except Exception:
            pass
        try:
            self.legend.setPen(pg.mkPen(0, 0, 0, 120))
        except Exception:
            pass
        try:
            self.legend.setLabelTextColor("k")
        except Exception:
            pass

    def mousePressEvent(self, event):
        if self.is_s_pressed:
            vb = self.getViewBox()
            pos = event.pos()
            data_pos = vb.mapSceneToView(pos)
            x, y = data_pos.x(), data_pos.y()

            if event.button() == Qt.LeftButton:
                # Start creating a new circle
                self.circle_centers.append((x, y))
                pen = pg.mkPen(color='r', width=2)  # Red outline
                circle = QGraphicsEllipseItem(x, y, 0, 0)
                circle.setPen(pen)
                self.addItem(circle)
                self.circles.append(circle)
                self.is_dragging = True
            elif event.button() == Qt.RightButton:
                # Remove circles if right-click is inside them
                for circle in self.circles:
                    rect = circle.rect()
                    if rect.contains(x, y):
                        center_idx = self.circles.index(circle)
                        self.circle_centers.pop(center_idx)
                        self.removeItem(circle)
                        if circle in self.circles:
                            self.circles.remove(circle)
        else:
            super().mousePressEvent(event)  # Allow default behavior

    def mouseReleaseEvent(self, event):
        if self.is_s_pressed:
            if event.button() == Qt.LeftButton:
                self.is_dragging = False
        else:
            super().mouseReleaseEvent(event)  # Allow default behavior

    def mouseMoveEvent(self, event):
        if self.is_s_pressed and self.is_dragging and self.circles:
            vb = self.getViewBox()
            pos = event.pos()
            data_pos = vb.mapSceneToView(pos)
            x, y = data_pos.x(), data_pos.y()
            center_x, center_y = self.circle_centers[-1]

            # Calculate new radius as the distance from the center
            radius = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5

            # Update ellipse
            self.circles[-1].setRect(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
        else:
            super().mouseMoveEvent(event)  # Allow default behavior

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S:
            self.is_s_pressed = True
        elif event.key() == Qt.Key_Space:
            #for undoing
            self.gui.trackstemp = self.gui.tracksdf.copy()
            self.gui.endstemp = self.gui.ends

            # Set to collect all tracks that should be combined
            trackstocombine = set()

            # Iterate over circles to find tracks within any circle
            for circle in self.circles:
                rect = circle.rect()
                center = np.array([rect.center().x(), rect.center().y()])
                radius = rect.width() / 2  # Since it's a circle, width should equal height

                for ID in self.gui.drawn:
                    track_subset = self.gui.tracksdf[(self.gui.tracksdf.ID == ID)\
                                                     & (self.gui.tracksdf.time > self.gui.endtime - self.gui.timesubt)\
                                                     & (self.gui.tracksdf.time < self.gui.endtime + self.gui.timeadd)
                                                     & (self.gui.tracksdf.time < self.gui.frame)]
                    distances = np.sqrt((track_subset.x - center[0])**2 + (track_subset.y - center[1])**2)
                    if np.any(distances <= radius):
                        trackstocombine.add(ID)

            if trackstocombine:
                base_id = min(trackstocombine)
                trackstocombine.remove(base_id)

                # Combine tracks logic
                for ID in trackstocombine:
                    totaldroppinglen = 0
                    track_mask = self.gui.tracksdf.ID == ID
                    base_track_times = self.gui.tracksdf[self.gui.tracksdf.ID == base_id].time.unique()
                    
                    dropping_indices = []
                    
                    for index, row in self.gui.tracksdf[track_mask].iterrows():
                        time = row['time']
                        if time not in base_track_times:
                            self.gui.tracksdf.at[index, 'ID'] = base_id
                        else:
                            # Prepare the mask for rows to drop
                            mask_to_drop = track_mask & (self.gui.tracksdf.time == time)
                            overlapping_count = mask_to_drop.sum()
                            
                            if overlapping_count > 1:
                                print("ERROR: DROPPING TOO MANY TRACKS")
                            totaldroppinglen += overlapping_count
                            
                            # Collect indices to drop at once later
                            dropping_indices.extend(self.gui.tracksdf[mask_to_drop].index)

                    if dropping_indices:
                        self.gui.tracksdf.drop(dropping_indices, inplace=True)
                        
                    if totaldroppinglen > 30:
                        print("Dropping", totaldroppinglen, "of track", ID)
                    if totaldroppinglen > 200:
                        errorwin = RemovingTracks()
                        errorwin.setWindowTitle("ERROR")
                        errorwin.exec()
                
                print(f"Tracks {trackstocombine} combined into ID: {base_id}")

            self.circles.clear()  # Clear all circles after operation
            self.circle_centers.clear()
            self.gui.respond("update_data")  # Refreshing the GUI with updated data

        elif event.key() == Qt.Key_D:
            #for undoing
            self.gui.trackstemp = self.gui.tracksdf.copy()
            self.gui.endstemp = self.gui.ends

            # Collect all tracks that should be removed
            trackstoremove = set()

            # Iterate over circles to find tracks within any circle
            for circle in self.circles:
                rect = circle.rect()
                center = np.array([rect.center().x(), rect.center().y()])
                radius = rect.width() / 2  # Since it's a circle, width should equal height

                for ID in self.gui.graphstodraw:
                    track_subset = self.gui.tracksdf[(self.gui.tracksdf.ID == ID)\
                                                     & (self.gui.tracksdf.time > self.gui.endtime - self.gui.timesubt)\
                                                     & (self.gui.tracksdf.time < self.gui.endtime + self.gui.timeadd)\
                                                     & (self.gui.tracksdf.time < self.gui.frame)]
                    distances = np.sqrt((track_subset.x - center[0])**2 + (track_subset.y - center[1])**2)
                    if np.any(distances <= radius):
                        trackstoremove.add(ID)

            for track in trackstoremove:
                if len(self.gui.tracksdf[(self.gui.tracksdf.ID == track)]) > 50:
                    print("removing long ID",track,"of length",len(self.gui.tracksdf[(self.gui.tracksdf.ID == track)]))
                if len(self.gui.tracksdf[(self.gui.tracksdf.ID == track)]) > 200:
                    errorwin = RemovingTracks()
                    errorwin.setWindowTitle("ERROR")
                    errorwin.exec()

                self.gui.tracksdf = self.gui.tracksdf[(self.gui.tracksdf.ID != track)]

            self.circles.clear()  # Clear all circles after operation
            self.circle_centers.clear()
            self.gui.respond("update_data")  # Refreshing the GUI with updated data

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_S:
            self.is_s_pressed = False

    def update_data(self,img):
        start_time=TIME.time()
        #gets updated list of ends
        if len(self.gui.tracksdf) > 0 and not self.gui.view_mode:
            self.gui.ends = self.gui.tracksdf.loc[
                self.gui.tracksdf.groupby('ID')['time'].idxmax()
            ].loc[
                lambda df: (df['time'] < (self.gui.tracksdf['time'].max() - 1))
            ].sort_values('time')['ID'].tolist()
        # checks for duplicates
        if len(self.gui.tracksdf) > 0 and len(self.gui.tracksdf[self.gui.tracksdf.duplicated(subset=['ID', 'time'], keep=False)].index):
            print("ERROR: duplicates at indices",self.gui.tracksdf[self.gui.tracksdf.duplicated(subset=['ID', 'time'], keep=False)].index)
        self.clear()
        self.image=pg.ImageItem()
        self.addItem(self.image)
        self.gui.win.timeedit.setText(str(int(self.gui.frame)-1))
        self.image.setLookupTable(self.lut)
        self.image.setImage(img[:,:],autoLevels=False,levels=[self.gui.minlevel,200])
        self._recreate_legend()
        colors=np.tile(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf', '#cacaca','#f3f134'],3)
        iter=0
        for key in self.plots.keys():
            self.plots[key].clear()

        self.plots={}
        # legend was recreated above; keep this here as a no-op safety if API changes
        try:
            self.legend.clear()
        except Exception:
            pass

        self.gui.drawn=[]
        numtracks=0

        timer_start = TIME.time()
        # In view mode, show tracks around current frame; in normal mode, show from starttime
        if self.gui.view_mode:
            start_time = self.gui.frame - 50
            end_time = self.gui.frame + 10
        else:
            start_time = self.gui.starttime - self.gui.timesubt
            end_time = self.gui.frame
        pen_styles = [QtCore.Qt.SolidLine, QtCore.Qt.DotLine, QtCore.Qt.DashLine]
        colors_len = len(colors)

        # Filter tracks dataframe once
        valid_time_mask = (self.gui.tracksdf.time > start_time) & (self.gui.tracksdf.time < end_time)
        filtered_tracks_df = self.gui.tracksdf[valid_time_mask]

        track_colors = {track: idx % colors_len for idx, track in enumerate(sorted(self.gui.graphstodraw))}

        for numtracks, track in enumerate(sorted(self.gui.graphstodraw)):
            data = filtered_tracks_df[filtered_tracks_df.ID == track]
            if len(data) <= 1:
                continue

            xs, ys = data.sort_values(by='time')[['x', 'y']].values.T
            color_idx = track_colors[track]
            pen_style = pen_styles[color_idx % len(pen_styles)]
            color = colors[color_idx]

            self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(color, width=5, style=pen_style))
            self.addItem(self.plots[track])

            if numtracks < 40:
                self.legend.addItem(self.plots[track], str(int(track)))

            self.gui.drawn.append(track)

        end_time = TIME.time()
        # print("done updating data in", np.round(end_time - timer_start, 3))

    def update_comp(self):
        self.circles.clear()
        if len(self.gui.ends) <= self.gui.enditer:
            # Enter view-only mode
            print("No more track endings to review. Entering view-only mode.")
            self.gui.win.compind.setText(f"<p style='background-color:lightgreen'>View Mode: All tracks processed!</p>")
            # Clear the explanatory message in view mode (keep UI uncluttered)
            self.gui.win.compexp.setText(f"<p style='background-color:white'></p>")
            # Clear combo boxes
            for i in range(5):
                self.gui.win.comboboxes[i].clear()
            # Set to middle of dataset for viewing
            if not hasattr(self.gui, 'view_mode') or not self.gui.view_mode:
                self.gui.view_mode = True
                max_time = self.gui.tracksdf['time'].max()
                if np.isnan(max_time) or len(self.gui.tracksdf) == 0:
                    # If no valid tracks, start at frame 0
                    self.gui.frame = 0
                    print("Warning: No valid track data found. Starting at frame 0.")
                else:
                    self.gui.frame = int(max_time / 2)
                # Initialize attributes needed for update_data
                self.gui.starttime = self.gui.frame
                self.gui.endtime = self.gui.frame
                self.gui.endx = 0
                self.gui.endy = 0
            self.get_tracks()
            self.gui.respond("update_data")
            return
        self.gui.ID = self.gui.ends[self.gui.enditer]
        self.gui.switchpercombo[self.gui.enditer] = 0
        if self.gui.ID in self.gui.switches.keys():
            self.gui.ID = self.gui.switches[self.gui.ID]
        if len(self.gui.tracksdf[self.gui.tracksdf.ID == self.gui.ID]) == 0:
            self.gui.enditer += 1
            self.update_comp()
        else:
            self.gui.starttime = int(np.max(self.gui.tracksdf[self.gui.tracksdf.ID == self.gui.ID].time.values)) - 5
            if self.gui.starttime + 10 < np.max(self.gui.tracksdf.time.values):
                self.gui.frame = self.gui.starttime + 10

            #gets all the data about when/where the worm track ends
            if self.gui.ID not in self.gui.tracksdf.ID.values:
                self.gui.win.compind.setText(f"<p style='background-color:white'>Track {str(self.gui.ID)} already removed or merged, go to next comparison.</p>")
                self.gui.win.compexp.setText(f"<p style='background-color:white'></p>")
                for i in range(5):
                    self.gui.win.comboboxes[i].clear()
                self.gui.respond("update_data")
            else:
                _, self.gui.endtime, self.gui.endx, self.gui.endy = list(self.gui.tracksdf[(self.gui.tracksdf.ID == self.gui.ID) & (self.gui.tracksdf.time == np.max(self.gui.tracksdf[self.gui.tracksdf.ID == self.gui.ID].time.values))].values)[0]
                self.get_tracks()
                self.gui.respond("update_data")
                #print("--- %s seconds for updating the comparison ---" % (TIME.time() - start_time))



    def get_tracks(self):
        self.gui.graphstodraw = []
        
        # Handle view mode differently
        if self.gui.view_mode:
            # In view mode, show all tracks near the current frame
            current_time = self.gui.frame
            for ID in np.unique(self.gui.tracksdf.ID.values):
                if len(self.gui.tracksdf[(self.gui.tracksdf.ID == ID) & 
                                        (np.abs(current_time - self.gui.tracksdf.time) < 50)]) > 0:
                    self.gui.graphstodraw.append(int(ID))
            # Don't populate combo boxes in view mode
            for i in range(5):
                self.gui.win.comboboxes[i].clear()
            return
        
        compindtext = "Comparison "+str(int(self.gui.enditer+1))+" out of "+str(int(len(self.gui.ends)))
        self.gui.win.compind.setText(f"<p style='background-color:white'>{compindtext}</p>")
        compexptext = "Track "+str(int(self.gui.ID))+" ended at time t="+str(int(self.gui.endtime))
        self.gui.win.compexp.setText(f"<p style='background-color:white'>{compexptext}</p>")
        #gets all the tagged worms in the area

        start_time = TIME.time()
        # IMPORTANT: Keep candidate selection consistent with what is actually DRAWN in update_data().
        # update_data() draws only a limited time window: (starttime - timesubt) .. frame.
        # Previously, this used abs(endtime-time) < timeadd (default timeadd=10000), which
        # caused the comparison dropdowns to include many tracks that were not drawn/visible.
        draw_start = self.gui.starttime - self.gui.timesubt
        draw_end = self.gui.frame

        df = self.gui.tracksdf
        for ID in np.unique(df.ID.values):
            subset = df[(df.ID == ID) & (df.time > draw_start) & (df.time < draw_end)]
            if len(subset) <= 1:
                continue
            near_end = subset[(np.abs(subset.x - self.gui.endx) < self.gui.xdist) &
                              (np.abs(subset.y - self.gui.endy) < self.gui.xdist)]
            if len(near_end) > 0:
                self.gui.graphstodraw.append(int(ID))
        for i in range(5):
            self.gui.win.comboboxes[i].clear()
            self.gui.win.comboboxes[i].addItems(list(map(str, np.sort(self.gui.graphstodraw))))


        #print("--- %s seconds for updating the tracks ---" % (TIME.time() - start_time))