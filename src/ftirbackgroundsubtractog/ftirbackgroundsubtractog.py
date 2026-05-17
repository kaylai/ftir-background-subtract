import wx
import wx.lib.intctrl
import sys
import os.path
import pickle
import matplotlib
matplotlib.use('wxAgg') #bad things happen if you don't use the wxAgg backend
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy
import math
import csv


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
        self.line = axis.axvline(x_pos, linewidth=linewidth, color=color)

        self.press = None
        self.background = None
        self.callback = callback
        self.__connect()

   
    def __connect(self):
        # connect to all the events we need
        self.cidpress = self.line.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.line.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.line.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)           


    def disconnect(self):
        # disconnect all the stored connection ids
        self.line.figure.canvas.mpl_disconnect(self.cidpress)
        self.line.figure.canvas.mpl_disconnect(self.cidrelease)
        self.line.figure.canvas.mpl_disconnect(self.cidmotion)

        
    def on_press(self, event):
        # on button press we will see if the mouse is over us and store some data
        if event.inaxes != self.line.axes: return
        if DraggableLine.lock is not None: return
        contains, attrd = self.line.contains(event)
        if not contains: return

        x0 = self.line.get_xdata()[0],
        self.press = x0, event.xdata, event.ydata
        DraggableLine.lock = self


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
    
    
    def on_motion(self, event):
        #on motion we will move the rect if the mouse is over us
        if DraggableLine.lock is not self: return
        if event.inaxes != self.line.axes: return
        x0, xpress, ypress = self.press
        dx = event.xdata - xpress

        self.line.set_xdata([x0[0] + dx]*2)
        self.line.set_linestyle('--')
        self.line.figure.canvas.draw_idle()

 
    def on_release(self, event):
        #on release we reset the press data
        if DraggableLine.lock is not self: return
        
        self.line.set_linestyle('-')
        self.press = None
        DraggableLine.lock = None
        self.line.figure.canvas.draw_idle()
        
        if self.callback is not None:
            self.callback(event.xdata)


