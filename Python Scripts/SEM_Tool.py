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
        app = wx.App()
        frame = wx.Frame(   parent=None,
                            title="SEM Realtime Diagnostic Tool",
                            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        frame.SetMinSize(wx.Size(1280, 720))
        frame.SetSize(frame.GetMinSize())
        frame.Centre()

        figure = matplotlib.figure.Figure()
        subplots = figure.subplots(nrows=2, ncols=2)
        subplots[0,0].set_title("Plot 1")
        subplots[0,1].set_title("Plot 2")
        subplots[1,0].set_title("Plot 3")
        subplots[1,1].set_title("Plot 4")
        frame.canvas = matplotlib.backends.backend_wxagg.FigureCanvasWxAgg(
                            parent=frame,
                            id=-1,
                            figure=figure)

        frame.panel = wx.Panel(parent=frame)
        plot_choices = ["SEM Image", "SEM Image 2D FFT"]
        frame.panel.plot1 = wx.RadioBox(parent=frame.panel,
                                        label="Plot 1",
                                        choices=plot_choices)
        frame.panel.plot2 = wx.RadioBox(parent=frame.panel,
                                        label="Plot 2",
                                        choices=plot_choices)
        frame.panel.plot3 = wx.RadioBox(parent=frame.panel,
                                        label="Plot 3",
                                        choices=plot_choices)
        frame.panel.plot4 = wx.RadioBox(parent=frame.panel,
                                        label="Plot 4",
                                        choices=plot_choices)
        frame.panel.zoom = wx.Slider(parent=frame.panel, style=wx.SL_LABELS)

        frame.panel.sizer = wx.BoxSizer(wx.VERTICAL)
        frame.panel.sizer.Add(frame.panel.plot1)
        frame.panel.sizer.Add(frame.panel.plot2)
        frame.panel.sizer.Add(frame.panel.plot3)
        frame.panel.sizer.Add(frame.panel.plot4)
        frame.panel.sizer.Add(frame.panel.zoom, flag=wx.EXPAND)
        frame.panel.SetSizer(frame.panel.sizer)

        frame.sizer = wx.FlexGridSizer(cols=2)
        frame.sizer.AddGrowableRow(idx=0)
        frame.sizer.AddGrowableCol(idx=0)
        frame.sizer.Add(window=frame.canvas, flag=wx.EXPAND)
        frame.sizer.Add(window=frame.panel, flag=wx.EXPAND)
        frame.SetSizer(frame.sizer)

        frame.Show()
        app.MainLoop()

if __name__ == "__main__":
    SEM_Tool()
