#   File:   SemController.py
#
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Provides an interface for controlling the SEM.

import sys
import win32com.client as win32

class SemController:

    def __init__(self):
        ole = 'CZ.EmApiCtrl.1'
        sys.argv = ['makepy', ole]
        win32.makepy.main()

        com = win32.Dispatch(ole)
        com.InitialiseRemoting()

if __name__ == '__main__':
    sem = SemController()