class BackgroundFittingControls(wx.Panel):
    def __init__(self, parent, plot_manager):
        self.plot_manager = plot_manager
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.BORDER_SIMPLE)
        
        #define vsizer
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        
        #define limit text boxes (integer-only)
        self.lims_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lower_lim_txtbox = wx.lib.intctrl.IntCtrl(self, wx.ID_ANY, value=0)
        self.upper_lim_txtbox = wx.lib.intctrl.IntCtrl(self, wx.ID_ANY, value=0)

        #define exclude limit text boxes and Get Limits button (integer-only)
        self.excl_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lower_excl_txtbox = wx.lib.intctrl.IntCtrl(self, wx.ID_ANY, value=0)
        self.upper_excl_txtbox = wx.lib.intctrl.IntCtrl(self, wx.ID_ANY, value=0)

        #define suggestion buttons
        self.suggestions = wx.BoxSizer(wx.HORIZONTAL)
        self.suggest_button = wx.Button(self, wx.ID_ANY, "3500") 
        self.suggest4500_button = wx.Button(self, wx.ID_ANY, "4500")
        self.suggest5200_button = wx.Button(self, wx.ID_ANY, "5200")
        self.suggestCO3_button = wx.Button(self, wx.ID_ANY, "CO3")
        self.suggestCO3_2_button = wx.Button(self, wx.ID_ANY, "CO3 (2)")
        
        #define Fit Order text box
        self.fit_order_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.fit_order_txtbox = wx.SpinCtrl(self, wx.ID_ANY, min=1, max=10, initial=1)
        
        # size text boxes
        for box in (self.lower_lim_txtbox, self.upper_lim_txtbox,
            self.lower_excl_txtbox, self.upper_excl_txtbox,
            self.fit_order_txtbox):
                box.SetMinSize((80, -1))
        
        #define Apply button
        self.apply_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.apply_button = wx.Button(self, wx.ID_ANY, "Apply")
        
        #Add Limit text boxes and buttons
        self.lims_hsizer.AddSpacer(5)
        self.lims_hsizer.Add(wx.StaticText(self, wx.ID_ANY,"Lower Limit:"),0, wx.ALIGN_CENTER_VERTICAL)
        self.lims_hsizer.Add(self.lower_lim_txtbox,0, wx.ALIGN_CENTER_VERTICAL)
        self.lims_hsizer.AddSpacer(10)
        self.lims_hsizer.Add(wx.StaticText(self, wx.ID_ANY,"Upper Limit:"),0, wx.ALIGN_CENTER_VERTICAL)
        self.lims_hsizer.Add(self.upper_lim_txtbox,0, wx.ALIGN_CENTER_VERTICAL)
        self.lims_hsizer.AddSpacer(10)
        self.lims_hsizer.AddSpacer(10)
        self.vsizer.Add(self.lims_hsizer,1,wx.ALIGN_CENTER_HORIZONTAL)
        
        #Add Exclude Limit text boxes and buttons
        self.excl_hsizer.AddSpacer(5)
        self.excl_hsizer.Add(wx.StaticText(self, wx.ID_ANY,"Exclude Low Limit:"),0, wx.ALIGN_CENTER_VERTICAL)
        self.excl_hsizer.Add(self.lower_excl_txtbox,0, wx.ALIGN_CENTER_VERTICAL)
        self.excl_hsizer.AddSpacer(10)
        self.excl_hsizer.Add(wx.StaticText(self, wx.ID_ANY,"Exclude Upper Limit:"),0, wx.ALIGN_CENTER_VERTICAL)
        self.excl_hsizer.Add(self.upper_excl_txtbox,0, wx.ALIGN_CENTER_VERTICAL)
        self.excl_hsizer.AddSpacer(10)
        self.vsizer.Add(self.excl_hsizer,1,wx.ALIGN_CENTER_HORIZONTAL)    
        
        #Add Fit order label and text box
        self.fit_order_sizer.AddSpacer(5)
        self.fit_order_sizer.Add(wx.StaticText(self, wx.ID_ANY,"Fit Order:"),0, wx.ALIGN_CENTER_VERTICAL)
        self.fit_order_sizer.Add(self.fit_order_txtbox,0, wx.ALIGN_CENTER_VERTICAL)
        #self.fit_order_sizer.AddSpacer(30)
        #self.fit_order_sizer.Add(self.apply_button,0,wx.ALIGN_CENTER_VERTICAL)
        #self.fit_order_sizer.AddSpacer(10)
        self.vsizer.AddSpacer(5)
        self.vsizer.Add(self.fit_order_sizer,0,wx.ALIGN_CENTER_HORIZONTAL)
        
        #Add Suggested Limits text
        self.suggestion_label = wx.StaticText(self, label="Suggested Limits:")
        self.vsizer.AddSpacer(5)
        self.vsizer.Add(self.suggestion_label,0,wx.ALIGN_LEFT)

        #Add suggestion buttons
        self.suggestions.AddSpacer(5)
        self.suggestions.Add(self.suggest_button,0, wx.ALIGN_CENTER_VERTICAL)
        self.suggestions.AddSpacer(10)
        self.suggestions.Add(self.suggest4500_button,0, wx.ALIGN_CENTER_VERTICAL)
        self.suggestions.AddSpacer(10)
        self.suggestions.Add(self.suggest5200_button,0, wx.ALIGN_CENTER_VERTICAL)
        self.suggestions.AddSpacer(10)
        self.suggestions.Add(self.suggestCO3_button,0, wx.ALIGN_CENTER_VERTICAL)
        self.suggestions.AddSpacer(10)
        self.suggestions.Add(self.suggestCO3_2_button,0, wx.ALIGN_CENTER_VERTICAL)
        self.suggestions.AddSpacer(10) 
        self.vsizer.Add(self.suggestions,1,wx.ALIGN_CENTER_HORIZONTAL)
        
        #Add Apply buttons
        self.apply_sizer.AddSpacer(5)
        self.apply_sizer.Add(self.apply_button,0,wx.ALIGN_CENTER_VERTICAL)
        self.apply_sizer.AddSpacer(5)
        self.apply_sizer.AddSpacer(5)
        self.vsizer.Add(self.apply_sizer,2,wx.ALIGN_CENTER_HORIZONTAL)
        
        # wx.EVT_BUTTON(self, self.apply_button.GetId(), self.on_apply)
        # wx.EVT_BUTTON(self, self.suggest_button.GetId(), self.on_suggest)
        # wx.EVT_BUTTON(self, self.suggestCO3_button.GetId(), self.on_suggestCO3)
        # wx.EVT_BUTTON(self, self.suggest4500_button.GetId(), self.on_suggest4500)
        # wx.EVT_BUTTON(self, self.suggest5200_button.GetId(), self.on_suggest5200)
        # wx.EVT_BUTTON(self, self.suggestCO3_2_button.GetId(), self.on_suggestCO3_2)
        self.Bind(wx.EVT_BUTTON, self.on_apply, self.apply_button)
        self.Bind(wx.EVT_BUTTON, self.on_suggest, self.suggest_button)
        self.Bind(wx.EVT_BUTTON, self.on_suggestCO3, self.suggestCO3_button)
        self.Bind(wx.EVT_BUTTON, self.on_suggest4500, self.suggest4500_button)
        self.Bind(wx.EVT_BUTTON, self.on_suggest5200, self.suggest5200_button)
        self.Bind(wx.EVT_BUTTON, self.on_suggestCO3_2, self.suggestCO3_2_button)
        self.SetSizer(self.vsizer)
        self.vsizer.Fit(self)
        self.SetAutoLayout(1)
        scan = self.plot_manager.get_current_scan()
        if scan is not None:
            self.update(scan)
        self.plot_manager.register_callback(self.update)
        
        # register auto-updating text boxes as user drags lines
        self.plot_manager.bkgd_selector.on_drag = self.on_line_drag
        
        # Start disabled until a file is loaded.
        self.set_non_editable()
    
    def _read_inputs(self):
        """
        Read and validate the four limit boxes. Returns a dict or raises ValueError.
        IntCtrl guarantees the values are already ints — no parsing needed.
        """
        lo = self.lower_lim_txtbox.GetValue()
        hi = self.upper_lim_txtbox.GetValue()
        excl_lo = self.lower_excl_txtbox.GetValue()
        excl_hi = self.upper_excl_txtbox.GetValue()

        if lo >= hi:
            raise ValueError("Lower limit must be less than upper limit")
        if excl_lo > excl_hi:
            raise ValueError("Exclude lower must be ≤ exclude upper")

        return {
            "bkgd_lowlim": lo,
            "bkgd_highlim": hi,
            "excl_lowlim": excl_lo,
            "excl_highlim": excl_hi,
            "bkgd_fit_order": self.fit_order_txtbox.GetValue(),
        }
    
    def on_line_drag(self):
        self.on_get_lims(None)
        
    def on_apply(self, evt):
        try:
            values = self._read_inputs()
        except ValueError as e:
            wx.MessageBox(str(e), "Invalid input", wx.OK | wx.ICON_ERROR)
            return

        wx.BeginBusyCursor()
        try:
            scan = self.plot_manager.get_current_scan()
            scan.manual_bkgd = True
            for attr, val in values.items():
                setattr(scan, attr, val)
            scan.calculate()
            self.plot_manager.update(scan)
        finally:
            wx.EndBusyCursor()
    
    def update(self, scan):
        self.fit_order_txtbox.SetValue(scan.bkgd_fit_order)
        self.lower_lim_txtbox.SetValue(int(round(scan.bkgd_lowlim)))
        self.upper_lim_txtbox.SetValue(int(round(scan.bkgd_highlim)))
        self.lower_excl_txtbox.SetValue(int(round(scan.excl_lowlim)))
        self.upper_excl_txtbox.SetValue(int(round(scan.excl_highlim)))
        self.set_editable()
    
    
    def set_non_editable(self):
        self.lower_lim_txtbox.Disable()
        self.upper_lim_txtbox.Disable()
        self.fit_order_txtbox.Disable()
        self.apply_button.Disable()
        self.suggest_button.Disable()
        self.suggestCO3_button.Disable()
        self.suggest4500_button.Disable()
        self.suggest5200_button.Disable()
        self.suggestCO3_2_button.Disable()
    
    
    def set_editable(self):
        self.lower_lim_txtbox.Enable()
        self.upper_lim_txtbox.Enable()
        self.fit_order_txtbox.Enable()
        self.apply_button.Enable()
        self.suggest_button.Enable()
        self.suggestCO3_button.Enable()
        self.suggest4500_button.Enable()
        self.suggest5200_button.Enable()
        self.suggestCO3_2_button.Enable()
        
    def on_get_lims(self, evt):
        
        lower_lim, upper_lim = self.plot_manager.bkgd_selector.get_lims()
        self.lower_lim_txtbox.SetValue(int(round(lower_lim)))
        self.upper_lim_txtbox.SetValue(int(round(upper_lim)))

        lower_lim, upper_lim = self.plot_manager.bkgd_selector.get_excl_lims()
        self.lower_excl_txtbox.SetValue(int(round(lower_lim)))
        self.upper_excl_txtbox.SetValue(int(round(upper_lim)))

    def on_suggest(self, evt):
        self.lower_lim_txtbox.SetValue(2400)
        self.upper_lim_txtbox.SetValue(4000)
        self.lower_excl_txtbox.SetValue(2590)
        self.upper_excl_txtbox.SetValue(3788)
        self.fit_order_txtbox.SetValue(1)

    def on_suggestCO3(self, evt):
        self.lower_lim_txtbox.SetValue(1242)
        self.upper_lim_txtbox.SetValue(2038)
        self.lower_excl_txtbox.SetValue(1362)
        self.upper_excl_txtbox.SetValue(1770)
        self.fit_order_txtbox.SetValue(3)

    def on_suggest5200(self, evt):
        self.lower_lim_txtbox.SetValue(4710)
        self.upper_lim_txtbox.SetValue(5960)
        self.lower_excl_txtbox.SetValue(5138)
        self.upper_excl_txtbox.SetValue(5280)
        self.fit_order_txtbox.SetValue(3)

    def on_suggest4500(self, evt):
        self.lower_lim_txtbox.SetValue(4050)
        self.upper_lim_txtbox.SetValue(5072)
        self.lower_excl_txtbox.SetValue(4300)
        self.upper_excl_txtbox.SetValue(4600)
        self.fit_order_txtbox.SetValue(3)

    def on_suggestCO3_2(self, evt):
        self.lower_lim_txtbox.SetValue(1499)
        self.upper_lim_txtbox.SetValue(2339)
        self.lower_excl_txtbox.SetValue(1551)
        self.upper_excl_txtbox.SetValue(2058)
        self.fit_order_txtbox.SetValue(5)
 

