from ftirbackgroundsubtractog.ftirbackgroundsubtractog import ControlWindow
import wx

if __name__ == '__main__':
    app = wx.App()
    ControlWindow(scan=None, title="FTIR Background Subtract")
    app.MainLoop()