from ftirbackgroundsubtractog.ftirbackgroundsubtractog import *
import wx

if __name__ == '__main__':
    app = wx.App()

    f = FileChooser()
    f.CenterOnScreen()
    f.Show()
    app.MainLoop()
