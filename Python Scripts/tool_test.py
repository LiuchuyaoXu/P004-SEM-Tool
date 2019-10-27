#   File:           tool_test.py
#
#   Description:    Code for testing purposes.
#
#   Author:         Liuchuyao Xu, 2019

import wx
import matplotlib.figure
import matplotlib.backends.backend_wxagg

class SEMTool:
    app = None
    frame = None
    canvas = None
    panel = None
    figure = None
    def init_app(self):
        self.app = wx.App()
    def init_frame(self):
        self.frame = wx.Frame(  parent=None,
                                title="SEM Realtime Diagnostic Tool",
                                style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.frame.SetMinSize(wx.Size(1280, 720))
        self.frame.SetSize(self.frame.GetMinSize())
        self.frame.Centre()
    def init_canvas(self): 
        self.figure = matplotlib.figure.Figure()
        self.subplots = self.figure.subplots(nrows=2, ncols=2)
        self.subplots[0,0].set_title("Plot 1")
        self.subplots[0,1].set_title("Plot 2")
        self.subplots[1,0].set_title("Plot 3")
        self.subplots[1,1].set_title("Plot 4")
        self.canvas = matplotlib.backends.backend_wxagg.FigureCanvasWxAgg(
                            parent=self.frame,
                            id=-1,
                            figure=self.figure)
    def init_panel(self):
        self.panel = wx.Panel(parent=self.frame)
        plot_choices = ["SEM Image", "SEM Image 2D FFT"]
        self.panel.plot1 = wx.RadioBox( parent=self.panel,
                                        label="Plot 1",
                                        choices=plot_choices)
        self.panel.plot2 = wx.RadioBox( parent=self.panel,
                                        label="Plot 2",
                                        choices=plot_choices)
        self.panel.plot3 = wx.RadioBox( parent=self.panel,
                                        label="Plot 3",
                                        choices=plot_choices)
        self.panel.plot4 = wx.RadioBox( parent=self.panel,
                                        label="Plot 4",
                                        choices=plot_choices)
        self.panel.zoom = wx.Slider(parent=self.panel, style=wx.SL_LABELS)
    def fit_panel(self):
        self.panel.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.sizer.Add(self.panel.plot1)
        self.panel.sizer.Add(self.panel.plot2)
        self.panel.sizer.Add(self.panel.plot3)
        self.panel.sizer.Add(self.panel.plot4)
        self.panel.sizer.Add(self.panel.zoom, flag=wx.EXPAND)
        self.panel.SetSizer(self.panel.sizer)
    def fit_frame(self):
        self.frame.sizer = wx.FlexGridSizer(cols=2)
        self.frame.sizer.AddGrowableRow(idx=0)
        self.frame.sizer.AddGrowableCol(idx=0)
        self.frame.sizer.Add(window=self.canvas, flag=wx.EXPAND)
        self.frame.sizer.Add(window=self.panel, flag=wx.EXPAND)
        self.frame.SetSizer(self.frame.sizer)
    def __init__(self):
        self.init_app()
        self.init_frame()
        self.init_canvas()
        self.init_panel()
        self.fit_panel()
        self.fit_frame()

        self.frame.Show()
        self.app.MainLoop()

if __name__ == "__main__":
    SEMTool()