class ControlWindow(wx.Frame):
    def __init__(self, scan, title):
        wx.Frame.__init__(self, None, wx.ID_ANY, title)
        self.SetDropTarget(FileDropTarget(self))
        self.top_panel = wx.Panel(self, wx.ID_ANY)

        # PlotManager builds the matplotlib Figure and a FigureCanvasWxAgg
        # widget parented to self.top_panel, so the plot lives inside this frame.
        self.plot_manager = PlotManager(self.top_panel, scan)

        self.main_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer.AddSpacer(10)
        self.main_sizer.Add(wx.StaticText(self.top_panel, wx.ID_ANY, "Background Fitting:"))
        self.controls = BackgroundFittingControls(self.top_panel, self.plot_manager)
        self.main_sizer.Add(self.controls, 0, wx.EXPAND)
        self.main_sizer.Add(self.plot_manager.canvas, 1, wx.EXPAND)

        self.main_hsizer.AddSpacer(5)
        self.main_hsizer.Add(self.main_sizer, 1, wx.EXPAND)
        self.main_hsizer.AddSpacer(5)

        self.top_panel.SetSizer(self.main_hsizer)
        self.top_panel.SetAutoLayout(1)

        # Give the window a sensible starting size; the canvas needs room.
        self.SetSize((900, 800))

        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # Add menu bar
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        open_item = file_menu.Append(wx.ID_OPEN, "&Open...\tCtrl+O", "Open an FTIR file")
        file_menu.AppendSeparator()
        quit_item = file_menu.Append(wx.ID_EXIT, "&Quit\tCtrl+Q", "Quit")
        menubar.Append(file_menu, "&File")
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.on_menu_open, open_item)
        self.Bind(wx.EVT_MENU, self.on_menu_quit, quit_item)

        self.Show()

    def load_file(self, path):
        wavenum, intensity = load_ftir_file(path)
        scan = ProcessedScan(wavenum, intensity)
        self.plot_manager.scan = scan # set the PlotManager's scan attr
        self.plot_manager.bkgd_selector.update(scan)
        self.plot_manager.figure.tight_layout()
        self.plot_manager.canvas.draw_idle()
        self.controls.set_editable()
        self.controls.update(scan) # populate default text box values
        self.SetTitle(os.path.basename(path) + " - FTIR Background Subtract")
    
    def on_menu_open(self, evt):
        with wx.FileDialog(self, "Open FTIR file",
                        wildcard="CSV files (*.csv;*.CSV)|*.csv;*.CSV|All files (*.*)|*.*",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            self.load_file(dlg.GetPath())

    def on_menu_quit(self, evt):
        self.Close()

    def on_close(self, evnt):
        self.Destroy()


class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, paths):
        if paths:
            self.window.load_file(paths[0])
        return True


