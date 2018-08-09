# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from six.moves.tkinter import PhotoImage, TclError


def set_icon(root):
    # https://stackoverflow.com/a/11180300
    icon = os.path.join(os.path.dirname(__file__), 'icon.gif')
    try:
        img = PhotoImage(file=icon)
        root.tk.call('wm', 'iconphoto', root._w, '-default', img)
    except TclError:
        from traceback import print_exc
        print_exc()
