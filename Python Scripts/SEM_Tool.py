#   File:           SEM_Tool.py
#
#   Description:    Implement the scanning electron microscope realtime     
#                   diagnostic tool.
#
#   Author:         Liuchuyao Xu, 2019

import wx
import matplotlib.figure
import matplotlib.backends.backend_wxagg

class SEMTool(wx.Frame):

    canvas = None
    panel = None

    def __init__(self):
        super().__init__(parent = None,
                         title = "SEM Realtime Diagnostic Tool")
        minSize = wx.Size(1280, 800)
        self.SetMinSize(minSize)
        self.SetSize(minSize)
        self.Centre()

        self.init_figure()
        self.init_panel()
        self.fit_panel()
        self.fit()

        self.Show()

    def init_figure(self):
        figure = matplotlib.figure.Figure()
        self.canvas = matplotlib.backends.backend_wxagg.FigureCanvasWxAgg(
                                                        parent=self,
                                                        id=-1,
                                                        figure=figure)
        self.canvas.plots = figure.subplots(nrows=2, ncols=2)
        self.canvas.plots[0,0].set_title("Original Image")
        self.canvas.plots[0,1].set_title("2D FFT")
        self.canvas.plots[1,0].set_title("X-Axis FFT")
        self.canvas.plots[1,1].set_title("Y-Axis FFT")
    
    def init_panel(self):
        self.panel = wx.Panel(parent=self)
        minSize = wx.Size(200, 800)
        self.panel.SetMinSize(minSize)
        self.panel.SetSize(minSize)
        self.panel.zoom = wx.Slider(parent=self.panel, style=wx.SL_LABELS)

    def fit_panel(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel.zoom, flag=wx.EXPAND)
        self.panel.SetSizer(sizer)

    def fit(self):
        sizer = wx.FlexGridSizer(cols=2)
        sizer.AddGrowableRow(idx=0)
        sizer.AddGrowableCol(idx=0)
        sizer.Add(window=self.canvas, flag=wx.EXPAND)
        sizer.Add(window=self.panel, flag=wx.EXPAND)
        self.SetSizer(sizer)

if __name__ == "__main__":
    app = wx.App()
    tool = SEMTool()
    app.MainLoop()