class ProcessedScan:
    def __init__(self, wavenum, intensity, bkgd_fit_order=1, bkgd_threshold=5.0):
        self.__is_calculated = False
        
        self.angles = wavenum   
        self.col_amount = intensity
        
        self.angle_err = numpy.ones_like(wavenum)*5
        self.col_err = numpy.abs((intensity/100.0)*5)
        
        # hard code to suggested 3500 total H2O+OH peak
        self.bkgd_lowlim = 2400
        self.bkgd_highlim = 4000
        self.excl_lowlim = 2590
        self.excl_highlim = 3788
        
        #background fitting parameters
        self.bkgd_fit_order = bkgd_fit_order
        self.bkgd_threshold = bkgd_threshold
        self.manual_bkgd = True
   
    
    def calculate(self):    
        self.__calculate_bkgd()
        return self
    
    def plot_bkgd_fit(self, ax):
        
        ignored = list(zip(*self.bkgd_ignored_pts))
        if ignored:
            ax.errorbar(ignored[0], ignored[1], ignored[3], ignored[2], 'r+')
        
        #subplot_calc.errorbar(not_bkgd_angles,not_bkgd_col_amounts, not_bkgd_col_err, not_bkgd_angle_err,'g+')        
        ax.errorbar(self.angles[self.bkgd_idxs], self.col_amount[self.bkgd_idxs], self.col_err[self.bkgd_idxs], self.angle_err[self.bkgd_idxs], 'b+')
        
        x = numpy.linspace(self.angles[self.bkgd_idxs[0][0]],self.angles[self.bkgd_idxs[0][-1]],2000 )
        ax.plot(x, [self.bkgd_func(i) for i in x], 'm-', linewidth=2)
   
   
      
    def __calculate_bkgd(self):
        
        #don't allow the background to be bigger than the scan data
        if self.bkgd_lowlim < min(self.angles[0], self.angles[-1]):
            self.bkgd_lowlim = min(self.angles[0], self.angles[-1]) 
        
        if self.bkgd_highlim > max(self.angles[0], self.angles[-1]):
            self.bkgd_highlim = max(self.angles[0], self.angles[-1])        
        
        is_lower_bkgd = self.angles > self.bkgd_lowlim
        is_higher_bkgd = self.angles < self.bkgd_highlim
        bkgd_mask = numpy.logical_and(is_lower_bkgd, is_higher_bkgd)
        
        is_lower_excl = self.angles > self.excl_lowlim
        is_higher_excl = self.angles < self.excl_highlim
        excl_mask = numpy.logical_and(is_lower_excl,is_higher_excl)
        
        self.bkgd_mask = numpy.logical_and(bkgd_mask, numpy.logical_not(excl_mask))
        
        
        bkgd_idxs = numpy.where(self.bkgd_mask)

        
        #fit a polynomial through the background
        ignored_pts = []
        
        while True:
            bkgd_angles = self.angles[bkgd_idxs]
            bkgd_col_amounts = self.col_amount[bkgd_idxs]
            bkgd_angle_err = self.angle_err[bkgd_idxs]
            bkgd_col_err = self.col_err[bkgd_idxs]
            
            polyfit_params = numpy.polyfit(bkgd_angles, bkgd_col_amounts, self.bkgd_fit_order)
            bkgd_function = numpy.poly1d(polyfit_params)
                 
            #calculate the residuals - ignoring those that are within error
            resid = find_residuals(bkgd_angles, bkgd_col_amounts, bkgd_angle_err, bkgd_col_err, bkgd_function)
            
            if len(numpy.nonzero(resid)[0]) == 0:
                break
            
            #remove the point with the greatest residual from the fit
            idx_to_skip = bkgd_idxs[0][numpy.argmax(resid)]
            ignored_pts.append((self.angles[idx_to_skip], self.col_amount[idx_to_skip], self.angle_err[idx_to_skip], self.col_err[idx_to_skip]))
            bkgd_idxs = (bkgd_idxs[0][numpy.where(bkgd_idxs[0] != idx_to_skip)],)
        
        #store the calculated background for all angles
        self.bkgd_func = bkgd_function
        self.bkgd_ignored_pts = ignored_pts
        self.bkgd_idxs = bkgd_idxs


