#   File:           SEM_Tool.py
#
#   Description:    Implement the realtime diagnostic tool for the scanning     
#                    eletron microscope.
#
#   Author:         Liuchuyao Xu, 2019

import wx
import matplotlib.figure
import matplotlib.backends.backend_wxagg

class SEM_Tool:
    def __init__(self):
        self.app = wx.App()

        self.app.frame = wx.Frame(parent=None, title="SEM Realtime Diagnostic Tool")
        self.app.frame.SetSize(1024, 768)
        self.app.frame.Centre()

        figure = matplotlib.figure.Figure()
        subplots = figure.subplots(nrows=2, ncols=2)
        subplots[0,0].set_title("Plot 1")
        subplots[0,1].set_title("Plot 2")
        subplots[1,0].set_title("Plot 3")
        subplots[1,1].set_title("Plot 4")
        self.app.frame.canvas = matplotlib.backends.backend_wxagg.FigureCanvasWxAgg(
                                parent=self.app.frame,
                                id=-1,
                                figure=figure)

        self.app.frame.Show()
        self.app.MainLoop()

if __name__ == "__main__":
    SEM_Tool()
