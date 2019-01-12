# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from six.moves.tkinter import (
    Button,
    Entry,
    Label,
    Listbox,
    Scrollbar,
    StringVar,
    TclError
)

from .. import app


# Based on: http://effbot.org/zone/tkinter-autoscrollbar.htm
class AutoScrollbar(Scrollbar):
    """A scrollbar that hides itself if it's not needed.
    Only Works if you use the grid geometry manager."""
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise TclError("cannot use pack with this widget")

    def place(self, **kw):
        raise TclError("cannot use place with this widget")


class MainUI(object):
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root

        self.selectedStatus = False

        # Widget Initialization
        self._listbox = Listbox(
            parent,
            font="{Segoe UI} 10",
            height=0,
            selectmode="extended",
            state="normal",
            cursor="hand2",
            exportselection=False,
        )
        self._listbox_scrollbar = AutoScrollbar(
            self._listbox
        )
        self._lbl_help = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            text="Hold [Ctrl] to select multiple items",
        )
        self._label_header = Label(
            parent,
            font="{Segoe UI} 16 bold",
            text="Playback items available for removal",
        )
        self._label_actions = Label(
            parent,
            font="{Segoe UI} 14 bold",
            text="Actions",
        )
        self._label_info = Label(
            parent,
            font="{Segoe UI} 14 bold",
            text="Info",
        )
        self._btnRefresh = Button(
            parent,
            font="{Segoe UI} 12 bold",
            text="Refresh",
        )
        self._btnRemoveSelected = Button(
            parent,
            font="{Segoe UI} 12 bold",
            wraplength=175,
            text="Remove Selected",
        )
        self._btnSelectDeselectAll = Button(
            parent,
            font="{Segoe UI} 12 bold",
            wraplength=175,
            text="Select / Deselect All",
        )
        self._btnLogin = Button(
            parent,
            font="{Segoe UI} 12 bold",
            text="Login/Auth",
        )
        self._lbl_ID = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            text="ID:",
        )
        self._lbl_PausedAt = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            text="Paused At:",
        )
        self._lbl_Progress = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            text="Progress:",
        )
        self.lbl_showName = StringVar(value="Show:")
        self._lbl_Show = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_showName,
        )
        self.lbl_season = StringVar(value="Season:")
        self._lbl_Season = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_season,
        )
        self.lbl_episode = StringVar(value="Episode:")
        self._lbl_Episode = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_episode,
        )
        self.lbl_episodeTitle = StringVar(value="Title:")
        self._lbl_Title = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_episodeTitle,
        )
        self.txt_ID = StringVar()
        self._txtID = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_ID,
            width=0,
        )
        self.txt_paused_at = StringVar()
        self._txtPausedAt = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_paused_at,
            width=0,
        )
        self.txt_progress = StringVar()
        self._txtProgress = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_progress,
            width=0,
        )
        self.txt_showName = StringVar()
        self._txtShowName = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_showName,
            width=0,
        )
        self.txt_season = StringVar()
        self._txtSeason = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_season,
            width=0,
        )
        self.txt_episode = StringVar()
        self._txtEpisode = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_episode,
            width=0,
        )
        self.txt_title = StringVar()
        self._txtTitle = Entry(
            parent,
            font="{Segoe UI Light} 12",
            readonlybackground="#ffffff",
            relief="flat",
            state="readonly",
            textvariable=self.txt_title,
            width=0,
        )
        self.lbl_loggedin = StringVar(value="Not logged in.")
        self._lbl_loggedin = Label(
            parent,
            font="{Segoe UI Light} 12 bold",
            textvariable=self.lbl_loggedin,
        )
        self._lbl_version = Label(
            parent,
            font="{Segoe UI Light} 10 bold",
            text="v%s" % app.__version__,
            foreground="blue",
            cursor="hand2",
        )

        # widget commands
        self._listbox.bind('<<ListboxSelect>>', self._listbox_onselect)
        self._listbox.config(
            yscrollcommand=self._listbox_scrollbar.set
        )
        self._listbox_scrollbar.config(
            orient='vertical',
            command=self._listbox.yview
        )
        self._btnRefresh.configure(
            command=self._btn_refresh_command
        )
        self._btnRemoveSelected.configure(
            command=self._btn_remove_selected_command
        )
        self._btnSelectDeselectAll.configure(
            command=self._btn_toggle_selection_command
        )
        self._btnLogin.configure(
            command=self._btn_login_command
        )
        self._lbl_version.bind('<Button-1>', self._open_repo)

        # Geometry Management
        self._listbox.grid(
            in_=parent,
            column=4,
            row=2,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=5,
            rowspan=10,
            sticky="nsew"
        )
        self._listbox.columnconfigure(
            0,
            weight=1
        )
        self._listbox.rowconfigure(
            0,
            weight=1
        )
        self._listbox_scrollbar.grid(
            column=4,
            rowspan=10,
            sticky="ns"
        )
        self._lbl_help.grid(
            in_=parent,
            column=4,
            row=11,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=5,
            sticky="nsew"
        )
        self._label_header.grid(
            in_=parent,
            column=4,
            row=1,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky="nsew"
        )
        self._label_actions.grid(
            in_=parent,
            column=1,
            row=9,
            columnspan=3,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky="nsew"
        )
        self._label_info.grid(
            in_=parent,
            column=1,
            row=1,
            columnspan=3,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky="nsew"
        )
        self._btnRefresh.grid(
            in_=parent,
            column=1,
            row=10,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._btnRemoveSelected.grid(
            in_=parent,
            column=2,
            row=10,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._btnSelectDeselectAll.grid(
            in_=parent,
            column=3,
            row=10,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._btnLogin.grid(
            in_=parent,
            column=2,
            row=11,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky=""
        )
        self._lbl_ID.grid(
            in_=parent,
            column=1,
            row=2,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_PausedAt.grid(
            in_=parent,
            column=1,
            row=3,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Progress.grid(
            in_=parent,
            column=1,
            row=4,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Show.grid(
            in_=parent,
            column=1,
            row=5,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Season.grid(
            in_=parent,
            column=1,
            row=6,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Episode.grid(
            in_=parent,
            column=1,
            row=7,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_Title.grid(
            in_=parent,
            column=1,
            row=8,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtID.grid(
            in_=parent,
            column=2,
            row=2,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtPausedAt.grid(
            in_=parent,
            column=2,
            row=3,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtProgress.grid(
            in_=parent,
            column=2,
            row=4,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtShowName.grid(
            in_=parent,
            column=2,
            row=5,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtSeason.grid(
            in_=parent,
            column=2,
            row=6,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtEpisode.grid(
            in_=parent,
            column=2,
            row=7,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._txtTitle.grid(
            in_=parent,
            column=2,
            row=8,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=7,
            rowspan=1,
            sticky="nsew"
        )
        self._lbl_loggedin.grid(
            in_=parent,
            column=1,
            row=11,
            columnspan=2,
            ipadx=0,
            ipady=0,
            padx=5,
            pady=5,
            rowspan=1,
            sticky="sw"
        )
        self._lbl_version.grid(
            in_=parent,
            column=1,
            row=1,
            columnspan=1,
            ipadx=0,
            ipady=0,
            padx=0,
            pady=0,
            rowspan=1,
            sticky="nw"
        )

        # Resize Behavior
        parent.resizable(False, False)
        parent.grid_rowconfigure(1, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(2, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(3, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(4, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(5, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(6, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(7, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(8, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(9, weight=0, minsize=30, pad=0)
        parent.grid_rowconfigure(10, weight=0, minsize=60, pad=0)
        parent.grid_rowconfigure(11, weight=0, minsize=30, pad=5)
        parent.grid_columnconfigure(1, weight=0, minsize=70, pad=5)
        parent.grid_columnconfigure(2, weight=0, minsize=175, pad=0)
        parent.grid_columnconfigure(3, weight=0, minsize=175, pad=0)
        parent.grid_columnconfigure(4, weight=0, minsize=400, pad=0)