def find_residuals(x, y, x_err, y_err, func):
    """
    Calculates the absolute distances of a data series from a trend line.
    However, any distances that are within the error bars are set 
    to zero. This makes it easy to see if a trend line fits some data within
    experimental error. 
    
    * x - numpy array of x data
    * y - numpy array of corresponding y data
    * x_err - absolute error in x direction (x +- x_err)
    * y_err - absolute error in y direction (y +- y_err)
    * func - a Python function that describes the trendline such that y_trend = func(x)
             where x is a single x value.
    """
    #convert func to numpy ufunc
    fit_func = numpy.frompyfunc(func, 1, 1)
    
    x_mins = x - x_err
    x_maxs = x + x_err
    
    #evaluate the distance between the data and the trendline at the extremes of
    #the x error.
    resid_mins = numpy.abs(y - fit_func(x_mins))
    resid_maxs = numpy.abs(y - fit_func(x_maxs))
    
    #get the smallest distance of each point from the fit line
    resid = numpy.minimum(resid_mins, resid_maxs)
    
    #set residuals that are within the error bars to zero
    resid[numpy.where(resid < y_err)] = 0
    
    return resid


class BackgroundFitDisplay:
    def __init__(self, ax):
        self.ax = ax
    
    def update(self, scan):
        self.ax.clear()
        self.ax.set_xlabel(r"Wavenumber (cm$^{-1}$)")
        self.ax.set_ylabel("Absorbance")
        scan.plot_bkgd_fit(self.ax)

        low_idx = numpy.argmin(numpy.abs(scan.angles-scan.bkgd_lowlim))
        high_idx = numpy.argmin(numpy.abs(scan.angles-scan.bkgd_highlim))

        wavenum = scan.angles[low_idx:high_idx]
        intensity = scan.col_amount[low_idx:high_idx]

        self.ax.plot(wavenum, intensity, 'k-')
        self.ax.invert_xaxis()
        
        
