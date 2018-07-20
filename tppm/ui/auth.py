from __future__ import absolute_import
from __future__ import unicode_literals

from Tkinter import Button, Entry, Label, StringVar


class AuthUI(object):
    def __init__(self, parent, app):
        self.top = parent
        parent.title('Auth window')

        self.parent = parent
        self.root = app

        # Widget Initialization
        self._label_header = Label(
            parent,
            font="{Segoe UI} 20 bold",
            foreground="#ff0000",
            text="Trakt Account Authorization",
        )
        self._button_get_code = Button(
            parent,
            font="{MS Sans Serif} 12 bold",
            text="Get PIN Code",
        )
        self._label_enter_code = Label(
            parent,
            font="{MS Sans Serif} 14",
            text="Enter the code:",
        )
        self._label_click = Label(
            parent,
            font="{MS Sans Serif} 14",
            text="Click the button to get a code:",
        )
        self.pin_code = StringVar()
        self._entry_code = Entry(
            parent,
            font="{MS Sans Serif} 14 bold",
            width=10,
            justify="center",
            textvariable=self.pin_code,
            state="disabled",
        )
        self._button_done = Button(
            parent,
            borderwidth=3,
            font="{MS Sans Serif} 12 bold",
            text="Done",
            state="disabled",
        )

        # widget commands
        self._button_get_code.configure(
            command=self.button_get_code_command
        )
        self._button_done.configure(
            command=self.button_done_command
        )

        # Geometry Management
        self._label_header.grid(
            in_=parent,
            column=1,
            row=1,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky="ew"
        )
        self._label_click.grid(
            in_=parent,
            column=1,
            row=2,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._button_get_code.grid(
            in_=parent,
            column=1,
            row=3,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._label_enter_code.grid(
            in_=parent,
            column=1,
            row=4,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._entry_code.grid(
            in_=parent,
            column=1,
            row=5,
            columnspan=1,
            ipadx=5,
            ipady=0,
            padx=5,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._button_done.grid(
            in_=parent,
            column=1,
            row=6,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )

        # Resize Behavior
        parent.resizable(False, False)
        parent.grid_rowconfigure(1, weight=1, minsize=40, pad=10)
        parent.grid_rowconfigure(2, weight=1, minsize=40, pad=10)
        parent.grid_rowconfigure(3, weight=1, minsize=40, pad=10)
        parent.grid_rowconfigure(4, weight=1, minsize=40, pad=10)
        parent.grid_rowconfigure(5, weight=1, minsize=50, pad=10)
        parent.grid_rowconfigure(6, weight=1, minsize=50, pad=10)
        parent.grid_columnconfigure(1, weight=1, minsize=0, pad=10)
