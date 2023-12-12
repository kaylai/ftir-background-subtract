"""
GUI application for processing FTIR data for CO2, CO3, H2O, and OH in silicate glasses.
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import toga_chart
import numpy as np
import csv
import os

import matplotlib.pyplot as pyplot
pyplot.ion

class FTIRBackgroundSubtract(toga.App):

    def startup(self):
        """On startup, the app creates two windows. The MainWindow is required for the app to run.
        The fileChoose_window is a normal toga.Window() object, which automatically opens to allow
        the user to choose a CSV file to plot.
        """
         # create and show main window
        self.main_window = toga.MainWindow(title="FTIR Background Subtract")
        # self.main_window.show()

        # Create elements to put in the fileChoose window
        fileChooser_box = toga.Box(style=Pack(direction=COLUMN))
        fileChoose_label = toga.Label(
            "Choose a CSV file: ",
            style=Pack(padding=(0.5))
        )
        fileChoose_button = toga.Button(
            "Choose File",
            on_press=self.fileChooser,
            style=Pack(padding=5)
        )

        # Create a box and add label
        label_box = toga.Box(style=Pack(direction=ROW, padding=5))
        label_box.add(fileChoose_label)

        # add elements to the main window
        fileChooser_box.add(fileChoose_label)
        fileChooser_box.add(fileChoose_button)

        # # create and show file chooser window
        # self.fileChoose_window = toga.Window(title="Choose a file")
        # self.fileChoose_window.content = fileChooser_box
        # self.fileChoose_window.show()

        self.fileChooser()

    def fileChooser(self):
        fileChooser = self.main_window.open_file_dialog(title="Choose a CSV File",
                                            file_types=["csv"],
                                            multiple_select=False,
                                            on_result=self.appWindows)

    def appWindows(self, window, path):
        """ Creates two windows: the plotting window, where the CSV file is plotted, and the anlaysis
        window, where the analytical controls and buttons are placed.
        """

        self.path = path
        self.filename = os.path.basename(path)

        """
        MAIN (PLOTTING) WINDOW
        """
        # Send the CSV to the plotting window (main_window)
        # Make the plotting box
        plotting_box = toga.Box(style=Pack(direction=COLUMN))
        plotting_label = toga.Label(
            "Do your plotting here",
            style=Pack(padding=(0.5))
        )

        testPrintPath_label = toga.Label(
            path,
            style=Pack(padding=(0.5))
        )

        # create a label box and add label
        label_box = toga.Box(style=Pack(direction=ROW, padding=5))
        label_box.add(plotting_label)
        label_box.add(testPrintPath_label)

        # add elements to the plotting box
        plotting_box.add(plotting_label)
        plotting_box.add(testPrintPath_label)

        # add all this to the main_window
        self.chart = toga_chart.Chart(style=Pack(flex=1), on_draw=self.plotData)
        self.main_window.content = self.chart
        self.main_window.show()

        """
        ANALYSIS WINDOW
        """
        # Make the analysis window
        analysis_window = toga.Window(title="Analysis Window")

        # Make the analysis box
        analysis_box = toga.Box(style=Pack(direction=COLUMN))
        analysis_label = toga.Label(
            "Do your analysis here",
            style=Pack(padding=(0.5))
        )

        testPrintPath_label = toga.Label(
            path,
            style=Pack(padding=(0.5))
        )

        # create a box and add label
        label_box = toga.Box(style=Pack(direction=ROW, padding=5))
        label_box.add(analysis_label)
        label_box.add(testPrintPath_label)

        # add elements to the main window
        analysis_box.add(analysis_label)
        analysis_box.add(testPrintPath_label)

        # add content and show window
        analysis_window.content = analysis_box
        analysis_window.show()
    
    def readCSV(self, path):
        reader = csv.reader(open(path, "rt"), dialect="excel") 

        wavenumber = []
        absorbance = []

        for line in reader:
            wavenumber.append(float(line[0]))
            absorbance.append(float(line[1]))
        
        return np.array(wavenumber), np.array(absorbance)
    
    def plotData(self, chart, figure, *args, **kwargs):
        """Use toga_chart to plot up the CSV data
        """
        # read in CSV data
        wavenumber, absorbance = self.readCSV(self.path)
        self.bkgd_lowlim = wavenumber[-1]
        self.bkgd_highlim = wavenumber[0]
        self.excl_lowlim = np.median(wavenumber)
        self.excl_highlim = np.median(wavenumber)

        ax = figure.add_subplot(1, 1, 1)
        ax.plot(wavenumber, absorbance, "-")

        # Set plot styling
        ax.invert_xaxis()
        ax.set_xlabel("Wavenumber")
        ax.set_ylabel("Absorbance")
        ax.set_title(self.filename)

        # add DraggableLines
        ax.cla()
        self.lim_line1 = DraggableLine(self.bkgd_lowlim, ax, color='g')
        self.lim_line2 = DraggableLine(self.bkgd_highlim, ax, color='g')
        self.excl_line1 = DraggableLine(self.excl_lowlim, ax, color='r')
        self.excl_line2 = DraggableLine(self.excl_highlim, ax, color='r')

        return ax


class BackgroundRangeSelector:
    def __init__(self, ax):
        self.ax = ax
        self.ax.invert_xaxis()
        self.lim_line1 = None
        self.lim_line2 = None
        self.plot = None
    
    def update(self, scan):
        self.ax.cla()
        if self.lim_line1 is None:
                self.lim_line1 = DraggableLine(scan.bkgd_lowlim, self.ax, color='g')
                self.lim_line2 = DraggableLine(scan.bkgd_highlim, self.ax, color='g')
                self.excl_line1 = DraggableLine(scan.excl_lowlim, self.ax, color='r')
                self.excl_line2 = DraggableLine(scan.excl_highlim, self.ax, color='r')
        else:
            self.lim_line1.set_xpos(scan.bkgd_lowlim)
            self.lim_line2.set_xpos(scan.bkgd_highlim)
            self.excl_line1.set_xpos(scan.excl_lowlim)
            self.excl_line2.set_xpos(scan.excl_highlim)

        self.plot = self.ax.plot(scan.angles, scan.col_amount,'b-')
        
    def get_lims(self):
        pos1 = self.lim_line1.get_xpos()
        pos2 = self.lim_line2.get_xpos()
        
        return min(pos1,pos2), max(pos1,pos2)

    def get_excl_lims(self):
        pos1 = self.excl_line1.get_xpos()
        pos2 = self.excl_line2.get_xpos()
        
        return min(pos1,pos2), max(pos1,pos2)
    

class DraggableLine:
    """
    This class is mostly based on the draggable rectangles example from 
    http://matplotlib.sourceforge.net/users/event_handling.html
    
    It provides a vertical line across 'axis' which can be dragged to any x
    position. Useful for picking limits.
    
        * x_pos - initial x position to draw line at
        * axis - axis to draw line into
        * callback - list of functions to run when the line gets moved. The functions
                     will be run in order, and will be passed the new x position of 
                     the line as their only argument.
    """
    
    lock = None
    
    def __init__(self, x_pos, axis, linewidth=2.0, color='r', callback=None):
        
        self.line = axis.plot([x_pos]*2,axis.get_ylim(), linewidth=linewidth, color=color)[0]

        self.press = None
        self.background = None
        self.callback = callback
        self.__connect()

   
    def __connect(self):
        #connect to all the events we need
        self.cidpress = self.line.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.line.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.line.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)           
        self.cidredraw = self.line.figure.canvas.mpl_connect('draw_event', self.on_redraw)


    def disconnect(self):
        #disconnect all the stored connection ids
        self.line.figure.canvas.mpl_disconnect(self.cidpress)
        self.line.figure.canvas.mpl_disconnect(self.cidrelease)
        self.line.figure.canvas.mpl_disconnect(self.cidmotion)
        self.line.figure.canvas.mpl_disconnect(self.cidredraw)

        
    def on_press(self, event):
        #on button press we will see if the mouse is over us and store some data
        if event.inaxes != self.line.axes: return
        if DraggableLine.lock is not None: return
        contains, attrd = self.line.contains(event)
        if not contains: return

        x0 = self.line.get_xdata()[0],
        self.press = x0, event.xdata, event.ydata
        DraggableLine.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.line.figure.canvas
        axes = self.line.axes
        self.line.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.line.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.line)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)


    def get_xpos(self):
        """
        Returns the current x position of the line.
        """
        return self.line.get_xdata()[0]
    
    
    def set_xpos(self,x_pos):
        """
        Sets the current x position of the line and redraws it.
        """
        self.line.set_xdata([x_pos]*2)
        self.line.axes.redraw_in_frame()
        
    
    def on_redraw(self, event):
        #reset the line's ylims so that you can't zoom to outside the size of the line
        self.line.set_ydata(self.line.axes.get_ylim())
        
        canvas = self.line.figure.canvas
        axes = self.line.axes        
        
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.line)

        # blit just the redrawn area
        canvas.blit(axes.bbox)
    
    
    def on_motion(self, event):
        #on motion we will move the rect if the mouse is over us
        if DraggableLine.lock is not self:
            return
        if event.inaxes != self.line.axes: return
        x0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress

        self.line.set_xdata([x0[0] + dx]*2)
        self.line.set_ydata(self.line.axes.get_ylim())
        self.line.set_linestyle('--')

        canvas = self.line.figure.canvas
        axes = self.line.axes
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.line)

        # blit just the redrawn area
        canvas.blit(axes.bbox)

 
    def on_release(self, event):
        #on release we reset the press data
        if DraggableLine.lock is not self:
            return
        
        self.line.set_linestyle('-')
        self.press = None
        DraggableLine.lock = None

        # turn off the rect animation property and reset the background
        self.line.set_animated(False)
        self.background = None

        # redraw the full figure
        self.line.figure.canvas.draw()
        
        if self.callback is not None:
            self.callback(event.xdata)


def main():
    return FTIRBackgroundSubtract()