class BackgroundSubtractedDisplay:
    def __init__(self, ax):
        self.ax = ax
        self.ax.invert_xaxis()
        self.wavenum = None
        self.intens = None
        self.markers = []   # list of (DraggableLine, annotation)
        self.ax.figure.canvas.mpl_connect('button_press_event', self._on_click)

    def update(self, scan):
        # Disconnect old markers' event handlers; ax.clear() kills the artists.
        for marker, _ in self.markers:
            marker.disconnect()
        self.markers = []

        self.ax.clear()
        self.ax.invert_xaxis()
        self.ax.set_xlabel(r"Wavenumber (cm$^{-1}$)")
        self.ax.set_ylabel("Absorbance (background subtracted)")

        low_idx = numpy.argmin(numpy.abs(scan.angles - scan.bkgd_lowlim))
        high_idx = numpy.argmin(numpy.abs(scan.angles - scan.bkgd_highlim))
        self.wavenum = scan.angles[low_idx:high_idx]
        self.intens = scan.col_amount[low_idx:high_idx] - scan.bkgd_func(self.wavenum)

        self.ax.plot(self.wavenum, self.intens, 'g-')
        self.ax.axhline(y=0, color='r')

    def _on_click(self, event):
        # Only respond to left-clicks in our axes, after Apply has populated data.
        if event.inaxes is not self.ax:
            return
        if self.wavenum is None or event.xdata is None:
            return
        if event.button != 1:
            return

        # If the click lands on an existing marker, do nothing — DraggableLine's
        # own on_press will take over for the drag.
        for marker, _ in self.markers:
            contains, _ = marker.line.contains(event)
            if contains:
                return

        # Add a new draggable marker at the closest data point.
        idx = numpy.argmin(numpy.abs(self.wavenum - event.xdata))
        x = self.wavenum[idx]
        y = self.intens[idx]

        marker = DraggableLine(x, self.ax, color='k', linewidth=1)
        label = self.ax.annotate(f"{y:.3f}", xy=(x, y),
                                 xytext=(5, 5), textcoords='offset points',
                                 fontsize=9)
        # Wire the drag-release callback once both objects exist.
        marker.callback = lambda new_x: self._update_marker(marker, label, new_x)
        self.markers.append((marker, label))
        self.ax.figure.canvas.draw_idle()

    def _update_marker(self, marker, label, new_x):
        # Snap line and label to the nearest data point and refresh the y-value.
        idx = numpy.argmin(numpy.abs(self.wavenum - new_x))
        x = self.wavenum[idx]
        y = self.intens[idx]
        marker.line.set_xdata([x, x])
        label.xy = (x, y)
        label.set_text(f"{y:.3f}")
        self.ax.figure.canvas.draw_idle()

