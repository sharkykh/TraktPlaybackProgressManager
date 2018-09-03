# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from six.moves.tkinter import PhotoImage, TclError


def center_toplevel(widget):
    # https://bbs.archlinux.org/viewtopic.php?pid=1167024#p1167024

    # Apparently a common hack to get the window size. Temporarily hide the
    # window to avoid update_idletasks() drawing the window in the wrong position.
    widget.withdraw()
    widget.update_idletasks()

    # Set window position
    x = (widget.winfo_screenwidth() - widget.winfo_reqwidth()) / 2
    y = (widget.winfo_screenheight() - widget.winfo_reqheight()) / 2
    widget.geometry('+%d+%d' % (x, y))

    # This seems to draw the window frame immediately, so only call deiconify()
    # after setting correct window position
    widget.deiconify()


def set_icon(root):
    # https://stackoverflow.com/a/11180300
    icon = os.path.join(os.path.dirname(__file__), 'icon.gif')
    try:
        img = PhotoImage(file=icon)
        root.tk.call('wm', 'iconphoto', root._w, '-default', img)
    except TclError:
        from traceback import print_exc
        print_exc()