class BackgroundRangeSelector:
    def __init__(self, ax):
        self.ax = ax
        self.ax.invert_xaxis()
        self.lim_line1 = None
        self.lim_line2 = None
        self.plot = None
        self.on_drag = None
    
    def update(self, scan):
        if self.lim_line1 is not None:
            self.lim_line1.disconnect()
            self.lim_line2.disconnect()
            self.excl_line1.disconnect()
            self.excl_line2.disconnect()

        self.ax.cla()
        self.ax.invert_xaxis()
        self.ax.set_xlabel(r"Wavenumber (cm$^{-1}$)")
        self.ax.set_ylabel("Absorbance")

        self.plot = self.ax.plot(scan.angles, scan.col_amount, 'b-')

        self.lim_line1 = DraggableLine(scan.bkgd_lowlim, self.ax, color='g',
                                       callback=self._line_dragged)
        self.lim_line2 = DraggableLine(scan.bkgd_highlim, self.ax, color='g',
                                       callback=self._line_dragged)
        self.excl_line1 = DraggableLine(scan.excl_lowlim, self.ax, color='r',
                                        callback=self._line_dragged)
        self.excl_line2 = DraggableLine(scan.excl_highlim, self.ax, color='r',
                                        callback=self._line_dragged)
        
    def get_lims(self):
        pos1 = self.lim_line1.get_xpos()
        pos2 = self.lim_line2.get_xpos()
        
        return min(pos1,pos2), max(pos1,pos2)

    def get_excl_lims(self):
        pos1 = self.excl_line1.get_xpos()
        pos2 = self.excl_line2.get_xpos()
        
        return min(pos1,pos2), max(pos1,pos2)
    
    def _line_dragged(self, _x):
        if self.on_drag is not None:
            self.on_drag()

class PlotManager:
    def __init__(self, parent, scan):
        self.callbacks = []
        self.scan = scan

        # Build an explicit Figure (not via pyplot) so the canvas can be
        # embedded as a wx widget inside `parent`.
        self.figure = Figure()
        self.canvas = FigureCanvas(parent, wx.ID_ANY, self.figure)

        bkgd_select_ax = self.figure.add_subplot(3, 1, 1)
        bkgd_fit_ax = self.figure.add_subplot(3, 1, 2)
        bkgd_subtracted_ax = self.figure.add_subplot(3, 1, 3)

        self.plots = []

        self.bkgd_selector = BackgroundRangeSelector(bkgd_select_ax)
        if scan is not None:
            self.bkgd_selector.update(scan)
        self.plots.append(self.bkgd_selector)

        self.bkgd_fit = BackgroundFitDisplay(bkgd_fit_ax)
        self.plots.append(self.bkgd_fit)

        self.bkgd_subtracted_plot = BackgroundSubtractedDisplay(bkgd_subtracted_ax)
        self.plots.append(self.bkgd_subtracted_plot)

    def get_current_scan(self):
        return self.scan

    def register_callback(self, f):
        self.callbacks.append(f)

    def update(self, scan):
        wx.BeginBusyCursor()
        for p in self.plots:
            p.update(scan)

        # Re-flow subplots so the now-populated axis labels don't overlap.
        self.figure.tight_layout()
        self.canvas.draw_idle()

        for f in self.callbacks:
            f(scan)

        wx.EndBusyCursor()

def load_ftir_file(filename):

    with open(filename, "rt") as f:
        reader = csv.reader(f, dialect="excel")
        wavenumber = []
        absorbance = []

        for line in reader:
            wavenumber.append(float(line[0]))
            absorbance.append(float(line[1]))
        
        return numpy.array(wavenumber), numpy.array(absorbance)

if __name__ == '__main__':
    app = wx.App()

    f = FileChooser()
    f.CenterOnScreen()
    f.Show()
    app.MainLoop()
